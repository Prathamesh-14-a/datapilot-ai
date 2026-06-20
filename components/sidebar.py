# src/components/sidebar.py
import base64
from pathlib import Path

import streamlit as st

from src.auth.session_manager import logout


LOGO_PATH = "assets/mini_logo.png"


# ---------- helpers ----------
def _logo_b64() -> str:
    try:
        return base64.b64encode(Path(LOGO_PATH).read_bytes()).decode()
    except Exception:
        return ""


def _icon(name: str) -> str:
    """Return inline SVG markup for a navigation icon (no emojis)."""
    icons = {
        "dashboard": '<path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>',
        "resume":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8" fill="none" stroke="currentColor" stroke-width="1.6"/><line x1="8" y1="13" x2="16" y2="13" stroke="currentColor" stroke-width="1.6"/><line x1="8" y1="17" x2="14" y2="17" stroke="currentColor" stroke-width="1.6"/>',
        "skills":    '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 3v9l6 3" fill="none" stroke="currentColor" stroke-width="1.8"/>',
        "salary":    '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "mentor":    '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" fill="none" stroke="currentColor" stroke-width="1.7"/>',
        "jobfit":    '<path d="M12 2l3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
        "market":    '<polyline points="3 17 9 11 13 15 21 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><polyline points="15 7 21 7 21 13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "profile":   '<circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M4 21a8 8 0 0 1 16 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "settings":  '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" fill="none" stroke="currentColor" stroke-width="1.5"/>',
        "logout":    '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><polyline points="16 17 21 12 16 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    }
    path = icons.get(name, icons["dashboard"])
    return f'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'


def _inject_css(logo_b64: str) -> None:
    st.markdown(
        f"""
        <style>
        /* ---- Hide Streamlit's default chrome ---- */
        [data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarNavSeparator"], [data-testid="stSidebarHeader"] {{
            display: none !important;
        }}
        [data-testid="collapsedControl"] {{ display: none !important; }}
        #MainMenu, footer {{ visibility: hidden; }}

        /* ---- Sidebar surface (glass + navy) ---- */
        section[data-testid="stSidebar"] {{
            background:
                radial-gradient(120% 60% at 0% 0%, rgba(56,189,248,0.18) 0%, transparent 55%),
                radial-gradient(120% 60% at 100% 100%, rgba(59,130,246,0.18) 0%, transparent 55%),
                linear-gradient(180deg, #06091a 0%, #0a1124 60%, #050816 100%) !important;
            border-right: 1px solid rgba(148,163,184,0.08);
            box-shadow: 0 0 60px rgba(56,189,248,0.08), inset -1px 0 0 rgba(255,255,255,0.03);
        }}
        section[data-testid="stSidebar"] > div:first-child {{ padding-top: 0.25rem; }}

        /* ---- Logo / header ---- */
        .dp-side-header {{
            position: relative;
            margin: 14px 12px 18px;
            padding: 18px 14px 16px;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
            border: 1px solid rgba(148,163,184,0.12);
            backdrop-filter: blur(14px);
            overflow: hidden;
        }}
        .dp-side-header::before {{
            content: "";
            position: absolute; inset: -40% -20% auto auto;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(56,189,248,0.35), transparent 60%);
            filter: blur(30px);
            pointer-events: none;
        }}
        .dp-side-logo {{
            display: flex; align-items: center; gap: 10px;
            position: relative; z-index: 1;
        }}
        .dp-side-logo img {{
            width: 38px; height: 38px; border-radius: 10px;
            background: rgba(255,255,255,0.04);
            padding: 4px;
            box-shadow: 0 0 24px rgba(56,189,248,0.45);
        }}
        .dp-side-brand {{
            font-family: 'Space Grotesk','Inter',sans-serif;
            font-weight: 700; font-size: 17px; letter-spacing: 0.2px;
            color: #f8fafc;
            line-height: 1;
        }}
        .dp-side-brand span {{
            background: linear-gradient(90deg,#60a5fa,#22d3ee);
            -webkit-background-clip: text; background-clip: text; color: transparent;
        }}
        .dp-side-tag {{
            margin-top: 4px;
            font-size: 11px; color: #94a3b8; letter-spacing: 0.3px;
        }}

        /* ---- Profile card ---- */
        .dp-side-profile {{
            margin: 0 12px 14px;
            padding: 12px 14px;
            display: flex; align-items: center; gap: 12px;
            border-radius: 14px;
            background: linear-gradient(180deg, rgba(56,189,248,0.06), rgba(59,130,246,0.03));
            border: 1px solid rgba(56,189,248,0.18);
            box-shadow: 0 0 20px rgba(56,189,248,0.08);
        }}
        .dp-side-avatar {{
            width: 36px; height: 36px; border-radius: 50%;
            display: grid; place-items: center;
            font-family: 'Space Grotesk',sans-serif; font-weight: 700; color: #0b1224;
            background: linear-gradient(135deg,#60a5fa,#22d3ee);
            box-shadow: 0 0 18px rgba(56,189,248,0.55);
        }}
        .dp-side-user {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
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

        /* ---- Section labels ---- */
        .dp-side-label {{
            margin: 6px 22px 6px;
            font-size: 10px; font-weight: 600; letter-spacing: 1.6px;
            color: #64748b; text-transform: uppercase;
        }}

        /* ---- Navigation buttons ---- */
        section[data-testid="stSidebar"] .stButton {{ margin: 2px 12px; }}
        section[data-testid="stSidebar"] .stButton > button {{
            position: relative;
            width: 100%;
            justify-content: flex-start;
            text-align: left;
            padding: 10px 12px 10px 14px;
            border-radius: 12px;
            border: 1px solid rgba(148,163,184,0.08);
            background: rgba(255,255,255,0.015);
            color: #cbd5e1;
            font-family: 'Inter',sans-serif;
            font-weight: 500; font-size: 13.5px;
            transition: all .22s ease;
            overflow: hidden;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            transform: translateX(2px);
            color: #f8fafc;
            background: linear-gradient(90deg, rgba(56,189,248,0.10), rgba(59,130,246,0.04));
            border-color: rgba(56,189,248,0.30);
            box-shadow: 0 6px 20px -8px rgba(56,189,248,0.35);
        }}
        /* Active nav state — applied via wrapper class below */
        .dp-nav-active .stButton > button {{
            color: #f8fafc !important;
            background: linear-gradient(90deg, rgba(56,189,248,0.18), rgba(59,130,246,0.06)) !important;
            border: 1px solid rgba(56,189,248,0.55) !important;
            box-shadow: 0 0 24px rgba(56,189,248,0.25), inset 0 0 0 1px rgba(56,189,248,0.15) !important;
        }}
        .dp-nav-active .stButton > button::before {{
            content: ""; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px;
            background: linear-gradient(180deg,#60a5fa,#22d3ee);
            border-radius: 0 4px 4px 0;
            box-shadow: 0 0 12px #22d3ee;
        }}
        .dp-nav-active .stButton > button::after {{
            content: ""; position: absolute; right: 14px; top: 50%;
            width: 6px; height: 6px; border-radius: 50%;
            background: #22d3ee; transform: translateY(-50%);
            box-shadow: 0 0 10px #22d3ee;
        }}

        /* Inline icon rendered before the button via row layout */
        .dp-nav-row {{ position: relative; }}
        .dp-nav-icon {{
            position: absolute; left: 26px; top: 50%; transform: translateY(-50%);
            color: #94a3b8; pointer-events: none; z-index: 2;
            transition: color .2s ease, transform .2s ease;
        }}
        .dp-nav-row:hover .dp-nav-icon {{ color: #22d3ee; transform: translateY(-50%) scale(1.08); }}
        .dp-nav-active .dp-nav-icon {{ color: #22d3ee; }}
        section[data-testid="stSidebar"] .dp-nav-row .stButton > button {{ padding-left: 44px; }}

        /* ---- Footer / logout ---- */
        .dp-side-divider {{
            height: 1px; margin: 14px 18px;
            background: linear-gradient(90deg, transparent, rgba(148,163,184,0.25), transparent);
        }}
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

        /* Footer brand strip */
        .dp-side-foot {{
            margin: 18px 16px 14px;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid rgba(148,163,184,0.08);
            background: rgba(255,255,255,0.02);
            font-size: 10.5px; color: #64748b; letter-spacing: 0.4px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .dp-side-foot b {{ color: #cbd5e1; font-weight: 600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _nav_item(label: str, icon_key: str, key: str, target_page: str, active: bool) -> None:
    wrapper_cls = "dp-nav-row" + (" dp-nav-active" if active else "")
    st.markdown(
        f'<div class="{wrapper_cls}"><span class="dp-nav-icon">{_icon(icon_key)}</span>',
        unsafe_allow_html=True,
    )
    if st.button(label, key=key, use_container_width=True):
        st.experimental_set_query_params()
        st.switch_page(target_page)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------- public API ----------
def show_sidebar():
    with st.sidebar:
        logo_b64 = _logo_b64()
        _inject_css(logo_b64)

        # Header
        logo_img = (
            f'<img src="data:image/png;base64,{logo_b64}" alt="DataPilot AI"/>'
            if logo_b64 else ""
        )
        st.markdown(
            f"""
            <div class="dp-side-header">
              <div class="dp-side-logo">
                {logo_img}
                <div>
                  <div class="dp-side-brand">DataPilot <span>AI</span></div>
                  <div class="dp-side-tag">Navigate Your Data Career</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Profile
        username = st.session_state.get("username", "User")
        initials = (username[:2] if username else "U").upper()
        st.markdown(
            f"""
            <div class="dp-side-profile">
              <div class="dp-side-avatar">{initials}</div>
              <div class="dp-side-user">
                <div class="dp-side-username">{username}</div>
                <div class="dp-side-status"><span class="dp-side-dot"></span> Active Session</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Determine active page from current script
        try:
            current = st.runtime.scriptrunner.get_script_run_ctx().page_script_hash  # noqa
        except Exception:
            current = ""
        active_label = st.session_state.get("_active_nav", "")

        def is_active(name: str) -> bool:
            return active_label == name

        # Workspace
        st.markdown('<div class="dp-side-label">Workspace</div>', unsafe_allow_html=True)
        _nav_item("Dashboard",         "dashboard", "nav_dashboard", "pages/3_Dashboard.py",        is_active("Dashboard"))
        _nav_item("Resume Analyzer",   "resume",    "nav_resume",    "pages/4_Resume_Analyzer.py",  is_active("Resume Analyzer"))
        _nav_item("Skill Gap Analysis","skills",    "nav_jobfit",    "pages/5_Skill_Analysis",      is_active("Skill Gap Analysis"))
        _nav_item("Salary Predictor",  "salary",    "nav_salary",    "pages/6_salary_predictor.py", is_active("Salary Predictor"))

        # Intelligence
        st.markdown('<div class="dp-side-label">Intelligence</div>', unsafe_allow_html=True)
        _nav_item("AI Career Mentor",  "mentor",    "nav_mentor",    "pages/7_AI_mentor.py",        is_active("AI Career Mentor"))
        _nav_item("Job Fit Predictor", "jobfit",    "nav_jobfit2",   "pages/8_Job_Fit_Predictor.py",is_active("Job Fit Predictor"))
        _nav_item("Market Insights",   "market",    "nav_market",    "pages/9_Market_Insights.py",  is_active("Market Insights"))

        # Account
        st.markdown('<div class="dp-side-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="dp-side-label">Account</div>', unsafe_allow_html=True)
        _nav_item("Profile", "profile", "nav_profile", "pages/10_Profile", is_active("Profile"))

        # Logout (separated, red accent)
        st.markdown('<div class="dp-logout dp-nav-row"><span class="dp-nav-icon">' + _icon("logout") + '</span>', unsafe_allow_html=True)
        if st.button("Logout", key="sidebar_logout", use_container_width=True):
            logout()
            st.switch_page("pages/1_Login.py")
        st.markdown("</div>", unsafe_allow_html=True)

        # Footer
        st.markdown(
            """
            <div class="dp-side-foot">
              <span><b>DataPilot AI</b> · v1.0</span>
              <span>© 2026</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
