import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.auth.session_manager import is_authenticated
from src.dashboard.dashboard_service import build_dashboard_snapshot


# pages/3_Dashboard.py  (and every other page)

from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Dashboard · DataPilot AI",
    page_icon="assets/mini_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Mark the active page so the sidebar highlights it
st.session_state["_active_nav"] = "Dashboard"   # change per page

show_sidebar()

# ---- page content below ----
st.title("Dashboard")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataPilot AI — Dashboard",
    page_icon="assets/mini_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("No user profile is loaded for this session.")
    st.stop()

snapshot = build_dashboard_snapshot(user_id)
latest_analysis = snapshot.get("latest_analysis")
latest_prediction = snapshot.get("latest_prediction")
latest_resume = snapshot.get("latest_resume")

if "show_full_history" not in st.session_state:
    st.session_state["show_full_history"] = False


# ─────────────────────────────────────────────────────────────
# HELPERS (unchanged behaviour)
# ─────────────────────────────────────────────────────────────
def _format_ts(value):
    if not value:
        return "No history yet"
    return value.strftime("%d %b %Y, %I:%M %p")

def _format_lpa(value):
    if value is None:
        return "No history yet"
    return f"₹{float(value) / 100000:.1f} LPA"

def _logo_b64():
    for p in ["assets/mini_logo.png", "static/logo.png", "logo.png"]:
        if Path(p).exists():
            return base64.b64encode(Path(p).read_bytes()).decode()
    return ""

def _logo_b64_():
    for p in ["assets/logo.png", "static/logo.png", "logo.png"]:
        if Path(p).exists():
            return base64.b64encode(Path(p).read_bytes()).decode()
    return ""

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS — premium dark SaaS theme
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root{
      --dp-bg:#06080F;
      --dp-bg-2:#0A0F1F;
      --dp-surface: rgba(15,22,40,0.55);
      --dp-surface-2: rgba(20,28,52,0.65);
      --dp-border: rgba(120,160,255,0.14);
      --dp-border-strong: rgba(120,180,255,0.28);
      --dp-text:#E6ECFA;
      --dp-text-dim:#8A95B2;
      --dp-blue:#2D7BFF;
      --dp-cyan:#3FD1FF;
      --dp-glow: 0 0 60px rgba(45,123,255,0.25);
    }

    .stApp{
      background:
        radial-gradient(1200px 600px at 10% -10%, rgba(45,123,255,0.18), transparent 60%),
        radial-gradient(900px 500px at 100% 10%, rgba(63,209,255,0.12), transparent 60%),
        radial-gradient(800px 600px at 50% 110%, rgba(80,90,255,0.10), transparent 60%),
        linear-gradient(180deg, #05070E 0%, #06080F 100%);
      color: var(--dp-text);
      font-family:'Inter', system-ui, sans-serif;
    }

    /* Floating orbs */
    .stApp::before, .stApp::after{
      content:""; position:fixed; pointer-events:none; z-index:0;
      width:520px; height:520px; border-radius:50%; filter:blur(90px); opacity:.45;
    }
    .stApp::before{ background:radial-gradient(circle, #2D7BFF 0%, transparent 70%); top:-160px; left:-160px; animation: dpFloat 16s ease-in-out infinite;}
    .stApp::after { background:radial-gradient(circle, #3FD1FF 0%, transparent 70%); bottom:-200px; right:-180px; animation: dpFloat 22s ease-in-out infinite reverse;}
    @keyframes dpFloat{ 0%,100%{transform:translate(0,0)} 50%{transform:translate(40px,-30px)} }

    .block-container{ padding-top:1.2rem !important; max-width:1320px; position:relative; z-index:1;}

    /* Hide default streamlit header chrome */
    
    #MainMenu,header, footer{ visibility:hidden;}

    [data-testid="stStatusWidget"] {
    display: none !important;
}

    /* ── HERO ── */
    .dp-hero{
      position:relative; overflow:hidden;
      border:1px solid var(--dp-border-strong);
      border-radius:24px;
      padding:34px 38px;
      background:
        radial-gradient(600px 200px at 90% 0%, rgba(63,209,255,0.18), transparent 70%),
        radial-gradient(500px 220px at 0% 100%, rgba(45,123,255,0.22), transparent 70%),
        linear-gradient(135deg, rgba(20,28,52,0.85), rgba(10,15,31,0.85));
      backdrop-filter: blur(18px);
      box-shadow: var(--dp-glow), inset 0 1px 0 rgba(255,255,255,0.04);
      animation: dpFade .8s ease both;
    }
    .dp-hero-row{ display:flex; align-items:center; gap:28px; flex-wrap:wrap;}
    .dp-hero-logo img{ height:74px; filter: drop-shadow(0 6px 24px rgba(63,209,255,0.35));}
    .dp-hero-text h1{
      font-family:'Space Grotesk', sans-serif; font-weight:700;
      font-size: 2.1rem; margin:0; letter-spacing:-0.02em;
      background: linear-gradient(90deg,#fff 0%, #B9D3FF 60%, #3FD1FF 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .dp-hero-text .dp-sub{ color:var(--dp-text-dim); margin-top:6px; font-size:.98rem;}
    .dp-hero-text .dp-desc{ color:#A9B4D0; margin-top:14px; max-width:780px; line-height:1.6; font-size:.95rem;}
    .dp-pill{
      display:inline-flex; align-items:center; gap:8px;
      padding:6px 14px; border-radius:999px;
      background: rgba(45,123,255,0.12);
      border:1px solid rgba(63,209,255,0.30);
      color:#9FD0FF; font-size:.78rem; font-weight:500;
      margin-bottom:14px;
    }
    .dp-pill .dot{ width:7px; height:7px; border-radius:50%; background:#3FD1FF; box-shadow:0 0 10px #3FD1FF;}

    /* ── SECTION TITLES ── */
    .dp-section{ display:flex; align-items:center; gap:10px; margin: 26px 0 14px;}
    .dp-section svg{ color:#3FD1FF;}
    .dp-section h3{
      font-family:'Space Grotesk',sans-serif; font-weight:600;
      font-size:1.15rem; margin:0; color:#EAF0FF; letter-spacing:-0.01em;
    }
    .dp-section .dp-section-sub{ color:var(--dp-text-dim); font-size:.85rem; margin-left:6px;}

    /* ── KPI CARDS ── */
    [data-testid="stMetric"]{
      background: linear-gradient(180deg, rgba(20,28,52,0.7), rgba(12,18,36,0.7));
      border:1px solid var(--dp-border);
      border-radius:18px; padding:18px 20px;
      backdrop-filter: blur(14px);
      transition: all .3s cubic-bezier(.2,.8,.2,1);
      position:relative; overflow:hidden;
      animation: dpFade .6s ease both;
    }
    [data-testid="stMetric"]::before{
      content:""; position:absolute; inset:0; border-radius:18px; padding:1px;
      background:linear-gradient(135deg, rgba(63,209,255,.4), transparent 40%, rgba(45,123,255,.35));
      -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
      -webkit-mask-composite: xor; mask-composite: exclude;
      opacity:0; transition: opacity .3s;
    }
    [data-testid="stMetric"]:hover{ transform: translateY(-4px); box-shadow: 0 18px 40px -18px rgba(45,123,255,0.45);}
    [data-testid="stMetric"]:hover::before{ opacity:1;}
    [data-testid="stMetricLabel"] p{ color:var(--dp-text-dim) !important; font-size:.78rem !important; text-transform:uppercase; letter-spacing:.08em; font-weight:500;}
    [data-testid="stMetricValue"]{
      font-family:'Space Grotesk',sans-serif !important;
      font-size:1.7rem !important; font-weight:700 !important;
      background: linear-gradient(90deg,#fff,#9FD0FF);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }

    /* ── BUTTONS as feature cards ── */
    .stButton > button{
      width:100%;
      background: linear-gradient(180deg, rgba(20,28,52,0.7), rgba(12,18,36,0.7)) !important;
      border:1px solid var(--dp-border) !important;
      color:#EAF0FF !important;
      border-radius:16px !important;
      padding: 18px 18px !important;
      font-weight:600 !important;
      text-align:left !important;
      justify-content:flex-start !important;
      transition: all .25s cubic-bezier(.2,.8,.2,1) !important;
      backdrop-filter: blur(12px);
      min-height:64px;
    }
    .stButton > button:hover{
      transform: translateY(-3px);
      border-color: rgba(63,209,255,0.45) !important;
      box-shadow: 0 14px 36px -16px rgba(63,209,255,0.55), inset 0 1px 0 rgba(255,255,255,0.05);
      background: linear-gradient(180deg, rgba(30,50,90,0.75), rgba(18,28,55,0.75)) !important;
    }
    .stButton > button:focus{ box-shadow:0 0 0 2px rgba(63,209,255,0.35) !important;}

    /* Feature card wrapper (for description below button) */
    .dp-feature-desc{
      color: var(--dp-text-dim);
      font-size:.82rem;
      margin:-6px 0 14px 4px;
      line-height:1.45;
    }

    /* ── ACTIVITY ITEM ── */
    .dp-activity{
      display:flex; gap:14px; align-items:flex-start;
      padding:14px 16px; margin-bottom:10px;
      background: linear-gradient(180deg, rgba(20,28,52,0.55), rgba(12,18,36,0.55));
      border:1px solid var(--dp-border);
      border-radius:14px; backdrop-filter:blur(12px);
      transition: all .25s ease;
    }
    .dp-activity:hover{ transform:translateX(4px); border-color: rgba(63,209,255,0.35); box-shadow: -6px 0 24px -10px rgba(63,209,255,0.4);}
    .dp-activity .ic{
      width:36px; height:36px; border-radius:10px; flex-shrink:0;
      background: linear-gradient(135deg, rgba(45,123,255,0.25), rgba(63,209,255,0.15));
      border:1px solid rgba(63,209,255,0.3);
      display:flex; align-items:center; justify-content:center; color:#9FD0FF;
    }
    .dp-activity .body{ flex:1; min-width:0;}
    .dp-activity .kind{ font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; color:#3FD1FF; font-weight:600;}
    .dp-activity .title{ color:#EAF0FF; font-weight:600; font-size:.95rem; margin-top:2px;}
    .dp-activity .meta{ color:var(--dp-text-dim); font-size:.8rem; margin-top:4px;}

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"]{
      gap:6px; background: rgba(15,22,40,0.5); padding:6px;
      border-radius:14px; border:1px solid var(--dp-border);
      backdrop-filter:blur(12px);
    }
    .stTabs [data-baseweb="tab"]{
      background:transparent; border-radius:10px; color:var(--dp-text-dim);
      padding:8px 16px; font-weight:500; font-size:.88rem;
      transition: all .2s;
    }
    .stTabs [data-baseweb="tab"]:hover{ color:#EAF0FF;}
    .stTabs [aria-selected="true"]{
      background: linear-gradient(135deg, rgba(45,123,255,0.35), rgba(63,209,255,0.25)) !important;
      color:#fff !important; box-shadow: 0 4px 14px -4px rgba(45,123,255,0.5);
    }
    .stTabs [data-baseweb="tab-highlight"]{ display:none;}

    /* DataFrame */
    [data-testid="stDataFrame"]{
      border:1px solid var(--dp-border); border-radius:14px; overflow:hidden;
      background: rgba(15,22,40,0.5); backdrop-filter:blur(12px);
    }

    /* Alerts/info */
    .stAlert{
      background: rgba(15,22,40,0.6) !important;
      border:1px solid var(--dp-border) !important;
      border-radius:12px !important; color:var(--dp-text-dim) !important;
      backdrop-filter:blur(12px);
    }

    /* Divider */
    hr{ border-color: var(--dp-border) !important; margin: 26px 0 !important;}

    /* Footer */
    .dp-footer{
      margin-top:48px; padding:26px 32px; border-radius:18px;
      border:1px solid var(--dp-border);
      background: linear-gradient(135deg, rgba(15,22,40,0.6), rgba(10,15,31,0.6));
      backdrop-filter:blur(14px);
      display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;
    }
    .dp-footer-brand{ display:flex; align-items:center; gap:14px;}
    .dp-footer-brand img{ height:36px;}
    .dp-footer-brand .name{ font-family:'Space Grotesk',sans-serif; font-weight:700; color:#EAF0FF;}
    .dp-footer-brand .tag{ color:var(--dp-text-dim); font-size:.8rem;}
    .dp-footer .meta{ color:var(--dp-text-dim); font-size:.8rem; text-align:right;}

    [data-testid="stStatusWidget"] {
    display: none !important;
    }
    /* Glass section wrapper */
    .dp-glass{
      border:1px solid var(--dp-border); border-radius:18px;
      background: linear-gradient(180deg, rgba(15,22,40,0.55), rgba(10,15,31,0.55));
      backdrop-filter: blur(14px);
      padding:18px 20px; margin-bottom:8px;
    }

    @keyframes dpFade { from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:translateY(0)} }

    /* Mobile Responsive Add-on */

@media (max-width:768px){

    /* ---------- GLOBAL SAFETY / NO HORIZONTAL SCROLL ---------- */
    html, body, .stApp{
      overflow-x: hidden !important;
    }
    .block-container{
      padding-top:.75rem !important;
      padding-left:1rem !important;
      padding-right:1rem !important;
      max-width:100% !important;
    }

    /* ---------- GENERIC COLUMN STACKING (st.columns) ---------- */
    div[data-testid="stHorizontalBlock"]{
      flex-direction: column !important;
      flex-wrap: wrap !important;
      gap: 12px !important;
      row-gap: 12px !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]{
      width: 100% !important;
      flex: 1 1 100% !important;
      min-width: 100% !important;
    }

    /* ---------- SPECIAL CASE: the 5-stat counts row → 2-column grid ---------- */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(5)),
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"]:nth-child(5)){
      flex-direction: row !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(5)) > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"]:nth-child(5)) > div[data-testid="stColumn"]{
      width: calc(50% - 6px) !important;
      flex: 1 1 calc(50% - 6px) !important;
      min-width: calc(50% - 6px) !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(5)) > div[data-testid="column"]:nth-child(5),
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"]:nth-child(5)) > div[data-testid="stColumn"]:nth-child(5){
      width: 100% !important;
      flex: 1 1 100% !important;
      min-width: 100% !important;
    }

    /* ---------- HERO ---------- */
    .dp-hero{
      padding: 20px 18px !important;
      border-radius: 18px !important;
    }
    .dp-hero-row{
      flex-direction: column !important;
      align-items: flex-start !important;
      gap: 16px !important;
    }
    .dp-hero-logo{
      align-self: center;
    }
    .dp-hero-logo img{
      height: 100px !important;
    }
    .dp-hero-text{
      width: 100% !important;
      min-width: 0 !important;
    }
    .dp-hero-text h1{
      font-size: 1.45rem !important;
      line-height: 1.3 !important;
      word-break: break-word;
    }
    .dp-hero-text .dp-sub{
      font-size: .85rem !important;
    }
    .dp-hero-text .dp-desc{
      font-size: .85rem !important;
      max-width: 100% !important;
      margin-top: 10px !important;
    }
    .dp-pill{
      font-size: .72rem !important;
      padding: 5px 12px !important;
      margin-bottom: 10px !important;
    }

    /* ---------- SECTION HEADERS ---------- */
    .dp-section{
      flex-wrap: wrap !important;
      margin: 18px 0 10px !important;
      row-gap: 4px;
    }
    .dp-section h3{
      font-size: 1rem !important;
    }
    .dp-section .dp-section-sub{
      font-size: .78rem !important;
      margin-left: 0 !important;
      flex-basis: 100%;
    }

    /* ---------- KPI METRIC CARDS ---------- */
    [data-testid="stMetric"]{
      padding: 14px 16px !important;
      border-radius: 14px !important;
    }
    [data-testid="stMetricLabel"] p{
      font-size: .7rem !important;
      white-space: normal !important;
    }
    [data-testid="stMetricValue"]{
      font-size: 1.3rem !important;
      white-space: normal !important;
      word-break: break-word;
    }

    /* ---------- QUICK ACTION BUTTONS ---------- */
    .stButton > button{
      padding: 14px 16px !important;
      min-height: 56px !important;
      font-size: .92rem !important;
      border-radius: 14px !important;
    }
    .dp-feature-desc{
      margin: -2px 0 16px 4px !important;
      font-size: .8rem !important;
    }

    /* ---------- CHARTS ---------- */
    .dp-glass{
      padding: 14px 14px !important;
      border-radius: 14px !important;
    }
    [data-testid="stPlotlyChart"]{
      width: 100% !important;
    }
    [data-testid="stPlotlyChart"] > div{
      width: 100% !important;
    }

    /* ---------- ACTIVITY ITEMS ---------- */
    .dp-activity{
      padding: 12px 12px !important;
      gap: 10px !important;
      border-radius: 12px !important;
    }
    .dp-activity .ic{
      width: 30px !important;
      height: 30px !important;
      border-radius: 8px !important;
    }
    .dp-activity .kind{
      font-size: .66rem !important;
    }
    .dp-activity .title{
      font-size: .88rem !important;
      word-break: break-word;
    }
    .dp-activity .meta{
      font-size: .74rem !important;
      word-break: break-word;
    }

    /* ---------- TABS (horizontally scrollable) ---------- */
    .stTabs [data-baseweb="tab-list"]{
      overflow-x: auto !important;
      flex-wrap: nowrap !important;
      -webkit-overflow-scrolling: touch;
      padding: 5px !important;
      gap: 4px !important;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar{
      height: 4px;
    }
    .stTabs [data-baseweb="tab"]{
      padding: 8px 12px !important;
      font-size: .78rem !important;
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }

    /* ---------- DATAFRAMES (horizontal scroll) ---------- */
    [data-testid="stDataFrame"]{
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch;
    }
    [data-testid="stDataFrame"] *{
      font-size: .8rem !important;
    }

    /* ---------- FOOTER ---------- */
    .dp-footer{
      flex-direction: column !important;
      align-items: flex-start !important;
      padding: 18px 18px !important;
      gap: 14px !important;
      text-align: left !important;
    }
    .dp-footer-brand{
      gap: 10px !important;
    }
    .dp-footer-brand img{
      height: 28px !important;
    }
    .dp-footer .meta{
      text-align: left !important;
      font-size: .74rem !important;
    }

    /* ---------- ALERTS / INFO BOXES ---------- */
    .stAlert{
      padding: 12px !important;
      font-size: .85rem !important;
    }

    /* ---------- FLOATING ORBS (prevent any overflow contribution) ---------- */
    .stApp::before, .stApp::after{
      width: 320px !important;
      height: 320px !important;
    }

    /* ---------- RESTORE SIDEBAR REOPEN TOGGLE (hidden by header{visibility:hidden}) ---------- */
    header[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"],
    header[data-testid="stHeader"] [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"]{
      visibility: visible !important;
      opacity: 1 !important;
      display: flex !important;
      pointer-events: auto !important;
      z-index: 999999 !important;
      position: fixed !important;
      top: 12px !important;
      left: 12px !important;
    }
    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="collapsedControl"] *{
      visibility: visible !important;
      pointer-events: auto !important;
    }
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button{
      background: rgba(15,22,40,0.7) !important;
      border: 1px solid var(--dp-border-strong) !important;
      border-radius: 10px !important;
      backdrop-filter: blur(12px) !important;
    }
    }
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
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────
logo_b64_ = _logo_b64_()
logo_html = f'<div class="dp-hero-logo"><img src="data:image/png;base64,{logo_b64_}"/></div>' if logo_b64_ else ""

st.markdown(
    f"""
    <div class="dp-hero">
      <div class="dp-hero-row">
        {logo_html}
        <div class="dp-hero-text" style="flex:1; min-width:280px;">
          <div class="dp-pill"><span class="dot"></span> AI Career Copilot · Live Session</div>
          <h1>Welcome back, {st.session_state['username']}</h1>
          <div class="dp-sub">Your AI Career Command Center</div>
          <div class="dp-desc">Track your growth, analyze opportunities, optimize your resume, and accelerate your data career with AI-powered intelligence.</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if latest_resume:
    st.markdown(
        f'<div style="color:#8A95B2; font-size:.85rem; margin:14px 4px 0;">Latest resume in your library: '
        f'<span style="color:#9FD0FF;">{latest_resume.resume_name}</span> · uploaded {_format_ts(getattr(latest_resume, "uploaded_at", None))}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# SECTION: PERFORMANCE METRICS
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dp-section">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
      <h3>Performance Overview</h3>
      <span class="dp-section-sub">Your latest career intelligence</span>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    ats_score = f"{latest_analysis.ats_score:.1f}%" if latest_analysis and latest_analysis.ats_score is not None else "No history yet"
    st.metric("ATS Score", ats_score)
with col2:
    skill_match = f"{latest_analysis.match_score:.1f}%" if latest_analysis and latest_analysis.match_score is not None else "No history yet"
    st.metric("Skill Match", skill_match)
with col3:
    expected_salary = _format_lpa(latest_prediction.predicted_salary) if latest_prediction else "No history yet"
    st.metric("Expected Salary", expected_salary)

st.write("")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Resumes", snapshot.get("counts", {}).get("resumes", 0))
with col2: st.metric("Analyses", snapshot.get("counts", {}).get("analyses", 0))
with col3: st.metric("Salary Predictions", snapshot.get("counts", {}).get("predictions", 0))
with col4: st.metric("AI Chats", snapshot.get("counts", {}).get("chats", 0))
with col5: st.metric("Job Fit Records", snapshot.get("counts", {}).get("job_fit_history", 0))


# ─────────────────────────────────────────────────────────────
# SECTION: QUICK ACTIONS (feature cards)
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dp-section" style="margin-top:34px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>
      <h3>Quick Actions</h3>
      <span class="dp-section-sub">Launch any AI workflow in one click</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Row 1
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Resume Analyzer", use_container_width=True, key="qa_resume"):
        st.switch_page("pages/4_Resume_Analyzer.py")
    st.markdown('<div class="dp-feature-desc">Analyze ATS compatibility and recruiter readiness.</div>', unsafe_allow_html=True)
with c2:
    if st.button("Skill Gap Analysis", use_container_width=True, key="qa_skill"):
        st.switch_page("pages/5_Skill_Analysis.py")
    st.markdown('<div class="dp-feature-desc">Identify missing skills and learning priorities.</div>', unsafe_allow_html=True)
with c3:
    if st.button("Salary Predictor", use_container_width=True, key="qa_salary"):
        st.switch_page("pages/6_salary_predictor.py")
    st.markdown('<div class="dp-feature-desc">Estimate your market value with AI precision.</div>', unsafe_allow_html=True)

# Row 2
c4, c5, c6 = st.columns(3)
with c4:
    if st.button("AI Career Mentor", use_container_width=True, key="qa_mentor"):
        st.switch_page("pages/7_AI_mentor.py")
    st.markdown('<div class="dp-feature-desc">Get personalized career guidance, on demand.</div>', unsafe_allow_html=True)
with c5:
    if st.button("Job Fit Predictor", use_container_width=True, key="qa_jobfit"):
        st.switch_page("pages/8_Job_Fit_predictor.py")
    st.markdown('<div class="dp-feature-desc">Find your strongest matching roles instantly.</div>', unsafe_allow_html=True)
with c6:
    if st.button("Market Intelligence", use_container_width=True, key="qa_market"):
        st.switch_page("pages/9_Market_Insights.py")
    st.markdown('<div class="dp-feature-desc">Track live salary and skill trends in the market.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SECTION: ANALYTICS CHARTS (side by side)
# ─────────────────────────────────────────────────────────────
analysis_trend = pd.DataFrame(snapshot.get("analysis_trend", []))
salary_trend = pd.DataFrame(snapshot.get("salary_trend", []))

st.markdown(
    """
    <div class="dp-section" style="margin-top:34px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><polyline points="7 14 12 9 16 13 21 8"/></svg>
      <h3>Analytics</h3>
      <span class="dp-section-sub">Trends across your career signals</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def _plot_line(df, x, ys, names, title):
    fig = go.Figure()
    palette = [("#3FD1FF", "rgba(63,209,255,0.18)"), ("#2D7BFF", "rgba(45,123,255,0.18)")]
    for i, y in enumerate(ys):
        color, fill = palette[i % 2]
        fig.add_trace(go.Scatter(
            x=df[x], y=df[y], mode="lines+markers", name=names[i],
            line=dict(color=color, width=3, shape="spline", smoothing=1.1),
            marker=dict(size=7, color=color, line=dict(color="#06080F", width=2)),
            fill="tozeroy", fillcolor=fill, hovertemplate=f"<b>{names[i]}</b><br>%{{x}}<br>%{{y}}<extra></extra>",
        ))
    fig.update_layout(
        title=dict(text=title, font=dict(family="Space Grotesk", size=15, color="#EAF0FF"), x=0.01, y=0.96),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#8A95B2", size=12),
        margin=dict(l=10, r=10, t=40, b=10), height=300,
        hoverlabel=dict(bgcolor="#0A0F1F", bordercolor="#3FD1FF", font=dict(color="#EAF0FF")),
        xaxis=dict(showgrid=False, showline=False, zeroline=False),
        yaxis=dict(gridcolor="rgba(120,160,255,0.08)", zeroline=False),
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(color="#8A95B2")),
    )
    return fig


chart_l, chart_r = st.columns(2)
with chart_l:
    st.markdown('<div class="dp-glass">', unsafe_allow_html=True)
    if not analysis_trend.empty:
        st.plotly_chart(
            _plot_line(analysis_trend, "date", ["ats_score", "match_score"], ["ATS Score", "Skill Match"], "ATS Trend"),
            use_container_width=True, config={"displayModeBar": False},
        )
    else:
        st.markdown('<div style="color:#8A95B2; padding:24px 8px;">ATS Trend will appear after your first resume analysis.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chart_r:
    st.markdown('<div class="dp-glass">', unsafe_allow_html=True)
    if not salary_trend.empty:
        st.plotly_chart(
            _plot_line(salary_trend, "date", ["salary_lpa"], ["Predicted Salary (LPA)"], "Salary Trend"),
            use_container_width=True, config={"displayModeBar": False},
        )
    else:
        st.markdown('<div style="color:#8A95B2; padding:24px 8px;">Salary Trend will appear after your first prediction.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SECTION: RECENT ACTIVITY
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dp-section" style="margin-top:34px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      <h3>Recent Activity</h3>
      <span class="dp-section-sub">Your latest movements on DataPilot AI</span>
    </div>
    """,
    unsafe_allow_html=True,
)

ACTIVITY_ICONS = {
    "Resume Analysis": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/></svg>',
    "Salary Prediction": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "AI Mentor Chat": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "Job Fit Analysis": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/></svg>',
}
DEFAULT_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/></svg>'

activity_items = snapshot.get("activity_items", [])
show_all_history = st.session_state["show_full_history"]
visible_activity_items = activity_items if show_all_history else activity_items[:5]

if visible_activity_items:
    for item in visible_activity_items:
        icon = ACTIVITY_ICONS.get(item.get("kind"), DEFAULT_ICON)
        st.markdown(
            f"""
            <div class="dp-activity">
              <div class="ic">{icon}</div>
              <div class="body">
                <div class="kind">{item['kind']}</div>
                <div class="title">{item['title']}</div>
                <div class="meta">{item['detail']} · {_format_ts(item['timestamp'])}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No history has been saved yet. Analyze a resume, predict a salary, or start a mentor chat to populate this dashboard.")

if st.button("Show all history" if not show_all_history else "Show latest 5", use_container_width=False, key="toggle_history"):
    st.session_state["show_full_history"] = not show_all_history
    st.rerun()


# ─────────────────────────────────────────────────────────────
# SECTION: HISTORY TABS
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dp-section" style="margin-top:34px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      <h3>History</h3>
      <span class="dp-section-sub">Full archive of your DataPilot activity</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def _render_history_table(rows, empty_message):
    if not rows:
        st.info(empty_message)
        return
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


history_tabs = st.tabs(["Resume Analyses", "Salary Predictions", "Resume Library", "AI Chats", "Job Fit History"])

with history_tabs[0]:
    analysis_rows = [
        {
            "Role": analysis.target_role,
            "ATS Score": f"{analysis.ats_score:.1f}%" if analysis.ats_score is not None else "N/A",
            "Skill Match": f"{analysis.match_score:.1f}%" if analysis.match_score is not None else "N/A",
            "Analyzed At": _format_ts(getattr(analysis, "analysis_date", None)),
        }
        for analysis in snapshot.get("analyses", [])
    ]
    _render_history_table(analysis_rows, "No analysis history yet. Run the Resume Analyzer to save real results here.")

with history_tabs[1]:
    prediction_rows = [
        {
            "Role": prediction.role,
            "Experience": prediction.experience,
            "Location": prediction.location,
            "Predicted Salary": f"₹{prediction.predicted_salary / 100000:.1f} LPA" if prediction.predicted_salary is not None else "N/A",
            "Predicted At": _format_ts(getattr(prediction, "prediction_date", None)),
        }
        for prediction in snapshot.get("predictions", [])
    ]
    _render_history_table(prediction_rows, "No salary prediction history yet. Use Salary Predictor to save real market estimates here.")

with history_tabs[2]:
    resume_rows = [
        {"Resume": resume.resume_name, "Uploaded At": _format_ts(getattr(resume, "uploaded_at", None))}
        for resume in snapshot.get("resumes", [])
    ]
    _render_history_table(resume_rows, "No resume uploads have been saved yet.")

with history_tabs[3]:
    chat_rows = [
        {"Conversation": chat.title, "Updated At": _format_ts(getattr(chat, "updated_at", None))}
        for chat in snapshot.get("chat_sessions", [])
    ]
    _render_history_table(chat_rows, "No AI Mentor chats have been saved yet.")

with history_tabs[4]:
    job_fit_rows = [
        {
            "Best Role": history.best_role,
            "Best Fit": f"{history.best_score:.2f}%" if history.best_score is not None else "N/A",
            "Missing Skills": history.missing_skills or "N/A",
            "Saved At": _format_ts(getattr(history, "created_at", None)),
        }
        for history in snapshot.get("job_fit_histories", [])
    ]
    _render_history_table(job_fit_rows, "No job fit history yet. Analyze a resume to save job fit results here.")


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
logo_b64 = _logo_b64()
footer_logo = f'<img src="data:image/png;base64,{logo_b64}"/>' if logo_b64 else ""
st.markdown(
    f"""
    <div class="dp-footer">
      <div class="dp-footer-brand">
        {footer_logo}
        <div>
          <div class="name">DataPilot AI</div>
          <div class="tag">Navigate Your Data Career.</div>
        </div>
      </div>
      <div class="meta">
        Version 1.0.0 · © 2026 DataPilot AI · All rights reserved.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
