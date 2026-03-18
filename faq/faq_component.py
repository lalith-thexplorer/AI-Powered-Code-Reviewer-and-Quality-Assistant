import json
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components

from faq.faq_data import FAQ_DATA


def _sync_faq_bridge_state() -> None:
    """Sync button/popup UI state from the hidden bridge widget into session state."""
    if "faq_open" not in st.session_state:
        st.session_state.faq_open = False
    if "faq_bridge" not in st.session_state:
        st.session_state.faq_bridge = ""
    if "_faq_bridge_seen" not in st.session_state:
        st.session_state._faq_bridge_seen = ""
    if "faq_active_tab_label" not in st.session_state:
        st.session_state.faq_active_tab_label = ""

    raw = st.session_state.get("faq_bridge", "")
    if not raw or raw == st.session_state.get("_faq_bridge_seen", ""):
        return

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        st.session_state._faq_bridge_seen = raw
        return

    st.session_state.faq_open = bool(payload.get("open", False))
    active_tab_label = str(payload.get("active_tab_label", "")).strip()
    if active_tab_label:
        st.session_state.faq_active_tab_label = active_tab_label
    st.session_state._faq_bridge_seen = raw


def get_current_screen_id() -> str:
    """
    Reads the current active screen from session state and returns the matching
    screen_id key from FAQ_DATA. Returns fallback "general" when not found.
    """
    app_state = st.session_state.get("app_state", "upload")
    if app_state != "ide":
        return "upload-screen"

    active_tab_label = str(st.session_state.get("faq_active_tab_label", "")).strip()
    if active_tab_label.startswith("📄"):
        return "file-tab"

    active_section = st.session_state.get("active_section", "🏠 Home")

    if active_section == "🎛️ Dashboard":
        dash_active_tab = st.session_state.get("dash_active_tab", "Advanced Filters")
        dashboard_map = {
            "Advanced Filters": "dashboard-advanced-filters",
            "Search": "dashboard-search",
            "Tests": "dashboard-tests",
            "Export": "dashboard-export",
            "Help": "dashboard-help",
        }
        return dashboard_map.get(dash_active_tab, "dashboard-screen")

    section_map = {
        "🏠 Home": "home-screen",
        "✅ Validation": "validation-screen",
        "📝 DocStrings": "docstrings-screen",
        "📈 Metrics": "metrics-screen",
    }

    screen_id = section_map.get(active_section)
    if screen_id:
        return screen_id

    return "general"


def render_faq_button() -> None:
    """Inject a persistent floating FAQ button into the parent document."""
    _sync_faq_bridge_state()

    st.markdown(
        """
        <style>
            .st-key-faq_bridge {
                display: none !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("faq_bridge", key="faq_bridge", label_visibility="collapsed")

    is_open_js = "true" if bool(st.session_state.get("faq_open", False)) else "false"
    components.html(
        f"""
        <script>
        (function() {{
            const hostWin = window.parent;
            const doc = window.parent.document;
            const btnId = "faq-floating-button";
            const styleId = "faq-floating-button-style";

            if (!doc.getElementById(styleId)) {{
                const style = doc.createElement("style");
                style.id = styleId;
                style.textContent = `
                    #${{btnId}} {{
                        position: fixed;
                        bottom: 28px;
                        right: 28px;
                        width: 48px;
                        height: 48px;
                        border-radius: 999px;
                        border: 1.5px solid #ffbf00;
                        background: rgba(20, 20, 30, 0.85);
                        box-shadow: 0 0 12px rgba(255, 191, 0, 0.4);
                        color: #ffbf00;
                        font: inherit;
                        font-weight: 700;
                        font-size: 22px;
                        line-height: 1;
                        cursor: pointer;
                        backdrop-filter: blur(10px);
                        -webkit-backdrop-filter: blur(10px);
                        transition: all 0.2s ease;
                        z-index: 999999;
                    }}
                    #${{btnId}}:hover {{
                        background: rgba(35, 35, 50, 0.92);
                        box-shadow: 0 0 18px rgba(255, 191, 0, 0.65);
                    }}
                    #${{btnId}}.faq-open {{
                        background: #ffbf00;
                        color: rgba(20, 20, 30, 0.95);
                        box-shadow: 0 0 18px rgba(255, 191, 0, 0.8);
                    }}
                `;
                doc.head.appendChild(style);
            }}

            function getActiveTabLabel() {{
                const selected = doc.querySelector('.stTabs [data-baseweb="tab"][aria-selected="true"]');
                return selected ? (selected.innerText || "").trim() : "";
            }}

            function getBridgeInput() {{
                return (
                    doc.querySelector(".st-key-faq_bridge input") ||
                    doc.querySelector('input[aria-label="faq_bridge"]') ||
                    doc.querySelector('input[id*="faq_bridge"]')
                );
            }}

            function pushBridgeState() {{
                const bridgeInput = getBridgeInput();
                if (!bridgeInput) return;

                const payload = JSON.stringify({{
                    open: !!hostWin.__faqOpen,
                    active_tab_label: getActiveTabLabel(),
                }});

                if (bridgeInput.value === payload) return;

                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                setter.call(bridgeInput, payload);
                bridgeInput.dispatchEvent(new Event("input", {{ bubbles: true }}));
                bridgeInput.dispatchEvent(new Event("change", {{ bubbles: true }}));
            }}

            const serverOpen = {is_open_js};
            if (typeof hostWin.__faqOpen !== "boolean") {{
                hostWin.__faqOpen = serverOpen;
            }} else if (serverOpen && !hostWin.__faqOpen) {{
                // Respect explicit server-side opens but do not force-close client state on reruns.
                hostWin.__faqOpen = true;
            }}

            hostWin.__setFaqOpen = function(nextOpen) {{
                hostWin.__faqOpen = !!nextOpen;
                const btn = doc.getElementById(btnId);
                if (btn) btn.classList.toggle("faq-open", !!hostWin.__faqOpen);
                if (typeof hostWin.__faqRenderPopup === "function") {{
                    hostWin.__faqRenderPopup();
                }}
                pushBridgeState();
            }};

            let btn = doc.getElementById(btnId);
            if (!btn) {{
                btn = doc.createElement("button");
                btn.id = btnId;
                btn.type = "button";
                btn.textContent = "?";
                btn.setAttribute("aria-label", "Open FAQ help");
                doc.body.appendChild(btn);
            }}

            // Always bind handler on each run so stale buttons remain interactive across reruns.
            btn.onclick = function() {{
                if (typeof hostWin.__setFaqOpen === "function") {{
                    hostWin.__setFaqOpen(!hostWin.__faqOpen);
                }}
            }};

            btn.classList.toggle("faq-open", !!hostWin.__faqOpen);
            if (typeof hostWin.__faqRenderPopup === "function") {{
                hostWin.__faqRenderPopup();
            }}

            if (!hostWin.__faqTabWatcherId) {{
                hostWin.__faqLastTopTabLabel = getActiveTabLabel();
                hostWin.__faqTabWatcherId = window.setInterval(function() {{
                    const nextLabel = getActiveTabLabel();
                    if (nextLabel !== hostWin.__faqLastTopTabLabel) {{
                        hostWin.__faqLastTopTabLabel = nextLabel;
                        if (hostWin.__faqOpen && typeof hostWin.__faqRenderPopup === "function") {{
                            hostWin.__faqRenderPopup();
                        }}
                        pushBridgeState();
                    }}
                }}, 250);
            }}

            pushBridgeState();
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def render_faq_popup(screen_name: str, faqs: List[Dict[str, str]]) -> None:
    """Render the FAQ popup overlay in the parent document."""
    payload = {
        "screen_name": screen_name,
        "faqs": faqs,
        "faq_data": FAQ_DATA,
        "context": {
            "app_state": st.session_state.get("app_state", "upload"),
            "active_section": st.session_state.get("active_section", "🏠 Home"),
            "dash_active_tab": st.session_state.get("dash_active_tab", "Advanced Filters"),
        },
    }
    payload_json = json.dumps(payload)

    components.html(
        f"""
        <script>
        (function() {{
            const hostWin = window.parent;
            const doc = window.parent.document;
            const popupId = "faq-popup-overlay";
            const styleId = "faq-popup-style";
            const data = {payload_json};

            hostWin.__faqPopupData = data;

            function getActiveTabLabel() {{
                const selected = doc.querySelector('.stTabs [data-baseweb="tab"][aria-selected="true"]');
                return selected ? (selected.innerText || "").trim() : "";
            }}

            function resolveScreenId(sourceData) {{
                const ctx = sourceData.context || {{}};
                if (ctx.app_state !== "ide") {{
                    return "upload-screen";
                }}

                const activeTopTab = getActiveTabLabel();
                if (activeTopTab.startsWith("📄")) {{
                    return "file-tab";
                }}

                if (ctx.active_section === "🎛️ Dashboard") {{
                    const map = {{
                        "Advanced Filters": "dashboard-advanced-filters",
                        "Search": "dashboard-search",
                        "Tests": "dashboard-tests",
                        "Export": "dashboard-export",
                        "Help": "dashboard-help",
                    }};
                    return map[ctx.dash_active_tab] || "dashboard-screen";
                }}

                const sectionMap = {{
                    "🏠 Home": "home-screen",
                    "✅ Validation": "validation-screen",
                    "📝 DocStrings": "docstrings-screen",
                    "📈 Metrics": "metrics-screen",
                }};
                return sectionMap[ctx.active_section] || "general";
            }}

            function resolveFaqEntry(sourceData) {{
                const dataMap = sourceData.faq_data || {{}};
                const resolvedId = resolveScreenId(sourceData);
                const general = dataMap.general || {{ screen_name: "General Help", faqs: [] }};
                const candidate = dataMap[resolvedId];

                if (!candidate || !Array.isArray(candidate.faqs) || candidate.faqs.length === 0) {{
                    return general;
                }}

                return candidate;
            }}

            if (!doc.getElementById(styleId)) {{
                const style = doc.createElement("style");
                style.id = styleId;
                style.textContent = `
                    @keyframes faq-popup-in {{
                        from {{ opacity: 0; transform: translateY(10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}

                    #${{popupId}} {{
                        position: fixed;
                        bottom: 90px;
                        right: 28px;
                        width: 420px;
                        max-height: 70vh;
                        overflow-y: auto;
                        border-radius: 16px;
                        background: rgba(15, 15, 25, 0.92);
                        border: 1px solid rgba(255, 191, 0, 0.3);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), 0 0 20px rgba(255, 191, 0, 0.1);
                        backdrop-filter: blur(20px);
                        -webkit-backdrop-filter: blur(20px);
                        padding: 20px;
                        z-index: 999999;
                        animation: faq-popup-in 0.25s ease;
                        color: #e0e0e0;
                        font: inherit;
                    }}

                    #${{popupId}}::-webkit-scrollbar {{ width: 4px; }}
                    #${{popupId}}::-webkit-scrollbar-track {{ background: transparent; }}
                    #${{popupId}}::-webkit-scrollbar-thumb {{ background: rgba(255, 191, 0, 0.3); border-radius: 999px; }}
                    #${{popupId}}::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 191, 0, 0.6); }}

                    .faq-popup-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 12px;
                    }}

                    .faq-popup-title {{
                        color: #ffbf00;
                        font-size: 15px;
                        font-weight: 700;
                    }}

                    .faq-popup-close {{
                        border: 1px solid rgba(255, 191, 0, 0.25);
                        border-radius: 8px;
                        background: rgba(20, 20, 30, 0.65);
                        color: #ffbf00;
                        font: inherit;
                        font-size: 13px;
                        cursor: pointer;
                        padding: 4px 8px;
                        transition: all 0.2s ease;
                    }}

                    .faq-popup-close:hover {{
                        background: rgba(255, 191, 0, 0.15);
                        border-color: rgba(255, 191, 0, 0.45);
                    }}

                    .faq-item {{
                        width: 100%;
                        margin-bottom: 8px;
                        background: rgba(255, 255, 255, 0.03);
                        border: 1px solid rgba(255, 191, 0, 0.15);
                        border-radius: 10px;
                        overflow: hidden;
                        transition: border-color 0.2s ease;
                    }}

                    .faq-question {{
                        padding: 12px 16px;
                        font-size: 13px;
                        font-weight: 500;
                        color: #e0e0e0;
                        cursor: pointer;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        transition: all 0.2s ease;
                        user-select: none;
                    }}

                    .faq-item:hover {{
                        border-color: rgba(255, 191, 0, 0.35);
                    }}

                    .faq-item:hover .faq-question {{
                        background: rgba(255, 191, 0, 0.06);
                        color: #ffbf00;
                    }}

                    .faq-chevron {{
                        color: #ffbf00;
                        transition: transform 0.2s ease;
                        margin-left: 10px;
                        flex-shrink: 0;
                    }}

                    .faq-answer {{
                        max-height: 0;
                        overflow: hidden;
                        padding: 0 16px 0 16px;
                        font-size: 12.5px;
                        line-height: 1.6;
                        color: rgba(255, 255, 255, 0.65);
                        border-top: 1px solid rgba(255, 191, 0, 0.1);
                        transition: max-height 0.2s ease, padding 0.2s ease;
                    }}

                    .faq-item.open .faq-chevron {{
                        transform: rotate(180deg);
                    }}

                    .faq-item.open .faq-answer {{
                        max-height: 500px;
                        padding: 0 16px 14px 16px;
                    }}
                `;
                doc.head.appendChild(style);
            }}

            hostWin.__faqRenderPopup = function() {{
                const sourceData = hostWin.__faqPopupData || data;
                const oldPopup = doc.getElementById(popupId);

                if (!hostWin.__faqOpen) {{
                    if (oldPopup) oldPopup.remove();
                    return;
                }}

                if (oldPopup) oldPopup.remove();

                const popup = doc.createElement("div");
                popup.id = popupId;

                const header = doc.createElement("div");
                header.className = "faq-popup-header";

                const resolvedEntry = resolveFaqEntry(sourceData);

                const title = doc.createElement("div");
                title.className = "faq-popup-title";
                title.textContent = `💡 ${{resolvedEntry.screen_name || "General Help"}} - Help`;

                const closeBtn = doc.createElement("button");
                closeBtn.className = "faq-popup-close";
                closeBtn.type = "button";
                closeBtn.textContent = "✕";
                closeBtn.addEventListener("click", function() {{
                    if (typeof hostWin.__setFaqOpen === "function") {{
                        hostWin.__setFaqOpen(false);
                    }} else {{
                        hostWin.__faqOpen = false;
                        popup.remove();
                    }}
                }});

                header.appendChild(title);
                header.appendChild(closeBtn);
                popup.appendChild(header);

                const faqItems = Array.isArray(resolvedEntry.faqs) ? resolvedEntry.faqs : [];
                let openIndex = -1;

                faqItems.forEach(function(item, idx) {{
                    const card = doc.createElement("div");
                    card.className = "faq-item";

                    const questionRow = doc.createElement("div");
                    questionRow.className = "faq-question";

                    const qText = doc.createElement("span");
                    qText.textContent = item.q || "";

                    const chevron = doc.createElement("span");
                    chevron.className = "faq-chevron";
                    chevron.textContent = "▾";

                    questionRow.appendChild(qText);
                    questionRow.appendChild(chevron);

                    const answer = doc.createElement("div");
                    answer.className = "faq-answer";
                    answer.textContent = item.a || "";

                    questionRow.addEventListener("click", function() {{
                        const wasOpen = openIndex === idx;
                        Array.from(popup.querySelectorAll(".faq-item.open")).forEach(function(openEl) {{
                            openEl.classList.remove("open");
                        }});
                        if (!wasOpen) {{
                            card.classList.add("open");
                            openIndex = idx;
                        }} else {{
                            openIndex = -1;
                        }}
                    }});

                    card.appendChild(questionRow);
                    card.appendChild(answer);
                    popup.appendChild(card);
                }});

                doc.body.appendChild(popup);
            }};

            hostWin.__faqRenderPopup();
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
