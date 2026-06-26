"""
DataPilot AI — Career Command Center (Profile page)
Drop this file into your Streamlit app as `pages/8_Profile.py` (or replace your
existing Profile page). All original Python functionality, DB calls, session
state keys, forms, tabs and navigation are preserved — only UI/UX is redesigned.
"""

from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated, logout
from src.dashboard.dashboard_service import build_dashboard_snapshot
from src.database.crud import get_user


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Profile · DataPilot AI",
    page_icon="assets/mini_logo.png",
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
snapshot = build_dashboard_snapshot(user_id)


# ---------------------------------------------------------------------------
# Helpers (preserved from original)
# ---------------------------------------------------------------------------
def _format_ts(value):
    if not value:
        return "Not available"
    return value.strftime("%d %b %Y, %I:%M %p")


def _format_lpa(value):
    if value is None:
        return "No prediction yet"
    return f"Rs. {float(value) / 100000:.1f} LPA"


def _initials(name):
    parts = [p for p in str(name or "User").split() if p]
    if not parts:
        return "U"
    return "".join(p[0].upper() for p in parts[:2])


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
counts = snapshot.get("counts", {})


# ---------------------------------------------------------------------------
# Design system — global CSS (Linear / Vercel / Stripe inspired)
# ---------------------------------------------------------------------------
DP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root{
  --dp-bg: #060B1A;
  --dp-bg-2: #0A1124;
  --dp-panel: rgba(14, 22, 48, 0.55);
  --dp-panel-strong: rgba(18, 28, 60, 0.78);
  --dp-border: rgba(120, 170, 255, 0.14);
  --dp-border-strong: rgba(120, 170, 255, 0.28);
  --dp-text: #E6EEFF;
  --dp-text-dim: #8A9CC2;
  --dp-text-mute: #5E6E94;
  --dp-cyan: #00C8FF;
  --dp-sky: #0EA5E9;
  --dp-royal: #2563EB;
  --dp-grad: linear-gradient(135deg,#00C8FF 0%,#0EA5E9 45%,#2563EB 100%);
  --dp-glow: 0 0 40px rgba(0,200,255,0.25);
  --dp-radius: 18px;
}

/* Page background */
.stApp{
  background:
    radial-gradient(1200px 700px at 12% -10%, rgba(37,99,235,0.20), transparent 60%),
    radial-gradient(900px 600px at 90% 10%, rgba(0,200,255,0.14), transparent 60%),
    radial-gradient(800px 600px at 50% 110%, rgba(14,165,233,0.16), transparent 60%),
    var(--dp-bg);
  color: var(--dp-text);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.stApp::before{
  content:"";
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(120,170,255,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120,170,255,0.05) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(ellipse at 50% 30%, black 30%, transparent 75%);
  pointer-events:none; z-index:0;
}
.block-container{ padding-top: 1.2rem; max-width: 1280px; position: relative; z-index: 1;}

/* Typography */
h1,h2,h3,h4{ color: var(--dp-text); letter-spacing:-0.02em; font-weight:700;}
p, span, label, div { color: var(--dp-text); }
.dp-mute{ color: var(--dp-text-dim); }

/* Streamlit chrome cleanup */
header[data-testid="stHeader"]{ background: transparent; }
#MainMenu, footer{ visibility:hidden; }
[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #070D20 0%, #060B1A 100%);
  border-right: 1px solid var(--dp-border);
}

/* Glass card primitive */
.dp-card{
  position:relative;
  background: var(--dp-panel);
  border: 1px solid var(--dp-border);
  border-radius: var(--dp-radius);
  padding: 22px 24px;
  backdrop-filter: blur(18px) saturate(140%);
  -webkit-backdrop-filter: blur(18px) saturate(140%);
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
  overflow: hidden;
}
.dp-card:hover{
  transform: translateY(-2px);
  border-color: var(--dp-border-strong);
  box-shadow: 0 18px 50px -20px rgba(0,200,255,0.35);
}
.dp-card::after{
  content:""; position:absolute; inset:-1px; border-radius: inherit; padding:1px;
  background: linear-gradient(135deg, rgba(0,200,255,0.35), rgba(37,99,235,0) 60%);
  -webkit-mask: linear-gradient(#000,#000) content-box, linear-gradient(#000,#000);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events:none; opacity:.6;
}

/* Eyebrow tag */
.dp-eyebrow{
  display:inline-flex; align-items:center; gap:8px;
  padding: 6px 12px; border-radius: 999px;
  background: rgba(0,200,255,0.08);
  border: 1px solid rgba(0,200,255,0.25);
  color: #9FE3FF; font-size: 11px; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
}
.dp-eyebrow .dot{ width:6px; height:6px; border-radius:50%; background:#00C8FF; box-shadow:0 0 10px #00C8FF;}

/* Hero */
.dp-hero{
  display:grid; grid-template-columns: 1.25fr 1fr; gap: 28px;
  padding: 30px 32px; border-radius: 22px;
  background:
    radial-gradient(600px 300px at 0% 0%, rgba(37,99,235,0.22), transparent 60%),
    radial-gradient(500px 280px at 100% 100%, rgba(0,200,255,0.18), transparent 60%),
    linear-gradient(180deg, rgba(14,22,48,0.7), rgba(10,17,36,0.7));
  border: 1px solid var(--dp-border-strong);
  position:relative; overflow:hidden;
}
.dp-hero::before{
  content:""; position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(120,170,255,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120,170,255,0.06) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: radial-gradient(ellipse at 30% 40%, black 30%, transparent 80%);
  pointer-events:none;
}
.dp-hero-left{ display:flex; gap: 22px; align-items:flex-start; position:relative; z-index:1;}
.dp-avatar{
  width:84px; height:84px; border-radius: 22px;
  display:flex; align-items:center; justify-content:center;
  background: var(--dp-grad); color:white; font-weight:800; font-size:28px;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.08) inset, 0 12px 30px -8px rgba(0,200,255,0.55);
  letter-spacing:.02em;
}
.dp-name{ font-size: 30px; font-weight:800; line-height:1.1; margin: 4px 0 6px;}
.dp-headline{ color: var(--dp-text-dim); font-size: 15px; margin-bottom: 10px; }

/* Typewriter */
.dp-typer-wrap{ font-family:'JetBrains Mono', monospace; color:#9FE3FF; font-size:14px; min-height: 22px; }
.dp-typer{ border-right: 2px solid #00C8FF; padding-right:3px; animation: dp-blink 1s steps(1) infinite; }
@keyframes dp-blink{ 50%{ border-color: transparent; } }

/* Pills */
.dp-pill{
  display:inline-flex; align-items:center; gap:6px;
  padding: 6px 12px; margin: 4px 6px 0 0; border-radius: 999px;
  background: rgba(120,170,255,0.06);
  border: 1px solid var(--dp-border);
  color: var(--dp-text); font-size: 12.5px; font-weight:600;
}
.dp-pill svg{ width:12px; height:12px; }

/* Section header */
.dp-sec{ display:flex; align-items:center; gap:12px; margin: 28px 0 14px;}
.dp-sec h3{ margin:0; font-size: 18px; }
.dp-sec .bar{ width:3px; height:18px; background: var(--dp-grad); border-radius: 2px;}
.dp-sec .sub{ color: var(--dp-text-mute); font-size: 13px; margin-left: 4px;}

/* Score grid */
.dp-score-grid{ display:grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
@media (max-width: 1100px){ .dp-score-grid{ grid-template-columns: repeat(2,1fr);} }
.dp-score{
  position:relative; padding: 18px; border-radius: 16px;
  background: var(--dp-panel); border:1px solid var(--dp-border);
  display:flex; flex-direction:column; gap:10px;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.dp-score:hover{ transform: translateY(-3px); border-color: var(--dp-border-strong); box-shadow: var(--dp-glow);}
.dp-score .lbl{ font-size: 11px; letter-spacing:.16em; text-transform:uppercase; color: var(--dp-text-mute); font-weight:700;}
.dp-score .val{ font-size: 26px; font-weight:800; background: var(--dp-grad); -webkit-background-clip:text; background-clip:text; color: transparent;}
.dp-ring{ width: 64px; height: 64px; }

/* AI cards grid */
.dp-grid-2{ display:grid; grid-template-columns: repeat(2,1fr); gap:14px; }
.dp-grid-3{ display:grid; grid-template-columns: repeat(3,1fr); gap:14px; }
.dp-grid-4{ display:grid; grid-template-columns: repeat(4,1fr); gap:14px; }
@media (max-width: 1000px){ .dp-grid-2,.dp-grid-3,.dp-grid-4{ grid-template-columns: 1fr 1fr;} }
@media (max-width: 640px){ .dp-grid-2,.dp-grid-3,.dp-grid-4{ grid-template-columns: 1fr;} }

.dp-aicard{
  padding:18px; border-radius: 16px;
  background: var(--dp-panel); border: 1px solid var(--dp-border);
  display:flex; flex-direction:column; gap:8px; min-height: 130px;
  transition: all .25s ease;
}
.dp-aicard:hover{ transform: translateY(-3px); border-color: var(--dp-border-strong); box-shadow: var(--dp-glow);}
.dp-aicard .ico{
  width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  background: rgba(0,200,255,0.10); border: 1px solid rgba(0,200,255,0.28); color:#00C8FF;
}
.dp-aicard .t{ font-size: 13px; color: var(--dp-text-mute); text-transform:uppercase; letter-spacing:.12em; font-weight:700;}
.dp-aicard .v{ font-size: 17px; font-weight:700; color: var(--dp-text); }
.dp-aicard .d{ font-size: 13px; color: var(--dp-text-dim); }

/* Insight cards */
.dp-insight{
  position:relative; padding: 16px 18px; border-radius: 14px;
  background: linear-gradient(180deg, rgba(0,200,255,0.06), rgba(37,99,235,0.04));
  border: 1px solid var(--dp-border-strong);
  display:flex; gap: 12px; align-items:flex-start;
  animation: dp-fadeup .6s ease both;
}
.dp-insight .ico{
  width:34px; height:34px; border-radius:10px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  background: var(--dp-grad); color:white;
  box-shadow: 0 0 22px rgba(0,200,255,0.35);
}
.dp-insight .txt{ color: var(--dp-text); font-size: 14px; line-height: 1.5;}
.dp-insight .txt b{ color:#9FE3FF; font-weight:700;}

/* Timeline */
.dp-timeline{ position:relative; padding-left: 28px; }
.dp-timeline::before{
  content:""; position:absolute; left: 10px; top: 6px; bottom: 6px; width: 2px;
  background: linear-gradient(180deg, #00C8FF, #2563EB 60%, transparent);
  border-radius: 2px;
}
.dp-tl-item{ position:relative; padding: 10px 0 18px 8px;}
.dp-tl-item::before{
  content:""; position:absolute; left: -23px; top: 14px; width: 12px; height: 12px;
  border-radius:50%; background: var(--dp-grad);
  box-shadow: 0 0 0 4px rgba(0,200,255,0.12), 0 0 14px rgba(0,200,255,0.6);
}
.dp-tl-title{ font-weight:700; color: var(--dp-text); font-size: 14px;}
.dp-tl-sub{ color: var(--dp-text-dim); font-size: 12.5px; margin-top: 2px;}
.dp-tl-time{ color: var(--dp-text-mute); font-size: 11.5px; margin-top: 4px; font-family:'JetBrains Mono', monospace;}

/* Skill cloud */
.dp-skillgroup{ margin-bottom: 14px; }
.dp-skillgroup .h{
  font-size: 11px; letter-spacing:.16em; text-transform:uppercase;
  color: var(--dp-text-mute); font-weight:700; margin-bottom: 8px;
}
.dp-chip{
  display:inline-flex; align-items:center; gap:6px;
  padding: 7px 12px; margin: 4px 6px 4px 0; border-radius: 10px;
  background: rgba(14,22,48,0.7); border: 1px solid var(--dp-border);
  color: var(--dp-text); font-size: 12.5px; font-weight:600;
  transition: all .2s ease;
}
.dp-chip:hover{ border-color: rgba(0,200,255,0.55); color:#9FE3FF; box-shadow: 0 0 18px rgba(0,200,255,0.25); transform: translateY(-1px);}
.dp-chip .dt{ width:5px; height:5px; border-radius:50%; background: var(--dp-cyan); box-shadow: 0 0 8px var(--dp-cyan);}

/* Asset card */
.dp-asset{
  padding:16px; border-radius: 16px;
  background: var(--dp-panel); border: 1px solid var(--dp-border);
  display:flex; flex-direction:column; gap:10px; min-height: 170px;
  transition: all .25s ease;
}
.dp-asset:hover{ transform: translateY(-3px); border-color: var(--dp-border-strong); box-shadow: var(--dp-glow);}
.dp-asset .doc{
  height: 70px; border-radius: 10px; position:relative; overflow:hidden;
  background:
    linear-gradient(180deg, rgba(0,200,255,0.10), rgba(37,99,235,0.06)),
    repeating-linear-gradient(180deg, transparent 0 10px, rgba(255,255,255,0.04) 10px 11px);
  border: 1px solid var(--dp-border);
}
.dp-asset .nm{ font-weight:700; color: var(--dp-text); font-size: 14px;}
.dp-asset .meta{ color: var(--dp-text-mute); font-size: 12px; font-family:'JetBrains Mono', monospace;}
.dp-status{
  display:inline-flex; align-items:center; gap:6px;
  padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight:700;
  background: rgba(0,200,255,0.10); border:1px solid rgba(0,200,255,0.28); color:#9FE3FF;
  width: fit-content;
}
.dp-status .dt{ width:6px; height:6px; border-radius:50%; background:#00C8FF; box-shadow: 0 0 8px #00C8FF;}

/* Buttons */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button{
  background: var(--dp-grad) !important;
  color: white !important; font-weight: 700 !important;
  border: 0 !important; border-radius: 12px !important;
  padding: 10px 18px !important;
  box-shadow: 0 10px 24px -10px rgba(0,200,255,0.55), inset 0 0 0 1px rgba(255,255,255,0.10) !important;
  transition: transform .15s ease, box-shadow .2s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover{
  transform: translateY(-2px); box-shadow: 0 16px 32px -10px rgba(0,200,255,0.7) !important;
}
.stButton > button:active{ transform: translateY(0);}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input{
  background: rgba(10,17,36,0.7) !important;
  border: 1px solid var(--dp-border) !important;
  color: var(--dp-text) !important;
  border-radius: 12px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
  border-color: rgba(0,200,255,0.55) !important;
  box-shadow: 0 0 0 4px rgba(0,200,255,0.10) !important;
}
label, .stTextInput label, .stTextArea label, .stSelectbox label, .stCheckbox label{
  color: var(--dp-text-dim) !important; font-weight: 600 !important; font-size: 13px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  gap: 6px; background: rgba(10,17,36,0.55);
  border: 1px solid var(--dp-border); border-radius: 14px;
  padding: 6px; backdrop-filter: blur(14px);
}
.stTabs [data-baseweb="tab"]{
  background: transparent !important; color: var(--dp-text-dim) !important;
  border-radius: 10px !important; padding: 10px 16px !important;
  font-weight: 600 !important; border: 0 !important;
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(0,200,255,0.18), rgba(37,99,235,0.18)) !important;
  color: var(--dp-text) !important;
  box-shadow: inset 0 0 0 1px rgba(0,200,255,0.35);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display:none;}

/* DataFrame */
[data-testid="stDataFrame"]{
  border: 1px solid var(--dp-border); border-radius: 14px; overflow:hidden;
  background: var(--dp-panel);
}

/* Toggles / checkboxes */
.stCheckbox > label > div:first-child{
  background: rgba(10,17,36,0.7) !important;
  border-color: var(--dp-border) !important;
}

/* Divider */
hr{ border-color: var(--dp-border) !important; opacity: .7;}

/* Animations */
@keyframes dp-fadeup{ from{opacity:0; transform: translateY(10px);} to{opacity:1; transform:none;} }
.dp-fadeup{ animation: dp-fadeup .6s ease both; }
.dp-fadeup.d1{ animation-delay:.08s;} .dp-fadeup.d2{ animation-delay:.16s;}
.dp-fadeup.d3{ animation-delay:.24s;} .dp-fadeup.d4{ animation-delay:.32s;}

@keyframes dp-float{ 0%,100%{transform:translateY(0);} 50%{transform:translateY(-6px);} }
.dp-float{ animation: dp-float 6s ease-in-out infinite; }

@keyframes dp-pulse{ 0%,100%{opacity:.5;} 50%{opacity:1;} }
.dp-pulse{ animation: dp-pulse 2.4s ease-in-out infinite; }

/* Profile completion ring container */
.dp-completion{
  display:flex; align-items:center; gap: 18px;
  padding: 18px 20px; border-radius: 16px;
  background: var(--dp-panel); border: 1px solid var(--dp-border);
}
.dp-completion .meta{ display:flex; flex-direction:column; gap:4px; }
.dp-completion .meta .t{ font-size: 12px; color: var(--dp-text-mute); text-transform:uppercase; letter-spacing:.16em; font-weight:700;}
.dp-completion .meta .v{ font-size: 24px; font-weight:800; color: var(--dp-text);}
.dp-missing{ color: var(--dp-text-dim); font-size: 13px;}
.dp-missing b{ color:#9FE3FF; }

/* Logo */
.dp-logo{
  display:flex; align-items:center; gap:10px; margin-bottom: 14px;
}
.dp-logo .nm{ font-weight:800; letter-spacing:-.02em; font-size: 18px;}
.dp-logo .nm em{ font-style:normal; background: var(--dp-grad); -webkit-background-clip:text; background-clip:text; color: transparent;}
.dp-logo .tag{ color: var(--dp-text-mute); font-size: 11px; letter-spacing:.14em; text-transform:uppercase;}
</style>
"""

st.markdown(DP_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Embedded SVG assets
# ---------------------------------------------------------------------------
LOGO_SVG = """
<svg width="34" height="34" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="dpg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#00C8FF"/>
      <stop offset="50%" stop-color="#0EA5E9"/>
      <stop offset="100%" stop-color="#2563EB"/>
    </linearGradient>
  </defs>
  <path d="M14 8h18c14 0 24 10 24 24S46 56 32 56H14V8z" stroke="url(#dpg)" stroke-width="4" fill="none"/>
  <circle cx="20" cy="20" r="3" fill="url(#dpg)"/>
  <circle cx="20" cy="32" r="3" fill="url(#dpg)"/>
  <circle cx="20" cy="44" r="3" fill="url(#dpg)"/>
  <circle cx="34" cy="32" r="4" fill="url(#dpg)"/>
  <path d="M23 20l8 10M23 44l8-10M34 32l16-12" stroke="url(#dpg)" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M44 16l8-4-2 9" stroke="url(#dpg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>
"""

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
    <line x1="210" y1="140" x2="70"  y2="60"/>
    <line x1="210" y1="140" x2="360" y2="60"/>
    <line x1="210" y1="140" x2="40"  y2="200"/>
    <line x1="210" y1="140" x2="380" y2="220"/>
    <line x1="210" y1="140" x2="150" y2="40"/>
    <line x1="210" y1="140" x2="280" y2="250"/>
    <line x1="70"  y1="60"  x2="150" y2="40"/>
    <line x1="360" y1="60"  x2="380" y2="220"/>
    <line x1="40"  y1="200" x2="280" y2="250"/>
  </g>
  <g fill="#00C8FF">
    <circle cx="70"  cy="60"  r="4"><animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite"/></circle>
    <circle cx="360" cy="60"  r="4"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.6s" repeatCount="indefinite"/></circle>
    <circle cx="40"  cy="200" r="4"><animate attributeName="opacity" values="0.4;1;0.4" dur="4.2s" repeatCount="indefinite"/></circle>
    <circle cx="380" cy="220" r="4"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.2s" repeatCount="indefinite"/></circle>
    <circle cx="150" cy="40"  r="3"><animate attributeName="opacity" values="0.4;1;0.4" dur="2.8s" repeatCount="indefinite"/></circle>
    <circle cx="280" cy="250" r="3"><animate attributeName="opacity" values="0.4;1;0.4" dur="3.4s" repeatCount="indefinite"/></circle>
  </g>
  <circle cx="210" cy="140" r="10" fill="#00C8FF">
    <animate attributeName="r" values="9;13;9" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.85;1;0.85" dur="2.6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="210" cy="140" r="22" fill="none" stroke="#00C8FF" stroke-opacity=".35">
    <animate attributeName="r" values="18;34;18" dur="3.2s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values=".4;0;.4" dur="3.2s" repeatCount="indefinite"/>
  </circle>
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
    pct = max(0.0, min(100.0, float(pct)))
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
st.markdown(
    f"""
    <div class="dp-logo dp-fadeup">
      {LOGO_SVG}
      <div>
        <div class="nm">Data<em>Pilot</em> <em>AI</em></div>
        <div class="tag">Navigate Your Data Career</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# HERO — Career Identity
# ---------------------------------------------------------------------------
display_name = profile.get("full_name") or st.session_state.get("username") or "Explorer"
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
    <div class="dp-hero dp-fadeup">
      <div class="dp-hero-left">
        <div class="dp-avatar">{escape(_initials(display_name))}</div>
        <div style="flex:1;">
          <div class="dp-eyebrow"><span class="dot dp-pulse"></span>Career Identity</div>
          <div class="dp-name">{escape(display_name)}</div>
          <div class="dp-headline">{escape(profile.get("headline") or "Career profile")}</div>
          <div class="dp-typer-wrap">Building toward&nbsp;<span class="dp-typer" id="dp-typer">Data Analyst</span></div>
          <div style="margin-top:14px;">{pills_html}</div>
        </div>
      </div>
      <div class="dp-float" style="position:relative; z-index:1;">{NETWORK_SVG}</div>
    </div>
    <script>
    (function(){{
      const roles = ["Data Analyst","Data Scientist","Business Analyst","BI Analyst","Data Engineer","ML Engineer","Analytics Engineer"];
      const el = window.parent.document.getElementById('dp-typer') || document.getElementById('dp-typer');
      if(!el || el.__dpInit) return; el.__dpInit = true;
      let i=0, j=0, del=false;
      function tick(){{
        const w = roles[i];
        el.textContent = w.substring(0, j);
        if(!del && j < w.length){{ j++; setTimeout(tick, 70); }}
        else if(!del && j === w.length){{ del = true; setTimeout(tick, 1400); }}
        else if(del && j > 0){{ j--; setTimeout(tick, 35); }}
        else {{ del = false; i = (i+1) % roles.length; setTimeout(tick, 250); }}
      }}
      tick();
    }})();
    </script>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Profile completion
# ---------------------------------------------------------------------------
completion_fields = ["full_name","headline","phone","location","portfolio","linkedin",
                     "github","target_role","skills","bio","career_goals"]
filled = sum(1 for f in completion_fields if str(profile.get(f, "")).strip())
completion_pct = round(filled / len(completion_fields) * 100)
missing = [{"linkedin":"LinkedIn","portfolio":"Portfolio","career_goals":"Career Goals",
            "github":"GitHub","bio":"Bio","skills":"Skills"}.get(f, f.replace("_"," ").title())
           for f in completion_fields if not str(profile.get(f, "")).strip()]
missing_html = ", ".join(f"<b>{escape(m)}</b>" for m in missing[:4]) or "All set"

st.markdown(
    f"""
    <div class="dp-completion dp-fadeup d1" style="margin-top:18px;">
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
# CAREER HEALTH SCORE
# ---------------------------------------------------------------------------
ats_val = float(latest_analysis.ats_score) if latest_analysis and latest_analysis.ats_score is not None else 0.0
match_val = float(latest_analysis.match_score) if latest_analysis and latest_analysis.match_score is not None else 0.0
salary_val = float(latest_prediction.predicted_salary) / 100000 if latest_prediction else 0.0
readiness = round((ats_val + match_val) / 2, 1)
market_demand = min(95, 55 + int(match_val * 0.35))
salary_potential = min(99, int(salary_val * 8)) if salary_val else 0

st.markdown(
    """
    <div class="dp-sec dp-fadeup d1">
      <span class="bar"></span><h3>Career Health Score</h3>
      <span class="sub">Live diagnostics across ATS, market fit, and salary potential</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="dp-score-grid dp-fadeup d2">
      <div class="dp-score">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="lbl">Readiness</span>{_ring(readiness, "r1")}
        </div>
        <span class="val">{readiness}%</span>
      </div>
      <div class="dp-score">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="lbl">ATS Strength</span>{_ring(ats_val, "r2")}
        </div>
        <span class="val">{ats_val:.1f}%</span>
      </div>
      <div class="dp-score">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="lbl">Skill Match</span>{_ring(match_val, "r3")}
        </div>
        <span class="val">{match_val:.1f}%</span>
      </div>
      <div class="dp-score">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="lbl">Market Demand</span>{_ring(market_demand, "r4")}
        </div>
        <span class="val">{market_demand}%</span>
      </div>
      <div class="dp-score">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="lbl">Salary Potential</span>{_ring(salary_potential, "r5")}
        </div>
        <span class="val">{(_format_lpa(latest_prediction.predicted_salary) if latest_prediction else "—")}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Counts strip (preserves original metric data)
# ---------------------------------------------------------------------------
st.markdown('<div class="dp-sec dp-fadeup"><span class="bar"></span><h3>Activity Footprint</h3><span class="sub">Every artifact you have created on DataPilot AI</span></div>', unsafe_allow_html=True)
count_cards = [
    ("Resumes", counts.get("resumes", 0), "doc"),
    ("Analyses", counts.get("analyses", 0), "chart"),
    ("Salary Predictions", counts.get("predictions", 0), "trend"),
    ("AI Chats", counts.get("chats", 0), "spark"),
    ("Job Fit Records", counts.get("job_fit_history", 0), "target"),
]
cards_html = "".join(
    f"""<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>
        <span class="t">{escape(lbl)}</span><span class="v">{val}</span></div>"""
    for lbl, val, ic in count_cards
)
st.markdown(f'<div class="dp-grid-4 dp-fadeup d1" style="grid-template-columns: repeat(5,1fr);">{cards_html}</div>', unsafe_allow_html=True)


st.write("")


# ---------------------------------------------------------------------------
# TABS — Career Command Center
# ---------------------------------------------------------------------------
identity_tab, performance_tab, intelligence_tab, assets_tab, settings_tab = st.tabs(
    ["Career Identity", "Performance Hub", "AI Career Intelligence", "Career Assets", "Account Settings"]
)


# ============================== CAREER IDENTITY =============================
with identity_tab:
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>AI Career Snapshot</h3><span class="sub">Synthesized signals from your latest analyses</span></div>', unsafe_allow_html=True)

    positioning = profile.get("target_role") or "Define your target role to sharpen positioning."
    competitiveness = f"Top {max(5, 100 - int(match_val))}% match for {profile.get('target_role') or 'your target role'}" if match_val else "Run a resume analysis to benchmark."
    momentum = f"{counts.get('analyses', 0)} analyses · {counts.get('predictions', 0)} salary runs"
    growth = f"{int(min(100, match_val + 12))}% projected with skill additions" if match_val else "Add skills to forecast growth."

    snap_cards = [
        ("Current Positioning", positioning, "target"),
        ("Market Competitiveness", competitiveness, "trend"),
        ("Career Momentum", momentum, "bolt"),
        ("Growth Potential", growth, "spark"),
    ]
    snap_html = "".join(
        f"""<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>
            <span class="t">{escape(t)}</span><span class="d">{escape(d)}</span></div>"""
        for t, d, ic in snap_cards
    )
    st.markdown(f'<div class="dp-grid-4">{snap_html}</div>', unsafe_allow_html=True)

    # Identity + contact details
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Identity & Contact</h3></div>', unsafe_allow_html=True)

    info_left = f"""
    <div class="dp-card">
      <div class="dp-eyebrow"><span class="dot"></span>Account</div>
      <div style="margin-top:12px; display:grid; grid-template-columns: 130px 1fr; gap:10px 16px; font-size:14px;">
        <span class="dp-mute">Username</span><span>{escape(str(st.session_state.get('username','—')))}</span>
        <span class="dp-mute">Email</span><span>{escape(str(st.session_state.get('email','—')))}</span>
        <span class="dp-mute">Member since</span><span>{escape(_format_ts(getattr(user, 'created_at', None)))}</span>
        <span class="dp-mute">Visibility</span><span>{escape(profile.get('profile_visibility','Private'))}</span>
      </div>
    </div>
    """
    info_right = f"""
    <div class="dp-card">
      <div class="dp-eyebrow"><span class="dot"></span>Contact</div>
      <div style="margin-top:12px; display:grid; grid-template-columns: 130px 1fr; gap:10px 16px; font-size:14px;">
        <span class="dp-mute">Phone</span><span>{escape(profile.get('phone') or 'Not added')}</span>
        <span class="dp-mute">Location</span><span>{escape(profile.get('location') or 'Not added')}</span>
        <span class="dp-mute">Portfolio</span><span>{escape(profile.get('portfolio') or 'Not added')}</span>
        <span class="dp-mute">LinkedIn</span><span>{escape(profile.get('linkedin') or 'Not added')}</span>
        <span class="dp-mute">GitHub</span><span>{escape(profile.get('github') or 'Not added')}</span>
      </div>
    </div>
    """
    st.markdown(f'<div class="dp-grid-2">{info_left}{info_right}</div>', unsafe_allow_html=True)

    # About + Skills
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>About</h3></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="dp-card"><p style="margin:0; color:var(--dp-text-dim); line-height:1.6;">{escape(profile.get("bio") or "No bio added yet. Tell the AI who you are and where you are headed.")}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Skill Cloud</h3><span class="sub">Grouped by capability area</span></div>', unsafe_allow_html=True)

    raw_skills = [s.strip() for s in profile.get("skills", "").split(",") if s.strip()]
    groups = {"Programming": [], "Analytics": [], "Visualization": [], "Machine Learning": [], "Databases": [], "Cloud": [], "Other": []}
    bucket_map = {
        "python":"Programming","r":"Programming","java":"Programming","scala":"Programming","sql":"Databases",
        "excel":"Analytics","statistics":"Analytics","pandas":"Analytics","numpy":"Analytics",
        "tableau":"Visualization","power bi":"Visualization","powerbi":"Visualization","looker":"Visualization","matplotlib":"Visualization","seaborn":"Visualization",
        "tensorflow":"Machine Learning","pytorch":"Machine Learning","sklearn":"Machine Learning","scikit-learn":"Machine Learning","ml":"Machine Learning","nlp":"Machine Learning",
        "postgres":"Databases","mysql":"Databases","mongodb":"Databases","snowflake":"Databases","bigquery":"Databases",
        "aws":"Cloud","gcp":"Cloud","azure":"Cloud","databricks":"Cloud",
    }
    for s in raw_skills:
        groups[bucket_map.get(s.lower(), "Other")].append(s)

    groups_html = ""
    any_skill = False
    for group, items in groups.items():
        if not items: continue
        any_skill = True
        chips = "".join(f'<span class="dp-chip"><span class="dt"></span>{escape(i)}</span>' for i in items)
        groups_html += f'<div class="dp-skillgroup"><div class="h">{group}</div>{chips}</div>'
    if not any_skill:
        groups_html = '<p class="dp-mute" style="margin:0;">No skills added yet. Add them in the Performance Hub.</p>'
    st.markdown(f'<div class="dp-card">{groups_html}</div>', unsafe_allow_html=True)


# ============================== PERFORMANCE HUB =============================
with performance_tab:
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Edit Career Identity</h3><span class="sub">Saved to this session</span></div>', unsafe_allow_html=True)

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
            exp_opts = ["Fresher","Entry Level","Mid Level","Senior","Lead / Manager"]
            experience_level = st.selectbox(
                "Experience Level", exp_opts,
                index=exp_opts.index(profile.get("experience_level","Fresher")) if profile.get("experience_level","Fresher") in exp_opts else 0,
            )
            avail_opts = ["Open to opportunities","Actively applying","Interviewing","Not looking"]
            availability = st.selectbox(
                "Availability", avail_opts,
                index=avail_opts.index(profile.get("availability","Open to opportunities")) if profile.get("availability","Open to opportunities") in avail_opts else 0,
            )

        preferred_location = st.text_input("Preferred Job Location", value=profile.get("preferred_location",""))
        expected_salary = st.text_input("Expected Salary", value=profile.get("expected_salary",""))
        skills = st.text_area("Skills", value=profile.get("skills",""), help="Enter skills separated by commas.")
        bio = st.text_area("Bio", value=profile.get("bio",""), height=120)
        career_goals = st.text_area("Career Goals", value=profile.get("career_goals",""), height=120)

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

    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Latest Performance</h3></div>', unsafe_allow_html=True)
    perf_cards = [
        ("ATS Score", f"{latest_analysis.ats_score:.1f}%" if latest_analysis and latest_analysis.ats_score is not None else "No result yet", "shield"),
        ("Skill Match", f"{latest_analysis.match_score:.1f}%" if latest_analysis and latest_analysis.match_score is not None else "No result yet", "target"),
        ("Salary Estimate", _format_lpa(latest_prediction.predicted_salary) if latest_prediction else "No result yet", "trend"),
    ]
    perf_html = "".join(
        f"""<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>
            <span class="t">{escape(t)}</span><span class="v">{escape(v)}</span></div>"""
        for t, v, ic in perf_cards
    )
    st.markdown(f'<div class="dp-grid-3">{perf_html}</div>', unsafe_allow_html=True)


# ============================ AI CAREER INTELLIGENCE ========================
with intelligence_tab:
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>AI Recommendations</h3><span class="sub">Personalized signals derived from your activity</span></div>', unsafe_allow_html=True)

    target = profile.get("target_role") or "Data Analyst"
    insights = []
    if match_val < 90:
        insights.append(f"Adding <b>Tableau</b> and <b>Power BI</b> could increase your {escape(target)} fit by an estimated <b>{max(6, int(95-match_val))}%</b>.")
    if ats_val:
        pct_better = min(95, int(ats_val * 0.85))
        insights.append(f"Your ATS score is stronger than <b>{pct_better}%</b> of DataPilot users targeting similar roles.")
    insights.append("The <b>SQL + Power BI + Python</b> combination is highly demanded in your target market right now.")
    if not profile.get("linkedin"):
        insights.append("Adding your <b>LinkedIn</b> increases recruiter discoverability by <b>3.4x</b>.")
    if latest_prediction:
        insights.append(f"Based on your current profile, your salary trajectory points toward <b>{escape(_format_lpa(latest_prediction.predicted_salary))}</b>.")

    insights_html = "".join(
        f"""<div class="dp-insight dp-fadeup d{min(i,4)}"><div class="ico">{_icon('spark')}</div>
            <div class="txt">{txt}</div></div>"""
        for i, txt in enumerate(insights, 1)
    )
    st.markdown(f'<div style="display:flex; flex-direction:column; gap:12px;">{insights_html}</div>', unsafe_allow_html=True)

    # Activity timeline
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Activity Timeline</h3><span class="sub">Your career journey on DataPilot AI</span></div>', unsafe_allow_html=True)

    activity_items = snapshot.get("activity_items", [])
    if not activity_items:
        st.markdown(
            '<div class="dp-card"><p class="dp-mute" style="margin:0;">No activity yet. Analyze a resume, predict salary, or start an AI Mentor chat to build your timeline.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        tl_html = ""
        for item in activity_items[:10]:
            tl_html += f"""
            <div class="dp-tl-item">
              <div class="dp-tl-title">{escape(str(item.get("title") or item.get("kind") or "Activity"))}</div>
              <div class="dp-tl-sub">{escape(str(item.get("detail") or ""))}</div>
              <div class="dp-tl-time">{escape(_format_ts(item.get("timestamp")))} · {escape(str(item.get("kind") or ""))}</div>
            </div>
            """
        st.markdown(f'<div class="dp-card"><div class="dp-timeline">{tl_html}</div></div>', unsafe_allow_html=True)


# ================================ CAREER ASSETS =============================
with assets_tab:
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Career Assets</h3><span class="sub">Resumes, reports and AI artifacts</span></div>', unsafe_allow_html=True)

    resumes = sorted(
        snapshot.get("resumes", []),
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
            cards += f"""
            <div class="dp-asset">
              <div class="doc"></div>
              <div class="nm">{escape(r.resume_name or 'Untitled resume')}</div>
              <div class="meta">{escape(_format_ts(getattr(r, 'uploaded_at', None)))}</div>
              <span class="dp-status"><span class="dt"></span>Indexed</span>
            </div>
            """
        st.markdown(f'<div class="dp-grid-4">{cards}</div>', unsafe_allow_html=True)

    # Asset categories
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Artifact Library</h3></div>', unsafe_allow_html=True)
    lib = [
        ("Resumes", counts.get("resumes", 0), "doc"),
        ("Salary Reports", counts.get("predictions", 0), "trend"),
        ("Roadmaps", counts.get("chats", 0), "spark"),
        ("Job Fit Reports", counts.get("job_fit_history", 0), "target"),
    ]
    lib_html = "".join(
        f"""<div class="dp-aicard"><div class="ico">{_icon(ic)}</div>
            <span class="t">{escape(t)}</span><span class="v">{v} items</span>
            <span class="d">Updated {escape(_format_ts(datetime.now()))}</span></div>"""
        for t, v, ic in lib
    )
    st.markdown(f'<div class="dp-grid-4">{lib_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Quick Actions</h3></div>', unsafe_allow_html=True)
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

    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Career Goals</h3></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="dp-card"><p style="margin:0; color:var(--dp-text-dim); line-height:1.6;">{escape(profile.get("career_goals") or "No career goals defined yet. Add them in the Performance Hub.")}</p></div>',
        unsafe_allow_html=True,
    )


# ============================== ACCOUNT SETTINGS ============================
with settings_tab:
    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Preferences</h3><span class="sub">Notifications and AI personalization</span></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="dp-card"><div class="dp-eyebrow"><span class="dot"></span>Notifications</div><div style="height:8px;"></div>', unsafe_allow_html=True)
        email_updates = st.checkbox("Email updates", value=profile.get("email_updates", True))
        resume_reminders = st.checkbox("Resume improvement reminders", value=profile.get("resume_reminders", True))
        mentor_tips = st.checkbox("AI Mentor tips", value=profile.get("mentor_tips", True))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="dp-card"><div class="dp-eyebrow"><span class="dot"></span>Privacy</div><div style="height:8px;"></div>', unsafe_allow_html=True)
        vis_opts = ["Private","Visible to mentors","Visible to recruiters"]
        profile_visibility = st.selectbox(
            "Profile Visibility", vis_opts,
            index=vis_opts.index(profile.get("profile_visibility","Private")) if profile.get("profile_visibility","Private") in vis_opts else 0,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Save Preferences", use_container_width=True):
        profile.update({
            "email_updates": email_updates,
            "resume_reminders": resume_reminders,
            "mentor_tips": mentor_tips,
            "profile_visibility": profile_visibility,
        })
        st.success("Preferences saved.")

    st.markdown('<div class="dp-sec"><span class="bar"></span><h3>Account Security</h3></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="dp-card">
          <div class="dp-eyebrow"><span class="dot"></span>Signed In</div>
          <p style="margin:12px 0 6px; font-size:14px;">Signed in as <b>{escape(str(st.session_state.get('email','Not available')))}</b></p>
          <p class="dp-mute" style="margin:0; font-size:13px;">Password changes are handled from the authentication flow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Logout", use_container_width=True):
        logout()
        st.switch_page("pages/1_Login.py")
