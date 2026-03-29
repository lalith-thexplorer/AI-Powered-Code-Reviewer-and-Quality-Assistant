import streamlit as st
import os
from core import parser
import zipfile
import io
import re
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from core import convert_docstring_style
from core import fix_code_with_ai
from core import generate_workspace_tests
from core.fix_code_with_ai import AVAILABLE_MODELS, DEFAULT_MODEL
import importlib
from faq.faq_data import FAQ_DATA
from faq.faq_component import get_current_screen_id, render_faq_button, render_faq_popup

def compress_name(name, max_len=18):
    """Universal utility to shorten long filenames/paths with ellipsis in the middle."""
    if not name or len(name) <= max_len:
        return name
    half = (max_len - 3) // 2
    return name[:half] + "..." + name[-half:]

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Bootstrap Icons
st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">', unsafe_allow_html=True)

# Custom CSS for modern dark productivity IDE aesthetic
st.markdown("""
<style>
    /* Dark base & glowing yellow accents */
    :root {
        --primary-yellow: #ffbf00;
        --bg-dark: #121212;
        --card-bg: #1e1e1e;
        --text-color: #e0e0e0;
        --outline-color: #333333;
        --border-radius: 12px;
        --sidebar-width: 260px;
    }
    
    html {
        scroll-behavior: smooth !important;
    }
    
    /* Freeze the entire page scroll — only inner panels should scroll */
    body, .stApp {
        background-color: var(--bg-dark);
        color: var(--text-color);
        font-family: 'Inter', 'Segoe UI', sans-serif;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Disable the main black Streamlit header bar completely */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
    }
    
    /* ============================================================
       Offset the main content area to account for fixed sidebar & top tabs
       ============================================================ */
    .block-container {
        padding-top: 0 !important;
        /* Offset the entire main block precisely to the right of the locked sidebar */
        padding-left: calc(var(--sidebar-width) + 1rem) !important;
        padding-right: 1.5rem !important;
        padding-bottom: 0 !important; /* Remove bottom padding to let editor hit the bottom */
        max-width: none !important;
        margin-top: 42px !important; /* Push main content down safely below the fixed tab strip */
    }
    
    /* ============================================================
       SIDEBAR — always visible, never collapsible
       ============================================================ */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 2px solid var(--outline-color) !important;
        /* Lock the sidebar open at all times */
        transform: none !important;
        visibility: visible !important;
        pointer-events: auto !important;
        min-width: var(--sidebar-width) !important;
        max-width: var(--sidebar-width) !important;
        width: var(--sidebar-width) !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        z-index: 9998 !important;
        overflow-y: auto !important;
        isolation: isolate !important;
    }

    /* Prevent the sidebar from ever sliding off-screen */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: none !important;
        margin-left: 0 !important;
    }
    
    /* Hide ALL collapse / expand controls — the hamburger, the arrow chevron, everything */
    [data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="stSidebarCollapsedControl"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"],
    .st-emotion-cache-dvne4q,          /* common collapse button cache class */
    .st-emotion-cache-1wrcr25 {        /* another common one */
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }

    /* Remove native padding at the top of the sidebar */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0 !important;
        margin-top: -10px !important;
    }
    
    /* --- Hide the sidebar collapse << button --- */
    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNavSeparator"],
    .st-emotion-cache-6q9sum,
    .st-emotion-cache-1wbqy5l {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* Explorer header */
    .explorer-header {
        margin-top: 0 !important;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--primary-yellow);
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--outline-color);
        margin-bottom: 0.75rem;
    }

    /* Section labels in sidebar */
    .sidebar-section-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #555;
        margin: 0.75rem 0 0.4rem;
        font-weight: 600;
    }

    /* Sidebar file uploader — yellow dashed style */
    .sidebar-uploader div[data-testid="stFileUploaderDropzone"] {
        border: 1px dashed var(--primary-yellow) !important;
        background: rgba(255, 191, 0, 0.05) !important;
        border-radius: 8px !important;
        padding: 0.4rem !important;
    }
    .sidebar-uploader div[data-testid="stFileUploaderDropzone"]:hover {
        background: rgba(255, 191, 0, 0.12) !important;
    }
    
    /* File Uploader styling */
    div[data-testid="stFileUploaderDropzone"] {
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--outline-color) !important;
        background-color: var(--card-bg) !important;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--primary-yellow) !important;
    }
    
    /* Unify Sidebar native columns into a single file container */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
        background-color: var(--card-bg);
        border: 1px solid var(--outline-color);
        border-radius: 6px;
        padding: 0;
        gap: 0 !important;
        margin-bottom: 2px;
        align-items: center;
        overflow: hidden;
        display: flex !important;
        flex-wrap: nowrap !important;
    }
    
    /* Reset inner column padding and manage flex shrinking */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        padding: 0 !important;
        min-width: 0 !important;
    }
    
    /* Force the first column (filename) to shrink when squeezed */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        flex: 1 1 auto !important;
        width: auto !important;
    }
    
    /* Force the action columns to strictly preserve their size */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2),
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) {
        flex: 0 0 32px !important;
        min-width: 32px !important;
        width: 32px !important;
    }
    
    /* Open File Button styling */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        border: none !important;
        background: transparent !important;
        justify-content: flex-start !important;
        padding-left: 12px !important;
        padding-right: 4px !important;
        border-radius: 6px 0 0 6px !important;
        margin: 0 !important;
        width: 100% !important;
        transition: all 0.2s;
    }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(1) button:hover {
        color: var(--primary-yellow) !important;
        background-color: #252525 !important;
    }
    
    /* Action buttons styling (download & delete) */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        border: none !important;
        background: transparent !important;
        border-left: 1px solid var(--outline-color) !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        color: #888 !important;
        transition: all 0.2s;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        border-radius: 0 !important; /* reset */
    }
    
    /* Delete button corner radius */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        border-radius: 0 6px 6px 0 !important;
    }
    
    /* Hover effects */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
        background-color: transparent !important;
        color: var(--primary-yellow) !important;
        text-shadow: 0 0 8px rgba(255, 191, 0, 0.4); 
    }
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover {
        background-color: rgba(255, 107, 107, 0.1) !important;
        color: #ff6b6b !important;
        text-shadow: 0 0 8px rgba(255,107,107,0.4);
    }
    
    /* Hide BOTH button inner wrappers and text so they don't shift the icon */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button > div,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button p,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button > div,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button p {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Force Streamlit Tooltip and inner component wrappers to span the entire column exactly */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stElementContainer"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stTooltipIcon"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[class*="stTooltipIcon"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stTooltipHoverTarget"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stDownloadButton"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) > div,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stElementContainer"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stTooltipIcon"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[class*="stTooltipIcon"],
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stTooltipHoverTarget"] {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
        flex-direction: row !important;
    }

    /* Download Icon styles */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button::before {
        font-family: "bootstrap-icons" !important;
        content: "\\f30a" !important; /* Unicode for bi-download */
        font-size: 1.05rem !important;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        -webkit-font-smoothing: antialiased;
        display: block !important;
        margin: auto !important;
        transform: translateX(3px) !important;
    }

    /* Trash Icon styles */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(3) button::before {
        font-family: "bootstrap-icons" !important;
        content: "\\f5de" !important; /* Unicode for bi-trash */
        font-size: 1.05rem !important;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        -webkit-font-smoothing: antialiased;
        display: block !important;
        margin: auto !important;
    }

    /* Metric Cards */
    .metric-card {
        background-color: var(--card-bg);
        border: 1px solid var(--outline-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: var(--primary-yellow);
        margin-top: 0.5rem;
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #aaaaaa;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Expander elements */
    .streamlit-expanderHeader {
        border-radius: var(--border-radius) !important;
        background-color: var(--card-bg) !important;
        border: 1px solid var(--outline-color) !important;
        font-weight: 600 !important;
        margin-bottom: 0px !important;
    }
    
    /* Fix for expander content background */
    div[data-testid="stExpanderDetails"] {
        background-color: #1a1a1a !important;
        border: 1px solid var(--outline-color) !important;
        border-top: none !important;
        border-bottom-left-radius: var(--border-radius);
        border-bottom-right-radius: var(--border-radius);
        padding: 1rem !important;
    }
    
    /* Primary buttons (hollow yellow theme) */
    button[kind="primary"] {
        border-radius: 8px !important;
        background-color: rgba(255, 191, 0, 0.08) !important;
        color: var(--primary-yellow) !important;
        font-weight: 600 !important;
        border: 1px solid var(--primary-yellow) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* Force ALL child elements inside primary buttons to inherit the yellow */
    button[kind="primary"] *,
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] code {
        color: var(--primary-yellow) !important;
        background: transparent !important;
    }
    
    /* Hover state: fill with yellow, text turns black */
    button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        background-color: var(--primary-yellow) !important;
        box-shadow: 0 4px 16px rgba(255, 191, 0, 0.4) !important;
        color: #000000 !important;
    }
    
    button[kind="primary"]:hover *,
    button[kind="primary"]:hover p,
    button[kind="primary"]:hover span,
    button[kind="primary"]:hover code {
        color: #000000 !important;
    }

    /* ============================================================
       SELECTBOX / DROPDOWN — visible outline for all dropdowns
       ============================================================ */
    /* The main visible trigger box */
    [data-testid="stSelectbox"] > div > div,
    [data-baseweb="select"] > div {
        background-color: #1e1e2e !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stSelectbox"] > div > div:hover,
    [data-baseweb="select"] > div:hover {
        border-color: rgba(255, 191, 0, 0.5) !important;
    }
    /* Dropdown list menu */
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] {
        background-color: #1e1e2e !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 8px !important;
    }
    /* Individual option items */
    [data-baseweb="menu"] li {
        color: #e0e0e0 !important;
    }
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [aria-selected="true"] {
        background-color: rgba(255, 191, 0, 0.12) !important;
        color: #ffbf00 !important;
    }

    /* Test Suite Cards */
    .test-suite-card {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: transform 0.2s;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .test-suite-card:hover {
        transform: translateX(4px);
    }
    .ts-passed {
        background: rgba(126, 237, 159, 0.08) !important;
        border-left: 4px solid #7bed9f !important;
    }
    .ts-failed {
        background: rgba(255, 107, 107, 0.08) !important;
        border-left: 4px solid #ff6b6b !important;
    }
    .ts-partial {
        background: rgba(255, 159, 67, 0.08) !important;
        border-left: 4px solid #ff9f43 !important;
    }
    .ts-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .ts-icon {
        font-size: 1.2rem;
    }
    .ts-name {
        font-weight: 600;
        color: #e0e0e0;
        font-size: 0.95rem;
    }
    .ts-stats {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.9rem;
        color: #aaaaaa;
        background: rgba(0,0,0,0.2);
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* ============================================================
       TEST GROUP HEADERS & BADGES (Glow Effect)
       ============================================================ */
    .test-group-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 15px;
        background: rgba(126, 237, 159, 0.05);
        border: 1px solid rgba(126, 237, 159, 0.2);
        border-radius: 12px;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 0 20px rgba(126, 237, 159, 0.08); /* Glow */
    }
    
    .test-group-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #7bed9f; /* Mint green */
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    .test-group-badge {
        background: rgba(126, 237, 159, 0.15);
        color: #7bed9f;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid rgba(126, 237, 159, 0.3);
    }

    /* FIX ROW ALIGNMENT — button & model selector same baseline
       ============================================================ */
    /* Only push the fix-button column to the bottom; keep the selectbox column top-aligned */
    div[data-testid="column"]:has(button[kind="primary"]) {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-end !important;
    }
    
    /* ============================================================
       TAB BAR — fixed to top, starts RIGHT AFTER the sidebar
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        position: fixed !important;
        top: 0 !important;
        /* Start flush at the sidebar's right edge */
        left: var(--sidebar-width) !important;
        right: 0 !important;
        z-index: 9999 !important;
        
        gap: 2px;
        background-color: #171717;
        padding: 5px 5px 0 5px;
        border-radius: 0;
        border: none !important;
        border-top: 1px solid var(--outline-color) !important;
        border-bottom: 1px solid var(--outline-color) !important;
        margin: 0 !important;

        /* Ensure tabs flow left-to-right from that left edge */
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: flex-end !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #1a1a1a;
        border-radius: 6px 6px 0 0;
        gap: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 15px;
        padding-right: 15px;
        border: none !important;
        border-bottom: none !important;
        color: #888888;
        flex-shrink: 0;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--bg-dark) !important;
        color: var(--primary-yellow) !important;
        border-bottom: 2px solid var(--primary-yellow) !important;
    }

    /* ============================================================
       EDITOR WORKSPACE CONTAINER (Analytics pane)
       ============================================================ */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1.5rem 0 !important;
        /* Let the main body scroll handle scrolling, no inner scroll */
        height: auto !important; 
        overflow: visible !important;
    }

    /* ============================================================
       FILE HEADER (Big File Tab in Main Panel)
       ============================================================ */
    .main-file-header-container {
        background-color: var(--card-bg);
        border: 1px solid var(--outline-color);
        border-radius: 8px;
        padding: 0 !important;
        margin-bottom: 2rem;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center;
        overflow: hidden;
    }
    
    .main-file-header-container > div[data-testid="column"] {
        padding: 0 !important;
        min-width: 0 !important;
    }
    
    /* Title column: shrinks with ellipsis */
    .main-file-header-container > div:nth-child(1) {
        flex: 1 1 auto !important;
        width: auto !important;
        padding: 12px 18px !important;
    }
    
    .main-file-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-color);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;
        font-family: monospace;
    }
    
    /* Close button column: strict size */
    .main-file-header-container > div:nth-child(2) {
        flex: 0 0 100px !important;
        min-width: 100px !important;
        border-left: 1px solid var(--outline-color);
    }
    
    .main-file-header-container button {
        height: 100% !important;
        width: 100% !important;
        min-height: 52px !important;
        border: none !important;
        background: transparent !important;
        color: #888 !important;
        border-radius: 0 8px 8px 0 !important;
        transition: all 0.2s !important;
    }
    
    .main-file-header-container button:hover {
        background-color: rgba(255, 107, 107, 0.1) !important;
        color: #ff6b6b !important;
    }

    /* ── AI Fix pill badges ── */
    .fix-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        margin: 2px 3px;
        vertical-align: middle;
    }
    .fix-pill-added   { background: rgba(80,200,120,0.15); color: #50c878; border: 1px solid #50c878; }
    .fix-pill-modified{ background: rgba(255,191,0,0.12);  color: #ffbf00; border: 1px solid #ffbf00; }
    .fix-pill-error   { background: rgba(255,107,107,0.15);color: #ff6b6b; border: 1px solid #ff6b6b; }

    /* ── Modified code section divider ── */
    .modified-code-header {
        font-size: 1rem;
        font-weight: 700;
        color: #50c878;
        margin: 1.5rem 0 0.5rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #50c878;
    }

    /* ============================================================
       DASHBOARD SECTION GLASS CARDS
       Uses st.container(border=True) → targets the native wrapper
       div[data-testid="stVerticalBlockBorderWrapper"].
       Matched only when it contains a .sc-header as a direct child.
       ============================================================ */

    /* ── Base glass style for sections ── */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .sc-header) {
        background: rgba(18, 18, 28, 0.60) !important;
        backdrop-filter: blur(18px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
        border-radius: 18px !important;
        padding: 1.4rem 1.6rem 1.6rem !important;
        margin-bottom: 1.6rem !important;
        box-shadow:
            0 8px 32px rgba(0,0,0,0.35),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
        position: relative !important;
        overflow: visible !important;
        transition: all 0.3s ease !important;
        width: 90% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Section header strip inside cards */
    .sc-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }
    .sc-header-icon {
        font-size: 1.45rem;
        line-height: 1;
        filter: drop-shadow(0 0 8px currentColor);
    }
    .sc-header h2, .sc-header h3 {
        margin: 0 !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)


# State Management for IDE Layout
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'upload'
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}
if 'open_tabs' not in st.session_state:
    st.session_state.open_tabs = ['📊 Dashboard']
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if '_pending_tab_switch' not in st.session_state:
    st.session_state._pending_tab_switch = None
if 'fix_model' not in st.session_state:
    st.session_state.fix_model = DEFAULT_MODEL
if 'fixed_codes' not in st.session_state:
    st.session_state.fixed_codes = {}   # fname -> fixed source string
if '_converter_split' not in st.session_state:
    st.session_state._converter_split = {}   # key: fname -> {'result': str, 'scope': str}
if 'dash_search' not in st.session_state:
    st.session_state.dash_search = ""
if 'dash_active_tab' not in st.session_state:
    st.session_state.dash_active_tab = "Advanced Filters"
if 'active_section' not in st.session_state:
    st.session_state.active_section = "🏠 Home"
if 'dash_filter' not in st.session_state:
    st.session_state.dash_filter = "All"
if 'help_selected_card' not in st.session_state:
    st.session_state.help_selected_card = None


def render_faq_overlay():
    """Render floating FAQ button and screen-specific popup with safe fallback."""
    render_faq_button()

    screen_id = get_current_screen_id()
    screen_entry = FAQ_DATA.get(screen_id)
    general_entry = FAQ_DATA.get("general", {"screen_name": "General Help", "faqs": []})

    if not screen_entry or not screen_entry.get("faqs"):
        screen_id = "general"
        screen_entry = general_entry

    st.session_state.faq_screen_id = screen_id
    st.session_state.faq_open = bool(st.session_state.get("faq_open", False))
    render_faq_popup(
        screen_entry.get("screen_name", "General Help"),
        screen_entry.get("faqs", []),
    )

# ── Session Lifecycle Cleanup Hook ──
# Wipes temporary workspace files on app startup/refresh
if '_session_init' not in st.session_state:
    import shutil
    for d in ["workspace_context", "workspace_tests/dynamic", "workspace_tests/cached"]:
        if os.path.exists(d):
            try: shutil.rmtree(d)
            except: pass
    os.makedirs("workspace_context", exist_ok=True)
    os.makedirs("workspace_tests/dynamic", exist_ok=True)
    os.makedirs("workspace_tests/cached", exist_ok=True)
    st.session_state._session_init = True

def process_uploaded_files(uploaded_files_list):
    # Clear old test state when new files are uploaded
    st.session_state.pop('workspace_test_json', None)
    st.session_state.pop('_last_test_hash', None)
    st.session_state.pop('skipped_test_files', None)
    
    has_files = False
    for file in uploaded_files_list:
        if file.name.endswith('.py'):
            # Clear manual fixes if you re-upload the same file name
            st.session_state.fixed_codes.pop(file.name, None)
            
            content = file.getvalue().decode("utf-8")
            st.session_state.file_data[file.name] = {
                'content': content,
                'results': parser.parse_file(content)
            }
            if file.name not in st.session_state.open_tabs:
                st.session_state.open_tabs.append(file.name)
            has_files = True
        elif file.name.endswith('.zip'):
            try:
                with zipfile.ZipFile(io.BytesIO(file.getvalue())) as z:
                    for zinfo in z.infolist():
                        if zinfo.filename.endswith('.py') and not zinfo.filename.startswith('__MACOSX/'):
                            with z.open(zinfo) as f:
                                content = f.read().decode('utf-8')
                                st.session_state.fixed_codes.pop(zinfo.filename, None)
                                st.session_state.file_data[zinfo.filename] = {
                                    'content': content,
                                    'results': parser.parse_file(content)
                                }
                                if zinfo.filename not in st.session_state.open_tabs:
                                    st.session_state.open_tabs.append(zinfo.filename)
                                has_files = True
            except Exception as e:
                st.error(f"Error reading zip file {file.name}: {e}")
    
    # --- PROACTIVE PURGE ---
    # Delete existing dynamic tests for these files so they are forced to regenerate
    dynamic_dir = "workspace_tests/dynamic"
    os.makedirs(dynamic_dir, exist_ok=True)
    for fname in st.session_state.file_data.keys():
        d_path = os.path.join(dynamic_dir, f"test_{fname}")
        if os.path.exists(d_path):
            try: os.remove(d_path)
            except: pass

    # --- PROACTIVE GENERATION ---
    # If a file is 100% documented upon upload, try to generate tests immediately in the background
    # This prepares the 'dynamic' test suite so it's ready before the user clicks "Run Tests"
    to_proactively_generate = []
    for fname, fdata in st.session_state.file_data.items():
        # Only if it's perfectly documented
        if "error" not in fdata['results']:
            funcs = fdata['results'].get('functions', [])
            doc_funcs = [f for f in funcs if f.get('has_docstring')]
            if funcs and len(doc_funcs) == len(funcs):
                # Check if we already have it in cache or dynamic
                dynamic_path = os.path.join("workspace_tests/dynamic", f"test_{fname}")
                cache_path   = os.path.join("workspace_tests/cached", f"test_{fname}")
                if not os.path.exists(dynamic_path) and not os.path.exists(cache_path):
                    to_proactively_generate.append((fname, fdata['content'], doc_funcs))
    
    if to_proactively_generate:
        from concurrent.futures import ThreadPoolExecutor
        model_id = st.session_state.fix_model
        dynamic_dir = "workspace_tests/dynamic"
        os.makedirs(dynamic_dir, exist_ok=True)
        
        def _proactive_task(args):
            fn, code, funcs, mid = args
            try:
                # Force reload generator to pick up recent code changes
                importlib.reload(generate_workspace_tests)
                t_code = generate_workspace_tests.generate_pytest_for_file(fn, code, funcs, model=mid)
                tf_path = os.path.join(dynamic_dir, f"test_{fn}")
                os.makedirs(os.path.dirname(tf_path), exist_ok=True)
                with open(tf_path, "w", encoding="utf-8") as tf:
                    tf.write(t_code)
            except: pass

        with ThreadPoolExecutor(max_workers=len(to_proactively_generate)) as executor:
            executor.map(_proactive_task, [(f, c, fs, model_id) for f, c, fs in to_proactively_generate])

    return has_files

def render_single_file(fname, fl_data):
    results = fl_data['results']
    
    with st.container(border=True):
        # Hidden anchor so single-file tabs use the same styled section shell as the major dashboard tabs.
        st.markdown("<span class='sc-header' style='display:none'></span>", unsafe_allow_html=True)

        #st.markdown('<div class="main-file-header-container">', unsafe_allow_html=True)
        col_title, col_actions = st.columns([0.76, 0.24], gap="small")
        
        display_name = compress_name(fname)

        with col_title:
            st.markdown(f'<div class="main-file-title" title="{fname}">📄 {display_name}</div>', unsafe_allow_html=True)
        with col_actions:
            col_close, col_delete = st.columns(2, gap="small")
            with col_close:
                if st.button("Close File", key=f"close_btn_{fname}", help="Close this file tab (File remains in workspace sidebar)", use_container_width=True):
                    if fname in st.session_state.open_tabs:
                        st.session_state.open_tabs.remove(fname)
                        st.rerun()
            with col_delete:
                if st.button("Delete File", key=f"delete_tab_btn_{fname}", help="Remove this file from the workspace", use_container_width=True):
                    st.session_state.pop('workspace_test_json', None)
                    st.session_state.pop('_last_test_hash', None)
                    st.session_state.pop('skipped_test_files', None)

                    del st.session_state.file_data[fname]
                    st.session_state.fixed_codes.pop(fname, None)
                    if fname in st.session_state.open_tabs:
                        st.session_state.open_tabs.remove(fname)
                    st.rerun()
        st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)
        components.html("""
        <script>
        (function() {
            const applyColors = (attempts) => {
                const btns = window.parent.document.querySelectorAll('button');
                let found = 0;
                btns.forEach(btn => {
                    const txt = (btn.innerText || '').trim();
                    if (txt.includes('Close File')) {
                        btn.style.setProperty('background-color', 'rgba(255, 193, 7, 0.18)', 'important');
                        btn.style.setProperty('color', '#ffc107', 'important');
                        btn.style.setProperty('border', '1px solid rgba(255, 193, 7, 0.55)', 'important');
                        found++;
                    } else if (txt.includes('Delete File')) {
                        btn.style.setProperty('background-color', 'rgba(220, 53, 69, 0.18)', 'important');
                        btn.style.setProperty('color', '#ff6b6b', 'important');
                        btn.style.setProperty('border', '1px solid rgba(220, 53, 69, 0.55)', 'important');
                        found++;
                    }
                });
                if (found < 2 && attempts < 20) {
                    window.setTimeout(() => applyColors(attempts + 1), 80);
                }
            };
            window.setTimeout(() => applyColors(0), 50);
        })();
        </script>
        """, height=0, width=0)

                
        if "error" in results:
            st.error(f"Failed to parse `{fname}`: {results['error']}")
            return
            
        total_f = results.get('total_functions', 0)
        funcs = results.get('functions', [])
        doc_f = sum(1 for f in funcs if f.get('has_docstring'))
        undoc_f = total_f - doc_f
        cov = results.get('coverage', 0)
        
        if total_f == 0:
            cov_color = "#888888" # Neutral gray for N/A
            cov_str = "N/A"
        else:
            cov_color = "var(--primary-yellow)" if cov == 100 else ("#ff6b6b" if cov < 50 else "#feca57")
            cov_str = f"{cov:.1f}%"
        
        # ── Metrics: all 4 in one row, home-tab theme ──────────────
        st.markdown("<span class='home-metrics-anchor' style='display:none;'></span>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Functions</div>
                <div class="metric-value">{total_f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Documented</div>
                <div class="metric-value" style="color: var(--primary-yellow);">{doc_f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Undocumented</div>
                <div class="metric-value" style="color: #ff6b6b;">{undoc_f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Coverage</div>
                <div class="metric-value" style="color: {cov_color};">{cov_str}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)

        # ── Single "Current Code" block ──────────────────────────────────
        is_fixed = fname in st.session_state.fixed_codes
        current_code = st.session_state.fixed_codes[fname] if is_fixed else fl_data['content']
        code_label = "### ✨ Current Code  `(AI Fixed)`" if is_fixed else "### 📄 Current Code"

        # Diff pills when AI fix is active
        if is_fixed:
            original_lines_set = set(fl_data['content'].splitlines())
            fixed_lines_set    = set(current_code.splitlines())
            added_count   = len(fixed_lines_set - original_lines_set)
            removed_count = len(original_lines_set - fixed_lines_set)
            st.markdown(
                f'<span class="fix-pill fix-pill-added">+{added_count} lines added/modified</span>'
                f'<span class="fix-pill fix-pill-modified">−{removed_count} lines changed</span>',
                unsafe_allow_html=True
            )

        _do_copy = False
        code_hdr_col, code_act_col = st.columns([0.65, 0.35], gap="small")
        with code_hdr_col:
            st.markdown(code_label)
        with code_act_col:
            st.write("")
            dl_col, cp_col = st.columns(2, gap="small")
            with dl_col:
                dl_fname = f"fixed_{fname}" if is_fixed else fname
                st.download_button(
                    label="⬇️ Download",
                    data=current_code,
                    file_name=dl_fname,
                    mime="text/plain",
                    use_container_width=True,
                    key=f"dl_current_{fname}"
                )
            with cp_col:
                _do_copy = st.button("📋 Copy", key=f"copy_code_{fname}", use_container_width=True)

        st.code(current_code, language="python")

        # Copy to clipboard on button click
        if _do_copy:
            _escaped = current_code.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
            components.html(f"""<script>
            (function(){{
                var txt = `{_escaped}`;
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(txt);
                }} else {{
                    var ta = document.createElement('textarea');
                    ta.value = txt; document.body.appendChild(ta);
                    ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
                }}
            }})();
            </script>""", height=0, width=0)
            st.toast("📋 Copied to clipboard!")

        st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)

        st.markdown("### 🔍 Function Breakdown")
        
        if total_f == 0:
            st.info("No Functions found.")
        else:
            for func in funcs:
                icon = "✅" if func["has_docstring"] else "❌"
                expander_label = f"{icon} **{func['name']}** (Lines: {func['start_line']} - {func['end_line']})"
                
                with st.expander(expander_label):
                    st.markdown(f"**Name:** `{func['name']}`")
                    st.markdown(f"**Starting Line:** {func['start_line']}")
                    st.markdown(f"**Ending Line:** {func['end_line']}")
                    st.markdown(f"**Has Docstring:** {'Yes ✅' if func['has_docstring'] else 'No ❌'}")
                    if func['has_docstring']:
                        st.markdown("**Docstring Content:**")
                        st.code(func['docstring'], language='python')
                
        st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)
        st.markdown(f"### 📥 Export `{fname}` Report")
        
        st.markdown("**Choose export type:**")
        export_format = st.selectbox(f"Select Export Format for {fname}", ["JSON", "Markdown", "CSV", "Plain Text"], label_visibility="collapsed")
        
        export_content = ""
        if export_format == "JSON":
            import json
            export_data = {
                "metrics": {
                    "total_functions": total_f,
                    "functions_with_docstrings": doc_f,
                    "functions_missing_docstrings": undoc_f,
                    "coverage_percentage": cov if total_f > 0 else "N/A"
                },
                "file": fname,
                "results": results.copy()
            }
            if total_f == 0:
                export_data["results"]["coverage"] = "N/A"
            export_content = json.dumps(export_data, indent=4)
            lang = "json"
            mime_type = "application/json"
            ext = "json"
        elif export_format == "Markdown":
            md_lines = [f"# ⚡ AI Code Reviewer Report: `{fname}`\n"]
            md_lines.append(f"- **Total Functions:** {total_f}")
            md_lines.append(f"- **Functions with Docstrings:** {doc_f}")
            md_lines.append(f"- **Functions missing Docstrings:** {undoc_f}")
            md_lines.append(f"- **Coverage:** {cov_str}\n")
            md_lines.append("### Functions Breakdown\n")
            for f in funcs:
                doc_status = "✅ Documented" if f['has_docstring'] else "❌ Missing"
                md_lines.append(f"- **`{f['name']}`** _(Lines {f['start_line']}-{f['end_line']})_ — {doc_status}")
                if f['has_docstring']:
                    md_lines.append("  ```python")
                    doc_lines = f['docstring'].split('\\n')
                    for line in doc_lines:
                        md_lines.append(f"  {line}")
                    md_lines.append("  ```\n")
            export_content = "\n".join(md_lines)
            lang = "markdown"
            mime_type = "text/markdown"
            ext = "md"
        elif export_format == "CSV":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Function Name", "Start Line", "End Line", "Has Docstring", "Docstring Content"])
            for f in funcs:
                doc_status = "TRUE" if f['has_docstring'] else "FALSE"
                writer.writerow([f['name'], f['start_line'], f['end_line'], doc_status, f.get('docstring', '')])
            export_content = output.getvalue()
            lang = "csv"
            mime_type = "text/csv"
            ext = "csv"
        else: # Plain Text
            txt_lines = [f"REPORT FOR FILE: {fname}\n" + "="*40]
            txt_lines.append(f"Total Functions: {total_f}")
            txt_lines.append(f"Functions with Docstrings: {doc_f}")
            txt_lines.append(f"Functions missing Docstrings: {undoc_f}")
            txt_lines.append(f"Coverage: {cov_str}\n")
            txt_lines.append("FUNCTION BREAKDOWN\n" + "-"*40)
            for f in funcs:
                doc_status = "YES" if f['has_docstring'] else "NO"
                txt_lines.append(f"* {f['name']} (Lines {f['start_line']}-{f['end_line']}) | Documented: {doc_status}")
                if f['has_docstring']:
                    txt_lines.append(f"  Docstring: {f['docstring']}")
            export_content = "\n".join(txt_lines)
            lang = "text"
            mime_type = "text/plain"
            ext = "txt"
            
        st.write("")
        st.download_button(
            label=f"⬇️ Download {fname} Report as .{ext}",
            data=export_content,
            file_name=f"{fname.replace('.py', '')}_report.{ext}",
            mime=mime_type,
            use_container_width=True
        )
        
        st.write("")
        st.markdown("**Live Preview:**")
        st.code(export_content, language=lang)

def render_docstring_converter():
    """Render the Docstring Style Converter section of the dashboard."""

    if not st.session_state.file_data:
        st.info("Upload Python files first to use the Style Converter.")
        return

    all_files = list(st.session_state.file_data.keys())

    # ── File selector
    sel_col, style_col = st.columns([0.55, 0.45])
    with sel_col:
        st.markdown("**File Selection:**")
        selected_file = st.selectbox(
            "Select File",
            options=all_files,
            index=0,
            key="conv_file_selector",
            label_visibility="collapsed",
        )

    file_content = st.session_state.file_data[selected_file]['content']

    # Always check the LATEST content (could be fixed by AI)
    live_content = st.session_state.fixed_codes.get(selected_file, file_content)

    # ── Detect style
    detected = convert_docstring_style.detect_style(live_content)
    STYLE_COLORS = {
        "Google":          ("#ffd166", "🟡"),
        "reST":            ("#26c6da", "🔵"),
        "NumPy":           ("#a066ff", "🟣"),
        "Mixed":           ("#ff4d4d", "🔀"),
        "None/Incomplete": ("#ff6b6b", "⚠️"),
    }
    s_color, s_icon = STYLE_COLORS.get(detected, ("#888", "❓"))

    with style_col:
        st.markdown("**Detected Style:**")
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.05);border:1px solid {s_color};"
            f"border-radius:8px;padding:6px 14px;display:flex;align-items:center;gap:12px; height: 38px;'>"
            f"<span style='font-size:1.3rem'>{s_icon}</span>"
            f"<div style='font-weight:700;color:{s_color};font-size:1rem;margin-top:2px;'>{detected}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    has_docs = detected != "None/Incomplete"

    # ── Scope selector + code preview (only when docs exist for conversion)
    ALL_STYLES = ["Google", "reST", "NumPy"]
    split_key = f"{selected_file}__conv"

    if has_docs:
        funcs = st.session_state.file_data[selected_file]['results'].get('functions', [])
        func_names = [f["name"] for f in funcs]
        scope_options = ["📄 Whole File"] + [f"⚙️ {n}" for n in func_names]

        # 4-column layout for files with docstrings
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([0.25, 0.25, 0.25, 0.25])
        
        with ctrl_col1:
            scope_sel = st.selectbox("Scope", options=scope_options, key=f"conv_scope_{selected_file}",
                                     label_visibility="visible")

        is_whole = scope_sel == "📄 Whole File"
        func_name = "" if is_whole else scope_sel.replace("⚙️ ", "")

        # Target style selector + convert
        available_targets = [s for s in ALL_STYLES if s != detected]
        with ctrl_col2:
            target_style = st.selectbox("Convert to", options=available_targets,
                                        key=f"conv_target_{selected_file}", label_visibility="visible")
        with ctrl_col3:
            conv_model = st.selectbox(
                "Model", options=list(AVAILABLE_MODELS.keys()),
                index=list(AVAILABLE_MODELS.keys()).index(st.session_state.fix_model),
                format_func=lambda x: AVAILABLE_MODELS[x],
                key=f"conv_model_{selected_file}", label_visibility="visible"
            )
        with ctrl_col4:
            st.write("")
            st.write("")
            if st.button("⚡ Convert", key=f"conv_btn_{selected_file}", type="primary", use_container_width=True):
                with st.spinner(f"🔄 Converting to {target_style} style…"):
                    try:
                        result, tests = convert_docstring_style.convert_style(
                            live_content, target_style,
                            scope="whole_file" if is_whole else "function",
                            func_name=func_name, model=conv_model,
                            filename=selected_file
                        )
                        st.session_state._converter_split[split_key] = {
                            "result": result, "original": live_content, "tests": tests,
                            "scope": "whole_file" if is_whole else "function",
                            "func_name": func_name, "target_style": target_style,
                        }
                        st.rerun()
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")

        # Code preview processing
        if is_whole:
            preview_code = live_content
        else:
            # Slice function from source
            try:
                import ast as _ast
                tree = _ast.parse(live_content)
                lines = live_content.splitlines()
                preview_code = live_content
                for node in _ast.walk(tree):
                    if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)) and node.name == func_name:
                        preview_code = "\n".join(lines[node.lineno - 1:node.end_lineno])
                        break
            except Exception:
                preview_code = live_content

    else:
        # No / incomplete docstrings → Generate mode
        st.info("⚠️ No complete docstrings detected. You can generate them using AI.")
        
        # 3-column layout for files without docstrings
        gen_col1, gen_col2, gen_col3 = st.columns([0.35, 0.35, 0.30])
        with gen_col1:
            gen_style = st.selectbox("Generate in style", options=ALL_STYLES,
                                     key=f"gen_style_{selected_file}", label_visibility="visible")
        with gen_col2:
            gen_model = st.selectbox(
                "Model", options=list(AVAILABLE_MODELS.keys()),
                index=list(AVAILABLE_MODELS.keys()).index(st.session_state.fix_model),
                format_func=lambda x: AVAILABLE_MODELS[x],
                key=f"gen_model_{selected_file}", label_visibility="visible"
            )
        with gen_col3:
            st.write("")
            st.write("")
            if st.button("✨ Generate", key=f"gen_btn_{selected_file}", type="primary", use_container_width=True):
                with st.spinner(f"✨ Generating {gen_style} docstrings…"):
                    try:
                        result, tests = convert_docstring_style.generate_docstrings(
                            live_content, gen_style, model=gen_model,
                            filename=selected_file
                        )
                        st.session_state._converter_split[split_key] = {
                            "result": result, "original": live_content, "tests": tests,
                            "scope": "whole_file", "func_name": "",
                            "target_style": gen_style,
                        }
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
                        
        preview_code = live_content

    # ── Unified view
    if split_key in st.session_state._converter_split:
        data = st.session_state._converter_split[split_key]
        result_code = data["result"]
        target_style = data["target_style"]

        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown("**🔵 Current Code**")
            with st.container(height=500):
                st.code(preview_code, language="python")

        with right_col:
            st.markdown(f"**🟢 {target_style} Style**")
            with st.container(height=500):
                st.code(result_code, language="python")

        # Action row (moved strictly below the split view)
        st.markdown("<br>", unsafe_allow_html=True)
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            # Apply
            if st.button("💾 Apply", key=f"conv_apply_{selected_file}", type="primary", use_container_width=True):
                st.session_state.fixed_codes[selected_file] = result_code
                st.session_state.file_data[selected_file]['results'] = parser.parse_file(result_code)
                
                # Cache tests
                if data.get("tests"):
                    os.makedirs("workspace_tests/cached", exist_ok=True)
                    cache_path = f"workspace_tests/cached/test_{selected_file}"
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(data["tests"])
                
                del st.session_state._converter_split[split_key]
                st.toast("✅ Applied to source code and cached tests!")
                st.rerun()

        with a2:
            # Dismiss
            if st.button("❌ Dismiss", key=f"conv_dismiss_{selected_file}", use_container_width=True):
                del st.session_state._converter_split[split_key]
                st.rerun()

        with a3:
            # Copy via JS injection
            if st.button("📋 Copy", key=f"conv_copy_{selected_file}", use_container_width=True):
                safe_code = result_code.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                import time as _time
                components.html(f"""
                <script id="copy-{_time.time()}">
                navigator.clipboard.writeText(`{safe_code}`).then(() => {{
                    console.log('Copied to clipboard');
                }});
                </script>
                """, height=0, width=0)
                st.toast("✅ Copied to clipboard!", icon="📋")

        with a4:
            # Download
            st.download_button(
                "⬇️ Download",
                data=result_code,
                file_name=f"{selected_file.replace('.py', '')}_{target_style.lower()}.py",
                mime="text/x-python",
                key=f"conv_dl_{selected_file}",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔍 Changes", expanded=True):
            import difflib
            diff = list(difflib.unified_diff(
                preview_code.splitlines(),
                result_code.splitlines(),
                fromfile="Current Code",
                tofile="Generated Code",
                lineterm=""
            ))
            
            if not diff:
                st.info("No changes detected.")
            else:
                diff_text = "\n".join(diff)
                with st.container(height=500):
                    st.code(diff_text, language="diff")
    else:
        st.markdown("**Current Code:**")
        with st.container(height=500):
            st.code(preview_code, language="python")

    st.markdown("---")


def render_overall_dashboard():

    # ── Compute metrics (outside containers so values are available for export later)
    total_files = len(st.session_state.file_data)
    total_funcs = 0
    total_doc_funcs = 0
    files_with_docstrings = 0
    
    for fname, fdata in st.session_state.file_data.items():
        if "error" not in fdata['results']:
            f_results = fdata['results']
            total_funcs += f_results.get('total_functions', 0)
            funcs = f_results.get('functions', [])
            f_doc_funcs = sum(1 for f in funcs if f.get('has_docstring'))
            total_doc_funcs += f_doc_funcs
            if f_doc_funcs > 0:
                files_with_docstrings += 1
                
    total_undoc_funcs = total_funcs - total_doc_funcs
        
    if total_funcs > 0:
        overall_cov = (total_doc_funcs / total_funcs) * 100
    else:
        overall_cov = 100.0 if total_files > 0 else 0.0
        
    # Calculate PEP stats
    total_errors = 0
    files_with_errors = 0
    functions_with_errors = 0
    for fname, fdata in st.session_state.file_data.items():
        if "error" not in fdata['results']:
            f_errors = fdata['results'].get('total_docstring_errors', 0)
            total_errors += f_errors
            if f_errors > 0:
                files_with_errors += 1
            for func in fdata['results'].get('functions', []):
                if len(func.get('docstring_errors', [])) > 0:
                    functions_with_errors += 1
    clean_functions = total_funcs - functions_with_errors
        
    # Selection logic for Sections
    active = st.session_state.active_section
    
    # ── Section Theme Colors for Glowing Accents ──
    section_themes = {
        "🏠 Home": "#ffbf00",
        "🎛️ Dashboard": "#a066ff",
        "✅ Validation": "#ff7043",
        "📝 DocStrings": "#26c6da",
        "📈 Metrics": "#7cff4f"
    }
    t_color = section_themes.get(active, "#333333")
    
    # Inject dynamic styling for the active section container
    st.markdown(f"""
    <style>
        body, .stApp {{
            background-color: #0d0d0d !important;
            background-image:
                radial-gradient(ellipse 900px 700px at 60% 50%, {t_color}55 0%, transparent 65%),
                radial-gradient(ellipse 600px 500px at 20% 80%, {t_color}30 0%, transparent 55%),
                radial-gradient(ellipse 400px 300px at 85% 15%, {t_color}22 0%, transparent 50%) !important;
        }}

        /* ── Section container: tinted border + matching glow ── */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .sc-header) {{
            background: rgba(10, 10, 20, 0.55) !important;
            backdrop-filter: blur(24px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
            
            /* High-fidelity Glass Borders: color-matched rim highlights */
            border-top: 1px solid {t_color}99 !important;
            border-left: 1px solid {t_color}55 !important;
            border-right: 1px solid {t_color}44 !important;
            border-bottom: 1px solid {t_color}44 !important;
            
            box-shadow:
                0 8px 32px rgba(0,0,0,0.5),
                0 0 0 1px {t_color}22,
                inset 0 1px 0 {t_color}55 !important;
                
            border-radius: 18px !important;
            padding: 1.4rem 1.6rem 1.6rem !important;
            margin-bottom: 1.6rem !important;
            width: 90% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            transition: all 0.4s ease !important;
        }}

        .sc-header-icon {{
            filter: drop-shadow(0 0 10px {t_color}88);
        }}

        /* ── Section header divider takes the theme color ── */
        .sc-header {{
            border-bottom: 1px solid {t_color}33 !important;
        }}

        /* ── Unified Dashboard Sub-Section Panels ── */
        .dashboard-panel {{
            background: rgba(15, 16, 26, 0.62);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 3px solid {t_color}99;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22);
        }}

        .dashboard-panel-title {{
            margin: 0;
            font-size: 1.35rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.35px;
            line-height: 1.2;
        }}

        .dashboard-panel-subtitle {{
            margin-top: 0.35rem;
            font-size: 0.96rem;
            color: #c9cada;
            line-height: 1.45;
        }}

        .dashboard-panel-divider {{
            height: 1px;
            width: 100%;
            margin: 0.85rem 0 1rem 0;
            background: linear-gradient(90deg, {t_color}55 0%, rgba(255, 255, 255, 0.08) 45%, transparent 100%);
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) .metric-card {{
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.10) 0%, rgba(160, 102, 255, 0.18) 24%, rgba(18, 18, 30, 0.80) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.16) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            box-shadow:
                0 10px 28px rgba(0, 0, 0, 0.24),
                0 0 0 1px rgba(160, 102, 255, 0.10),
                inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
            margin-bottom: 1.15rem !important;
            height: 128px !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) .metric-card:hover {{
            transform: translateY(-2px) !important;
            border-color: rgba(160, 102, 255, 0.38) !important;
            box-shadow:
                0 14px 34px rgba(0, 0, 0, 0.28),
                0 0 18px rgba(160, 102, 255, 0.14),
                inset 0 1px 0 rgba(255, 255, 255, 0.09) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) .metric-title {{
            color: #cbbde8 !important;
            letter-spacing: 1.15px !important;
            font-size: 0.8rem !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) .metric-value {{
            color: #f7f2ff !important;
            text-shadow: 0 0 18px rgba(160, 102, 255, 0.28) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) [data-testid="stDataFrame"] {{
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            background: rgba(10, 11, 20, 0.92) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) [data-testid="stDataFrame"] [role="columnheader"] {{
            background: linear-gradient(180deg, rgba(160, 102, 255, 0.24) 0%, rgba(28, 20, 50, 0.92) 100%) !important;
            color: #f7f2ff !important;
            border-bottom: 1px solid rgba(160, 102, 255, 0.38) !important;
            font-weight: 700 !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) [data-testid="stDataFrame"] [role="gridcell"] {{
            background: rgba(12, 13, 22, 0.9) !important;
            color: #ececf7 !important;
            border-color: rgba(160, 102, 255, 0.12) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) [data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {{
            background: rgba(33, 24, 58, 0.96) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) div[data-testid="stTextInput"] input {{
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(160, 102, 255, 0.26) !important;
            color: #f7f2ff !important;
            border-radius: 12px !important;
            backdrop-filter: blur(14px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(14px) saturate(180%) !important;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) div[data-testid="stTextInput"] input::placeholder {{
            color: #b8b1ca !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-panel) div[data-testid="stTextInput"] input:focus {{
            border-color: rgba(160, 102, 255, 0.62) !important;
            box-shadow: 0 0 0 1px rgba(160, 102, 255, 0.24), 0 0 18px rgba(160, 102, 255, 0.16) !important;
        }}

        /* ── Home Metrics Tiles themed with active section color ── */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.home-metrics-anchor) .metric-card {{
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, {t_color}22 24%, rgba(18, 18, 30, 0.80) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-left: 3px solid {t_color}99 !important;
            border-radius: 16px !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            box-shadow:
                0 10px 26px rgba(0, 0, 0, 0.24),
                0 0 0 1px {t_color}22,
                inset 0 1px 0 rgba(255, 255, 255, 0.10) !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.home-metrics-anchor) .metric-card:hover {{
            transform: translateY(-2px) !important;
            border-color: {t_color}66 !important;
            box-shadow:
                0 14px 34px rgba(0, 0, 0, 0.28),
                0 0 18px {t_color}33,
                inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.home-metrics-anchor) .metric-title {{
            color: #d8d0b0 !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.home-metrics-anchor) .metric-value {{
            text-shadow: none !important;
        }}

        .dashboard-filter-note {{
            margin: 0.15rem 0 0.8rem 0;
            color: #d3d5e4;
            font-size: 0.93rem;
        }}

        /* ── Help Guide clickable cards (metric-card style) ── */
        div[data-testid="stButton"][class*="st-key-help_card_btn_"] > button {{
            min-height: 122px !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.10) 0%, rgba(160, 102, 255, 0.18) 24%, rgba(18, 18, 30, 0.80) 100%) !important;
            color: #f7f2ff !important;
            font-weight: 700 !important;
            text-align: left !important;
            padding: 0.95rem 1rem !important;
            backdrop-filter: blur(14px) saturate(170%) !important;
            -webkit-backdrop-filter: blur(14px) saturate(170%) !important;
            box-shadow:
                0 10px 26px rgba(0, 0, 0, 0.22),
                0 0 0 1px rgba(160, 102, 255, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.10) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
        }}

        div[data-testid="stButton"][class*="st-key-help_card_btn_"] > button:hover {{
            transform: translateY(-2px) !important;
            border-color: rgba(160, 102, 255, 0.40) !important;
            box-shadow:
                0 14px 34px rgba(0, 0, 0, 0.28),
                0 0 20px rgba(160, 102, 255, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
        }}

        /* ── Strong Glowing Content Separator ── */
        .dash-content-separator {{
            height: 2px;
            width: 100%;
            margin: 0.8rem 0 1.5rem 0;
            background: linear-gradient(
                90deg,
                transparent 0%,
                {t_color}55 12%,
                {t_color}bb 35%,
                {t_color} 50%,
                {t_color}bb 65%,
                {t_color}55 88%,
                transparent 100%
            );
            box-shadow:
                0 0 16px {t_color}88,
                0 0 32px {t_color}55,
                0 0 50px {t_color}22;
            border-radius: 2px;
            position: relative;
        }}

        .dash-content-separator::after {{
            content: '';
            position: absolute;
            top: 4px;
            left: 8%;
            right: 8%;
            height: 1px;
            background: linear-gradient(90deg, transparent, {t_color}33, transparent);
            border-radius: 1px;
        }}

        /* ── Dashboard navbar embedded title (leftmost col of frosted bar) ── */
        .dash-navbar-title {{
            font-size: 1.08rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 2.6rem;
            padding-left: 0.5rem;
            text-shadow: 0 0 22px rgba(160, 102, 255, 0.65), 0 0 6px rgba(160, 102, 255, 0.35);
        }}

    </style>
    """, unsafe_allow_html=True)

    if active == "🎛️ Dashboard":
        with st.container(border=True):
            # Hidden anchor keeps the outer glass-container CSS selector (:has(.sc-header)) working
            st.markdown("<span class='sc-header' style='display:none'></span>", unsafe_allow_html=True)

            # Build list of all functions across all files
            all_functions = []
            for fname, fdata in st.session_state.file_data.items():
                if "error" not in fdata['results']:
                    for func in fdata['results'].get('functions', []):
                        # add file context to function
                        func_copy = func.copy()
                        func_copy['file'] = fname
                        all_functions.append(func_copy)

            def render_dashboard_panel_header(icon: str, title: str, subtitle: str):
                st.markdown(
                    f"""
                    <div class='dashboard-panel'>
                        <div class='dashboard-panel-title'>{icon} {title}</div>
                        <div class='dashboard-panel-subtitle'>{subtitle}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                        
            # ── Dashboard Tabs (Frosted Glass Nav Bar) ──
            st.markdown("""
            <style>
            /* ── Frosted Glass Tab Navigation Bar ──
               Target: the stHorizontalBlock (columns row) that is a DIRECT child of
               the stVerticalBlock which contains the #dash-tabs-target anchor.
               This avoids matching any parent containers.
            */
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target)
            > div[data-testid="stHorizontalBlock"] {
                background: rgba(160, 102, 255, 0.07) !important;
                backdrop-filter: blur(22px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(22px) saturate(200%) !important;
                border: 1px solid rgba(160, 102, 255, 0.18) !important;
                border-top: 1px solid rgba(160, 102, 255, 0.42) !important;
                border-radius: 16px !important;
                padding: 0.35rem 0.5rem !important;
                box-shadow:
                    0 4px 28px rgba(0, 0, 0, 0.38),
                    0 0 0 1px rgba(160, 102, 255, 0.06),
                    inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
            }

            /* Hide anchor span (CSS-targeting only) */
            span#dash-tabs-target { display: none !important; }

            /* ── Inactive Tab Buttons ── */
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button[kind="secondary"] {
                background: transparent !important;
                border: 1px solid rgba(160, 102, 255, 0.22) !important;
                color: #bba8d8 !important;
                border-radius: 10px !important;
                font-weight: 500 !important;
                font-size: 0.85rem !important;
                transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button[kind="secondary"]:hover {
                background: rgba(160, 102, 255, 0.14) !important;
                border-color: rgba(160, 102, 255, 0.55) !important;
                color: #dccfff !important;
                box-shadow: 0 0 14px rgba(160, 102, 255, 0.22) !important;
                transform: translateY(-1px) !important;
            }

            /* ── Active (Primary) Tab Button ── */
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button[kind="primary"] {
                background: linear-gradient(145deg, rgba(160, 102, 255, 0.38) 0%, rgba(120, 72, 210, 0.44) 100%) !important;
                border: 1px solid rgba(160, 102, 255, 0.78) !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                font-size: 0.85rem !important;
                box-shadow:
                    0 4px 18px rgba(160, 102, 255, 0.4),
                    0 0 0 0.5px rgba(255, 255, 255, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            /* ── Prevent text overflow on tab buttons — show ellipsis ── */
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button {
                overflow: hidden !important;
            }
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button > div {
                overflow: hidden !important;
                width: 100% !important;
            }
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button div[data-testid="stMarkdownContainer"] {
                overflow: hidden !important;
                width: 100% !important;
            }
            div[data-testid="stVerticalBlock"]:has(span#dash-tabs-target) button p {
                display: block !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                white-space: nowrap !important;
                max-width: 100% !important;
                width: 100% !important;
                margin: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            tabs_cont = st.container()
            with tabs_cont:
                st.markdown("<span id='dash-tabs-target'></span>", unsafe_allow_html=True)
                dcol0, dcol1, dcol2, dcol3, dcol4, dcol5 = st.columns(6)
            with dcol0:
                st.markdown("<div class='dash-navbar-title'>🎛️ Dashboard</div>", unsafe_allow_html=True)
            with dcol1:
                if st.button("🔍 Advanced Filters", use_container_width=True, type="primary" if st.session_state.dash_active_tab == "Advanced Filters" else "secondary"):
                    st.session_state.dash_active_tab = "Advanced Filters"
                    st.rerun()
            with dcol2:
                if st.button("🔎 Search", use_container_width=True, type="primary" if st.session_state.dash_active_tab == "Search" else "secondary"):
                    st.session_state.dash_active_tab = "Search"
                    st.rerun()
            with dcol3:
                if st.button("🧪 Tests", use_container_width=True, type="primary" if st.session_state.dash_active_tab == "Tests" else "secondary"):
                    st.session_state.dash_active_tab = "Tests"
                    st.rerun()
            with dcol4:
                if st.button("📥 Export", use_container_width=True, type="primary" if st.session_state.dash_active_tab == "Export" else "secondary"):
                    st.session_state.dash_active_tab = "Export"
                    st.rerun()
            with dcol5:
                if st.button("💡 Help", use_container_width=True, type="primary" if st.session_state.dash_active_tab == "Help" else "secondary"):
                    st.session_state.dash_active_tab = "Help"
                    st.rerun()

            st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)

            if st.session_state.dash_active_tab == "Advanced Filters":
                with st.container(border=True):
                    render_dashboard_panel_header(
                        "🔍",
                        "Advanced Filters",
                        "Filter functions by documentation status and get a quick quality snapshot for your current workspace.",
                    )

                    advanced_records = []
                    for func in all_functions:
                        docstring_error_count = len(func.get('docstring_errors', []))
                        has_docstring = func.get('has_docstring', False)
                        if not has_docstring:
                            documentation_state = "No doc string"
                            validation_state = "Not checked"
                        elif docstring_error_count == 0:
                            documentation_state = "Has doc string"
                            validation_state = "Looks good"
                        else:
                            documentation_state = "Has doc string"
                            validation_state = "Has issues"

                        advanced_records.append(
                            {
                                "name": func['name'],
                                "file": func['file'],
                                "line": func['start_line'],
                                "documentation_state": documentation_state,
                                "validation_state": validation_state,
                                "docstring_error_count": docstring_error_count,
                            }
                        )

                    total_dash_funcs = len(advanced_records)
                    has_docstring_count = sum(1 for item in advanced_records if item['documentation_state'] == "Has doc string")
                    no_docstring_count = sum(1 for item in advanced_records if item['documentation_state'] == "No doc string")
                    file_options = ["All files"] + sorted({item['file'] for item in advanced_records})
                    status_options = ["All", "Has doc string", "No doc string"]
                    validation_options = ["Any", "Looks good", "Has issues", "Not checked"]
                    sort_options = [
                        "Function name (A-Z)",
                        "Function name (Z-A)",
                        "File name (A-Z)",
                        "Line number (Low-High)",
                        "Most validation issues",
                    ]

                    selected_status = st.session_state.get("dash_adv_status", "All")
                    if selected_status not in status_options:
                        selected_status = "All"
                    selected_file = st.session_state.get("dash_adv_file", "All files")
                    if selected_file not in file_options:
                        selected_file = "All files"
                    selected_validation = st.session_state.get("dash_adv_validation", "Any")
                    if selected_validation not in validation_options:
                        selected_validation = "Any"
                    selected_sort = st.session_state.get("dash_adv_sort", "Function name (A-Z)")
                    if selected_sort not in sort_options:
                        selected_sort = "Function name (A-Z)"

                    filtered_records = advanced_records
                    if selected_status != "All":
                        filtered_records = [item for item in filtered_records if item['documentation_state'] == selected_status]
                    if selected_file != "All files":
                        filtered_records = [item for item in filtered_records if item['file'] == selected_file]
                    if selected_validation != "Any":
                        filtered_records = [item for item in filtered_records if item['validation_state'] == selected_validation]

                    if selected_sort == "Function name (A-Z)":
                        filtered_records = sorted(filtered_records, key=lambda item: item['name'].lower())
                    elif selected_sort == "Function name (Z-A)":
                        filtered_records = sorted(filtered_records, key=lambda item: item['name'].lower(), reverse=True)
                    elif selected_sort == "File name (A-Z)":
                        filtered_records = sorted(filtered_records, key=lambda item: (item['file'].lower(), item['line']))
                    elif selected_sort == "Line number (Low-High)":
                        filtered_records = sorted(filtered_records, key=lambda item: (item['line'], item['file'].lower(), item['name'].lower()))
                    else:
                        filtered_records = sorted(filtered_records, key=lambda item: (item['docstring_error_count'], item['name'].lower()), reverse=True)

                    filtered_count = len(filtered_records)
                    visible_ratio = (filtered_count / total_dash_funcs * 100) if total_dash_funcs > 0 else 0

                    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
                    with fcol1:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Functions</div><div class="metric-value">{total_dash_funcs}</div></div>', unsafe_allow_html=True)
                    with fcol2:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Has Doc String</div><div class="metric-value">{has_docstring_count}</div></div>', unsafe_allow_html=True)
                    with fcol3:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Showing</div><div class="metric-value">{filtered_count}</div></div>', unsafe_allow_html=True)
                    with fcol4:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Workspace Shown</div><div class="metric-value">{visible_ratio:.1f}%</div></div>', unsafe_allow_html=True)

                    st.markdown("<div class='dashboard-panel-divider'></div>", unsafe_allow_html=True)

                    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
                    with filter_col1:
                        selected_status = st.selectbox("Doc string", status_options, index=status_options.index(selected_status), key="dash_adv_status")
                    with filter_col2:
                        selected_file = st.selectbox("File", file_options, index=file_options.index(selected_file), key="dash_adv_file")
                    with filter_col3:
                        selected_validation = st.selectbox("Check result", validation_options, index=validation_options.index(selected_validation), key="dash_adv_validation")
                    with filter_col4:
                        selected_sort = st.selectbox("Sort by", sort_options, index=sort_options.index(selected_sort), key="dash_adv_sort")

                    import pandas as pd
                    if filtered_records:
                        df1 = pd.DataFrame(
                            [
                                {
                                    "Function": item['name'],
                                    "File": item['file'],
                                    "Doc String": item['documentation_state'],
                                    "Check Result": item['validation_state'],
                                    "Issues": item['docstring_error_count'],
                                    "Line": item['line'],
                                }
                                for item in filtered_records
                            ]
                        )
                        st.dataframe(
                            df1,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Function": st.column_config.TextColumn("Function", width="medium"),
                                "File": st.column_config.TextColumn("File", width="medium"),
                                "Doc String": st.column_config.TextColumn("Doc String", width="medium"),
                                "Check Result": st.column_config.TextColumn("Check Result", width="medium"),
                                "Issues": st.column_config.NumberColumn("Issues", width="small"),
                                "Line": st.column_config.NumberColumn("Line", width="small"),
                            },
                        )
                        download_col1, download_col2, download_col3 = st.columns([1.2, 1, 1.2])
                        with download_col2:
                            st.download_button(
                                "⬇️ Download Filtered Results",
                                data=df1.to_csv(index=False).encode("utf-8"),
                                file_name="advanced_filters_results.csv",
                                mime="text/csv",
                                use_container_width=True,
                                key="dash_adv_download_csv",
                            )
                    else:
                        st.info("No functions match the selected filter combination.")

            elif st.session_state.dash_active_tab == "Search":
                with st.container(border=True):
                    render_dashboard_panel_header(
                        "🔎",
                        "Search Functions",
                        "Case-insensitive search across all parsed functions with consistent metrics and results table output.",
                    )

                    search_q = st.session_state.get("dash_search_input", "").lower().strip()
                    search_records = []
                    for func in all_functions:
                        has_docstring = func.get('has_docstring', False)
                        issues_count = len(func.get('docstring_errors', []))
                        search_records.append(
                            {
                                "name": func['name'],
                                "file": func['file'],
                                "line": func['start_line'],
                                "doc_string": "Has doc string" if has_docstring else "No doc string",
                                "check_result": "Has issues" if issues_count > 0 else ("Looks good" if has_docstring else "Not checked"),
                            }
                        )

                    filtered_search_records = [
                        item for item in search_records
                        if search_q in item['name'].lower() or search_q in item['file'].lower()
                    ] if search_q else search_records

                    total_dash_funcs = len(search_records)
                    matched_count = len(filtered_search_records)
                    match_rate = (matched_count / total_dash_funcs * 100) if total_dash_funcs > 0 else 0

                    scol1, scol2, scol3 = st.columns(3)
                    with scol1:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Functions</div><div class="metric-value">{total_dash_funcs}</div></div>', unsafe_allow_html=True)
                    with scol2:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Showing</div><div class="metric-value">{matched_count}</div></div>', unsafe_allow_html=True)
                    with scol3:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Workspace Shown</div><div class="metric-value">{match_rate:.1f}%</div></div>', unsafe_allow_html=True)

                    st.markdown("<div class='dashboard-panel-divider'></div>", unsafe_allow_html=True)
                    st.session_state.dash_search = st.text_input(
                        "Search Functions",
                        placeholder="Search by function or file name...",
                        key="dash_search_input",
                        label_visibility="collapsed",
                    )
                    st.markdown(
                        "<div class='dashboard-filter-note'>Type your search text, then press <strong>Enter</strong> to apply it.</div>",
                        unsafe_allow_html=True,
                    )

                    if filtered_search_records:
                        import pandas as pd
                        df2 = pd.DataFrame(
                            [
                                {
                                    "Function": item['name'],
                                    "File": item['file'],
                                    "Doc String": item['doc_string'],
                                    "Check Result": item['check_result'],
                                    "Line": item['line'],
                                }
                                for item in filtered_search_records
                            ]
                        )
                        st.dataframe(
                            df2,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Function": st.column_config.TextColumn("Function", width="medium"),
                                "File": st.column_config.TextColumn("File", width="medium"),
                                "Doc String": st.column_config.TextColumn("Doc String", width="medium"),
                                "Check Result": st.column_config.TextColumn("Check Result", width="medium"),
                                "Line": st.column_config.NumberColumn("Line", width="small"),
                            },
                        )
                    else:
                        st.info("No functions match the criteria.")

            elif st.session_state.dash_active_tab == "Tests":
                import json, subprocess, os, shutil
                import pandas as pd

                tests_section = st.container(border=True)
                with tests_section:
                    render_dashboard_panel_header(
                        "🧪",
                        "Workspace Tests",
                        "Run static baseline suites plus AI-generated project suites with a consistent diagnostics and reporting layout.",
                    )
                    st.markdown("<div class='dashboard-panel-divider'></div>", unsafe_allow_html=True)
                
        
                
                with tests_section:
                    tests_cont = st.container()
                    with tests_cont:
                        st.markdown("<span id='tests-btn-target'></span>", unsafe_allow_html=True)
                        has_run = '_last_test_hash' in st.session_state
                        run_btn_text = "▶️ Rerun Tests" if has_run else "▶️ Run Tests"
                        
                        run_clicked = False
                        if has_run:
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                run_clicked = st.button(run_btn_text, use_container_width=True, help="Execute all snapshot tests and AI-generated file tests")
                            with col_btn2:
                                if st.button("🧨 Clear Cache", use_container_width=True, help="Wipe all AI test caches and re-run everything from scratch"):
                                    st.session_state.pop('workspace_test_json', None)
                                    st.session_state.pop('_last_test_hash', None)
                                    st.session_state.pop('skipped_test_files', None)
                                    for d in ["workspace_tests/dynamic", "workspace_tests/cached"]:
                                        if os.path.exists(d):
                                            try: shutil.rmtree(d)
                                            except: pass
                                    st.rerun()
                        else:
                            # Use a column layout to ensure the CSS styling applies consistently
                            col_btn1 = st.columns(1)[0]
                            with col_btn1:
                                run_clicked = st.button(run_btn_text, use_container_width=True, help="Execute all snapshot tests and AI-generated file tests")

                if run_clicked:
                    workspace_root = "workspace_context"
                    test_root = "workspace_tests"
                    fixed_test_dir = os.path.join(test_root, "fixed")
                    dynamic_test_dir = os.path.join(test_root, "dynamic")

                    # ── State Fingerprinting (Instant Re-run Optimization) ──
                    import hashlib
                    def get_workspace_hash():
                        h = hashlib.sha256()
                        # Hash the configuration
                        h.update(st.session_state.get('doc_style', 'Google').encode('utf-8'))
                        h.update(st.session_state.get('fix_model', '').encode('utf-8'))
                        
                        # Hash the files (sorted by name for consistency)
                        for fn in sorted(st.session_state.file_data.keys()):
                            h.update(fn.encode('utf-8'))
                            h.update(st.session_state.file_data[fn]['content'].encode('utf-8'))
                            if fn in st.session_state.fixed_codes:
                                h.update(st.session_state.fixed_codes[fn].encode('utf-8'))
                        return h.hexdigest()
                    
                    current_hash = get_workspace_hash()
                    last_hash = st.session_state.get('_last_test_hash')
                    
                    if current_hash == last_hash and 'workspace_test_json' in st.session_state:
                        st.toast("🚀 Instant Re-run: No changes detected, reusing results.", icon="⚡")
                    else:
                        # 1. Nuclear clean (Preserve cached for lazy speed relative to AI, but clean dynamic for fresh report)
                        for d in [workspace_root, dynamic_test_dir, "__pycache__", ".pytest_cache"]:
                            if os.path.exists(d):
                                try: shutil.rmtree(d)
                                except: pass
                        
                        if os.path.exists(fixed_test_dir):
                            try: shutil.rmtree(fixed_test_dir)
                            except: pass
                        
                        os.makedirs(workspace_root, exist_ok=True)
                        os.makedirs(fixed_test_dir, exist_ok=True)
                        os.makedirs(dynamic_test_dir, exist_ok=True)
                        
                        # 2. Snapshot: Write session state codes to workspace_context (Handle Nested Folders)
                        for fname, fdata in st.session_state.file_data.items():
                            content = st.session_state.fixed_codes.get(fname, fdata['content'])
                            fpath = os.path.join(workspace_root, fname)
                            os.makedirs(os.path.dirname(fpath), exist_ok=True)
                            with open(fpath, "w", encoding="utf-8") as f:
                                f.write(content)
                        
                        # 3. Layer 1: Copy Fixed Tests from 'Test/' folder
                        static_source = "Test"
                        if os.path.exists(static_source):
                            for item in os.listdir(static_source):
                                if item.endswith(".py"):
                                    shutil.copy2(os.path.join(static_source, item), os.path.join(fixed_test_dir, item))

                        # Keep Test/ untouched in repo, but rewrite imports in copied fixed tests
                        # to match the restructured package layout.
                        fixed_import_map = {
                            r"^\s*import\s+parser\b": "from core import parser",
                            r"^\s*from\s+parser\s+import\s+": "from core.parser import ",
                            r"^\s*import\s+fix_code_with_ai\b": "from core import fix_code_with_ai",
                            r"^\s*from\s+fix_code_with_ai\s+import\s+": "from core.fix_code_with_ai import ",
                            r"^\s*import\s+convert_docstring_style\b": "from core import convert_docstring_style",
                            r"^\s*from\s+convert_docstring_style\s+import\s+": "from core.convert_docstring_style import ",
                            r"^\s*import\s+generate_workspace_tests\b": "from core import generate_workspace_tests",
                            r"^\s*from\s+generate_workspace_tests\s+import\s+": "from core.generate_workspace_tests import ",
                            r"^\s*from\s+faq_data\s+import\s+": "from faq.faq_data import ",
                            r"^\s*from\s+faq_component\s+import\s+": "from faq.faq_component import ",
                        }

                        if os.path.exists(fixed_test_dir):
                            for item in os.listdir(fixed_test_dir):
                                if not item.endswith(".py"):
                                    continue
                                fixed_path = os.path.join(fixed_test_dir, item)
                                try:
                                    with open(fixed_path, "r", encoding="utf-8") as rf:
                                        fixed_raw = rf.read()
                                    for pattern, repl in fixed_import_map.items():
                                        fixed_raw = re.sub(pattern, repl, fixed_raw, flags=re.MULTILINE)

                                    # Also rewrite patch target strings used by unittest.mock.patch.
                                    # Example: @patch("convert_docstring_style.get_client")
                                    patch_string_map = {
                                        '"convert_docstring_style.': '"core.convert_docstring_style.',
                                        "'convert_docstring_style.": "'core.convert_docstring_style.",
                                        '"fix_code_with_ai.': '"core.fix_code_with_ai.',
                                        "'fix_code_with_ai.": "'core.fix_code_with_ai.",
                                        '"generate_workspace_tests.': '"core.generate_workspace_tests.',
                                        "'generate_workspace_tests.": "'core.generate_workspace_tests.",
                                        '"parser.': '"core.parser.',
                                        "'parser.": "'core.parser.",
                                    }
                                    for old_ref, new_ref in patch_string_map.items():
                                        fixed_raw = fixed_raw.replace(old_ref, new_ref)

                                    with open(fixed_path, "w", encoding="utf-8") as wf:
                                        wf.write(fixed_raw)
                                except Exception:
                                    pass
                        
                        # 4. Layer 2: Generate Dynamic Tests (Turbo Parallel Approach)
                        progress_text = st.empty()
                        progress_bar = st.progress(0)
                        total_files = len(st.session_state.file_data)
                        skipped_test_files = []
                        
                        # Identify what actually needs generation
                        to_generate = []
                        for fname, fdata in st.session_state.file_data.items():
                            # Lazy re-parse if results are missing or empty on first run
                            if not fdata.get('results') or not fdata['results'].get('functions'):
                                fdata['results'] = parser.parse_file(fdata['content'])
                                
                            if "error" in fdata['results']:
                                skipped_test_files.append((fname, f"Parser Error: {fdata['results']['error']}"))
                                continue
                                
                            funcs = fdata['results'].get('functions', [])
                            documented_funcs = [f for f in funcs if f.get('has_docstring')]
                            
                            if not funcs:
                                skipped_test_files.append((fname, "No functions found in file"))
                                continue
                                
                            if len(documented_funcs) < len(funcs):
                                skipped_test_files.append((fname, f"Missing docstrings ({len(documented_funcs)}/{len(funcs)} documented)"))
                                continue
                            
                            test_path = os.path.join(dynamic_test_dir, f"test_{fname}")
                            cache_path = os.path.join("workspace_tests/cached", f"test_{fname}")
                            
                            if not os.path.exists(test_path):
                                if os.path.exists(cache_path):
                                    shutil.copy2(cache_path, test_path)
                                else:
                                    to_generate.append((fname, fdata['content'], documented_funcs))
                        
                        if to_generate:
                            from concurrent.futures import ThreadPoolExecutor
                            # Force reload generator to pick up recent code changes
                            importlib.reload(generate_workspace_tests)
                            progress_text.markdown(f"**⚡ Parallel Generating {len(to_generate)} test suite(s)...**")
                            
                            def _gen_task(args):
                                fn, code, funcs, mid = args
                                try:
                                    t_code = generate_workspace_tests.generate_pytest_for_file(fn, code, funcs, model=mid)
                                    tf_path = os.path.join(dynamic_test_dir, f"test_{fn}")
                                    os.makedirs(os.path.dirname(tf_path), exist_ok=True)
                                    with open(tf_path, "w", encoding="utf-8") as tf:
                                        tf.write(t_code)
                                    return True
                                except: return False

                            model_id = st.session_state.fix_model
                            with ThreadPoolExecutor(max_workers=4) as executor:
                                list(executor.map(_gen_task, [(f, c, fs, model_id) for f, c, fs in to_generate]))

                        # 4.5 Normalize dynamic test imports so stale cache cannot break collection
                        for fname in st.session_state.file_data.keys():
                            tf_path = os.path.join(dynamic_test_dir, f"test_{fname}")
                            if not os.path.exists(tf_path):
                                continue

                            module_name = fname.rsplit('.', 1)[0] if '.' in fname else fname
                            module_name = module_name.replace("/", ".").replace("\\", ".")
                            expected_header = f"import pytest\nfrom {module_name} import *\n\n"

                            try:
                                with open(tf_path, "r", encoding="utf-8") as rf:
                                    raw_test = rf.read()

                                # Strip any previous top-level pytest + module imports, then enforce expected header.
                                raw_test = re.sub(r"^\s*import\s+pytest\s*$", "", raw_test, flags=re.MULTILINE)
                                raw_test = re.sub(r"^\s*from\s+[A-Za-z_][A-Za-z0-9_\.]*\s+import\s+\*\s*$", "", raw_test, flags=re.MULTILINE)
                                normalized_test = expected_header + raw_test.strip() + "\n"

                                with open(tf_path, "w", encoding="utf-8") as wf:
                                    wf.write(normalized_test)
                            except Exception:
                                pass
                        
                        # 5. Environment & Execution
                        with open("conftest.py", "w") as f:
                            # Prioritize workspace_context so user modules don't conflict with app internal modules
                            # Use forward slashes to avoid Windows backslash escape bug
                            w_abs = os.path.abspath(workspace_root).replace("\\", "/")
                            f.write(f"import sys, os\nsys.path.insert(0, '{w_abs}')\n")
                            f.write(f"sys.path.insert(1, os.getcwd().replace('\\\\', '/'))\n")
                        
                        progress_text.markdown("**Executing Unified Test Suite...**")
                        progress_bar.progress(0.9)
                        
                        try:
                            # Robustness: Force delete old report to avoid reading stale data on failure
                            if os.path.exists(".workspace_report.json"):
                                try: os.remove(".workspace_report.json")
                                except: pass
                                
                            import sys
                            result = subprocess.run([
                                sys.executable, "-m", "pytest", fixed_test_dir, dynamic_test_dir,
                                "--json-report", "--json-report-file=.workspace_report.json",
                                "-p", "no:cacheprovider", "--tb=short", "-v"
                            ], capture_output=True, text=True)
                            
                            if os.path.exists(".workspace_report.json"):
                                with open(".workspace_report.json", "r") as rfile:
                                    rep = json.load(rfile)
                                    st.session_state.workspace_test_json = rep
                                    
                                    # Identify collection errors
                                    for coll in rep.get('collectors', []):
                                        if coll.get('outcome') == 'failed':
                                            # These are critical errors preventing a file from being tested
                                            node = coll['nodeid'].replace("\\", "/")
                                            filename = node.split("/")[-1].replace("test_", "")
                                            skipped_test_files.append((filename, f"Pytest Collection Error: {coll.get('longrepr', 'Unknown error')}"))

                                    st.session_state.skipped_test_files = skipped_test_files
                                    st.session_state._last_test_hash = current_hash
                                    st.rerun()
                            else:
                                st.error("Test report was not generated.")
                        except Exception as e:
                            st.error(f"Execution Error: {e}")
                        
                        progress_text.empty()
                        progress_bar.empty()

                # Render Results
                with tests_section:
                    skipped_files = []
                    w_json = None
                    all_tests = []
                    if 'workspace_test_json' in st.session_state:
                        skipped_files = st.session_state.get('skipped_test_files', [])
                        w_json = st.session_state.workspace_test_json
                        all_tests = w_json.get('tests', [])

                    if w_json is None:
                        st.info("Run tests to see summary, charts, and downloadable reports.")
                        return
                    
                    t_total = len(all_tests)
                    t_pass = sum(1 for t in all_tests if t.get('outcome') == 'passed')
                    t_fail = sum(1 for t in all_tests if t.get('outcome') in ('failed', 'error'))
                    t_rate = (t_pass / t_total * 100) if t_total > 0 else 0
                    
                    st.markdown("#### 📝 Test summary")
                    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
                    with tcol1: st.markdown(f'<div class="metric-card"><div class="metric-title">Tests Run</div><div class="metric-value">{t_total}</div></div>', unsafe_allow_html=True)
                    with tcol2: st.markdown(f'<div class="metric-card"><div class="metric-title">Passed</div><div class="metric-value" style="color:#7bed9f">{t_pass}</div></div>', unsafe_allow_html=True)
                    with tcol3: st.markdown(f'<div class="metric-card"><div class="metric-title">Failed</div><div class="metric-value" style="color:#ff6b6b">{t_fail}</div></div>', unsafe_allow_html=True)
                    with tcol4: st.markdown(f'<div class="metric-card"><div class="metric-title">Success Rate</div><div class="metric-value">{t_rate:.1f}%</div></div>', unsafe_allow_html=True)
                    
                    st.download_button("📥 Download Test Report (JSON)", data=json.dumps(w_json, indent=2), file_name="workspace_report.json", mime="application/json", use_container_width=True)
                    
                    st.markdown("---")
                    
                    # ── Build data for chart and results ──
                    fixed_results = [t for t in all_tests if "workspace_tests/fixed" in t['nodeid'].replace("\\", "/")]
                    dynamic_results = [t for t in all_tests if "workspace_tests/dynamic" in t['nodeid'].replace("\\", "/")]
                    
                    chart_data = []
                    static_label_map = {
                        "coverage_reporter": "Coverage Math",
                        "dashboard": "Dashboard Filter",
                        "parser": "Parser",
                        "validation": "Validation",
                        "generator": "Style Generator",
                        "llm_integration": "LLM Integration",
                    }
                    
                    # Helper to group by file for the chart
                    def get_file_stats(tests, layer_name, prefix_strip):
                        stats = {}
                        for t in tests:
                            node = t['nodeid'].replace("\\", "/")
                            f_path = node.split('::')[0]
                            display_name = f_path
                            if prefix_strip in display_name:
                                display_name = display_name.split(prefix_strip)[-1].lstrip("/")
                            display_name = display_name.replace(".py", "").replace("test_", "")
                            if display_name not in stats:
                                stats[display_name] = {'passed': 0, 'failed': 0, 'layer': layer_name}
                            if t.get('outcome') == 'passed':
                                stats[display_name]['passed'] += 1
                            else:
                                stats[display_name]['failed'] += 1
                        return stats

                    all_stats = {}
                    all_stats.update(get_file_stats(fixed_results, "🛡️ App Health", "workspace_tests/fixed"))
                    all_stats.update(get_file_stats(dynamic_results, "💻 Your Code", "workspace_tests/dynamic"))
                    
                    # We no longer add skipped files to all_stats so they don't appear in the chart data.
                    # But we keep track of them for the detailed results expanders below.
                    skipped_files = st.session_state.get('skipped_test_files', [])
                    
                    for f_name, s in all_stats.items():
                        label = static_label_map.get(f_name, f_name)
                        chart_data.append({
                            "Test Suite": label,
                            "Passed": s['passed'],
                            "Failed": s['failed'],
                            "Layer": s['layer']
                        })

                    # ── Render Overview Column Layout ──
                    if chart_data:
                        import plotly.graph_objects as go
                        import pandas as pd
                        df_chart = pd.DataFrame(chart_data)
                        
                        st.markdown("#### 📊 Test Results")
                        fig = go.Figure()
                        # Apply name compression to chart labels
                        chart_labels = [compress_name(l, 14) for l in df_chart['Test Suite']]
                        
                        # Stacked Bar: Failed at bottom, Passed on top
                        fig.add_trace(go.Bar(
                            name='Failed', x=chart_labels, y=df_chart['Failed'],
                            marker_color='#ff6b6b', marker_line_color='rgba(0,0,4,0.3)', marker_line_width=1,
                            text=df_chart['Failed'].apply(lambda x: f"{x}" if x > 0 else ""), textposition='inside',
                        ))
                        fig.add_trace(go.Bar(
                            name='Passed', x=chart_labels, y=df_chart['Passed'],
                            marker_color='#7bed9f', marker_line_color='rgba(0,0,4,0.3)', marker_line_width=1,
                            text=df_chart['Passed'], textposition='inside',
                        ))
                        
                        fig.update_layout(
                            barmode='stack', height=380,
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#e0e0e0', margin=dict(l=10, r=10, t=20, b=60),
                            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickangle=-30, tickfont=dict(size=10)),
                            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Number of Tests'),
                            legend=dict(orientation='h', yanchor='top', y=-0.3, xanchor='center', x=0.5),
                            bargap=0.3
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")

                    # ── Detailed Results Section ──
                    
                    def format_simple_error_msg(longrepr):
                        lines = str(longrepr).split('\n')
                        error_msg = "An unexpected error caused the test to fail."
                        expected = "See Raw Traceback for details"
                        obtained = "See Raw Traceback for details"
                        test_case_code = "Could not parse exact test case"
                        
                        # Extract the exact line of code that failed
                        first_e_idx = -1
                        for i, line in enumerate(lines):
                            if line.startswith("E   "):
                                first_e_idx = i
                                break
                        if first_e_idx > 0:
                            # Sometimes the line before 'E ' is just '    ^^^^^^^^^^'
                            prev_line = lines[first_e_idx - 1].strip()
                            if prev_line.replace("^", "").strip() == "":
                                if first_e_idx > 1:
                                    test_case_code = lines[first_e_idx - 2].strip()
                            else:
                                test_case_code = prev_line
                        
                        for line in lines:
                            if line.startswith("E   AssertionError:"):
                                error_msg = line.replace("E   AssertionError:", "").strip()
                            elif line.startswith("E   Failed: DID NOT RAISE"):
                                error_msg = "The function was expected to crash or raise a specific error upon bad input, but it didn't."
                                expected = line.replace("E   Failed: DID NOT RAISE", "").strip()
                                obtained = "Function executed successfully without crashing."
                            elif "Obtained:" in line:
                                obtained = line.split("Obtained:")[-1].strip()
                            elif "Expected:" in line:
                                expected = line.split("Expected:")[-1].strip()
                            elif any(line.startswith(e) for e in ["E   TypeError:", "E   ValueError:", "E   KeyError:", "E   AttributeError:", "E   IndexError:", "E   NameError:", "E   ZeroDivisionError:"]):
                                error_msg = f"The function crashed with an internal error: {line.replace('E   ', '').strip()}"
                                obtained = "Function Crashed"
                                
                        # Fallback for standard basic equality tests
                        if expected == "See Raw Traceback for details" and obtained == "See Raw Traceback for details":
                            for line in lines:
                                if line.startswith("E   assert ") and " == " in line:
                                    parts = line.replace("E   assert ", "").split(" == ")
                                    if len(parts) == 2:
                                        obtained = parts[0].strip()
                                        expected = parts[1].strip()
                                        break
                                        
                        md = f"**Test Case Executed:**\n`{test_case_code}`\n\n"
                        md += f"**Issue:** {error_msg}\n\n"
                        md += f"- **Expected:** `{expected}`\n"
                        md += f"- **Output from function:** `{obtained}`\n"
                        return md
                    
                    def render_test_group(title, tests, prefix_to_strip, skipped_list=None):
                        # Calculate results for badge
                        t_total = len(tests)
                        t_pass = sum(1 for t in tests if t.get('outcome') == 'passed')
                        badge_html = f'<span class="test-group-badge">{t_pass}/{t_total} Passed</span>' if t_total > 0 else ""
                        
                        st.markdown(f"""
                            <div class="test-group-header">
                                <h4 class="test-group-title">{title}</h4>
                                {badge_html}
                            </div>
                        """, unsafe_allow_html=True)
                        if not tests and not skipped_list:
                            st.info("No tests in this category.")
                            return
                            
                        file_map = {}
                        for t in tests:
                            node = t['nodeid'].replace("\\", "/")
                            f_path = node.split('::')[0]
                            display_name = f_path
                            if prefix_to_strip in display_name:
                                display_name = display_name.split(prefix_to_strip)[-1].lstrip("/")
                            display_name = display_name.replace(".py", "").replace("test_", "")
                            file_map.setdefault(display_name, []).append(t)
                            
                        # Render skipped files first
                        if skipped_list:
                            for sf_item in skipped_list:
                                if isinstance(sf_item, tuple):
                                    sf, reason = sf_item
                                else:
                                    sf, reason = sf_item, "Missing Docstrings"
                                    
                                sf_display = sf.replace(".py", "")
                                indicator = "⚠️" if "Collection Error" not in reason else "🔴"
                                with st.expander(f"{indicator} {sf_display} — SKIPPED ({reason})"):
                                    if "docstrings" in reason.lower():
                                        st.warning("🧠 **AI Context Required:** The AI needs a proper understanding of what your functions are intended to do in order to accurately generate reliable test cases. Without descriptions, it might hallucinate incorrect tests or fail entirely. Generate Docstrings for this file verify them and try again.")
                                        if st.button("Fix now in DocStrings Tab ↗️", key=f"nav_doc_{sf_display}"):
                                            st.session_state.active_section = "📝 DocStrings"
                                            st.rerun()
                                    else:
                                        st.error(reason)

                        for f_name, f_tests in file_map.items():
                            t_passed = sum(1 for t in f_tests if t['outcome'] == 'passed')
                            t_total = len(f_tests)
                            all_passed = (t_passed == t_total)
                            icon = "✅" if all_passed else "❌"
                            f_status = f"{t_passed}/{t_total} Passed"
                            with st.expander(f"{icon} {f_name} — {f_status}"):
                                for t in f_tests:
                                    t_name = t['nodeid'].split('::')[-1]
                                    outcome = t['outcome']
                                    o_icon = "🟢" if outcome == "passed" else "🔴"
                                    st.markdown(f"{o_icon} **{t_name}**: {outcome.upper()}")
                                    if outcome in ('failed', 'error'):
                                        lr = t.get('call', {}).get('longrepr') or t.get('setup', {}).get('longrepr', "No details.")
                                        
                                        # Simple Explanation
                                        st.markdown(format_simple_error_msg(lr))
                                        
                                        # Raw Traceback immediately below
                                        st.markdown("**💻 Raw Traceback:**")
                                        st.code(lr)
                                
                                # Final Polish: View the generated test code
                                st.markdown("---")
                                cache_path = os.path.join("workspace_tests/cached", f"test_{f_name}.py")
                                dynamic_path = os.path.join("workspace_tests/dynamic", f"test_{f_name}.py")
                                
                                test_file_to_show = ""
                                if os.path.exists(cache_path): test_file_to_show = cache_path
                                elif os.path.exists(dynamic_path): test_file_to_show = dynamic_path
                                
                                if test_file_to_show:
                                    st.markdown(f"#### 👀 AI-Generated Test Code ({f_name})")
                                    try:
                                        with open(test_file_to_show, "r", encoding="utf-8") as tf:
                                            st.code(tf.read(), language="python")
                                    except:
                                        st.error("Could not load test file.")
                    
                    render_test_group("🛡️ App Health Test Suites", fixed_results, "workspace_tests/fixed")
                    render_test_group("🛠️ Project Code Tests", dynamic_results, "workspace_tests/dynamic", skipped_list=skipped_files)
                    
                    st.write("")

            elif st.session_state.dash_active_tab == "Export":
                import json
                import io
                import csv
                with st.container(border=True):
                    render_dashboard_panel_header(
                        "📥",
                        "Export Reports",
                        "Download a high-level docstring coverage report with overall metrics, file summaries, and simple function-level status.",
                    )

                    export_function_rows = []
                    export_file_rows = []
                    for fname, fdata in st.session_state.file_data.items():
                        res = fdata['results']
                        if "error" in res:
                            export_file_rows.append(
                                {
                                    "File": fname,
                                    "Total Functions": 0,
                                    "Has Doc String": 0,
                                    "No Doc String": 0,
                                    "Coverage": "N/A",
                                }
                            )
                            continue

                        funcs = res.get('functions', [])
                        file_total = len(funcs)
                        file_doc = sum(1 for func in funcs if func.get('has_docstring'))
                        file_missing = file_total - file_doc
                        file_cov = "N/A" if file_total == 0 else f"{(file_doc / file_total) * 100:.1f}%"

                        export_file_rows.append(
                            {
                                "File": fname,
                                "Total Functions": file_total,
                                "Has Doc String": file_doc,
                                "No Doc String": file_missing,
                                "Coverage": file_cov,
                            }
                        )

                        for func in funcs:
                            export_function_rows.append(
                                {
                                    "File": fname,
                                    "Function": func['name'],
                                    "Line": func['start_line'],
                                    "Doc String": "Has doc string" if func.get('has_docstring') else "No doc string",
                                }
                            )

                    export_report = {
                        "overall_metrics": {
                            "total_files": total_files,
                            "total_functions": total_funcs,
                            "functions_with_docstrings": total_doc_funcs,
                            "functions_missing_docstrings": total_undoc_funcs,
                            "overall_docstring_coverage": round(overall_cov, 1) if total_funcs > 0 else "N/A",
                        },
                        "files": export_file_rows,
                        "functions": export_function_rows,
                    }

                    st.markdown("<div class='dashboard-panel-divider'></div>", unsafe_allow_html=True)
                    ecolm1, ecolm2, ecolm3, ecolm4 = st.columns(4)
                    with ecolm1:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Files</div><div class="metric-value">{total_files}</div></div>', unsafe_allow_html=True)
                    with ecolm2:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Functions</div><div class="metric-value">{total_funcs}</div></div>', unsafe_allow_html=True)
                    with ecolm3:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">Has Doc String</div><div class="metric-value">{total_doc_funcs}</div></div>', unsafe_allow_html=True)
                    with ecolm4:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">No Doc String</div><div class="metric-value">{total_undoc_funcs}</div></div>', unsafe_allow_html=True)

                    if export_function_rows:
                        export_format = st.selectbox(
                            "Select Export Format",
                            ["JSON", "Markdown", "CSV", "Plain Text"],
                            key="dash_export_format",
                            label_visibility="collapsed",
                        )

                        export_content = ""
                        mime_type = "text/plain"
                        ext = "txt"
                        lang = "text"

                        if export_format == "JSON":
                            export_content = json.dumps(export_report, indent=2)
                            mime_type = "application/json"
                            ext = "json"
                            lang = "json"
                        elif export_format == "Markdown":
                            md_lines = ["# Dashboard Docstring Report\n"]
                            md_lines.append("## Overall Metrics")
                            md_lines.append(f"- **Total Files:** {total_files}")
                            md_lines.append(f"- **Total Functions:** {total_funcs}")
                            md_lines.append(f"- **Has Doc String:** {total_doc_funcs}")
                            md_lines.append(f"- **No Doc String:** {total_undoc_funcs}")
                            md_lines.append(f"- **Coverage:** {overall_cov:.1f}%\n" if total_funcs > 0 else "- **Coverage:** N/A\n")

                            md_lines.append("## File Summary")
                            for row in export_file_rows:
                                md_lines.append(f"- **{row['File']}**: {row['Has Doc String']} has doc string, {row['No Doc String']} no doc string (Coverage: {row['Coverage']})")

                            md_lines.append("\n## Function Summary")
                            for row in export_function_rows:
                                md_lines.append(f"- `{row['File']}` :: `{row['Function']}` (Line {row['Line']}) - {row['Doc String']}")

                            export_content = "\n".join(md_lines)
                            mime_type = "text/markdown"
                            ext = "md"
                            lang = "markdown"
                        elif export_format == "CSV":
                            csv_buffer = io.StringIO()
                            writer = csv.writer(csv_buffer)
                            writer.writerow(["OVERALL METRICS"])
                            writer.writerow(["Total Files", total_files])
                            writer.writerow(["Total Functions", total_funcs])
                            writer.writerow(["Has Doc String", total_doc_funcs])
                            writer.writerow(["No Doc String", total_undoc_funcs])
                            writer.writerow(["Coverage", f"{overall_cov:.1f}%" if total_funcs > 0 else "N/A"])
                            writer.writerow([])
                            writer.writerow(["FILE SUMMARY"])
                            writer.writerow(["File", "Total Functions", "Has Doc String", "No Doc String", "Coverage"])
                            for row in export_file_rows:
                                writer.writerow([row["File"], row["Total Functions"], row["Has Doc String"], row["No Doc String"], row["Coverage"]])
                            writer.writerow([])
                            writer.writerow(["FUNCTION SUMMARY"])
                            writer.writerow(["File", "Function", "Line", "Doc String"])
                            for row in export_function_rows:
                                writer.writerow([row["File"], row["Function"], row["Line"], row["Doc String"]])

                            export_content = csv_buffer.getvalue()
                            mime_type = "text/csv"
                            ext = "csv"
                            lang = "csv"
                        else:
                            txt_lines = ["DASHBOARD DOCSTRING REPORT\n" + "=" * 40]
                            txt_lines.append("OVERALL METRICS")
                            txt_lines.append("-" * 20)
                            txt_lines.append(f"Total Files: {total_files}")
                            txt_lines.append(f"Total Functions: {total_funcs}")
                            txt_lines.append(f"Has Doc String: {total_doc_funcs}")
                            txt_lines.append(f"No Doc String: {total_undoc_funcs}")
                            txt_lines.append(f"Coverage: {overall_cov:.1f}%\n" if total_funcs > 0 else "Coverage: N/A\n")

                            txt_lines.append("FILE SUMMARY\n" + "=" * 40)
                            for row in export_file_rows:
                                txt_lines.append(f"{row['File']}: {row['Has Doc String']} has doc string, {row['No Doc String']} no doc string (Coverage: {row['Coverage']})")

                            txt_lines.append("\nFUNCTION SUMMARY\n" + "=" * 40)
                            for row in export_function_rows:
                                txt_lines.append(f"{row['File']} :: {row['Function']} (Line {row['Line']}) - {row['Doc String']}")

                            export_content = "\n".join(txt_lines)
                            mime_type = "text/plain"
                            ext = "txt"
                            lang = "text"

                        ctrl_col1, ctrl_col2 = st.columns([0.65, 0.35])
                        with ctrl_col1:
                            st.markdown(f"**Selected Format:** {export_format}")
                        with ctrl_col2:
                            st.download_button(
                                label=f"⬇️ Download .{ext}",
                                data=export_content,
                                file_name=f"dashboard_docstring_report.{ext}",
                                mime=mime_type,
                                use_container_width=True,
                                key="dash_export_download",
                            )

                        st.write("")
                        st.markdown("**Live Preview:**")
                        st.code(export_content, language=lang)
                    else:
                        st.info("No functions found to export.")

            elif st.session_state.dash_active_tab == "Help":
                with st.container(border=True):
                    render_dashboard_panel_header(
                        "💡",
                        "Help & Guides",
                        "Open any dashboard tab card to view feature details and how-to steps.",
                    )

                    help_cards = [
                        {
                            "title": "🧭 Left Panel: Explorer",
                            "features": [
                                "Navigation selector for Home, Dashboard, Validation, DocStrings, and Metrics.",
                                "AI Fix Model selector to control model usage across generation/fix flows.",
                                "Add Files uploader (py/zip) plus interactive file list with open/download/delete actions.",
                            ],
                            "how_to": [
                                "Choose your working section from Navigation first.",
                                "Select AI Fix Model before running test/docstring generation tasks.",
                                "Upload files, then open any file row to review or edit code.",
                            ],
                        },
                        {
                            "title": "🏠 Main Tab: Home",
                            "features": [
                                "Workspace-level summary metrics for files, functions, and doc string coverage.",
                                "Validation health metrics such as clean files/functions overview.",
                                "Quick high-level status snapshot for overall code quality.",
                            ],
                            "how_to": [
                                "Open Home first to understand current workspace quality baseline.",
                                "Use coverage and clean metrics to prioritize next actions.",
                                "Move to Validation or Dashboard based on issues discovered here.",
                            ],
                        },
                        {
                            "title": "🎛️ Main Tab: Dashboard (Overview)",
                            "features": [
                                "Frosted sub-tab navigation with Advanced Filters, Search, Tests, Export, and Help.",
                                "Focused workflows for investigating, testing, and exporting doc string quality data.",
                                "Consistent metrics-first layouts for fast understanding before deep actions.",
                            ],
                            "how_to": [
                                "Use Dashboard when you need focused analysis and actions.",
                                "Switch sub-tabs based on task: filter/search/test/export/help.",
                                "Return to Home for a broad health snapshot after actions.",
                            ],
                        },
                        {
                            "title": "🔎 Dashboard Tab: Advanced Filters",
                            "features": [
                                "Filter by doc string status, file, check result, and sorting mode.",
                                "Metrics update immediately to reflect active filters.",
                                "Filtered table supports focused export for review workflows.",
                            ],
                            "how_to": [
                                "Pick a status filter first (all/has/no doc string).",
                                "Narrow further using file and check result selectors.",
                                "Sort results and download the filtered view if needed.",
                            ],
                        },
                        {
                            "title": "🔍 Dashboard Tab: Search",
                            "features": [
                                "Search across function names and file names.",
                                "Result metrics plus a themed table for quick scanning.",
                                "Enter-driven apply pattern for clean interaction.",
                            ],
                            "how_to": [
                                "Type your keyword in the search box.",
                                "Press Enter to apply and inspect the updated results.",
                                "Clear the query to return to the full data view.",
                            ],
                        },
                        {
                            "title": "🧪 Dashboard Tab: Tests",
                            "features": [
                                "Runs snapshot and AI-generated tests for workspace files.",
                                "Displays suite-level pass/fail and summary counts.",
                                "Supports cache clearing to force full regeneration.",
                            ],
                            "how_to": [
                                "Click run tests after uploading or editing files.",
                                "Use clear cache when results look stale.",
                                "Inspect failures first, then iterate with fixes.",
                            ],
                        },
                        {
                            "title": "📤 Dashboard Tab: Export",
                            "features": [
                                "Choose report format (JSON/Markdown/CSV/Plain Text).",
                                "One-click download for the currently selected format.",
                                "Live preview validates report content before export.",
                            ],
                            "how_to": [
                                "Select the format that matches your target workflow.",
                                "Review live preview for structure and values.",
                                "Download and share the generated report artifact.",
                            ],
                        },
                        {
                            "title": "💡 Dashboard Tab: Help",
                            "features": [
                                "Central place to understand every app area.",
                                "Card-based layout with expandable dropdown guides.",
                                "Feature notes plus practical usage instructions.",
                            ],
                            "how_to": [
                                "Open the card for the area you are using.",
                                "Read Features for capabilities, then How to Use for steps.",
                                "Return anytime as a quick in-app reference.",
                            ],
                        },
                        {
                            "title": "✅ Main Tab: Validation",
                            "features": [
                                "File-by-file doc string/PEP validation visibility.",
                                "Issue-focused breakdown to identify weak documentation points.",
                                "Action support for improving compliance quality.",
                            ],
                            "how_to": [
                                "Open Validation after initial upload or major edits.",
                                "Identify files/functions with repeated violations.",
                                "Apply fixes, then re-check status to confirm improvement.",
                            ],
                        },
                        {
                            "title": "📝 Main Tab: DocStrings",
                            "features": [
                                "Docstring style detection for current codebase.",
                                "Conversion/generation workflows (Google, reST, NumPy).",
                                "Side-by-side previews, diff, apply, copy, and download actions.",
                            ],
                            "how_to": [
                                "Choose file and scope, then pick target style.",
                                "Run conversion or generation and inspect preview/diff.",
                                "Apply changes to workspace when output looks correct.",
                            ],
                        },
                        {
                            "title": "📈 Main Tab: Metrics",
                            "features": [
                                "Consolidated metrics for documentation quality across workspace.",
                                "High-level trend and coverage indicators.",
                                "Quick insight panel for reporting and decision-making.",
                            ],
                            "how_to": [
                                "Use Metrics for overall reporting and tracking progress.",
                                "Compare values before and after fixes/conversions.",
                                "Use alongside Export when sharing final summaries.",
                            ],
                        },
                        {
                            "title": "📄 File Tabs (Opened Files)",
                            "features": [
                                "Per-file editor with function breakdown and coverage tiles.",
                                "Original/modified code flows and download options.",
                                "Per-file report export with format selection and live preview.",
                            ],
                            "how_to": [
                                "Open a file from Explorer to inspect or edit source.",
                                "Review function-level doc string status in the breakdown area.",
                                "Export file-specific reports when detailed evidence is needed.",
                            ],
                        },
                    ]

                    st.markdown("<span class='help-card-anchor' style='display:none'></span>", unsafe_allow_html=True)
                    card_cols = st.columns(3)
                    for i, card in enumerate(help_cards):
                        with card_cols[i % 3]:
                            if st.button(card["title"], key=f"help_card_btn_{i}", use_container_width=True):
                                st.session_state.help_selected_card = i
                                st.rerun()

                    selected_idx = st.session_state.get("help_selected_card")
                    if selected_idx is not None and 0 <= selected_idx < len(help_cards):
                        selected_card = help_cards[selected_idx]

                        if hasattr(st, "dialog"):
                            @st.dialog(selected_card["title"])
                            def _show_help_card_dialog():
                                st.markdown("**Features**")
                                for item in selected_card["features"]:
                                    st.markdown(f"- {item}")

                                st.markdown("**How to Use**")
                                for item in selected_card["how_to"]:
                                    st.markdown(f"- {item}")

                                if st.button("Close", use_container_width=True, key=f"help_close_btn_{selected_idx}"):
                                    st.session_state.help_selected_card = None
                                    st.rerun()

                            _show_help_card_dialog()
                        else:
                            with st.container(border=True):
                                st.markdown(f"### {selected_card['title']}")
                                st.markdown("**Features**")
                                for item in selected_card["features"]:
                                    st.markdown(f"- {item}")

                                st.markdown("**How to Use**")
                                for item in selected_card["how_to"]:
                                    st.markdown(f"- {item}")

                                if st.button("Close", use_container_width=True, key=f"help_close_fallback_{selected_idx}"):
                                    st.session_state.help_selected_card = None
                                    st.rerun()

    elif active == "🏠 Home":
        # ── 1. Analytics Dashboard (Home Section)
        with st.container(border=True):
            st.markdown("""
            <div class='sc-header'>
                <span class='sc-header-icon' style='color:#ffbf00'>🏠</span>
                <h2>Home</h2>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<span class='home-metrics-anchor' style='display:none;'></span>", unsafe_allow_html=True)

            clean_files = total_files - files_with_errors
            files_doc_color = "#7bed9f" if total_files > 0 and files_with_docstrings == total_files else ("#feca57" if files_with_docstrings > 0 else "#ff6b6b")
            doc_funcs_color = "#7bed9f" if total_funcs > 0 and total_doc_funcs == total_funcs else ("#feca57" if total_doc_funcs > 0 else "#ff6b6b")
            undoc_funcs_color = "#7bed9f" if total_funcs > 0 and total_undoc_funcs == 0 else ("#feca57" if total_undoc_funcs <= max(1, total_funcs // 3) else "#ff6b6b")
            clean_files_color = "#7bed9f" if total_files > 0 and clean_files == total_files else ("#feca57" if clean_files > 0 else "#ff6b6b")
            compliant_color = "#7bed9f" if total_funcs > 0 and clean_functions == total_funcs else ("#feca57" if clean_functions > 0 else "#ff6b6b")
            violations_color = "#7bed9f" if total_errors == 0 else ("#feca57" if total_errors <= max(1, total_funcs // 4) else "#ff6b6b")

            # Row 1 of metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Files</div>
                    <div class="metric-value">{total_files}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Files Having Doc String</div>
                    <div class="metric-value" style="color: {files_doc_color};">{files_with_docstrings}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total No. of Functions</div>
                    <div class="metric-value">{total_funcs}</div>
                </div>
                """, unsafe_allow_html=True)

            # Row 2 of metrics
            col4, col5, col6 = st.columns(3)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Functions Having Doc String</div>
                    <div class="metric-value" style="color: {doc_funcs_color};">{total_doc_funcs}</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Functions Not Having Doc String</div>
                    <div class="metric-value" style="color: {undoc_funcs_color};">{total_undoc_funcs}</div>
                </div>
                """, unsafe_allow_html=True)
            with col6:
                cov_color = "#7bed9f" if overall_cov == 100 else ("#ff6b6b" if overall_cov < 50 else "#feca57")
                if total_funcs == 0:
                    cov_color = "#888888"
                    cov_str = "N/A"
                else:
                    cov_str = f"{overall_cov:.1f}%"
                    
                st.markdown(f"""
                <div class="metric-card" style="border-color: {cov_color};">
                    <div class="metric-title">Coverage Percentage</div>
                    <div class="metric-value" style="color: {cov_color};">{cov_str}</div>
                </div>
                """, unsafe_allow_html=True)

            # Row 3 of metrics (Validation)
            col7, col8, col9 = st.columns(3)
            with col7:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Clean Files / Total Files</div>
                    <div class="metric-value" style="color: {clean_files_color};">{clean_files} / {total_files}</div>
                </div>
                """, unsafe_allow_html=True)
            with col8:
                st.markdown(f"""
                <div class="metric-card" style="border-color: {compliant_color};">
                    <div class="metric-title">100% Compliant Functions</div>
                    <div class="metric-value" style="color: {compliant_color};">{clean_functions} / {total_funcs}</div>
                </div>
                """, unsafe_allow_html=True)
            with col9:
                st.markdown(f"""
                <div class="metric-card" style="border-color: {violations_color};">
                    <div class="metric-title">Total Docstring Violations (PEP/Params)</div>
                    <div class="metric-value" style="color: {violations_color};">{total_errors}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)

            st.markdown("### 📁 File Breakdown")
            
            if total_files == 0:
                st.info("No files uploaded.")
            else:
                for fname, fdata in st.session_state.file_data.items():
                    res = fdata['results']
                    if "error" in res:
                        with st.expander(f"⚠️ {fname} — Error Parsing"):
                            st.error(res["error"])
                        continue
                        
                    cov = res.get('coverage', 0)
                    total_f = res.get('total_functions', 0)
                    
                    if total_f == 0:
                        c_icon = "⚪"
                    else:
                        c_icon = "🟢" if cov == 100 else ("🔴" if cov < 50 else "🟡")
                        
                    with st.expander(f"{c_icon} 📄 {fname}"):
                        funcs = res.get('functions', [])
                        doc_f = sum(1 for f in funcs if f.get('has_docstring'))
                        undoc_f = total_f - doc_f
                        file_style = res.get('detected_style', 'Unknown')
                        
                        # Show Mixed Style Warning
                        if file_style == "Mixed":
                            st.warning("🔀 **Mixed Styles Detected:** This file contains multiple different docstring formats. We highly recommend using the Style Converter below to normalize them into a single style.")
                        
                        st.markdown(f"**Detected Style:** `{file_style}`")
                        st.markdown(f"**Total Functions:** {total_f}")
                        st.markdown(f"**Functions with Docstrings:** {doc_f}")
                        st.markdown(f"**Functions missing Docstrings:** {undoc_f}")
                        st.markdown(f"**Total Coverage:** {cov:.1f}%" if total_f > 0 else "**Total Coverage:** N/A")
                        
                        st.markdown("---")
                        st.markdown("**Function details:**")
                        
                        if total_f == 0:
                            st.info("No Functions found.")
                        else:
                            for i, func in enumerate(funcs):
                                st.markdown(f"- **Function {i+1} Name:** `{func['name']}`")
                                st.markdown(f"  - **Starting Line:** {func['start_line']}")
                                st.markdown(f"  - **Ending Line:** {func['end_line']}")
                                st.markdown(f"  - **Has Docstring:** {'Yes ✅' if func['has_docstring'] else 'No ❌'}")
                                st.markdown("---")
                    
    elif active == "✅ Validation":
        # ── 2. PEP Validation Section
        with st.container(border=True):
            st.markdown("""
            <div class='sc-header'>
                <span class='sc-header-icon' style='color:#ff7043'>✅</span>
                <h2>Validation</h2>
            </div>
            """, unsafe_allow_html=True)
            render_pep_validation_dashboard()

    elif active == "📝 DocStrings":
        # ── 3. DocStrings Section
        with st.container(border=True):
            st.markdown("""
            <div class='sc-header'>
                <span class='sc-header-icon' style='color:#26c6da'>📝</span>
                <h2>DocStrings</h2>
            </div>
            """, unsafe_allow_html=True)
            render_docstring_converter()

    elif active == "📈 Metrics":
        # ── 4. Metrics Section
        with st.container(border=True):
            st.markdown("""
            <div class='sc-header'>
                <span class='sc-header-icon' style='color:#a066ff'>📈</span>
                <h2>Metrics</h2>
            </div>
            """, unsafe_allow_html=True)
    
            st.markdown("**Choose export type:**")
            export_format = st.selectbox("Select Export Format", ["JSON", "Markdown", "CSV", "Plain Text"], label_visibility="collapsed")
        
            export_content = ""
            if export_format == "JSON":
                import json
                export_data = {
                    "overall_metrics": {
                        "total_files": total_files,
                        "total_functions": total_funcs,
                        "functions_with_docstrings": total_doc_funcs,
                        "functions_missing_docstrings": total_undoc_funcs,
                        "overall_coverage_percentage": round(overall_cov, 1) if total_funcs > 0 else "N/A"
                    },
                    "files": {}
                }
                for fname, fdata in st.session_state.file_data.items():
                    file_res = fdata['results'].copy() # Make a copy so we don't mutate session state
                    if file_res.get('total_functions', 0) == 0:
                        file_res['coverage'] = "N/A"
                    export_data["files"][fname] = file_res
                    
                export_content = json.dumps(export_data, indent=4)
                lang = "json"
                mime_type = "application/json"
                ext = "json"
            elif export_format == "Markdown":
                md_lines = ["# ⚡ AI Code Reviewer Report\n"]
                md_lines.append("## 📊 Overall Metrics")
                md_lines.append(f"- **Total Files:** {total_files}")
                md_lines.append(f"- **Total Functions:** {total_funcs}")
                md_lines.append(f"- **Functions with Docstrings:** {total_doc_funcs}")
                md_lines.append(f"- **Functions missing Docstrings:** {total_undoc_funcs}")
                md_lines.append(f"- **Overall Coverage:** {overall_cov:.1f}%\n" if total_funcs > 0 else "- **Overall Coverage:** N/A\n")
                
                md_lines.append("## 📁 File Breakdown")
                for fname, fdata in st.session_state.file_data.items():
                    res = fdata['results']
                    md_lines.append(f"### 📄 {fname}")
                    if "error" in res:
                        md_lines.append(f"**Error:** {res['error']}\n")
                        continue
                    
                    f_totals = res.get('total_functions', 0)
                    f_cov = "N/A" if f_totals == 0 else f"{res.get('coverage', 0):.1f}%"
                    md_lines.append(f"- **Total Functions:** {f_totals}")
                    md_lines.append(f"- **Coverage:** {f_cov}\n")
                    md_lines.append("### Functions Breakdown\n")
                    for f in res.get('functions', []):
                        doc_status = "✅ Documented" if f['has_docstring'] else "❌ Missing"
                        md_lines.append(f"- **`{f['name']}`** _(Lines {f['start_line']}-{f['end_line']})_ — {doc_status}")
                    md_lines.append("\n---\n")
                export_content = "\n".join(md_lines)
                lang = "markdown"
                mime_type = "text/markdown"
                ext = "md"
            elif export_format == "CSV":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write Header
                writer.writerow(["File Name", "Function Name", "Start Line", "End Line", "Has Docstring"])
                
                # Write Data
                for fname, fdata in st.session_state.file_data.items():
                    res = fdata['results']
                    if "error" in res:
                        writer.writerow([fname, "ERROR_PARSING", "", "", ""])
                        continue
                        
                    for f in res.get('functions', []):
                        doc_status = "TRUE" if f['has_docstring'] else "FALSE"
                        writer.writerow([fname, f['name'], f['start_line'], f['end_line'], doc_status])
                        
                export_content = output.getvalue()
                lang = "csv"
                mime_type = "text/csv"
                ext = "csv"
            else: # Plain Text
                txt_lines = ["AI CODE REVIEWER REPORT\n" + "="*40]
                txt_lines.append("OVERALL METRICS")
                txt_lines.append("-" * 20)
                txt_lines.append(f"Total Files: {total_files}")
                txt_lines.append(f"Total Functions: {total_funcs}")
                txt_lines.append(f"Functions with Docstrings: {total_doc_funcs}")
                txt_lines.append(f"Functions missing Docstrings: {total_undoc_funcs}")
                txt_lines.append(f"Overall Coverage: {overall_cov:.1f}%\n" if total_funcs > 0 else "Overall Coverage: N/A\n")
                
                txt_lines.append("FILE BREAKDOWN\n" + "="*40 + "\n")
                for fname, fdata in st.session_state.file_data.items():
                    res = fdata['results']
                    txt_lines.append(f"FILE: {fname}")
                    if "error" in res:
                        txt_lines.append(f"Error: {res['error']}\n")
                        continue
                        
                    f_totals = res.get('total_functions', 0)
                    f_cov = "N/A" if f_totals == 0 else f"{res.get('coverage', 0):.1f}%"
                    txt_lines.append(f"Total Functions: {f_totals}")
                    txt_lines.append(f"Coverage: {f_cov}\n")
                    for f in res.get('functions', []):
                        doc_status = "YES" if f['has_docstring'] else "NO"
                        txt_lines.append(f"  * {f['name']} (Lines {f['start_line']}-{f['end_line']}) | Documented: {doc_status}")
                    txt_lines.append("\n" + "-"*40 + "\n")
                export_content = "\n".join(txt_lines)
                lang = "text"
                mime_type = "text/plain"
                ext = "txt"
                
            st.write("") # small spacing
            st.download_button(
                label=f"⬇️ Download as .{ext}",
                data=export_content,
                file_name=f"code_review_report.{ext}",
                mime=mime_type,
                use_container_width=True
            )
        
            st.write("") # small spacing
            st.markdown("**Live Preview:**")
            st.code(export_content, language=lang)

def render_pep_validation_dashboard():
    # --- CHARTS (Moved to top as requested) ---
    #st.markdown("### 📈 Error Distribution")
    
    # Prepare data for charts
    error_counts = {}
    file_errors = {}
    has_any_parseable_file = False
    all_documented_and_perfect = True

    for fname, fdata in st.session_state.file_data.items():
        if "error" in fdata['results']:
            all_documented_and_perfect = False
            continue

        has_any_parseable_file = True
        _graph_funcs = fdata['results'].get('functions', [])
        _graph_doc_f = sum(1 for _f in _graph_funcs if _f.get('has_docstring'))
        _graph_total_f = len(_graph_funcs)
        f_errs = fdata['results'].get('total_docstring_errors', 0)

        # Keep dashboard status conservative when some functions are still undocumented.
        if _graph_total_f > 0 and _graph_doc_f < _graph_total_f:
            all_documented_and_perfect = False

        if f_errs > 0:
            all_documented_and_perfect = False

        # Only include files that actually have at least one docstring in the graph.
        if _graph_doc_f == 0:
            continue

        file_errors[fname] = f_errs
        for func in _graph_funcs:
            for e in func.get('docstring_errors', []):
                code = e['code']
                error_counts[code] = error_counts.get(code, 0) + 1

    # ── Refined dark-theme palettes ──
    PIE_COLORS = [
        '#4cc9f0',  # vivid sky blue
        '#f72585',  # hot pink
        '#7bed9f',  # mint green
        '#ffd166',  # warm yellow
        '#a855f7',  # electric purple
        '#06d6a0',  # emerald teal
        '#ff9f43',  # warm amber
        '#c77dff',  # soft violet
    ]

    BAR_COLORS = [
        '#ff6b6b',  # coral red
        '#ff9f43',  # warm amber
        '#ffd166',  # golden yellow
        '#f72585',  # hot pink
        '#ff4d4d',  # bright red
        '#ff7c43',  # deep orange
    ]

    # Use a real sc-header container so the glass card applies properly
    with st.container(border=True):
        st.markdown("""
        <div class='sc-header'>
            <span class='sc-header-icon' style='color:#ff7043'>📊</span>
            <h3 style='margin:0;font-size:1rem;font-weight:600;color:#e0e0e0'>Error Distribution</h3>
        </div>
        """, unsafe_allow_html=True)

        has_incomplete_docstrings = any(
            len(fdata['results'].get('functions', [])) > 0 and
            sum(1 for _f in fdata['results'].get('functions', []) if _f.get('has_docstring')) < len(fdata['results'].get('functions', []))
            for fdata in st.session_state.file_data.values()
            if "error" not in fdata['results']
        )

        if has_incomplete_docstrings:
            st.info("📝 Some functions are still missing docstrings. Charts below show available validated/docstring data.")

        if not has_any_parseable_file:
            st.info("No parseable files available for validation graphs.")
        else:
            chart_col1, chart_col2 = st.columns(2, gap="large")

            with chart_col1:
                if error_counts:
                    df_pie = pd.DataFrame(list(error_counts.items()), columns=['Error Code', 'Count'])
                    fig_pie = px.pie(
                        df_pie, values='Count', names='Error Code',
                        title='Errors by Rule Type', hole=0.45,
                        color_discrete_sequence=PIE_COLORS
                    )
                    fig_pie.update_traces(
                        textfont_size=12,
                        textfont_color='white',
                        marker=dict(line=dict(color='rgba(10,10,20,0.8)', width=2.5))
                    )
                    fig_pie.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e0e0',
                        title_font_size=14,
                        title_font_color='#ffd166',
                        title_x=0.5,
                        title_xanchor='center',
                        legend=dict(
                            orientation='h',
                            yanchor='top',
                            y=-0.15,
                            xanchor='center',
                            x=0.5,
                            font=dict(color='#cccccc', size=10),
                            bgcolor='rgba(0,0,0,0)',
                        ),
                        margin=dict(l=10, r=10, t=45, b=60),
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    if all_documented_and_perfect:
                        st.info('No errors found to chart.')

            with chart_col2:
                if any(v > 0 for v in file_errors.values()):
                    df_bar = pd.DataFrame(list(file_errors.items()), columns=['File', 'Errors'])
                    df_bar = df_bar[df_bar['Errors'] > 0].sort_values(by='Errors', ascending=False)
                    df_bar['Display File'] = df_bar['File'].apply(lambda x: compress_name(x, 18))

                    bar_colors_applied = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(df_bar))]

                    fig_bar = px.bar(
                        df_bar, x='Display File', y='Errors',
                        title='Errors by File',
                        text='Errors',
                    )
                    fig_bar.update_traces(
                        marker_color=bar_colors_applied,
                        marker_line_color='rgba(0,0,0,0.3)',
                        marker_line_width=1.2,
                        textposition='outside',
                        textfont=dict(color='#e0e0e0', size=11),
                    )
                    fig_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e0e0',
                        title_font_size=14,
                        title_font_color='#ffd166',
                        title_x=0.5,
                        xaxis=dict(
                            gridcolor='rgba(255,255,255,0.06)',
                            tickangle=-30,
                            tickfont=dict(color='#aaaaaa', size=10),
                            showline=True,
                            linecolor='rgba(255,255,255,0.08)',
                        ),
                        yaxis=dict(
                            gridcolor='rgba(255,255,255,0.06)',
                            tickfont=dict(color='#aaaaaa'),
                            showline=False,
                        ),
                        showlegend=False,
                        margin=dict(l=10, r=10, t=45, b=10),
                        bargap=0.3,
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    if all_documented_and_perfect:
                        st.info('All files are clean.')

    st.markdown("<div class='dash-content-separator'></div>", unsafe_allow_html=True)

    # ── Frosted Glass Validation Controls Bar ──
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"]:has(span#val-navbar-target)
    > div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 112, 67, 0.07) !important;
        backdrop-filter: blur(22px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(22px) saturate(200%) !important;
        border: 1px solid rgba(255, 112, 67, 0.18) !important;
        border-top: 1px solid rgba(255, 112, 67, 0.42) !important;
        border-radius: 16px !important;
        padding: 0.35rem 0.5rem !important;
        box-shadow:
            0 4px 28px rgba(0, 0, 0, 0.38),
            0 0 0 1px rgba(255, 112, 67, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
        min-height: 58px !important;
        align-items: center !important;
    }
    span#val-navbar-target { display: none !important; }
    .val-navbar-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 2.6rem;
        padding-left: 0.5rem;
        text-shadow: 0 0 22px rgba(255, 112, 67, 0.65), 0 0 6px rgba(255, 112, 67, 0.35);
    }
    </style>
    """, unsafe_allow_html=True)

    val_navbar_cont = st.container()
    with val_navbar_cont:
        st.markdown("<span id='val-navbar-target'></span>", unsafe_allow_html=True)
        vcol0, vcol1 = st.columns([0.7, 0.3])
    with vcol0:
        st.markdown("<div class='val-navbar-title'>📋 Files &amp; Validation Breakdown</div>", unsafe_allow_html=True)
    with vcol1:
        # Only show Fix All for files that have docstrings AND have errors
        files_needing_fix = [
            fname for fname, fdata in st.session_state.file_data.items()
            if "error" not in fdata['results']
            and fdata['results'].get('total_docstring_errors', 0) > 0
            and sum(1 for _f in fdata['results'].get('functions', []) if _f.get('has_docstring')) > 0
        ]
        if files_needing_fix:
            if st.button(
                f"🔧 Fix All with AI ({len(files_needing_fix)} files)",
                key="fix_all_btn",
                type="primary",
                use_container_width=True
            ):
                progress_bar = st.progress(0, text="Starting AI fixes...")
                total = len(files_needing_fix)
                for idx, fname in enumerate(files_needing_fix):
                    display_fix_name = compress_name(fname, 24)
                    progress_bar.progress(
                        (idx) / total,
                        text=f"Fixing `{display_fix_name}` ({idx+1}/{total})..."
                    )
                    try:
                        # Bulk Fix logic
                        original = st.session_state.file_data[fname]['content']
                        funcs    = st.session_state.file_data[fname]['results'].get('functions', [])
                        model    = st.session_state.fix_model
                        
                        # docstyle handle
                        res_fdata = st.session_state.file_data[fname]['results']
                        detected_style = res_fdata.get('docstring_style', 'Google')
                        if detected_style == 'None/Incomplete' or not detected_style:
                            detected_style = 'Google'

                        # Ensure cache dir
                        os.makedirs("workspace_tests/cached", exist_ok=True)
                        
                        fixed, _ = fix_code_with_ai.fix_docstrings(original, funcs, model=model, style=detected_style, filename=fname)
                        
                        if fixed != original:
                            st.session_state.file_data[fname]['content'] = fixed
                            # Persist to workspace_context
                            ctx_path = f"workspace_context/{fname}"
                            with open(ctx_path, "w", encoding="utf-8") as f:
                                f.write(fixed)
                            
                            # Re-parse first, then generate canonical tests from parsed functions.
                            st.session_state.file_data[fname]['results'] = parser.parse_file(fixed)
                            updated_results = st.session_state.file_data[fname]['results']
                            cache_path = f"workspace_tests/cached/test_{fname}"

                            if "error" not in updated_results:
                                updated_funcs = updated_results.get('functions', [])
                                documented_funcs = [f for f in updated_funcs if f.get('has_docstring')]
                                if updated_funcs and len(updated_funcs) == len(documented_funcs):
                                    canonical_tests = generate_workspace_tests.generate_pytest_for_file(
                                        fname,
                                        fixed,
                                        documented_funcs,
                                        model=model,
                                    )
                                    with open(cache_path, "w", encoding="utf-8") as f:
                                        f.write(canonical_tests)
                                elif os.path.exists(cache_path):
                                    # Avoid stale cached tests when file isn't fully documented yet.
                                    try:
                                        os.remove(cache_path)
                                    except Exception:
                                        pass
                    except Exception as e:
                        st.error(f"Failed to fix `{fname}`: {e}")
                progress_bar.progress(1.0, text="✅ All files fixed!")
                st.rerun()
        else:
            # Keep navbar height stable when the action button is not shown.
            st.markdown("<div style='height: 2.6rem;'></div>", unsafe_allow_html=True)

    total_files = len(st.session_state.file_data)
    if total_files == 0:
        st.info("No files uploaded.")
        return

    for fname, fdata in st.session_state.file_data.items():
        res = fdata['results']
        display_fname = compress_name(fname, 26)
        if "error" in res:
            with st.expander(f"⚠️ {display_fname} — Parse Error"):
                st.error(res["error"])
            continue

        # Check if the file has any docstrings at all
        _val_funcs = res.get('functions', [])
        _val_doc_f = sum(1 for _f in _val_funcs if _f.get('has_docstring'))
        if _val_doc_f == 0 and len(_val_funcs) > 0:
            with st.expander(f"⚠️ {display_fname} — SKIPPED (No docstrings to validate)"):
                st.markdown("""
                <div style='background:rgba(255,112,67,0.08);border:1px solid rgba(255,112,67,0.35);
                border-radius:12px;padding:1rem 1.2rem;'>
                    <div style='font-size:1.1rem;font-weight:700;color:#ff7043;margin-bottom:0.5rem;'>
                        ⚠️ Skipped: no docstrings found
                    </div>
                    <div style='color:#e0e0e0;font-size:0.9rem;line-height:1.6;'>
                        Reason: Validation checks docstring quality, but this file has <strong>incomplete documented functions</strong>.
                        Generate docstrings first in the <strong>📝 DocStrings</strong> tab, then navigate back to Validation tab.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
                if st.button(
                    f"📝 Go to DocStrings tab →",
                    key=f"goto_docstring_{fname}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.active_section = "📝 DocStrings"
                    st.rerun()
            continue

        f_errors = res.get('total_docstring_errors', 0)
        is_fixed = fname in st.session_state.fixed_codes
        icon = "✅" if f_errors == 0 else "🔴"
        fixed_tag = " 🟢 Fixed" if is_fixed and f_errors == 0 else ""

        with st.expander(f"{icon} {display_fname} — {f_errors} Rules Broken{fixed_tag}"):
            if f_errors == 0:
                if is_fixed:
                    st.success("✅ All issues fixed by AI! No violations remain.")
                else:
                    st.success("All functions comply with the selected strictness rules!")
            else:
                for func in res.get('functions', []):
                    errors = func.get('docstring_errors', [])
                    if errors:
                        st.markdown(f"**Function:** `{func['name']}` _(Defined at line {func['start_line']})_")
                        for e in errors:
                            st.markdown(f"- ⚠️ **Line {e['line']}:** [{e['code']}] {e['message']}")
                        st.markdown("---")

                # Per-file Fix button — only shown when errors exist
                st.markdown("")
                fix_col_model, fix_col_btn = st.columns([0.5, 0.5])
                with fix_col_model:
                    # Per-file model override
                    per_file_model_key = f"model_override_{fname}"
                    if per_file_model_key not in st.session_state:
                        st.session_state[per_file_model_key] = st.session_state.fix_model
                    chosen_model = st.selectbox(
                        "Choose an AI Model to fix this file",
                        options=list(AVAILABLE_MODELS.keys()),
                        index=list(AVAILABLE_MODELS.keys()).index(st.session_state[per_file_model_key]),
                        format_func=lambda x: AVAILABLE_MODELS[x],
                        label_visibility="visible",
                        key=f"model_select_{fname}"
                    )
                    st.session_state[per_file_model_key] = chosen_model

                with fix_col_btn:
                    st.write("")
                    st.write("")
                    if st.button(
                        f"🔧 Fix `{display_fname}` with AI",
                        key=f"fix_single_{fname}",
                        type="primary",
                        use_container_width=True
                    ):
                        with st.spinner(f"🤖 AI is fixing `{display_fname}`..."):
                            try:
                                original = st.session_state.file_data[fname]['content']
                                funcs    = res.get('functions', [])
                                model    = st.session_state[per_file_model_key]
                                
                                detected_style = res.get('docstring_style', 'Google')
                                if detected_style == 'None/Incomplete' or not detected_style:
                                    detected_style = 'Google'
                                    
                                # Ensure cached directory exists
                                os.makedirs("workspace_tests/cached", exist_ok=True)

                                # fix_docstrings returns fixed code; tests are regenerated canonically below.
                                fixed, _ = fix_code_with_ai.fix_docstrings(
                                    original_code=original, 
                                    functions_with_errors=funcs, 
                                    model=model,
                                    style=detected_style,
                                    filename=fname
                                )

                                if fixed != original:
                                    st.session_state.file_data[fname]['content'] = fixed
                                    # Update context
                                    ctx_path = f"workspace_context/{fname}"
                                    with open(ctx_path, "w", encoding="utf-8") as f:
                                        f.write(fixed)
                                    
                                    # Re-parse first, then generate canonical tests from parsed functions.
                                    st.session_state.file_data[fname]['results'] = parser.parse_file(fixed)
                                    updated_results = st.session_state.file_data[fname]['results']
                                    cache_path = f"workspace_tests/cached/test_{fname}"

                                    if "error" not in updated_results:
                                        updated_funcs = updated_results.get('functions', [])
                                        documented_funcs = [f for f in updated_funcs if f.get('has_docstring')]
                                        if updated_funcs and len(updated_funcs) == len(documented_funcs):
                                            canonical_tests = generate_workspace_tests.generate_pytest_for_file(
                                                fname,
                                                fixed,
                                                documented_funcs,
                                                model=model,
                                            )
                                            with open(cache_path, "w", encoding="utf-8") as f:
                                                f.write(canonical_tests)
                                        elif os.path.exists(cache_path):
                                            # Avoid stale cached tests when file isn't fully documented yet.
                                            try:
                                                os.remove(cache_path)
                                            except Exception:
                                                pass

                                    st.rerun()
                            except Exception as e:
                                st.error(f"Fix failed: {e}")

            # Show diff summary pills if fixed
            if is_fixed:
                original_lines = set(st.session_state.file_data[fname]['content'].splitlines())
                fixed_lines    = set(st.session_state.fixed_codes[fname].splitlines())
                added   = len(fixed_lines - original_lines)
                removed = len(original_lines - fixed_lines)
                st.markdown(
                    f'<span class="fix-pill fix-pill-added">+{added} lines added/modified</span>'
                    f'<span class="fix-pill fix-pill-modified">−{removed} lines changed</span>'
                    f'<span class="fix-pill fix-pill-modified">Model: {AVAILABLE_MODELS.get(st.session_state.fixed_codes.get("__model__" + fname, st.session_state.fix_model), "")}</span>',
                    unsafe_allow_html=True
                )


if st.session_state.app_state == 'upload':
    st.markdown("""
        <style>
        /* 1. ROOT OVERRIDES */
        header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { 
            display: none !important; 
            visibility: hidden; 
        }
        
        /* 2. BACKGROUND THEME — deep space with vivid neon blobs */
        .stApp {
            background:
                radial-gradient(ellipse 900px 700px at 8% 15%,  rgba(254, 202, 87, 0.22),  transparent 55%),
                radial-gradient(ellipse 700px 600px at 92% 10%,  rgba(255, 107, 107, 0.18), transparent 52%),
                radial-gradient(ellipse 600px 500px at 50% 85%,  rgba(72,  95, 255, 0.20), transparent 60%),
                radial-gradient(ellipse 500px 400px at 15% 90%,  rgba(0,  210, 176, 0.12), transparent 55%),
                radial-gradient(ellipse 800px 600px at 80% 75%,  rgba(154, 77,  255, 0.14), transparent 58%),
                linear-gradient(160deg, #08090f 0%, #0d0f1c 50%, #090b12 100%) !important;
            overflow: hidden !important;
        }

        /* 3. CENTER THE CONTAINER */
        [data-testid="stMain"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
            background: transparent !important;
        }

        /* 4. THE MAIN GLASS SLAB */
        .block-container {
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.06) 0%,
                rgba(255, 191, 0,   0.04) 40%,
                rgba(72,  95,  255, 0.04) 100%
            ) !important;
            backdrop-filter: blur(40px) saturate(200%) !important;
            -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 50px !important;
            padding: clamp(28px, 3.4vh, 44px) clamp(24px, 3vw, 40px) !important;
            width: fit-content !important;
            max-width: min(92vw, 860px) !important;
            min-width: 0 !important;
            height: auto !important;
            text-align: center !important;
            box-shadow:
                0 0 0 1px rgba(255, 191, 0, 0.08),
                0 40px 100px rgba(0, 0, 0, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto !important;
            margin-top: -5vh !important;
        }

        .upload-title {
            color: white;
            font-size: clamp(2.5rem, 8vw, 4.2rem);
            font-weight: 900;
            margin: 0;
            background: linear-gradient(to bottom, #ffffff, var(--primary-yellow));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
            line-height: 1.1;
        }

        .upload-tagline {
            color: #d1d6e6;
            font-size: clamp(0.95rem, 2.1vw, 1.1rem);
            font-weight: 500;
            margin-top: 10px;
            margin-bottom: 10px;
            opacity: 0.9;
            letter-spacing: 0.22px;
            text-shadow: 0 0 16px rgba(255, 191, 0, 0.12);
        }

        .upload-helper {
            width: 100%;
            max-width: 600px;
            margin: 0 auto 0.7rem auto;
            padding: 0.5rem 0.75rem;
            text-align: center;
            font-size: 0.88rem;
            color: #c7cde0;
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-left: 3px solid rgba(255, 191, 0, 0.6);
            border-radius: 12px;
            background: linear-gradient(120deg, rgba(255, 255, 255, 0.05), rgba(255, 191, 0, 0.05));
        }

        /* Scrolling glass feature cards */
        .upload-feature-strip {
            width: 100%;
            max-width: 700px;
            overflow-x: hidden;
            overflow-y: visible;
            padding-top: 6px;
            padding-bottom: 6px;
            margin: 0.85rem auto 1.45rem auto;
            mask-image: linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%);
            -webkit-mask-image: linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%);
        }

        .upload-feature-track {
            display: flex;
            gap: 0.9rem;
            width: max-content;
            animation: upload-cards-scroll 34s linear infinite;
        }

        .upload-feature-track:hover {
            animation-play-state: paused;
        }

        .upload-feature-card {
            width: 290px;
            min-height: 158px;
            border-radius: 18px;
            padding: 0.95rem 1rem;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 191, 0, 0.06) 55%, rgba(72, 95, 255, 0.08));
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-top: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.08),
                0 10px 30px rgba(0, 0, 0, 0.35),
                0 0 0 1px rgba(255, 191, 0, 0.08);
            backdrop-filter: blur(18px) saturate(160%);
            -webkit-backdrop-filter: blur(18px) saturate(160%);
            flex-shrink: 0;
            transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
        }

        .upload-feature-card:hover {
            border-color: var(--primary-yellow);
            border-top-color: var(--primary-yellow);
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.14),
                0 12px 34px rgba(0, 0, 0, 0.42),
                0 0 0 1px rgba(255, 191, 0, 0.45),
                0 0 24px rgba(255, 191, 0, 0.32);
            transform: translateY(0);
        }

        .upload-feature-title {
            font-size: 1rem;
            font-weight: 800;
            color: #ffe082;
            margin-bottom: 0.7rem;
            letter-spacing: 0.2px;
        }

        .upload-feature-emoji {
            font-size: 2rem;
            line-height: 1;
            margin: 0 0 0.75rem 0;
            filter: drop-shadow(0 0 10px rgba(255, 191, 0, 0.28));
        }

        .upload-feature-desc {
            font-size: 0.9rem;
            line-height: 1.5;
            color: #d8dbe6;
        }

        .upload-action-card {
            width: 100%;
            max-width: 650px;
            margin: 0.1rem auto 0 auto;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-action-anchor) {
            width: 100% !important;
            max-width: 650px !important;
            margin: 0.1rem auto 0 auto !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-action-anchor) [data-testid="stFileUploader"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-action-anchor) [data-testid="stButton"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-action-anchor) div[data-testid="stAlert"] {
            max-width: 100% !important;
        }

        @keyframes upload-cards-scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        div[data-testid="stAlert"] {
            width: 100% !important;
            max-width: 600px !important;
            margin: 0.7rem auto 0.1rem auto !important;
            box-sizing: border-box !important;
            text-align: left !important;
        }

        /* Keep uploader centered inside flex container */
        [data-testid="stFileUploader"] {
            width: 100% !important;
            max-width: 600px !important;
            margin: 0 auto !important;
            text-align: left !important;
        }
        
        /* Center Streamlit native buttons */
        [data-testid="stButton"] {
            display: flex;
            justify-content: center;
            width: 100% !important;
            margin: 0 auto !important;
        }
        
        [data-testid="stButton"] button {
            width: auto !important;
            min-width: 250px !important;
            margin: 0 auto !important;
            border-radius: 8px !important;
        }

        /* Ensure markdown cells inherit centering */
        [data-testid="stMarkdownContainer"] {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="upload-title">⚡ AI Code Reviewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-tagline">Docstring quality cockpit for Python workspaces</div>', unsafe_allow_html=True)

    upload_feature_cards = [
        ("Instant Analysis", "⚡", "Drop your files. Get full docstring coverage, function counts, and compliance mapped out in seconds."),
        ("AI Docstring Fixing", "🧠", "Missing or broken docstrings? AI rewrites them for you — one file or the entire workspace."),
        ("Style Conversion", "🎨", "Switch between Google, reST, and NumPy docstring styles instantly. Per function or whole file."),
        ("Three-Layer Validation", "🔍", "PEP 257 + parameter accuracy + AST safety net. Every docstring checked from every angle."),
        ("Auto Test Generation", "🧪", "AI writes and runs pytest suites for your code. Live results, diagnostics, and tracebacks included."),
        ("Smart Dashboard", "📊", "Filter, search, and track every function across your workspace. Metrics update as you fix."),
        ("Flexible Exports", "📥", "Download coverage reports as JSON, Markdown, CSV, or Plain Text — per file or workspace-wide."),
        ("IDE-Like Interface", "🖥️", "Dark theme, fixed sidebar, multi-tab viewer. Built to feel like a dev tool, not a web form."),
    ]

    staged_uploads = st.session_state.get("upload_files_main")
    show_feature_cards = not bool(staged_uploads)
    if show_feature_cards:
        cards_markup = "".join(
            [
                f"<div class='upload-feature-card'><div class='upload-feature-title'>{title}</div><div class='upload-feature-emoji'>{emoji}</div><div class='upload-feature-desc'>{desc}</div></div>"
                for title, emoji, desc in (upload_feature_cards * 2)
            ]
        )
        st.markdown(
            f"""
            <div class='upload-feature-strip'>
                <div class='upload-feature-track'>
                    {cards_markup}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown("<span class='upload-action-anchor' style='display:none;'></span>", unsafe_allow_html=True)
        st.markdown('<div class="upload-helper">Upload .py files or .zip source folders, then click <b>Analyze Workspace</b>.</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload files",
            type=['py', 'zip'],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="upload_files_main"
        )

        warn_box = st.empty()
        if st.button("🚀 Analyze Workspace", type="primary", use_container_width=True):
            if not uploaded_files:
                warn_box.warning("Please upload at least one file.")
            else:
                # Inject a full-screen loading overlay immediately
                # Inject a full-screen loading overlay via an iframe to perfectly escape the CSS stacking context
                loading_overlay = st.empty()
                with loading_overlay:
                    components.html("""
                    <script>
                    // Inject overlay directly into the PARENT document's body
                    // This fully escapes Streamlit's stacking context
                    const overlay = window.parent.document.createElement('div');
                    overlay.id = 'fullscreen-loading-overlay';
                    overlay.innerHTML = `
                        <div style="
                            width:60px; height:60px;
                            border:4px solid rgba(255,191,0,0.2);
                            border-top:4px solid #ffbf00;
                            border-radius:50%;
                            animation:spin 1s linear infinite;
                            margin-bottom:20px;
                        "></div>
                        <div style="color:white;font-size:1.5rem;font-weight:600;letter-spacing:1px;font-family:sans-serif;">
                            Analyzing Workspace...
                        </div>
                    `;
                    overlay.style.cssText = `
                        position: fixed !important;
                        top: 0 !important; left: 0 !important;
                        right: 0 !important; bottom: 0 !important;
                        width: 100vw !important; height: 100vh !important;
                        background: rgba(0,0,0,0.85) !important;
                        backdrop-filter: blur(5px) !important;
                        z-index: 9999999 !important;
                        display: flex !important;
                        flex-direction: column !important;
                        justify-content: center !important;
                        align-items: center !important;
                    `;
                
                    // Inject keyframe animation into parent
                    const style = window.parent.document.createElement('style');
                    style.id = 'fullscreen-loading-style';
                    style.textContent = '@keyframes spin { 0%{transform:rotate(0deg)} 100%{transform:rotate(360deg)} }';
                    window.parent.document.head.appendChild(style);
                    window.parent.document.body.appendChild(overlay);
                    </script>
                    """, height=0, width=0)
                
                # Perform the blocking parse
                success = process_uploaded_files(uploaded_files)
                
                # Clear overlay and route
                loading_overlay.empty()
                # Clean up the parent-injected overlay
                components.html("""
                <script>
                const el = window.parent.document.getElementById('fullscreen-loading-overlay');
                if(el) el.remove();
                const styleEl = window.parent.document.getElementById('fullscreen-loading-style');
                if(styleEl) styleEl.remove();
                </script>
                """, height=0, width=0)
                
                if success:
                    st.session_state.app_state = 'ide'
                    st.rerun()
                else:
                    st.error("No valid Python files found.")

elif st.session_state.app_state == 'ide':
    # --- SIDEBAR (IDE Left Panel) ---
    with st.sidebar:
        st.markdown('<div class="explorer-header">📂 Explorer</div>', unsafe_allow_html=True)

        # Navigation
        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)

        nav_options = ["🏠 Home", "🎛️ Dashboard", "📝 DocStrings", "✅ Validation", "📈 Metrics"]
        selected_nav = st.selectbox(
            "navigation_selector",
            options=nav_options,
            index=nav_options.index(st.session_state.active_section),
            label_visibility="collapsed",
            key="navigation_selector"
        )
        if selected_nav != st.session_state.active_section:
            st.session_state.active_section = selected_nav
            if '📊 Dashboard' not in st.session_state.open_tabs:
                st.session_state.open_tabs.insert(0, '📊 Dashboard')
            st.session_state._pending_tab_switch = '📊 Dashboard'
            st.rerun()

        # AI Fix Model selector
        st.markdown('<div class="sidebar-section-label">Choose AI Fix Model</div>', unsafe_allow_html=True)
        new_fix_model = st.selectbox(
            "fix_model_selector",
            options=list(AVAILABLE_MODELS.keys()),
            index=list(AVAILABLE_MODELS.keys()).index(st.session_state.fix_model),
            format_func=lambda x: AVAILABLE_MODELS[x],
            label_visibility="collapsed",
            key="fix_model_selector"
        )
        if new_fix_model != st.session_state.fix_model:
            st.session_state.fix_model = new_fix_model
        
        # Add Files uploader
        st.markdown('<div class="sidebar-section-label">Add Files</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-uploader">', unsafe_allow_html=True)
        new_files = st.file_uploader("➕ Add files", type=['py', 'zip'], accept_multiple_files=True, key=f"add_{st.session_state.uploader_key}", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        if new_files:
            with st.spinner("Analyzing Workspace... Please wait."):
                process_uploaded_files(new_files)
            st.session_state.uploader_key += 1
            st.rerun()
                
        # File list
        st.markdown('<div class="sidebar-section-label">Files</div>', unsafe_allow_html=True)
        
        if not st.session_state.file_data:
            st.info("No files in workspace.")
            st.session_state.app_state = 'upload'
            st.rerun()
            
        for fname in list(st.session_state.file_data.keys()):
            display_name = compress_name(fname, 13)
                
            col1, col2, col3 = st.columns([0.70, 0.15, 0.15])
            with col1:
                if st.button(f"📄 {display_name}", key=f"open_{fname}", help=fname, use_container_width=True):
                    if fname not in st.session_state.open_tabs:
                        st.session_state.open_tabs.append(fname)
                    st.session_state._pending_tab_switch = fname
                    st.rerun()
            with col2:
                # Download fixed code if available, otherwise original
                file_content_to_dl = st.session_state.fixed_codes.get(
                    fname,
                    st.session_state.file_data[fname]['content']
                )
                dl_fname = f"fixed_{fname}" if fname in st.session_state.fixed_codes else fname
                st.download_button(
                    " ",
                    data=file_content_to_dl,
                    file_name=dl_fname,
                    key=f"dl_{fname}",
                    use_container_width=True,
                    help="Download fixed version" if fname in st.session_state.fixed_codes else "Download original"
                )
            with col3:
                # Use Bootstrap trash icon HTML inside the button via CSS
                if st.button(" ", key=f"del_{fname}", use_container_width=True):
                    # Clear results and fingerprint so test dashboard resets
                    st.session_state.pop('workspace_test_json', None)
                    st.session_state.pop('_last_test_hash', None)
                    st.session_state.pop('skipped_test_files', None)
                    
                    del st.session_state.file_data[fname]
                    st.session_state.fixed_codes.pop(fname, None)
                    if fname in st.session_state.open_tabs:
                        st.session_state.open_tabs.remove(fname)
                    st.rerun()


    # --- MAIN CONTENT (IDE Center Panel with Tabs) ---
    if not st.session_state.open_tabs:
        st.session_state.open_tabs = ['📊 Dashboard']
        
    # Ensure standalone PEP tab is removed from state if it existed
    if '✅ PEP Validation' in st.session_state.open_tabs:
        st.session_state.open_tabs.remove('✅ PEP Validation')

    # Compress tab names for uniform width rendering
    tab_names_display = []
    for t_name in st.session_state.open_tabs:
        if t_name == '📊 Dashboard':
            tab_names_display.append(st.session_state.active_section)
        else:
            compressed = compress_name(t_name, 15)
            tab_names_display.append("📄 " + compressed)
                
    tabs = st.tabs(tab_names_display)
    
    for i, tab_name in enumerate(st.session_state.open_tabs):
        with tabs[i]:
            if tab_name == '📊 Dashboard':
                render_overall_dashboard()
            elif tab_name in st.session_state.file_data:
                render_single_file(tab_name, st.session_state.file_data[tab_name])

    # Auto-switch tab + optional scroll logic
    pending_switch = st.session_state._pending_tab_switch

    if pending_switch:
        target_index = None
        if pending_switch in st.session_state.open_tabs:
            target_index = st.session_state.open_tabs.index(pending_switch)
        st.session_state._pending_tab_switch = None

        if target_index is not None:
            expected_tabs_count = len(st.session_state.open_tabs)
            components.html(f"""
            <script>
            (() => {{
                const targetIndex = {target_index};
                const expectedTabsCount = {expected_tabs_count};
                let attempts = 0;

                const clickTargetTab = () => {{
                    const tabLists = window.parent.document.querySelectorAll('.stTabs [data-baseweb="tab-list"]');
                    let mainTabEls = null;

                    tabLists.forEach((tabList) => {{
                        if (mainTabEls) return;
                        const candidates = tabList.querySelectorAll('[data-baseweb="tab"]');
                        if (candidates.length === expectedTabsCount) {{
                            mainTabEls = candidates;
                        }}
                    }});

                    if (!mainTabEls && tabLists.length > 0) {{
                        // Fallback: use the first tab list when exact size match is not found.
                        mainTabEls = tabLists[0].querySelectorAll('[data-baseweb="tab"]');
                    }}

                    if (mainTabEls && mainTabEls.length > targetIndex && mainTabEls[targetIndex]) {{
                        mainTabEls[targetIndex].scrollIntoView({{ block: 'nearest', inline: 'center' }});
                        mainTabEls[targetIndex].click();
                        return;
                    }}

                    attempts += 1;
                    if (attempts < 20) {{
                        window.setTimeout(clickTargetTab, 75);
                    }}
                }};

                clickTargetTab();
            }})();
            </script>
            """, height=0, width=0)

render_faq_overlay()
