import streamlit as st
import os
import parser
import zipfile
import io
import streamlit.components.v1 as components

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
    
    /* Force the second column (Delete button) to strictly preserve its size */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
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
    
    /* Delete button styling */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        border: none !important;
        background: transparent !important;
        border-left: 1px solid var(--outline-color) !important;
        border-radius: 0 6px 6px 0 !important;
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
    }
    
    /* Turn text/emoji red on hover */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
        background-color: rgba(255, 107, 107, 0.1) !important;
        color: #ff6b6b !important;
        text-shadow: 0 0 8px rgba(255,107,107,0.4); /* Glow for effect */
    }
    
    /* Hide BOTH button inner wrappers and text so they don't shift the icon */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button > div,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button p {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Inject Bootstrap Icon via CSS and center it absolutely */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) button::before {
        font-family: "bootstrap-icons" !important;
        content: "\\f5de" !important; /* Unicode for bi-trash */
        font-size: 1.05rem !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        -webkit-font-smoothing: antialiased;
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
    
    /* Primary buttons (yellow) */
    button[kind="primary"] {
        border-radius: 8px !important;
        background-color: var(--primary-yellow) !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 191, 0, 0.3) !important;
        color: #000000 !important;
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
        border-bottom: 1px solid var(--outline-color);
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
        border: 1px solid var(--outline-color);
        border-bottom: none;
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
        background-color: var(--bg-dark) !important;
        border: 1px solid var(--outline-color) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 2.5rem !important;
        height: calc(100vh - 42px) !important; 
        overflow-y: auto !important;
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

def process_uploaded_files(uploaded_files_list):
    has_files = False
    for file in uploaded_files_list:
        if file.name.endswith('.py'):
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
                                st.session_state.file_data[zinfo.filename] = {
                                    'content': content,
                                    'results': parser.parse_file(content)
                                }
                                if zinfo.filename not in st.session_state.open_tabs:
                                    st.session_state.open_tabs.append(zinfo.filename)
                                has_files = True
            except Exception as e:
                st.error(f"Error reading zip file {file.name}: {e}")
    return has_files

def render_single_file(fname, fl_data):
    results = fl_data['results']
    
    st.markdown('<div class="main-file-header-container">', unsafe_allow_html=True)
    col_title, col_close = st.columns([0.85, 0.15])
    
    display_name = fname
    if len(fname) > 18:
        display_name = fname[:8] + "..." + fname[-7:]

    with col_title:
        st.markdown(f'<div class="main-file-title" title="{fname}">📄 {display_name}</div>', unsafe_allow_html=True)
    with col_close:
        if st.button("✖ Close File", key=f"close_btn_{fname}", help="Close this file tab (File remains in workspace sidebar)"):
            if fname in st.session_state.open_tabs:
                st.session_state.open_tabs.remove(fname)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
            
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
    
    # Row 1 of metrics
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total No. of Functions</div>
            <div class="metric-value">{total_f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Functions Having Doc String</div>
            <div class="metric-value" style="color: var(--primary-yellow);">{doc_f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Row 2 of metrics
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Functions Not Having Doc String</div>
            <div class="metric-value" style="color: #ff6b6b;">{undoc_f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-color: {cov_color};">
            <div class="metric-title">Coverage Percentage</div>
            <div class="metric-value" style="color: {cov_color};">{cov_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Original Code")
    edited_code = st.text_area("Edit code", value=fl_data['content'], height=400, label_visibility="collapsed")
    st.download_button(
        label=f"⬇️ Download Edited {fname}",
        data=edited_code,
        file_name=fname,
        mime="text/plain",
        use_container_width=True
    )
    st.write("")
        
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
            
    st.markdown("<br>", unsafe_allow_html=True)
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

def render_overall_dashboard():
    st.markdown("## 📊 Whole Project Dashboard")
    st.markdown("---")
    
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
            <div class="metric-value">{files_with_docstrings}</div>
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
            <div class="metric-value" style="color: var(--primary-yellow);">{total_doc_funcs}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Functions Not Having Doc String</div>
            <div class="metric-value" style="color: #ff6b6b;">{total_undoc_funcs}</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        cov_color = "var(--primary-yellow)" if overall_cov == 100 else ("#ff6b6b" if overall_cov < 50 else "#feca57")
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

    st.markdown("### 📁 File Breakdown")
    
    if total_files == 0:
        st.info("No files uploaded.")
        return
        
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
                    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📥 Export the Report")
    
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
                    

# --- VIEW ROUTING ---

if st.session_state.app_state == 'upload':
    st.markdown("""
        <style>
        /* 1. ROOT OVERRIDES */
        header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { 
            display: none !important; 
            visibility: hidden; 
        }
        
        /* 2. BACKGROUND THEME */
        .stApp {
            background: 
                radial-gradient(1200px 800px at 12% 10%, rgba(254, 202, 87, 0.15), transparent 60%),
                radial-gradient(900px 700px at 85% 20%, rgba(255, 107, 107, 0.08), transparent 58%),
                linear-gradient(180deg, #0f1117, #0b0d14) !important;
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

        /* 4. THE MAIN GLASS SLAB (overriding Streamlit container) */
        .block-container {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(35px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(35px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 50px !important;
            padding: 60px 40px !important;
            width: 90vw !important;
            max-width: 800px !important;
            text-align: center !important;
            box-shadow: 0 40px 100px rgba(0, 0, 0, 0.5) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto !important;
            margin-top: -5vh !important; /* visually center slightly higher */
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

        .upload-subtitle {
            color: #e2e8f0;
            font-size: clamp(1.1rem, 3vw, 1.3rem); 
            font-weight: 500;
            margin-top: 10px; 
            margin-bottom: 35px;
            opacity: 0.7;
            letter-spacing: 0.5px;
            text-shadow: 0 0 25px rgba(254, 202, 87, 0.2);
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
    st.markdown('<div class="upload-subtitle">Upload your Python files or ZIP folders to begin the analysis</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload files", 
        type=['py', 'zip'], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    st.write("")
    
    # Use columns to strictly center the native Streamlit button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        if st.button("🚀 Analyze Workspace", type="primary", use_container_width=True):
            if not uploaded_files:
                st.warning("Please upload at least one file.")
            else:
                success = process_uploaded_files(uploaded_files)
                if success:
                    st.session_state.app_state = 'ide'
                    st.rerun()
                else:
                    st.error("No valid Python files found.")

elif st.session_state.app_state == 'ide':
    # --- SIDEBAR (IDE Left Panel) ---
    with st.sidebar:
        st.markdown('<div class="explorer-header">📂 Explorer</div>', unsafe_allow_html=True)
        
        # Add Files uploader
        st.markdown('<div class="sidebar-section-label">Add Files</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-uploader">', unsafe_allow_html=True)
        new_files = st.file_uploader("➕ Add files", type=['py', 'zip'], accept_multiple_files=True, key=f"add_{st.session_state.uploader_key}", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        if new_files:
            process_uploaded_files(new_files)
            st.session_state.uploader_key += 1
            st.rerun()
            
        # Navigation
        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
        nav_col1, nav_col2 = st.columns([0.99, 0.01])
        with nav_col1:
            if st.button("📊 Project Dashboard", key="nav_dash", use_container_width=True):
                if '📊 Dashboard' not in st.session_state.open_tabs:
                    st.session_state.open_tabs.insert(0, '📊 Dashboard')
                st.session_state._pending_tab_switch = '📊 Dashboard'
                st.rerun()
                
        # File list
        st.markdown('<div class="sidebar-section-label">Files</div>', unsafe_allow_html=True)
        
        if not st.session_state.file_data:
            st.info("No files in workspace.")
            st.session_state.app_state = 'upload'
            st.rerun()
            
        for fname in list(st.session_state.file_data.keys()):
            display_name = fname
            if len(fname) > 18:
                display_name = fname[:8] + "..." + fname[-7:]
                
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                if st.button(f"📄 {display_name}", key=f"open_{fname}", help=fname, use_container_width=True):
                    if fname not in st.session_state.open_tabs:
                        st.session_state.open_tabs.append(fname)
                    st.session_state._pending_tab_switch = fname
                    st.rerun()
            with col2:
                # Use Bootstrap trash icon HTML inside the button
                if st.button(" ", key=f"del_{fname}", help=f"Delete {fname} entirely from workspace analysis", use_container_width=True):
                    del st.session_state.file_data[fname]
                    if fname in st.session_state.open_tabs:
                        st.session_state.open_tabs.remove(fname)
                    st.rerun()
                    
    # --- MAIN CONTENT (IDE Center Panel with Tabs) ---
    if not st.session_state.open_tabs:
        st.session_state.open_tabs = ['📊 Dashboard']
        
    tabs = st.tabs(st.session_state.open_tabs)
    
    for i, tab_name in enumerate(st.session_state.open_tabs):
        with tabs[i]:
            if tab_name == '📊 Dashboard':
                render_overall_dashboard()
            elif tab_name in st.session_state.file_data:
                render_single_file(tab_name, st.session_state.file_data[tab_name])

    # Auto-switch tab when triggered from sidebar
    if st.session_state._pending_tab_switch:
        target = st.session_state._pending_tab_switch
        st.session_state._pending_tab_switch = None
        safe_target = target.replace("'", "\\'")
        components.html(f"""
        <script>
        const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        for (const t of tabs) {{
            if (t.textContent.trim() === '{safe_target}') {{
                t.click();
                break;
            }}
        }}
        </script>
        """, height=0)