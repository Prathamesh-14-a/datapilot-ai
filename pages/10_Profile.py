
from datetime import datetime
from html import escape
from textwrap import dedent
import base64
from pathlib import Path

import streamlit as st

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated, logout
from src.config.paths import ASSETS_DIR
from src.dashboard.dashboard_service import build_dashboard_snapshot
from src.database.crud import get_user

logo = ASSETS_DIR / "mini_logo.png"
b64 = base64.b64encode(logo.read_bytes()).decode()

LOGO_SRC = f'<img src="data:image/png;base64,{b64}" class="dp-logo-img">'

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Profile · DataPilot AI",
    page_icon=str(ASSETS_DIR / "mini_logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("No user profile is loaded for this session.")
    st.stop()

user = get_user(user_id)
snapshot = build_dashboard_snapshot(user_id) or {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _format_ts(value):
    if not value:
        return "Not available"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value)


def _format_lpa(value):
    if value is None or value == "":
        return "No prediction yet"
    try:
        return f"Rs. {float(value) / 100000:.1f} LPA"
    except (TypeError, ValueError):
        return str(value)


def _initials(name):
    parts = [p for p in str(name or "User").split() if p]
    if not parts:
        return "U"
    return "".join(p[0].upper() for p in parts[:2])


def _safe(value, fallback="Not added"):
    s = "" if value is None else str(value).strip()
    return escape(s) if s else escape(fallback)


def _profile_defaults():
    return {
        "full_name": st.session_state.get("username", ""),
        "headline": "Aspiring Data Professional",
        "phone": "",
        "location": "",
        "portfolio": "",
        "linkedin": "",
        "github": "",
        "target_role": "",
        "experience_level": "Fresher",
        "availability": "Open to opportunities",
        "preferred_location": "Remote / Hybrid",
        "expected_salary": "",
        "bio": "",
        "skills": "",
        "career_goals": "",
        "email_updates": True,
        "resume_reminders": True,
        "mentor_tips": True,
        "profile_visibility": "Private",
    }


def _get_profile():
    key = f"profile_details_{user_id}"
    if key not in st.session_state:
        st.session_state[key] = _profile_defaults()
    return st.session_state[key]


profile = _get_profile()
latest_analysis = snapshot.get("latest_analysis")
latest_prediction = snapshot.get("latest_prediction")
latest_resume = snapshot.get("latest_resume")
counts = snapshot.get("counts", {}) or {}


# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
DP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root{
  --dp-bg:#060B1A; --dp-bg-2:#0A1124;
  --dp-panel:rgba(14,22,48,0.55); --dp-panel-strong:rgba(18,28,60,0.78);
  --dp-border:rgba(120,170,255,0.14); --dp-border-strong:rgba(120,170,255,0.28);
  --dp-text:#E6EEFF; --dp-text-dim:#8A9CC2; --dp-text-mute:#5E6E94;
  --dp-cyan:#00C8FF; --dp-sky:#0EA5E9; --dp-royal:#2563EB;
  --dp-grad:linear-gradient(135deg,#00C8FF 0%,#0EA5E9 45%,#2563EB 100%);
  --dp-glow:0 0 40px rgba(0,200,255,0.25); --dp-radius:18px;
}
.stApp{
  background:
    radial-gradient(1200px 700px at 12% -10%, rgba(37,99,235,0.20), transparent 60%),
    radial-gradient(900px 600px at 90% 10%, rgba(0,200,255,0.14), transparent 60%),
    radial-gradient(800px 600px at 50% 110%, rgba(14,165,233,0.16), transparent 60%),
    var(--dp-bg);
  color:var(--dp-text); font-family:'Inter',system-ui,-apple-system,sans-serif;
}
.block-container{ padding-top:1.2rem; max-width:1280px; }
h1,h2,h3,h4{ color:var(--dp-text); letter-spacing:-0.02em; font-weight:700;}
p,span,label,div{ color:var(--dp-text); }
.dp-mute{ color:var(--dp-text-dim); }

header[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer{ visibility:hidden; }
[data-testid="stStatusWidget"] {
    display: none !important;
}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#070D20 0%,#060B1A 100%);
  border-right:1px solid var(--dp-border);
}

.dp-card{
  position:relative; background:var(--dp-panel);
  border:1px solid var(--dp-border); border-radius:var(--dp-radius);
  padding:22px 24px; backdrop-filter:blur(18px) saturate(140%);
  transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease;
}
.dp-card:hover{
  transform:translateY(-2px); border-color:var(--dp-border-strong);
  box-shadow:0 18px 50px -20px rgba(0,200,255,0.35);
}

/* ===========================
   DataPilot Logo Header
=========================== */

.dp-logo{
    display:flex;
    align-items:center;
    gap:18px;

    width:fit-content;

    padding:16px 22px;

    background:rgba(14,20,40,.55);
    backdrop-filter:blur(20px);
    -webkit-backdrop-filter:blur(20px);

    border:1px solid rgba(255,255,255,.08);
    border-radius:22px;

    box-shadow:
        0 15px 50px rgba(0,0,0,.35),
        inset 0 1px 0 rgba(255,255,255,.05);

    transition:.35s ease;
}

.dp-logo:hover{
    transform:translateY(-2px);
    border-color:rgba(0,200,255,.25);
    box-shadow:
        0 25px 60px rgba(0,0,0,.45),
        0 0 35px rgba(0,200,255,.12);
}

/* Logo Image */

.dp-logo img{

    width:68px;
    height:68px;

    object-fit:contain;

    border-radius:18px;

    padding:10px;

    background:linear-gradient(
        135deg,
        rgba(255,255,255,.08),
        rgba(255,255,255,.02)
    );

    border:1px solid rgba(255,255,255,.08);

    box-shadow:
        0 0 25px rgba(0,200,255,.15);

    transition:.35s;
}

.dp-logo:hover img{

    transform:rotate(-4deg) scale(1.05);

    box-shadow:
        0 0 40px rgba(0,200,255,.35);
}


/* Company Name */

.dp-logo .nm{

    font-size:34px;
    font-weight:800;
    letter-spacing:-1px;
    line-height:1;

    color:#ffffff;
}

.dp-logo .nm em{

    font-style:normal;

    background:linear-gradient(
        90deg,
        #00C8FF,
        #2563EB
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}


/* Tagline */

.dp-logo .tag{

    margin-top:6px;

    color:#93A7C4;

    font-size:14px;

    letter-spacing:.12em;

    text-transform:uppercase;
}


/* Mobile */

@media (max-width:768px){

    .dp-logo{

        padding:12px 16px;

        gap:14px;
    }

    .dp-logo img{

        width:54px;
        height:54px;
    }

    .dp-logo .nm{

        font-size:26px;
    }

    .dp-logo .tag{

        font-size:11px;
    }
.dp-logo-img{
    width:68px;
    height:68px;
    object-fit:contain;
    border-radius:16px;
    transition:.3s;
}

.dp-logo-img:hover{
    transform:scale(1.06) rotate(-4deg);
}

}
.dp-eyebrow{
  display:inline-flex; align-items:center; gap:8px;
  padding:6px 12px; border-radius:999px;
  background:rgba(0,200,255,0.08); border:1px solid rgba(0,200,255,0.25);
  color:#9FE3FF; font-size:11px; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
}
.dp-eyebrow .dot{ width:6px; height:6px; border-radius:50%; background:#00C8FF; box-shadow:0 0 10px #00C8FF;}

.dp-hero{
  display:grid; grid-template-columns:1.25fr 1fr; gap:28px;
  padding:30px 32px; border-radius:22px;
  background:
    radial-gradient(600px 300px at 0% 0%, rgba(37,99,235,0.22), transparent 60%),
    radial-gradient(500px 280px at 100% 100%, rgba(0,200,255,0.18), transparent 60%),
    linear-gradient(180deg, rgba(14,22,48,0.7), rgba(10,17,36,0.7));
  border:1px solid var(--dp-border-strong); position:relative; overflow:hidden;
}
.dp-hero-left{ display:flex; gap:22px; align-items:flex-start; }
.dp-avatar{
  width:84px; height:84px; border-radius:22px;
  display:flex; align-items:center; justify-content:center;
  background:var(--dp-grad); color:white; font-weight:800; font-size:28px;
  box-shadow:0 12px 30px -8px rgba(0,200,255,0.55);
}
.dp-name{ font-size:30px; font-weight:800; line-height:1.1; margin:4px 0 6px;}
.dp-headline{ color:var(--dp-text-dim); font-size:15px; margin-bottom:10px; }
.dp-typer-wrap{ font-family:'JetBrains Mono', monospace; color:#9FE3FF; font-size:14px; }

.dp-pill{
  display:inline-flex; align-items:center; gap:6px;
  padding:6px 12px; margin:4px 6px 0 0; border-radius:999px;
  background:rgba(120,170,255,0.06); border:1px solid var(--dp-border);
  color:var(--dp-text); font-size:12.5px; font-weight:600;
}

.dp-sec{ display:flex; align-items:center; gap:12px; margin:28px 0 14px;}
.dp-sec h3{ margin:0; font-size:18px; }
.dp-sec .bar{ width:3px; height:18px; background:var(--dp-grad); border-radius:2px;}
.dp-sec .sub{ color:var(--dp-text-mute); font-size:13px; margin-left:4px;}

.dp-score-grid{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; }
@media (max-width:1100px){ .dp-score-grid{ grid-template-columns:repeat(2,1fr);} }
.dp-score{
  padding:18px; border-radius:16px; background:var(--dp-panel);
  border:1px solid var(--dp-border); display:flex; flex-direction:column; gap:10px;
}
.dp-score:hover{ border-color:var(--dp-border-strong); box-shadow:var(--dp-glow);}
.dp-score .lbl{ font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--dp-text-mute); font-weight:700;}
.dp-score .val{
  font-size:26px; font-weight:800;
  background:var(--dp-grad); -webkit-background-clip:text; background-clip:text; color:transparent;
}
.dp-ring{ width:64px; height:64px; }

.dp-grid-2{ display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
.dp-grid-3{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
.dp-grid-4{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
@media (max-width:1000px){ .dp-grid-2,.dp-grid-3,.dp-grid-4{ grid-template-columns:1fr 1fr;} }
@media (max-width:640px){ .dp-grid-2,.dp-grid-3,.dp-grid-4{ grid-template-columns:1fr;} }

.dp-aicard{
  padding:18px; border-radius:16px; background:var(--dp-panel);
  border:1px solid var(--dp-border);
  display:flex; flex-direction:column; gap:8px; min-height:130px;
}
.dp-aicard:hover{ border-color:var(--dp-border-strong); box-shadow:var(--dp-glow);}
.dp-aicard .ico{
  width:36px; height:36px; border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  background:rgba(0,200,255,0.10); border:1px solid rgba(0,200,255,0.28); color:#00C8FF;
}
.dp-aicard .t{ font-size:13px; color:var(--dp-text-mute); text-transform:uppercase; letter-spacing:.12em; font-weight:700;}
.dp-aicard .v{ font-size:17px; font-weight:700; color:var(--dp-text); }
.dp-aicard .d{ font-size:13px; color:var(--dp-text-dim); }

.dp-insight{
  padding:16px 18px; border-radius:14px;
  background:linear-gradient(180deg, rgba(0,200,255,0.06), rgba(37,99,235,0.04));
  border:1px solid var(--dp-border-strong);
  display:flex; gap:12px; align-items:flex-start;
}
.dp-insight .ico{
  width:34px; height:34px; border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  background:var(--dp-grad); color:white;
}
.dp-insight .txt{ color:var(--dp-text); font-size:14px; line-height:1.5;}
.dp-insight .txt b{ color:#9FE3FF; font-weight:700;}

.dp-timeline{ position:relative; padding-left:28px; }
.dp-timeline::before{
  content:""; position:absolute; left:10px; top:6px; bottom:6px; width:2px;
  background:linear-gradient(180deg,#00C8FF,#2563EB 60%, transparent); border-radius:2px;
}
.dp-tl-item{ position:relative; padding:10px 0 18px 8px;}
.dp-tl-item::before{
  content:""; position:absolute; left:-23px; top:14px; width:12px; height:12px;
  border-radius:50%; background:var(--dp-grad);
}
.dp-tl-title{ font-weight:700; color:var(--dp-text); font-size:14px;}
.dp-tl-sub{ color:var(--dp-text-dim); font-size:12.5px; margin-top:2px;}
.dp-tl-time{ color:var(--dp-text-mute); font-size:11.5px; margin-top:4px; font-family:'JetBrains Mono',monospace;}

.dp-skillgroup{ margin-bottom:14px; }
.dp-skillgroup .h{ font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--dp-text-mute); font-weight:700; margin-bottom:8px;}
.dp-chip{
  display:inline-flex; align-items:center; gap:6px;
  padding:7px 12px; margin:4px 6px 4px 0; border-radius:10px;
  background:rgba(14,22,48,0.7); border:1px solid var(--dp-border);
  color:var(--dp-text); font-size:12.5px; font-weight:600;
}
.dp-chip .dt{ width:5px; height:5px; border-radius:50%; background:var(--dp-cyan);}

.dp-asset{
  padding:16px; border-radius:16px; background:var(--dp-panel);
  border:1px solid var(--dp-border);
  display:flex; flex-direction:column; gap:10px; min-height:170px;
}
.dp-asset .doc{
  height:70px; border-radius:10px;
  background:
    linear-gradient(180deg, rgba(0,200,255,0.10), rgba(37,99,235,0.06)),
    repeating-linear-gradient(180deg, transparent 0 10px, rgba(255,255,255,0.04) 10px 11px);
  border:1px solid var(--dp-border);
}
.dp-asset .nm{ font-weight:700; color:var(--dp-text); font-size:14px;}
.dp-asset .meta{ color:var(--dp-text-mute); font-size:12px; font-family:'JetBrains Mono',monospace;}
.dp-status{
  display:inline-flex; align-items:center; gap:6px;
  padding:3px 8px; border-radius:999px; font-size:11px; font-weight:700;
  background:rgba(0,200,255,0.10); border:1px solid rgba(0,200,255,0.28); color:#9FE3FF;
  width:fit-content;
}

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button{
  background:var(--dp-grad) !important; color:white !important; font-weight:700 !important;
  border:0 !important; border-radius:12px !important; padding:10px 18px !important;
  box-shadow:0 10px 24px -10px rgba(0,200,255,0.55) !important;
}
.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div, .stNumberInput input{
  background:rgba(10,17,36,0.7) !important; border:1px solid var(--dp-border) !important;
  color:var(--dp-text) !important; border-radius:12px !important;
}
label, .stTextInput label, .stTextArea label, .stSelectbox label, .stCheckbox label{
  color:var(--dp-text-dim) !important; font-weight:600 !important; font-size:13px !important;
}

.stTabs [data-baseweb="tab-list"]{
  gap:6px; background:rgba(10,17,36,0.55);
  border:1px solid var(--dp-border); border-radius:14px; padding:6px;
}
.stTabs [data-baseweb="tab"]{
  background:transparent !important; color:var(--dp-text-dim) !important;
  border-radius:10px !important; padding:10px 16px !important;
  font-weight:600 !important; border:0 !important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg, rgba(0,200,255,0.18), rgba(37,99,235,0.18)) !important;
  color:var(--dp-text) !important;
  box-shadow: inset 0 0 0 1px rgba(0,200,255,0.35);
}

hr{ border-color:var(--dp-border) !important; }

.dp-completion{
  display:flex; align-items:center; gap:18px;
  padding:18px 20px; border-radius:16px;
  background:var(--dp-panel); border:1px solid var(--dp-border);
}
.dp-completion .meta .t{ font-size:12px; color:var(--dp-text-mute); text-transform:uppercase; letter-spacing:.16em; font-weight:700;}
.dp-completion .meta .v{ font-size:24px; font-weight:800; color:var(--dp-text);}
.dp-missing{ color:var(--dp-text-dim); font-size:13px;}
.dp-missing b{ color:#9FE3FF; }

/* ==========================================================
    GLOBAL - Hide Streamlit default UI
    ========================================================== */

  #MainMenu{
      display:none !important;
  }

  footer{
      display:none !important;
  }

  [data-testid="stSidebarNav"],
  [data-testid="stSidebarNavItems"],
  [data-testid="stSidebarNavSeparator"],
  [data-testid="stSidebarHeader"],
  [data-testid="collapsedControl"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"]{
      display:none !important;
  }

</style>
"""
st.markdown(DP_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SVGs and icons
# ---------------------------------------------------------------------------

NETWORK_SVG = """
<svg viewBox="0 0 420 280" width="100%" height="240" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="ng" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00C8FF" stop-opacity=".9"/>
      <stop offset="100%" stop-color="#2563EB" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="nl" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#00C8FF" stop-opacity=".75"/>
      <stop offset="100%" stop-color="#2563EB" stop-opacity=".15"/>
    </linearGradient>
  </defs>
  <circle cx="210" cy="140" r="120" fill="url(#ng)" opacity=".55"/>
  <g stroke="url(#nl)" stroke-width="1.2" fill="none">
    <line x1="210" y1="140" x2="70" y2="60"/>
    <line x1="210" y1="140" x2="360" y2="60"/>
    <line x1="210" y1="140" x2="40" y2="200"/>
    <line x1="210" y1="140" x2="380" y2="220"/>
    <line x1="210" y1="140" x2="150" y2="40"/>
    <line x1="210" y1="140" x2="280" y2="250"/>
  </g>
  <g fill="#00C8FF">
    <circle cx="70" cy="60" r="4"/><circle cx="360" cy="60" r="4"/>
    <circle cx="40" cy="200" r="4"/><circle cx="380" cy="220" r="4"/>
    <circle cx="150" cy="40" r="3"/><circle cx="280" cy="250" r="3"/>
  </g>
  <circle cx="210" cy="140" r="10" fill="#00C8FF"/>
</svg>
"""


def _icon(name: str) -> str:
    icons = {
        "spark":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M12 2v6M12 16v6M2 12h6M16 12h6M5 5l4 4M15 15l4 4M19 5l-4 4M9 15l-5 4"/></svg>',
        "chart":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M3 3v18h18M7 14l4-4 4 4 5-6"/></svg>',
        "trend":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M3 17l6-6 4 4 8-8M14 7h7v7"/></svg>',
        "target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z"/></svg>',
        "bolt":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/></svg>',
        "user":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 5-6 8-6s6.5 2 8 6"/></svg>',
        "pin":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 22s7-7 7-13a7 7 0 10-14 0c0 6 7 13 7 13z"/><circle cx="12" cy="9" r="2.5"/></svg>',
        "doc":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>',
    }
    return icons.get(name, "")


def _ring(pct: float, label: str = "") -> str:
    try:
        pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        pct = 0.0
    r = 26
    c = 2 * 3.14159 * r
    off = c * (1 - pct / 100)
    return f"""
    <svg class="dp-ring" viewBox="0 0 64 64">
      <defs>
        <linearGradient id="rg{label}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#00C8FF"/><stop offset="100%" stop-color="#2563EB"/>
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="{r}" stroke="rgba(120,170,255,0.15)" stroke-width="6" fill="none"/>
      <circle cx="32" cy="32" r="{r}" stroke="url(#rg{label})" stroke-width="6" fill="none"
        stroke-linecap="round" stroke-dasharray="{c:.2f}" stroke-dashoffset="{off:.2f}"
        transform="rotate(-90 32 32)"/>
      <text x="32" y="36" text-anchor="middle" fill="#E6EEFF" font-size="13" font-weight="700" font-family="Inter">{int(pct)}%</text>
    </svg>
    """


# ---------------------------------------------------------------------------
# Brand header
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="dp-logo">
    {LOGO_SRC}
    <div>
        <div class="nm">Data<span>Pilot</span> AI</div>
        <div class="tag">Career Identity & Professional Insights</div>
    </div>
</div>
<br>
""", unsafe_allow_html=True)
# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
display_name = profile.get("full_name") or st.session_state.get("username") or "Explorer"
target_role_display = profile.get("target_role") or "Data Analyst"

pills_html = ""
for icon, value in [
    ("target", profile.get("target_role")),
    ("user", profile.get("experience_level")),
    ("bolt", profile.get("availability")),
    ("pin", profile.get("preferred_location")),
]:
    if value:
        pills_html += f'<span class="dp-pill">{_icon(icon)}{escape(str(value))}</span>'

st.markdown(
    f"""
    <div class="dp-hero">
      <div class="dp-hero-left">
        <div class="dp-avatar">{escape(_initials(display_name))}</div>
        <div style="flex:1;">
          <div class="dp-eyebrow"><span class="dot"></span>Career Identity</div>
          <div class="dp-name">{escape(str(display_name))}</div>
          <div class="dp-headline">{escape(str(profile.get("headline") or "Career profile"))}</div>
          <div style="margin-top:14px;">{pills_html}</div>
        </div>
      </div>
      <div style="position:relative;">{NETWORK_SVG}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Profile completion
# ---------------------------------------------------------------------------
completion_fields = ["full_name", "headline", "phone", "location", "portfolio", "linkedin",
                     "github", "target_role", "skills", "bio", "career_goals"]
filled = sum(1 for f in completion_fields if str(profile.get(f, "")).strip())
completion_pct = round(filled / len(completion_fields) * 100)
missing_labels = {"linkedin": "LinkedIn", "portfolio": "Portfolio", "career_goals": "Career Goals",
                  "github": "GitHub", "bio": "Bio", "skills": "Skills"}
missing = [missing_labels.get(f, f.replace("_", " ").title())
           for f in completion_fields if not str(profile.get(f, "")).strip()]
missing_html = ", ".join(f"<b>{escape(m)}</b>" for m in missing[:4]) or "All set"

st.markdown(
    f"""
    <div class="dp-completion" style="margin-top:18px;">
      {_ring(completion_pct, "comp")}
      <div class="meta" style="flex:1;">
        <span class="t">Profile Completion</span>
        <span class="v">{completion_pct}% complete</span>
        <span class="dp-missing">Missing: {missing_html}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Career Health Score
# ---------------------------------------------------------------------------
def _f(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


ats_val = _f(getattr(latest_analysis, "ats_score", None)) if latest_analysis else 0.0
match_val = _f(getattr(latest_analysis, "match_score", None)) if latest_analysis else 0.0
salary_raw = getattr(latest_prediction, "predicted_salary", None) if latest_prediction else None
salary_val = _f(salary_raw) / 100000 if salary_raw else 0.0
readiness = round((ats_val + match_val) / 2, 1)
market_demand = min(95, 55 + int(match_val * 0.35))
salary_potential = min(99, int(salary_val * 8)) if salary_val else 0  


# ---------------------------------------------------------------------------
# Activity Footprint
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="dp-sec"><span class="bar"></span><h3>Activity Footprint</h3>'
    '<span class="sub">Every artifact you have created on DataPilot AI</span></div>',
    unsafe_allow_html=True,
)
count_cards = [
    ("Resumes", counts.get("resumes", 0), "doc"),
    ("Analyses", counts.get("analyses", 0), "chart"),
    ("Salary Predictions", counts.get("predictions", 0), "trend"),
    ("AI Chats", counts.get("chats", 0), "spark"),
    ("Job Fit Records", counts.get("job_fit_history", 0), "target"),
]
cards_html = "".join(
    f'<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>'
    f'<span class="t">{escape(lbl)}</span><span class="v">{escape(str(val))}</span></div>'
    for lbl, val, ic in count_cards
)
st.markdown(
    f'<div class="dp-grid-4" style="grid-template-columns: repeat(5,1fr);">{cards_html}</div>',
    unsafe_allow_html=True,
)

st.write("")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
identity_tab, performance_tab, intelligence_tab, assets_tab, settings_tab = st.tabs(
    ["Career Identity", "Performance Hub", "AI Career Intelligence", "Career Assets", "Account Settings"]
)


# ============================== CAREER IDENTITY =============================
with identity_tab:
    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>AI Career Snapshot</h3>'
        '<span class="sub">Synthesized signals from your latest analyses</span></div>',
        unsafe_allow_html=True,
    )

    positioning = profile.get("target_role") or "Define your target role to sharpen positioning."
    competitiveness = (f"Top {max(5, 100 - int(match_val))}% match for "
                       f"{profile.get('target_role') or 'your target role'}"
                       if match_val else "Run a resume analysis to benchmark.")
    momentum = f"{counts.get('analyses', 0)} analyses · {counts.get('predictions', 0)} salary runs"
    growth = (f"{int(min(100, match_val + 12))}% projected with skill additions"
              if match_val else "Add skills to forecast growth.")

    snap_cards = [
        ("Current Positioning", positioning, "target"),
        ("Market Competitiveness", competitiveness, "trend"),
        ("Career Momentum", momentum, "bolt"),
        ("Growth Potential", growth, "spark"),
    ]
    snap_html = "".join(
        f'<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>'
        f'<span class="t">{escape(str(t))}</span><span class="d">{escape(str(d))}</span></div>'
        for t, d, ic in snap_cards
    )
    st.markdown(f'<div class="dp-grid-4">{snap_html}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Identity & Contact</h3></div>',
        unsafe_allow_html=True,
    )

    info_left = dedent(f"""
    <div class="dp-card">
      <div class="dp-eyebrow"><span class="dot"></span>Account</div>
      <div style="margin-top:12px; display:grid; grid-template-columns:130px 1fr; gap:10px 16px; font-size:14px;">
        <span class="dp-mute">Username</span><span>{_safe(st.session_state.get('username'), '—')}</span>
        <span class="dp-mute">Email</span><span>{_safe(st.session_state.get('email'), '—')}</span>
        <span class="dp-mute">Member since</span><span>{escape(_format_ts(getattr(user, 'created_at', None)))}</span>
        <span class="dp-mute">Visibility</span><span>{_safe(profile.get('profile_visibility'), 'Private')}</span>
      </div>
    </div>
    """).strip()
    info_right = dedent(f"""
    <div class="dp-card">
      <div class="dp-eyebrow"><span class="dot"></span>Contact</div>
      <div style="margin-top:12px; display:grid; grid-template-columns:130px 1fr; gap:10px 16px; font-size:14px;">
        <span class="dp-mute">Phone</span><span>{_safe(profile.get('phone'))}</span>
        <span class="dp-mute">Location</span><span>{_safe(profile.get('location'))}</span>
        <span class="dp-mute">Portfolio</span><span>{_safe(profile.get('portfolio'))}</span>
        <span class="dp-mute">LinkedIn</span><span>{_safe(profile.get('linkedin'))}</span>
        <span class="dp-mute">GitHub</span><span>{_safe(profile.get('github'))}</span>
      </div>
    </div>
    """).strip()
    st.markdown(f'<div class="dp-grid-2">{info_left}{info_right}</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>About</h3></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="dp-card"><p style="margin:0; color:var(--dp-text-dim); line-height:1.6;">'
        f'{escape(profile.get("bio") or "No bio added yet. Tell the AI who you are and where you are headed.")}'
        f'</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Skill Cloud</h3>'
        '<span class="sub">Grouped by capability area</span></div>',
        unsafe_allow_html=True,
    )

    raw_skills = [s.strip() for s in str(profile.get("skills", "")).split(",") if s.strip()]
    groups = {"Programming": [], "Analytics": [], "Visualization": [],
              "Machine Learning": [], "Databases": [], "Cloud": [], "Other": []}
    bucket_map = {
        "python": "Programming", "r": "Programming", "java": "Programming", "scala": "Programming",
        "sql": "Databases",
        "excel": "Analytics", "statistics": "Analytics", "pandas": "Analytics", "numpy": "Analytics",
        "tableau": "Visualization", "power bi": "Visualization", "powerbi": "Visualization",
        "looker": "Visualization", "matplotlib": "Visualization", "seaborn": "Visualization",
        "tensorflow": "Machine Learning", "pytorch": "Machine Learning",
        "sklearn": "Machine Learning", "scikit-learn": "Machine Learning",
        "ml": "Machine Learning", "nlp": "Machine Learning",
        "postgres": "Databases", "mysql": "Databases", "mongodb": "Databases",
        "snowflake": "Databases", "bigquery": "Databases",
        "aws": "Cloud", "gcp": "Cloud", "azure": "Cloud", "databricks": "Cloud",
    }
    for s in raw_skills:
        groups[bucket_map.get(s.lower(), "Other")].append(s)

    groups_html = ""
    any_skill = False
    for group, items in groups.items():
        if not items:
            continue
        any_skill = True
        chips = "".join(f'<span class="dp-chip"><span class="dt"></span>{escape(i)}</span>' for i in items)
        groups_html += f'<div class="dp-skillgroup"><div class="h">{escape(group)}</div>{chips}</div>'
    if not any_skill:
        groups_html = '<p class="dp-mute" style="margin:0;">No skills added yet. Add them in the Performance Hub.</p>'
    st.markdown(f'<div class="dp-card">{groups_html}</div>', unsafe_allow_html=True)


# ============================== PERFORMANCE HUB =============================
with performance_tab:
    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Edit Career Identity</h3>'
        '<span class="sub">Saved to this session</span></div>',
        unsafe_allow_html=True,
    )

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
            headline = st.text_input("Profile Headline", value=profile.get("headline", ""))
            phone = st.text_input("Phone", value=profile.get("phone", ""))
            location = st.text_input("Location", value=profile.get("location", ""))
            portfolio = st.text_input("Portfolio Website", value=profile.get("portfolio", ""))
        with col2:
            linkedin = st.text_input("LinkedIn URL", value=profile.get("linkedin", ""))
            github = st.text_input("GitHub URL", value=profile.get("github", ""))
            target_role = st.text_input("Target Role", value=profile.get("target_role", ""))
            exp_opts = ["Fresher", "Entry Level", "Mid Level", "Senior", "Lead / Manager"]
            cur_exp = profile.get("experience_level", "Fresher")
            experience_level = st.selectbox(
                "Experience Level", exp_opts,
                index=exp_opts.index(cur_exp) if cur_exp in exp_opts else 0,
            )
            avail_opts = ["Open to opportunities", "Actively applying", "Interviewing", "Not looking"]
            cur_avail = profile.get("availability", "Open to opportunities")
            availability = st.selectbox(
                "Availability", avail_opts,
                index=avail_opts.index(cur_avail) if cur_avail in avail_opts else 0,
            )

        preferred_location = st.text_input("Preferred Job Location", value=profile.get("preferred_location", ""))
        expected_salary = st.text_input("Expected Salary", value=str(profile.get("expected_salary", "")))
        skills = st.text_area("Skills", value=profile.get("skills", ""),
                              help="Enter skills separated by commas.")
        bio = st.text_area("Bio", value=profile.get("bio", ""), height=120)
        career_goals = st.text_area("Career Goals", value=profile.get("career_goals", ""), height=120)

        saved = st.form_submit_button("Save Profile", use_container_width=True)

    if saved:
        profile.update({
            "full_name": full_name, "headline": headline, "phone": phone, "location": location,
            "portfolio": portfolio, "linkedin": linkedin, "github": github, "target_role": target_role,
            "experience_level": experience_level, "availability": availability,
            "preferred_location": preferred_location, "expected_salary": expected_salary,
            "skills": skills, "bio": bio, "career_goals": career_goals,
        })
        st.success("Profile updated successfully.")

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Latest Performance</h3></div>',
        unsafe_allow_html=True,
    )
    perf_cards = [
        ("ATS Score",
         f"{latest_analysis.ats_score:.1f}%" if latest_analysis and getattr(latest_analysis, "ats_score", None) is not None else "No result yet",
         "shield"),
        ("Skill Match",
         f"{latest_analysis.match_score:.1f}%" if latest_analysis and getattr(latest_analysis, "match_score", None) is not None else "No result yet",
         "target"),
        ("Salary Estimate",
         _format_lpa(salary_raw) if latest_prediction else "No result yet",
         "trend"),
    ]
    perf_html = "".join(
        f'<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>'
        f'<span class="t">{escape(t)}</span><span class="v">{escape(v)}</span></div>'
        for t, v, ic in perf_cards
    )
    st.markdown(f'<div class="dp-grid-3">{perf_html}</div>', unsafe_allow_html=True)


# ============================ AI CAREER INTELLIGENCE ========================
with intelligence_tab:
    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>AI Recommendations</h3>'
        '<span class="sub">Personalized signals derived from your activity</span></div>',
        unsafe_allow_html=True,
    )

    target = profile.get("target_role") or "Data Analyst"
    insights = []
    if match_val < 90:
        insights.append(
            f"Adding <b>Tableau</b> and <b>Power BI</b> could increase your "
            f"{escape(target)} fit by an estimated <b>{max(6, int(95 - match_val))}%</b>."
        )
    if ats_val:
        pct_better = min(95, int(ats_val * 0.85))
        insights.append(
            f"Your ATS score is stronger than <b>{pct_better}%</b> of DataPilot users targeting similar roles."
        )
    insights.append(
        "The <b>SQL + Power BI + Python</b> combination is highly demanded in your target market right now."
    )
    if not profile.get("linkedin"):
        insights.append("Adding your <b>LinkedIn</b> increases recruiter discoverability by <b>3.4x</b>.")
    if latest_prediction:
        insights.append(
            f"Based on your current profile, your salary trajectory points toward "
            f"<b>{escape(_format_lpa(salary_raw))}</b>."
        )

    insights_html = "".join(
        f'<div class="dp-insight"><div class="ico">{_icon("spark")}</div>'
        f'<div class="txt">{txt}</div></div>'
        for txt in insights
    )
    st.markdown(
        f'<div style="display:flex; flex-direction:column; gap:12px;">{insights_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Activity Timeline</h3>'
        '<span class="sub">Your career journey on DataPilot AI</span></div>',
        unsafe_allow_html=True,
    )

    activity_items = snapshot.get("activity_items", []) or []
    if not activity_items:
        st.markdown(
            '<div class="dp-card"><p class="dp-mute" style="margin:0;">'
            'No activity yet. Analyze a resume, predict salary, or start an AI Mentor '
            'chat to build your timeline.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        tl_html = ""
        for item in activity_items[:10]:
            title = item.get("title") or item.get("kind") or "Activity"
            detail = item.get("detail") or ""
            kind = item.get("kind") or ""
            ts = _format_ts(item.get("timestamp"))
            tl_html += (
                '<div class="dp-tl-item">'
                f'<div class="dp-tl-title">{escape(str(title))}</div>'
                f'<div class="dp-tl-sub">{escape(str(detail))}</div>'
                f'<div class="dp-tl-time">{escape(ts)} · {escape(str(kind))}</div>'
                '</div>'
            )
        st.markdown(
            f'<div class="dp-card"><div class="dp-timeline">{tl_html}</div></div>',
            unsafe_allow_html=True,
        )


# ================================ CAREER ASSETS =============================
with assets_tab:
    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Career Assets</h3>'
        '<span class="sub">Resumes, reports and AI artifacts</span></div>',
        unsafe_allow_html=True,
    )

    resumes = sorted(
        snapshot.get("resumes", []) or [],
        key=lambda r: getattr(r, "uploaded_at", datetime.min) or datetime.min,
        reverse=True,
    )

    if not resumes:
        st.markdown(
            '<div class="dp-card"><p class="dp-mute" style="margin:0;">No resumes uploaded yet.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        cards = ""
        for r in resumes[:8]:
            name = getattr(r, "resume_name", None) or "Untitled resume"
            uploaded = _format_ts(getattr(r, "uploaded_at", None))
            cards += (
                '<div class="dp-asset">'
                '<div class="doc"></div>'
                f'<div class="nm">{escape(str(name))}</div>'
                f'<div class="meta">{escape(uploaded)}</div>'
                '<span class="dp-status">Indexed</span>'
                '</div>'
            )
        st.markdown(f'<div class="dp-grid-4">{cards}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Artifact Library</h3></div>',
        unsafe_allow_html=True,
    )
    lib = [
        ("Resumes", counts.get("resumes", 0), "doc"),
        ("Salary Reports", counts.get("predictions", 0), "trend"),
        ("Roadmaps", counts.get("chats", 0), "spark"),
        ("Job Fit Reports", counts.get("job_fit_history", 0), "target"),
    ]
    now_ts = _format_ts(datetime.now())
    lib_html = "".join(
        f'<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>'
        f'<span class="t">{escape(t)}</span><span class="v">{escape(str(v))} items</span>'
        f'<span class="d">Updated {escape(now_ts)}</span></div>'
        for t, v, ic in lib
    )
    st.markdown(f'<div class="dp-grid-4">{lib_html}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Quick Actions</h3></div>',
        unsafe_allow_html=True,
    )
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Analyze Resume", use_container_width=True):
            st.switch_page("pages/4_Resume_Analyzer.py")
    with a2:
        if st.button("Predict Salary", use_container_width=True):
            st.switch_page("pages/6_salary_predictor.py")
    with a3:
        if st.button("Open AI Mentor", use_container_width=True):
            st.switch_page("pages/7_AI_mentor.py")

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Career Goals</h3></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="dp-card"><p style="margin:0; color:var(--dp-text-dim); line-height:1.6;">'
        f'{escape(profile.get("career_goals") or "No career goals defined yet. Add them in the Performance Hub.")}'
        f'</p></div>',
        unsafe_allow_html=True,
    )


# ============================== ACCOUNT SETTINGS ============================
with settings_tab:
    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Preferences</h3>'
        '<span class="sub">Notifications and AI personalization</span></div>',
        unsafe_allow_html=True,
    )

    # NOTE: We do NOT wrap native Streamlit widgets inside an HTML <div> that
    # we open in one st.markdown and close in another. Streamlit auto-closes
    # its own containers, which made the trailing </div> render as raw text.
    # Section headers below act as the visual grouping instead.

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="dp-eyebrow" style="margin-bottom:10px;">'
            '<span class="dot"></span>Notifications</div>',
            unsafe_allow_html=True,
        )
        email_updates = st.checkbox("Email updates",
                                    value=bool(profile.get("email_updates", True)))
        resume_reminders = st.checkbox("Resume improvement reminders",
                                       value=bool(profile.get("resume_reminders", True)))
        mentor_tips = st.checkbox("AI Mentor tips",
                                  value=bool(profile.get("mentor_tips", True)))
    with c2:
        st.markdown(
            '<div class="dp-eyebrow" style="margin-bottom:10px;">'
            '<span class="dot"></span>Privacy</div>',
            unsafe_allow_html=True,
        )
        vis_opts = ["Private", "Visible to mentors", "Visible to recruiters"]
        cur_vis = profile.get("profile_visibility", "Private")
        profile_visibility = st.selectbox(
            "Profile Visibility", vis_opts,
            index=vis_opts.index(cur_vis) if cur_vis in vis_opts else 0,
        )

    if st.button("Save Preferences", use_container_width=True):
        profile.update({
            "email_updates": email_updates,
            "resume_reminders": resume_reminders,
            "mentor_tips": mentor_tips,
            "profile_visibility": profile_visibility,
        })
        st.success("Preferences saved.")

    st.markdown(
        '<div class="dp-sec"><span class="bar"></span><h3>Account Security</h3></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="dp-card">
          <div class="dp-eyebrow"><span class="dot"></span>Signed In</div>
          <p style="margin:12px 0 6px; font-size:14px;">Signed in as
            <b>{_safe(st.session_state.get('email'), 'Not available')}</b></p>
          <p class="dp-mute" style="margin:0; font-size:13px;">
            Password changes are handled from the authentication flow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Logout", use_container_width=True):
        logout()
        st.switch_page("pages/1_Login.py")
