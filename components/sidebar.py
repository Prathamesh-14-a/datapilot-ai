# src/components/sidebar.py
"""
DataPilot AI — Enterprise Collapsible Sidebar
----------------------------------------------
Modern SaaS navigation inspired by Linear, Notion, Vercel & Stripe.
Features:
  • Collapsible (260px ↔ 70px) with smooth CSS transitions
  • Glassmorphism + dark futuristic theme, blue-cyan AI branding
  • Active page glow, hover micro-interactions, tooltips when collapsed
  • Profile card with online status, branded footer, logout
  • Persistent state via st.session_state, navigation via st.switch_page
"""

import base64
from pathlib import Path
import streamlit as st

from src.auth.session_manager import logout


LOGO_PATH = "assets/mini_logo.png"

# ---------------------------------------------------------------------------
# Navigation registry — single source of truth
# ---------------------------------------------------------------------------
NAV_SECTIONS = [
    ("Workspace", [
        ("Dashboard",          "dashboard", "pages/3_Dashboard.py"),
        ("Resume Analyzer",    "resume",    "pages/4_Resume_Analyzer.py"),
        ("Skill Gap Analysis", "skills",    "pages/5_Skill_Analysis.py"),
        ("Salary Predictor",   "salary",    "pages/6_salary_predictor.py"),
    ]),
    ("Intelligence", [
        ("AI Career Mentor",   "mentor",    "pages/7_AI_mentor.py"),
        ("Job Fit Predictor",  "jobfit",    "pages/8_Job_Fit_Predictor.py"),
        ("Market Insights",    "market",    "pages/9_Market_Insights.py"),
    ]),
    ("Account", [
        ("Profile",            "profile",   "pages/10_Profile.py"),
    ]),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _logo_b64() -> str:
    try:
        return base64.b64encode(Path(LOGO_PATH).read_bytes()).decode()
    except Exception:
        return ""


def _icon(name: str) -> str:
    """Inline SVG markup for navigation icons (no emojis)."""
    icons = {
        "dashboard": '<path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>',
        "resume":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8" fill="none" stroke="currentColor" stroke-width="1.6"/><line x1="8" y1="13" x2="16" y2="13" stroke="currentColor" stroke-width="1.6"/><line x1="8" y1="17" x2="14" y2="17" stroke="currentColor" stroke-width="1.6"/>',
        "skills":    '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 3v9l6 3" fill="none" stroke="currentColor" stroke-width="1.8"/>',
        "salary":    '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "mentor":    '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" fill="none" stroke="currentColor" stroke-width="1.7"/>',
        "jobfit":    '<path d="M12 2l3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
        "market":    '<polyline points="3 17 9 11 13 15 21 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><polyline points="15 7 21 7 21 13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "profile":   '<circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M4 21a8 8 0 0 1 16 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "logout":    '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><polyline points="16 17 21 12 16 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "chevron":   '<polyline points="15 18 9 12 15 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    }
    path = icons.get(name, icons["dashboard"])
    return (
        f'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{path}</svg>'
    )


# ---------------------------------------------------------------------------
# CSS — collapsible glassmorphic theme
# ---------------------------------------------------------------------------
def _inject_css(collapsed: bool) -> None:
    width = "70px" if collapsed else "260px"
    label_display = "none" if collapsed else "block"
    header_text_display = "none" if collapsed else "flex"
    profile_text_display = "none" if collapsed else "flex"
    section_label_display = "none" if collapsed else "block"
    footer_display = "none" if collapsed else "flex"
    button_text_opacity = "0" if collapsed else "1"
    button_padding_left = "0" if collapsed else "44px"
    button_justify = "center" if collapsed else "flex-start"

    st.markdown(
        f"""
        <style>
        /* Hide Streamlit chrome */
        [data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarNavSeparator"], [data-testid="stSidebarHeader"],
        [data-testid="collapsedControl"] {{ display: none !important; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* Sidebar shell — animated width */
        section[data-testid="stSidebar"] {{
            width: {width} !important;
            min-width: {width} !important;
            max-width: {width} !important;
            transition: width .35s cubic-bezier(.4,0,.2,1),
                        min-width .35s cubic-bezier(.4,0,.2,1),
                        max-width .35s cubic-bezier(.4,0,.2,1) !important;
            background:
                radial-gradient(120% 60% at 0% 0%, rgba(56,189,248,0.18) 0%, transparent 55%),
                radial-gradient(120% 60% at 100% 100%, rgba(59,130,246,0.18) 0%, transparent 55%),
                linear-gradient(180deg, #06091a 0%, #0a1124 60%, #050816 100%) !important;
            border-right: 1px solid rgba(148,163,184,0.08);
            box-shadow: 0 0 60px rgba(56,189,248,0.08),
                        inset -1px 0 0 rgba(255,255,255,0.03);
            overflow-x: hidden !important;
        }}
        section[data-testid="stSidebar"] > div:first-child {{ padding-top: .25rem; }}

        /* Toggle button (top) */
        .dp-toggle-wrap {{
            display: flex;
            justify-content: {"center" if collapsed else "flex-end"};
            padding: 10px 14px 4px;
        }}
        .dp-toggle-wrap .stButton > button {{
            width: 32px !important; height: 32px !important;
            min-height: 32px !important; padding: 0 !important;
            border-radius: 8px !important;
            background: rgba(255,255,255,0.05) !important;
            border:  1px solid rgba(255,255,255,0.12) !important;
            color: white !important;
            display: flex; align-items: center; justify-content: center;
            transition: all .25s ease !important;
        }}
        .dp-toggle-wrap .stButton > button:hover {{
            background: white !important;
            color: black !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            border-color: rgba(56,189,248,0.4) !important;
            transform: scale(1.05);
        }}
        .dp-toggle-icon {{
            display: inline-block;
            transition: transform .35s ease;
            transform: rotate({"180deg" if collapsed else "0deg"});
        }}

        /* Header */
        .dp-side-header {{
            position: relative;
            margin: 8px 12px 16px;
            padding: {"14px 8px" if collapsed else "16px 14px"};
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
            border: 1px solid rgba(148,163,184,0.12);
            backdrop-filter: blur(14px);
            overflow: hidden;
            transition: padding .3s ease;
        }}
        .dp-side-header::before {{
            content: "";
            position: absolute; inset: -40% -20% auto auto;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(56,189,248,0.35), transparent 60%);
            filter: blur(30px); pointer-events: none;
        }}
        .dp-side-logo {{
            display: flex; align-items: center; gap: 10px;
            justify-content: {"center" if collapsed else "flex-start"};
            position: relative; z-index: 1;
        }}
        .dp-side-logo img {{
            width: 38px; height: 38px; border-radius: 10px;
            background: rgba(255,255,255,0.04); padding: 4px;
            box-shadow: 0 0 24px rgba(56,189,248,0.45);
            flex-shrink: 0;
        }}
        .dp-side-brand-wrap {{
            display: {header_text_display};
            flex-direction: column;
            opacity: {button_text_opacity};
            transition: opacity .25s ease;
        }}
        .dp-side-brand {{
            font-family: 'Space Grotesk','Inter',sans-serif;
            font-weight: 700; font-size: 17px; color: #f8fafc; line-height: 1;
            white-space: nowrap;
        }}
        .dp-side-brand span {{
            background: linear-gradient(90deg,#60a5fa,#22d3ee);
            -webkit-background-clip: text; background-clip: text; color: transparent;
        }}
        .dp-side-tag {{
            margin-top: 4px; font-size: 11px; color: #94a3b8;
            letter-spacing: .3px; white-space: nowrap;
        }}

        /* Profile card */
        .dp-side-profile {{
            margin: 0 12px 14px;
            padding: {"10px" if collapsed else "12px 14px"};
            display: flex; align-items: center;
            justify-content: {"center" if collapsed else "flex-start"};
            gap: 12px;
            border-radius: 14px;
            background: linear-gradient(180deg, rgba(56,189,248,0.06), rgba(59,130,246,0.03));
            border: 1px solid rgba(56,189,248,0.18);
            box-shadow: 0 0 20px rgba(56,189,248,0.08);
            transition: all .3s ease;
        }}
        .dp-side-avatar {{
            position: relative;
            width: 36px; height: 36px; border-radius: 50%;
            display: grid; place-items: center;
            font-family: 'Space Grotesk',sans-serif; font-weight: 700;
            color: #0b1224; font-size: 13px;
            background: linear-gradient(135deg,#60a5fa,#22d3ee);
            box-shadow: 0 0 18px rgba(56,189,248,0.55);
            flex-shrink: 0;
        }}
        .dp-side-avatar::after {{
            content: "";
            position: absolute; bottom: -1px; right: -1px;
            width: 10px; height: 10px; border-radius: 50%;
            background: #22d3ee;
            border: 2px solid #0a1124;
            box-shadow: 0 0 8px #22d3ee;
            animation: dp-pulse 2s ease-in-out infinite;
        }}
        .dp-side-user {{
            display: {profile_text_display};
            flex-direction: column; gap: 2px; min-width: 0;
            opacity: {button_text_opacity};
            transition: opacity .25s ease;
        }}
        .dp-side-username {{
            color: #e2e8f0; font-size: 13px; font-weight: 600;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            max-width: 150px;
        }}
        .dp-side-status {{
            display: inline-flex; align-items: center; gap: 6px;
            font-size: 11px; color: #94a3b8;
        }}
        .dp-side-dot {{
            width: 7px; height: 7px; border-radius: 50%;
            background: #22d3ee;
            box-shadow: 0 0 8px #22d3ee, 0 0 16px rgba(34,211,238,0.6);
            animation: dp-pulse 2s ease-in-out infinite;
        }}
        @keyframes dp-pulse {{ 0%,100% {{opacity:1}} 50% {{opacity:.45}} }}

        /* Section labels */
        .dp-side-label {{
            display: {section_label_display};
            margin: 10px 22px 6px;
            font-size: 10px; font-weight: 600; letter-spacing: 1.6px;
            color: #64748b; text-transform: uppercase;
        }}
        .dp-side-label-spacer {{
            display: {"block" if collapsed else "none"};
            height: 14px;
            margin: 6px 22px;
            border-top: 1px solid rgba(148,163,184,0.08);
        }}

        /* Navigation buttons */
        section[data-testid="stSidebar"] .stButton {{ margin: 2px 12px; }}
        section[data-testid="stSidebar"] .stButton > button {{
            position: relative;
            width: 100%;
            justify-content: {button_justify};
            text-align: {"center" if collapsed else "left"};
            padding: 10px 12px 10px {button_padding_left};
            border-radius: 12px;
            border: 1px solid rgba(148,163,184,0.08);
            background: rgba(255,255,255,0.015);
            color: #cbd5e1;
            font-family: 'Inter',sans-serif;
            font-weight: 500; font-size: 13.5px;
            transition: all .25s ease, padding .3s ease;
            overflow: hidden; white-space: nowrap;
            min-height: 42px;
        }}
        section[data-testid="stSidebar"] .stButton > button > div {{
            opacity: {button_text_opacity};
            transition: opacity .2s ease;
            {"display: none;" if collapsed else ""}
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            transform: translateX({"0" if collapsed else "2px"});
            color: #f8fafc;
            background: linear-gradient(90deg, rgba(56,189,248,0.10), rgba(59,130,246,0.04));
            border-color: rgba(56,189,248,0.30);
            box-shadow: 0 6px 20px -8px rgba(56,189,248,0.35);
        }}

        /* Active nav state */
        .dp-nav-active .stButton > button {{
            color: #f8fafc !important;
            background: linear-gradient(90deg, rgba(56,189,248,0.18), rgba(59,130,246,0.06)) !important;
            border: 1px solid rgba(56,189,248,0.55) !important;
            box-shadow: 0 0 24px rgba(56,189,248,0.25),
                        inset 0 0 0 1px rgba(56,189,248,0.15) !important;
        }}
        .dp-nav-active .stButton > button::before {{
            content: ""; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px;
            background: linear-gradient(180deg,#60a5fa,#22d3ee);
            border-radius: 0 4px 4px 0;
            box-shadow: 0 0 12px #22d3ee;
        }}

        /* Inline icon */
        .dp-nav-row {{ position: relative; }}
        .dp-nav-icon {{
            position: absolute;
            left: {"50%" if collapsed else "26px"};
            top: 50%;
            transform: translate({"-50%, -50%" if collapsed else "0, -50%"});
            color: #94a3b8; pointer-events: none; z-index: 2;
            transition: color .2s ease, transform .2s ease;
        }}
        .dp-nav-row:hover .dp-nav-icon {{
            color: #22d3ee;
            transform: translate({"-50%, -50%" if collapsed else "0, -50%"}) scale(1.1);
        }}
        .dp-nav-active .dp-nav-icon {{ color: #22d3ee; }}

        /* Tooltip when collapsed */
        .dp-nav-row[data-tip]::after {{
            content: attr(data-tip);
            position: absolute;
            left: calc(100% + 14px); top: 50%;
            transform: translateY(-50%) translateX(-6px);
            background: #0f172a;
            color: #e2e8f0;
            font-size: 12px; font-weight: 500;
            padding: 6px 10px; border-radius: 8px;
            border: 1px solid rgba(56,189,248,0.35);
            box-shadow: 0 8px 24px rgba(0,0,0,0.5),
                        0 0 16px rgba(56,189,248,0.2);
            white-space: nowrap;
            opacity: 0; pointer-events: none;
            transition: opacity .2s ease, transform .2s ease;
            z-index: 9999;
            display: {"block" if collapsed else "none"};
        }}
        .dp-nav-row[data-tip]:hover::after {{
            opacity: 1;
            transform: translateY(-50%) translateX(0);
        }}

        /* Divider */
        .dp-side-divider {{
            height: 1px; margin: 14px 18px;
            background: linear-gradient(90deg, transparent, rgba(148,163,184,0.25), transparent);
        }}

        /* Logout accent */
        .dp-logout .stButton > button {{
            color: #fca5a5 !important;
            background: linear-gradient(90deg, rgba(239,68,68,0.08), rgba(239,68,68,0.02)) !important;
            border: 1px solid rgba(239,68,68,0.28) !important;
        }}
        .dp-logout .stButton > button:hover {{
            color: #fee2e2 !important;
            background: linear-gradient(90deg, rgba(239,68,68,0.20), rgba(239,68,68,0.05)) !important;
            border-color: rgba(239,68,68,0.55) !important;
            box-shadow: 0 6px 20px -8px rgba(239,68,68,0.55) !important;
        }}
        .dp-logout .dp-nav-icon {{ color: #fca5a5; }}

        /* Footer */
        .dp-side-foot {{
            display: {footer_display};
            margin: 18px 16px 14px;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid rgba(148,163,184,0.08);
            background: rgba(255,255,255,0.02);
            font-size: 10.5px; color: #64748b; letter-spacing: .4px;
            align-items: center; justify-content: space-between;
        }}
        .dp-side-foot b {{ color: #cbd5e1; font-weight: 600; }}

        /* Mobile */
        @media (max-width: 768px) {{
            section[data-testid="stSidebar"] {{
                width: {width} !important;
                min-width: {width} !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
def _render_toggle(collapsed: bool) -> None:
    """Top-right toggle button to collapse/expand the sidebar."""
    st.markdown('<div class="dp-toggle-wrap">', unsafe_allow_html=True)
    if st.button(
        "›" if collapsed else "‹",
        key="dp_sidebar_toggle",
        help="Expand sidebar" if collapsed else "Collapse sidebar",
    ):
        st.session_state["dp_sidebar_collapsed"] = not collapsed
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_header(logo_b64: str) -> None:
    logo_img = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="DataPilot AI"/>'
        if logo_b64
        else '<div style="width:38px;height:38px;border-radius:10px;'
             'background:linear-gradient(135deg,#60a5fa,#22d3ee);'
             'box-shadow:0 0 24px rgba(56,189,248,0.45);flex-shrink:0;"></div>'
    )
    st.markdown(
        f"""
        <div class="dp-side-header">
          <div class="dp-side-logo">
            {logo_img}
            <div class="dp-side-brand-wrap">
              <div class="dp-side-brand">Data<span>Pilot AI</span></div>
              <div class="dp-side-tag">Navigate Your Data Career</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_profile() -> None:
    username = st.session_state.get("username", "User")
    initials = (username[:2] if username else "U").upper()
    st.markdown(
        f"""
        <div class="dp-side-profile">
          <div class="dp-side-avatar">{initials}</div>
          <div class="dp-side-user">
            <div class="dp-side-username">{username}</div>
            <div class="dp-side-status">
              <span class="dp-side-dot"></span> Active Session
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _nav_item(label: str, icon_key: str, key: str, target_page: str,
              active: bool, collapsed: bool) -> None:
    """Render a single nav button with icon, active state, and tooltip."""
    wrapper_cls = "dp-nav-row" + (" dp-nav-active" if active else "")
    tip_attr = f'data-tip="{label}"' if collapsed else ""

    st.markdown(
        f'<div class="{wrapper_cls}" {tip_attr}>'
        f'<span class="dp-nav-icon">{_icon(icon_key)}</span>',
        unsafe_allow_html=True,
    )
    # Use a non-breaking space when collapsed so the button still renders
    btn_label = label if not collapsed else "\u00A0"
    if st.button(btn_label, key=key, use_container_width=True):
        st.session_state["_active_nav"] = label
        st.switch_page(target_page)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_section(title: str, items: list, collapsed: bool,
                    active_label: str) -> None:
    if collapsed:
        st.markdown('<div class="dp-side-label-spacer"></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="dp-side-label">{title}</div>',
                    unsafe_allow_html=True)
    for label, icon_key, page in items:
        key = f"nav_{label.lower().replace(' ', '_')}"
        _nav_item(label, icon_key, key, page,
                  active=(active_label == label), collapsed=collapsed)


def _render_logout(collapsed: bool) -> None:
    st.markdown('<div class="dp-side-divider"></div>', unsafe_allow_html=True)
    tip_attr = 'data-tip="Logout"' if collapsed else ""
    st.markdown(
        f'<div class="dp-nav-row dp-logout" {tip_attr}>'
        f'<span class="dp-nav-icon">{_icon("logout")}</span>',
        unsafe_allow_html=True,
    )
    btn_label = "Logout" if not collapsed else "\u00A0"
    if st.button(btn_label, key="sidebar_logout", use_container_width=True):
        logout()
        st.switch_page("pages/1_Login.py")
    st.markdown("</div>", unsafe_allow_html=True)


def _render_footer() -> None:
    st.markdown(
        """
        <div class="dp-side-foot">
          <span><b>DataPilot AI</b> · v1.0</span>
          <span>© 2026</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def show_sidebar() -> None:
    """Render the full collapsible DataPilot AI sidebar."""
    # Persist collapsed state across pages
    if "dp_sidebar_collapsed" not in st.session_state:
        st.session_state["dp_sidebar_collapsed"] = False
    collapsed = st.session_state["dp_sidebar_collapsed"]

    with st.sidebar:
        _inject_css(collapsed)
        _render_toggle(collapsed)
        _render_header(_logo_b64())
        _render_profile()

        active_label = st.session_state.get("_active_nav", "Dashboard")
        for section_title, items in NAV_SECTIONS:
            _render_section(section_title, items, collapsed, active_label)

        _render_logout(collapsed)
        _render_footer()
