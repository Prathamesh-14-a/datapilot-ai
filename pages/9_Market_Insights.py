import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64
from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated
from src.config.paths import ASSETS_DIR, DATA_DIR


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Market Insights · DataPilot AI",
    page_icon=str(ASSETS_DIR / "mini_logo.png"),
    layout="wide"
)

# streamlit interaction config
config = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": False,
    "staticPlot": True
}

# --------------------------------------------------
# AUTH
# --------------------------------------------------
if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

# --------------------------------------------------
# PREMIUM CSS / DESIGN SYSTEM
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --dp-bg-0: #020617;
  --dp-bg-1: #07112A;
  --dp-bg-2: #08142F;
  --dp-cyan: #00C8FF;
  --dp-cyan-2: #00D9FF;
  --dp-sky: #38BDF8;
  --dp-blue: #0EA5E9;
  --dp-indigo: #2563EB;
  --dp-blue-soft: #60A5FA;
  --dp-text: #E2E8F0;
  --dp-text-dim: #94A3B8;
  --dp-border: rgba(56,189,248,0.18);
  --dp-glow: 0 0 40px rgba(0,200,255,0.25);
}

html, body, [class*="css"], .stApp, .main, .block-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: var(--dp-text) !important;
}

.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(0,200,255,0.18), transparent 60%),
    radial-gradient(900px 500px at 100% 0%, rgba(37,99,235,0.18), transparent 60%),
    radial-gradient(1000px 600px at 50% 110%, rgba(14,165,233,0.12), transparent 60%),
    linear-gradient(180deg, #020617 0%, #07112A 50%, #08142F 100%) !important;
  background-attachment: fixed !important;
}

/* Animated gradient mesh overlay */
.stApp::before {
  content: "";
  position: fixed; inset: 0;
  background:
    radial-gradient(600px 300px at 20% 30%, rgba(0,217,255,0.10), transparent 70%),
    radial-gradient(700px 400px at 80% 70%, rgba(37,99,235,0.10), transparent 70%);
  animation: meshShift 18s ease-in-out infinite alternate;
  pointer-events: none; z-index: 0;
}
@keyframes meshShift {
  0%   { transform: translate3d(0,0,0) scale(1); opacity: .9; }
  100% { transform: translate3d(-30px,20px,0) scale(1.05); opacity: 1; }
}

/* Grid overlay + noise */
.stApp::after {
  content: "";
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(56,189,248,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56,189,248,0.05) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 80%);
  pointer-events: none; z-index: 0;
}

.block-container { padding-top: 1.5rem !important; max-width: 1400px; position: relative; z-index: 1; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stStatusWidget"] {
    display: none !important;
}

/* ---------- HERO ---------- */
.dp-hero {
  position: relative;
  border-radius: 28px;
  padding: 48px 56px;
  background: linear-gradient(135deg, rgba(8,20,47,0.85) 0%, rgba(7,17,42,0.7) 100%);
  border: 1px solid var(--dp-border);
  box-shadow: 0 30px 80px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
  backdrop-filter: blur(20px);
  overflow: hidden;
  margin-bottom: 32px;
}
.dp-hero::before {
  content:""; position:absolute; inset:-1px;
  background: linear-gradient(135deg, rgba(0,200,255,0.6), transparent 40%, rgba(37,99,235,0.5));
  border-radius: 28px; padding:1px;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events:none; opacity:.5;
}
.dp-hero-grid { display:grid; grid-template-columns: 1.2fr 1fr; gap: 40px; align-items:center; }
@media (max-width: 980px){ .dp-hero-grid { grid-template-columns: 1fr; } }

.dp-badge {
  display:inline-flex; align-items:center; gap:10px;
  padding: 8px 16px; border-radius: 999px;
  background: rgba(0,200,255,0.08);
  border: 1px solid rgba(0,200,255,0.35);
  font-size: 12px; letter-spacing: 0.18em; font-weight: 600;
  color: var(--dp-cyan-2); text-transform: uppercase;
}
.dp-badge .dot {
  width:8px; height:8px; border-radius:50%; background: var(--dp-cyan);
  box-shadow: 0 0 12px var(--dp-cyan);
  animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.4)} }

.dp-h1 {
  font-size: clamp(36px, 4.4vw, 58px);
  line-height: 1.05; font-weight: 800; letter-spacing: -0.03em;
  margin: 18px 0 14px;
  background: linear-gradient(180deg, #ffffff 0%, #cfe7ff 70%, #7cc8ff 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.dp-sub { color: var(--dp-text-dim); font-size: 16px; line-height: 1.7; max-width: 620px; }

.dp-pills { display:flex; flex-wrap:wrap; gap:8px; margin-top: 22px; }
.dp-pill {
  display:inline-flex; align-items:center; gap:8px;
  padding:7px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 500;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(56,189,248,0.18);
  color: #cbd5e1;
}
.dp-pill::before{content:"◆"; color: var(--dp-cyan); font-size: 9px;}

.dp-cta {
  display:inline-flex; align-items:center; gap:10px;
  margin-top: 28px; padding: 14px 24px; border-radius: 14px;
  background: linear-gradient(135deg, #00C8FF 0%, #2563EB 100%);
  color: #001229 !important; font-weight: 700; font-size: 14px; letter-spacing: .02em;
  border: 1px solid rgba(0,217,255,0.6);
  box-shadow: 0 10px 30px rgba(0,200,255,0.35), inset 0 1px 0 rgba(255,255,255,0.4);
  text-decoration:none !important; cursor: pointer;
  transition: transform .2s ease, box-shadow .2s ease;
}
.dp-cta:hover { transform: translateY(-2px); box-shadow: 0 18px 50px rgba(0,200,255,0.55); }

/* Typewriter */
.dp-type-wrap {
  margin-top: 22px; font-family: 'JetBrains Mono', monospace;
  font-size: 15px; color: var(--dp-text-dim);
}
.dp-type-prefix { color: #cbd5e1; margin-right: 8px; }
.dp-type {
  display:inline-block; min-width: 220px;
  color: var(--dp-cyan-2); font-weight: 600;
  border-right: 2px solid var(--dp-cyan);
  overflow: hidden; white-space: nowrap; vertical-align: bottom;
  animation: roles 24s steps(1,end) infinite, blink .9s step-end infinite;
}
@keyframes blink { 50% { border-color: transparent; } }
@keyframes roles {
  0%,11%   { content: "Data Analysts"; }
  12%,22%  { content: "Data Scientists"; }
  23%,33%  { content: "Data Engineers"; }
  34%,44%  { content: "ML Engineers"; }
  45%,55%  { content: "BI Analysts"; }
  56%,66%  { content: "Analytics Engineers"; }
  67%,77%  { content: "Business Analysts"; }
  78%,88%  { content: "Prompt Engineers"; }
  89%,100% { content: "AI Engineers"; }
}
.dp-type::after {
  content: "Data Analysts";
  animation: rolesText 24s steps(1,end) infinite;
}
@keyframes rolesText {
  0%,11%   { content: "Data Analysts"; }
  12%,22%  { content: "Data Scientists"; }
  23%,33%  { content: "Data Engineers"; }
  34%,44%  { content: "ML Engineers"; }
  45%,55%  { content: "BI Analysts"; }
  56%,66%  { content: "Analytics Engineers"; }
  67%,77%  { content: "Business Analysts"; }
  78%,88%  { content: "Prompt Engineers"; }
  89%,100% { content: "AI Engineers"; }
}

/* ---------- SECTION TITLES ---------- */
.dp-section {
  display:flex; align-items:center; gap:14px; margin: 36px 0 18px;
}
.dp-section-bar { width:4px; height:26px; border-radius: 4px;
  background: linear-gradient(180deg, var(--dp-cyan), var(--dp-indigo));
  box-shadow: 0 0 16px var(--dp-cyan);
}
.dp-section h2 { font-size: 22px; font-weight: 700; margin: 0; letter-spacing: -0.01em; color:#fff; }
.dp-section .hint { color: var(--dp-text-dim); font-size: 13px; margin-left: 10px; }

/* ---------- GLASS CARDS ---------- */
.dp-card {
  position: relative;
  background: linear-gradient(180deg, rgba(8,20,47,0.7), rgba(7,17,42,0.55));
  border: 1px solid var(--dp-border);
  border-radius: 18px; padding: 22px;
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03);
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
  overflow: hidden;
}
.dp-card:hover {
  transform: translateY(-3px);
  border-color: rgba(0,200,255,0.45);
  box-shadow: 0 18px 60px rgba(0,200,255,0.22);
}

/* KPI */
.dp-kpi-grid { display:grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
@media (max-width: 1100px){ .dp-kpi-grid { grid-template-columns: repeat(2,1fr); } }
.dp-kpi { padding: 22px 22px 20px; }
.dp-kpi .label {
  font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--dp-text-dim); font-weight: 600;
}
.dp-kpi .value {
  margin-top: 12px; font-size: 30px; font-weight: 800; color: #fff;
  letter-spacing: -0.02em;
  background: linear-gradient(180deg,#fff,#9fd8ff);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.dp-kpi .meta { margin-top: 8px; font-size: 12px; color: var(--dp-text-dim); display:flex; align-items:center; gap:6px;}
.dp-kpi .meta .up { color: var(--dp-cyan-2); font-weight:600; }
.dp-kpi .icon {
  position:absolute; top:18px; right:18px; width:36px; height:36px;
  display:flex; align-items:center; justify-content:center; border-radius: 10px;
  background: rgba(0,200,255,0.10); border: 1px solid rgba(0,200,255,0.25);
  color: var(--dp-cyan-2);
}

/* Filter cards */
.dp-filter-label { font-size: 11px; letter-spacing: 0.18em; color: var(--dp-cyan-2); font-weight: 700; text-transform: uppercase;}
.dp-filter-value { font-size: 20px; font-weight: 700; color: #fff; margin-top: 6px;}
.dp-filter-sub { font-size: 12px; color: var(--dp-text-dim); margin-top: 4px;}

/* Streamlit input restyling */
.stSelectbox [data-baseweb="select"] > div {
  background: rgba(8,20,47,0.7) !important;
  border: 1px solid var(--dp-border) !important;
  border-radius: 12px !important;
  color: #fff !important;
  min-height: 48px;
}
.stSelectbox [data-baseweb="select"]:hover > div { border-color: rgba(0,200,255,0.5) !important; }
label, .stSelectbox label { color: var(--dp-text-dim) !important; font-weight: 600 !important; font-size: 12px !important; letter-spacing: 0.1em; text-transform: uppercase; }

/* Opportunity cards */
.dp-opp {
  display:grid; grid-template-columns: 1fr; gap: 12px;
}
.dp-opp-card {
  display:grid; grid-template-columns: 56px 1fr auto; gap: 18px; align-items:center;
  padding: 18px 22px; border-radius: 16px;
  background: linear-gradient(135deg, rgba(0,200,255,0.07), rgba(37,99,235,0.05));
  border: 1px solid rgba(56,189,248,0.22);
  transition: all .25s ease;
}
.dp-opp-card:hover { border-color: rgba(0,217,255,0.55); transform: translateX(4px); box-shadow: 0 10px 40px rgba(0,200,255,0.18);}
.dp-opp-rank {
  width:48px; height:48px; border-radius: 12px; display:flex; align-items:center; justify-content:center;
  background: linear-gradient(135deg, #00C8FF, #2563EB); color: #001229; font-weight: 800; font-size: 18px;
  box-shadow: 0 0 24px rgba(0,200,255,0.45);
}
.dp-opp-name { font-size: 16px; font-weight: 700; color:#fff; }
.dp-opp-meta { font-size: 12px; color: var(--dp-text-dim); margin-top: 4px; display:flex; gap: 14px; flex-wrap:wrap;}
.dp-opp-meta span b { color: var(--dp-cyan-2); font-weight: 600; }
.dp-opp-cta {
  padding: 8px 14px; border-radius: 10px; font-size: 12px; font-weight: 600;
  background: rgba(0,200,255,0.12); color: var(--dp-cyan-2);
  border: 1px solid rgba(0,200,255,0.35);
}

/* Insights side panel */
.dp-insights { padding: 22px; }
.dp-insights h3 { font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--dp-cyan-2); margin: 0 0 16px; font-weight:700;}
.dp-insight-row { display:flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed rgba(56,189,248,0.12); font-size: 13px;}
.dp-insight-row:last-child{border-bottom:none;}
.dp-insight-row .k { color: var(--dp-text-dim); }
.dp-insight-row .v { color:#fff; font-weight: 600; }

/* Footer */
.dp-footer {
  margin-top: 48px; padding: 28px 32px; border-radius: 20px;
  background: linear-gradient(135deg, rgba(8,20,47,0.7), rgba(7,17,42,0.5));
  border: 1px solid var(--dp-border);
  display:flex; justify-content:space-between; align-items:center; gap:20px;
  backdrop-filter: blur(14px);
}
.dp-footer .brand { display:flex; align-items:center; gap: 12px; font-weight: 800; color:#fff; letter-spacing: -0.01em;}
.dp-footer .brand .logo {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, #00C8FF, #2563EB);
  display:flex; align-items:center; justify-content:center; color: #001229; font-weight:900;
  box-shadow: 0 0 18px rgba(0,200,255,0.5);
}
.dp-footer .live { display:flex; align-items:center; gap:8px; color: var(--dp-text-dim); font-size: 12px; }
.dp-footer .live .pulse { width:8px; height:8px; border-radius:50%; background: #22ee99; box-shadow: 0 0 12px #22ee99; animation: pulse 1.8s infinite;}

.dp-footer-brand{ display:flex; align-items:center; gap:14px;}
.dp-footer-brand img{ height:36px;}
.dp-footer-brand .name{ font-family:'Space Grotesk',sans-serif; font-weight:700; color:#EAF0FF;}
.dp-footer-brand .tag{ color:var(--dp-text-dim); font-size:.8rem;}
.dp-footer .meta{ color:var(--dp-text-dim); font-size:.8rem; text-align:right;}

/* Fade in */
@keyframes fadeUp { from{opacity:0; transform: translateY(14px);} to{opacity:1; transform:none;} }
.dp-hero, .dp-card, .dp-footer, .dp-opp-card { animation: fadeUp .6s ease both; }

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
""", unsafe_allow_html=True)


_responsive_css = ASSETS_DIR / "css" / "page10_responsive.css"
if _responsive_css.exists():
    with open(_responsive_css, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA  (UNCHANGED)
# --------------------------------------------------
skill_df = pd.read_csv(DATA_DIR / "processed" / "top_skill_by_role_cleaned.csv")
location_df = pd.read_csv(DATA_DIR / "processed" / "location_distribution.csv")
salary_df = pd.read_csv(DATA_DIR / "processed" / "salary_jobs.csv")
jobs_df = pd.read_csv(DATA_DIR / "processed" / "jobs_with_skills.csv")
exp_df = pd.read_csv(DATA_DIR / "Salary Prediction Data" / "salary_final_data.csv")

# --------------------------------------------------
# HERO
# --------------------------------------------------
hero_svg = """
<svg viewBox="0 0 520 380" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00D9FF" stop-opacity="0.55"/>
      <stop offset="60%" stop-color="#2563EB" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#020617" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00C8FF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#00D9FF" stop-opacity="1"/>
      <stop offset="100%" stop-color="#2563EB" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#00C8FF" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#00C8FF" stop-opacity="0"/>
    </linearGradient>
    <filter id="f"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>

  <circle cx="260" cy="190" r="180" fill="url(#glow)"/>

  <!-- grid -->
  <g stroke="#1e3a5f" stroke-width="0.6" opacity="0.5">
    <path d="M0 60 H520 M0 120 H520 M0 180 H520 M0 240 H520 M0 300 H520"/>
    <path d="M60 0 V380 M140 0 V380 M220 0 V380 M300 0 V380 M380 0 V380 M460 0 V380"/>
  </g>

  <!-- area + line -->
  <path d="M20 280 C 80 260, 130 240, 180 220 S 290 160, 350 130 S 460 80, 500 60 L500 340 L20 340 Z" fill="url(#area)"/>
  <path d="M20 280 C 80 260, 130 240, 180 220 S 290 160, 350 130 S 460 80, 500 60"
        fill="none" stroke="url(#line)" stroke-width="2.5">
    <animate attributeName="stroke-dasharray" from="0,1200" to="1200,0" dur="3.5s" repeatCount="indefinite"/>
  </path>

  <!-- nodes -->
  <g fill="#00D9FF">
    <circle cx="180" cy="220" r="4"><animate attributeName="r" values="3;6;3" dur="2s" repeatCount="indefinite"/></circle>
    <circle cx="280" cy="180" r="4"><animate attributeName="r" values="3;6;3" dur="2.4s" repeatCount="indefinite"/></circle>
    <circle cx="380" cy="110" r="5"><animate attributeName="r" values="4;7;4" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="460" cy="80"  r="4"><animate attributeName="r" values="3;6;3" dur="2.8s" repeatCount="indefinite"/></circle>
  </g>

  <!-- center pulse -->
  <g transform="translate(260,190)">
    <circle r="10" fill="#00D9FF" opacity="0.9"/>
    <circle r="18" fill="none" stroke="#00D9FF" stroke-width="1.5" opacity="0.7">
      <animate attributeName="r" values="14;42;14" dur="2.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;0;0.7" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <circle r="28" fill="none" stroke="#2563EB" stroke-width="1" opacity="0.5">
      <animate attributeName="r" values="20;60;20" dur="3.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0;0.5" dur="3.2s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- connections -->
  <g stroke="#38BDF8" stroke-width="0.8" opacity="0.6">
    <line x1="260" y1="190" x2="120" y2="90"/>
    <line x1="260" y1="190" x2="430" y2="60"/>
    <line x1="260" y1="190" x2="450" y2="290"/>
    <line x1="260" y1="190" x2="90"  y2="290"/>
  </g>
  <g fill="#60A5FA">
    <circle cx="120" cy="90" r="3"/>
    <circle cx="430" cy="60" r="3"/>
    <circle cx="450" cy="290" r="3"/>
    <circle cx="90"  cy="290" r="3"/>
  </g>

  <!-- floating particles -->
  <g fill="#00D9FF" opacity="0.8">
    <circle cx="60" cy="50" r="1.6"><animate attributeName="cy" values="50;30;50" dur="5s" repeatCount="indefinite"/></circle>
    <circle cx="490" cy="200" r="1.6"><animate attributeName="cy" values="200;180;200" dur="6s" repeatCount="indefinite"/></circle>
    <circle cx="40" cy="320" r="1.4"><animate attributeName="cy" values="320;300;320" dur="4.5s" repeatCount="indefinite"/></circle>
  </g>
</svg>
"""

st.markdown(f"""
<div class="dp-hero">
  <div class="dp-hero-grid">
    <div>
      <div class="dp-badge"><span class="dot"></span> Market Intelligence Engine</div>
      <h1 class="dp-h1">Understand Data Career<br/>Market Trends In Real Time</h1>
      <p class="dp-sub">Track salaries, hiring demand, skill trends, location intelligence, and emerging opportunities across the modern data ecosystem.</p>
      <div class="dp-type-wrap">
        <span class="dp-type-prefix">// Market Intelligence For</span><span class="dp-type"></span>
      </div>
      <div class="dp-pills">
        <span class="dp-pill">Market Intelligence</span>
        <span class="dp-pill">Salary Analytics</span>
        <span class="dp-pill">Hiring Trends</span>
        <span class="dp-pill">Skill Demand</span>
        <span class="dp-pill">Career Forecasting</span>
      </div>
      <a class="dp-cta" href="#analyze">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-6"/></svg>
        Analyze Market Demand
      </a>
    </div>
    <div>{hero_svg}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.markdown("""
<div id="analyze" class="dp-section">
  <div class="dp-section-bar"></div>
  <h2>Configure Intelligence</h2>
  <span class="hint">Select target role and market</span>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    selected_role = st.selectbox(
        "Target Role",
        sorted(exp_df["Standardized_Job_Title"].unique()) ,
        index = 2
    )
with c2:
    selected_location = st.selectbox(
        "Target Location",
        ["All"] + sorted(location_df["Location"].unique().tolist())
    )

# --------------------------------------------------
# FILTER DATA  (UNCHANGED LOGIC)
# --------------------------------------------------
skill_filtered = skill_df[skill_df["Standardized_Job_Title"] == selected_role]
salary_filtered = salary_df[salary_df["Standardized_Job_Title"] == selected_role]
job_filtered = jobs_df[jobs_df["Standardized_Job_Title"] == selected_role]

if selected_location == "All":
    exp_filtered = exp_df[exp_df["Standardized_Job_Title"] == selected_role]
else:
    exp_filtered = exp_df[
        (exp_df["Standardized_Job_Title"] == selected_role)
        & (exp_df["Location"] == selected_location)
    ]

if selected_location != "All":
    location_filtered = exp_df[exp_df["Location"] == selected_location]
else:
    location_filtered = location_df

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.markdown("""
<div class="dp-section">
  <div class="dp-section-bar"></div>
  <h2>Market Overview</h2>
  <span class="hint">Live performance signals</span>
</div>
""", unsafe_allow_html=True)

avg_salary = exp_filtered["salary_avg"].mean() if not salary_filtered.empty else 0
max_salary = exp_filtered["salary_avg"].max() if not exp_filtered.empty else 0
if not skill_filtered.empty:
    top_skill = skill_filtered.sort_values("Count", ascending=False).iloc[0]["Skill"]
    demand_score = min(100, int(skill_filtered["Count"].sum() / 10))
else:
    top_skill = "N/A"
    demand_score = 0
competition_index = min(100, int(len(job_filtered) / 5)) if not job_filtered.empty else 0

def kpi_icon(name):
    icons = {
        "salary": '<path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        "peak":   '<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
        "skill":  '<path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"/>',
        "demand": '<path d="M3 12h4l3-9 4 18 3-9h4"/>',
        "comp":   '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'
    }
    return f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icons[name]}</svg>'

st.markdown(f"""
<div class="dp-kpi-grid">
  <div class="dp-card dp-kpi">
    <div class="icon">{kpi_icon("salary")}</div>
    <div class="label">Average Salary</div>
    <div class="value">₹ {avg_salary:,.0f}</div>
    <div class="meta"><span class="up">▲ Market avg</span> · {selected_role}</div>
  </div>
  <div class="dp-card dp-kpi">
    <div class="icon">{kpi_icon("peak")}</div>
    <div class="label">Highest Salary</div>
    <div class="value">₹ {max_salary:,.0f}</div>
    <div class="meta"><span class="up">▲ Top quartile</span> · ceiling</div>
  </div>
  <div class="dp-card dp-kpi">
    <div class="icon">{kpi_icon("skill")}</div>
    <div class="label">Top Skill</div>
    <div class="value" style="font-size:24px">{top_skill}</div>
    <div class="meta"><span class="up">▲ High demand</span> · trending</div>
  </div>
  <div class="dp-card dp-kpi">
    <div class="icon">{kpi_icon("demand")}</div>
    <div class="label">Demand Score</div>
    <div class="value">{demand_score}<span style="font-size:18px;color:var(--dp-text-dim)">/100</span></div>
    <div class="meta"><span class="up">▲ Hiring momentum</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Live trend mini-svg + competition
mini_trend = """
<svg viewBox="0 0 600 120" width="100%" height="120" preserveAspectRatio="none">
  <defs>
    <linearGradient id="mt" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#00D9FF" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#00D9FF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M0 90 L60 80 L120 85 L180 70 L240 75 L300 55 L360 60 L420 40 L480 45 L540 25 L600 20 L600 120 L0 120 Z" fill="url(#mt)"/>
  <path d="M0 90 L60 80 L120 85 L180 70 L240 75 L300 55 L360 60 L420 40 L480 45 L540 25 L600 20" stroke="#00D9FF" stroke-width="2.2" fill="none"/>
  <g fill="#00D9FF"><circle cx="300" cy="55" r="3"/><circle cx="420" cy="40" r="3"/><circle cx="540" cy="25" r="3"/><circle cx="600" cy="20" r="4"><animate attributeName="r" values="3;6;3" dur="1.8s" repeatCount="indefinite"/></circle></g>
</svg>
"""

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
lc, rc = st.columns([2,1])
with lc:
    st.markdown(f"""
        <div class="dp-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
            <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:var(--dp-text-dim);font-weight:600">
                Market Trajectory
            </div>
            <div style="font-size:18px;font-weight:700;color:#fff;margin-top:4px">
                Demand Index — {selected_role}
            </div>
            </div>
        </div>

        {mini_trend}
       
        """, unsafe_allow_html=True)
with rc:
    st.markdown(f"""
    <div class="dp-card" style="height:100%">
      <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:var(--dp-text-dim);font-weight:600">Hiring Competition Index</div>
      <div style="font-size:42px;font-weight:800;color:#fff;margin-top:8px;background:linear-gradient(180deg,#fff,#9fd8ff);-webkit-background-clip:text;background-clip:text;color:transparent">{competition_index}</div>
      <div style="height:8px;background:rgba(255,255,255,0.06);border-radius:99px;margin-top:14px;overflow:hidden">
        <div style="height:100%;width:{competition_index}%;background:linear-gradient(90deg,#00C8FF,#2563EB);box-shadow:0 0 12px #00C8FF"></div>
      </div>
      <div style="margin-top:10px;font-size:12px;color:var(--dp-text-dim)">Based on {len(job_filtered)} active postings</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# PLOTLY THEME  
# --------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis=dict(gridcolor="rgba(56,189,248,0.08)", zerolinecolor="rgba(56,189,248,0.1)", linecolor="rgba(56,189,248,0.2)"),
    yaxis=dict(gridcolor="rgba(56,189,248,0.08)", zerolinecolor="rgba(56,189,248,0.1)", linecolor="rgba(56,189,248,0.2)"),
    hoverlabel=dict(bgcolor="#07112A", bordercolor="#00C8FF", font=dict(color="#fff", family="Inter")),
)
CYAN_SEQ = ["#00D9FF","#38BDF8","#0EA5E9","#60A5FA","#2563EB","#1E40AF","#0891B2","#0369A1","#075985","#1e3a8a"]

# --------------------------------------------------
# CHARTS GRID
# --------------------------------------------------
st.markdown("""
<div class="dp-section">
  <div class="dp-section-bar"></div>
  <h2>Advanced Analytics</h2>
  <span class="hint">Skill demand, salary, location intelligence</span>
</div>
""", unsafe_allow_html=True)

g1, g2 = st.columns(2)

with g1:
    st.markdown(f'''<div class="dp-card"> 
    <div style="font-size:11px;letter-spacing:0.18em;
                text-transform:uppercase;
                color:var(--dp-cyan-2);font-weight:700;margin-bottom:6px">
                Top Skills
    </div>
    <div style="font-size:18px;
                font-weight:700;
                color:#fff;margin-bottom:10px">
                Ranked Demand · {selected_role}
    </div>
    </div>''', unsafe_allow_html=True)
    
    top_skills_data = skill_filtered.sort_values("Count", ascending=True).tail(15)
    fig = px.bar(
        top_skills_data, x="Count", y="Skill", orientation="h",
        color="Count", color_continuous_scale=[[0,"#0EA5E9"],[1,"#00D9FF"]]
    )
    fig.update_traces(marker_line_width=0, hovertemplate="<b>%{y}</b><br>Demand: %{x}<extra></extra>")
    fig.update_layout(**PLOTLY_LAYOUT, height=460, coloraxis_showscale=False, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config = config )
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown(f'''<div class="dp-card">
    <div style="font-size:11px;
                letter-spacing:0.18em;text-transform:uppercase;
                color:var(--dp-cyan-2);font-weight:700;margin-bottom:6px">
                Salary Growth
    </div>
    <div style="font-size:18px;font-weight:700;
                color:#fff;margin-bottom:10px">
                Progression by Experience
        </div>
        </div>''', unsafe_allow_html=True)

    exp_filtered["Exp_Group"] = pd.cut(
        exp_filtered["Experience_Years"],
        bins=[0,2,5,8,12,20],
        labels=["0-2","2-5","5-8","8-12","12+"]
    )
    salary_chart = exp_filtered.groupby("Exp_Group")["salary_avg"].median().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=salary_chart["Exp_Group"].astype(str), y=salary_chart["salary_avg"],
        mode="lines+markers", line=dict(color="#00D9FF", width=3, shape="spline"),
        marker=dict(size=10, color="#00D9FF", line=dict(color="#fff", width=2)),
        fill="tozeroy", fillcolor="rgba(0,217,255,0.18)",
        hovertemplate="<b>%{x} yrs</b><br>₹ %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=460, showlegend=False,
                      xaxis_title="Experience", yaxis_title="Median Salary (₹)")
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

# Radar + Distribution
g3, g4 = st.columns(2)
with g3:
    st.markdown(f'''<div class="dp-card">
    <div style="font-size:11px;letter-spacing:0.18em;
                text-transform:uppercase;color:var(--dp-cyan-2);
                font-weight:700;margin-bottom:6px">
                Skill Radar
    </div>
                <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:10px">
                Top 6 Skill Demand Profile
    </div>
                </div>''', unsafe_allow_html=True)
    radar = skill_filtered.sort_values("Count", ascending=False).head(6)
    fig = go.Figure()
    if not radar.empty:
        fig.add_trace(go.Scatterpolar(
            r=radar["Count"].tolist() + [radar["Count"].iloc[0]],
            theta=radar["Skill"].tolist() + [radar["Skill"].iloc[0]],
            fill="toself", line=dict(color="#00D9FF", width=2),
            fillcolor="rgba(0,200,255,0.25)", name="Demand"
        ))
    fig.update_layout(**PLOTLY_LAYOUT, height=420,
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(gridcolor="rgba(56,189,248,0.15)", color="#94A3B8"),
                   angularaxis=dict(gridcolor="rgba(56,189,248,0.15)", color="#E2E8F0")))
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

with g4:
    st.markdown(f'''<div class="dp-card"> 
                <div style="font-size:11px;letter-spacing:0.18em;
                text-transform:uppercase;color:var(--dp-cyan-2);
                font-weight:700;margin-bottom:6px">
                Salary Distribution
                </div>
            <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:10px">
                Compensation Histogram</div>
                </div>''', unsafe_allow_html=True)
    fig = px.histogram(exp_filtered, x="salary_avg", nbins=30,
                       color_discrete_sequence=["#00D9FF"])
    fig.update_traces(marker_line_color="#0EA5E9", marker_line_width=1,
                      hovertemplate="₹ %{x:,.0f}<br>%{y} roles<extra></extra>")
    fig.update_layout(**PLOTLY_LAYOUT, height=420, bargap=0.08,
                      xaxis_title="Salary (₹)", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

# Locations + Treemap
g5, g6 = st.columns(2)
with g5:
    st.markdown(f'''<div class="dp-card"> 
    <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
                color:var(--dp-cyan-2);font-weight:700;margin-bottom:6px">
                Location Intelligence</div>
        <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:10px">
                Top Hiring Markets</div>
                </div>''', unsafe_allow_html=True)
    top_locations = location_df.sort_values("count", ascending=False).head(10)
    fig = px.pie(top_locations, names="Location", values="count", hole=0.6,
                 color_discrete_sequence=CYAN_SEQ)
    fig.update_traces(textposition="outside", textinfo="label+percent",
                      marker=dict(line=dict(color="#020617", width=2)),
                      hovertemplate="<b>%{label}</b><br>%{value} roles<extra></extra>")
    fig.update_layout(**PLOTLY_LAYOUT, height=420, showlegend=False,
                      annotations=[dict(text=f"{int(top_locations['count'].sum())}<br><span style='font-size:11px;color:#94A3B8'>TOTAL ROLES</span>",
                                        x=0.5, y=0.5, font_size=22, showarrow=False, font_color="#fff")])
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

with g6:
    st.markdown(f'''<div class="dp-card">
    <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
                color:var(--dp-cyan-2);font-weight:700;margin-bottom:6px">
                Skill Treemap
                </div>
    <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:10px">
                Demand Density</div>
                </div>''', unsafe_allow_html=True)
    fig = px.treemap(skill_filtered, path=["Skill"], values="Count",
                     color="Count", color_continuous_scale=[[0,"#0c4a6e"],[0.5,"#0EA5E9"],[1,"#00D9FF"]])
    fig.update_traces(marker=dict(line=dict(color="#020617", width=2)),
                      hovertemplate="<b>%{label}</b><br>Demand: %{value}<extra></extra>",
                      textfont=dict(family="Inter", size=13, color="#fff"))
    fig.update_layout(**PLOTLY_LAYOUT, height=420, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

# Heatmap + Funnel
g7, g8 = st.columns(2)
with g7:
    st.markdown('''<div class="dp-card">
                <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
                color:var(--dp-cyan-2);font-weight:700;margin-bottom:6px">Hiring Heatmap</div>
                <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:10px">
                Role × Location Demand</div>
                </div>''', unsafe_allow_html=True)
    top_roles = exp_df["Standardized_Job_Title"].value_counts().head(8).index.tolist()
    top_locs = exp_df["Location"].value_counts().head(10).index.tolist()
    heat = exp_df[exp_df["Standardized_Job_Title"].isin(top_roles) & exp_df["Location"].isin(top_locs)]
    pivot = heat.pivot_table(index="Standardized_Job_Title", columns="Location",
                              values="salary_avg", aggfunc="count").fillna(0)
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale=[[0,"#020617"],[0.4,"#0EA5E9"],[1,"#00D9FF"]],
        hovertemplate="<b>%{y}</b> in <b>%{x}</b><br>%{z} roles<extra></extra>",
        showscale=False
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=420)
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

with g8:
    st.markdown('''<div class="dp-card">
                <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
                color:var(--dp-cyan-2);font-weight:700;margin-bottom:6px">Career Funnel</div>
    <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:10px">Experience Bands</div>
                </div>''', unsafe_allow_html=True)
    bands = pd.cut(exp_filtered["Experience_Years"], bins=[0,2,5,9,14,30],
                   labels=["Entry","Mid","Senior","Lead","Executive"])
    counts = bands.value_counts().reindex(["Entry","Mid","Senior","Lead","Executive"]).fillna(0)
    fig = go.Figure(go.Funnel(
        y=counts.index, x=counts.values,
        textinfo="value+percent initial",
        marker=dict(color=["#00D9FF","#38BDF8","#0EA5E9","#2563EB","#1E40AF"],
                    line=dict(color="#020617", width=2)),
        connector=dict(line=dict(color="rgba(56,189,248,0.3)", width=1))
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=420)
    st.plotly_chart(fig, use_container_width=True , config = config)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# OPPORTUNITY ENGINE + INSIGHTS PANEL
# --------------------------------------------------
st.markdown("""
<div class="dp-section">
  <div class="dp-section-bar"></div>
  <h2>AI Opportunity Engine</h2>
  <span class="hint">Personalized skill intelligence</span>
</div>
""", unsafe_allow_html=True)

user_skills = st.session_state.get("resume_skills", [])
market_skills = skill_filtered.sort_values("Count", ascending=False)["Skill"].head(10).tolist()
missing_skills = [
    skill for skill in market_skills
    if skill.lower() not in [s.lower() for s in user_skills]
]

left_col, right_col = st.columns([2.2, 1])

with left_col:
    if len(user_skills) == 0:
        st.markdown("""
        <div class="dp-card" style="text-align:center;padding:48px 24px">
          <div style="font-size:42px;margin-bottom:10px">
            <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#00D9FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
          </div>
          <div style="font-size:18px;font-weight:700;color:#fff;margin-top:6px">Upload Your Resume To Unlock Personalization</div>
          <div style="color:var(--dp-text-dim);margin-top:8px">Analyze a resume to surface tailored skill recommendations & ROI estimates.</div>
        </div>
        """, unsafe_allow_html=True)
    elif missing_skills:
        cards_html = '<div class="dp-opp">'
        max_count = skill_filtered["Count"].max() if not skill_filtered.empty else 1
        for i, skill in enumerate(missing_skills, 1):
            row = skill_filtered[skill_filtered["Skill"] == skill]
            cnt = int(row["Count"].iloc[0]) if not row.empty else 0
            priority = min(100, int(cnt / max_count * 100)) if max_count else 0
            difficulty = ["Beginner","Intermediate","Advanced"][i % 3]
            uplift = 8 + (priority // 10)
            cards_html += (
                f'<div class="dp-opp-card">'
                f'<div class="dp-opp-rank">{i:02d}</div>'
                f'<div>'
                f'<div class="dp-opp-name">{skill}</div>'
                f'<div class="dp-opp-meta">'
                f'<span>Priority <b>{priority}/100</b></span>'
                f'<span>Impact <b>High</b></span>'
                f'<span>Difficulty <b>{difficulty}</b></span>'
                f'<span>Salary Uplift <b>+{uplift}%</b></span>'
                f'<span>Learning ROI <b>{priority + 20}</b></span>'
                f'</div></div>'
                f'<div class="dp-opp-cta">Add Skill →</div>'
                f'</div>'
            )
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="dp-card" style="text-align:center;padding:42px 24px">
          <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#00D9FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
          <div style="font-size:18px;font-weight:700;color:#fff;margin-top:10px">Your skills are strongly aligned with market demand</div>
          <div style="color:var(--dp-text-dim);margin-top:6px">You're hitting the top 10 in-demand skills for this role.</div>
        </div>
        """, unsafe_allow_html=True)

with right_col:
    trend = "▲ Rising" if demand_score > 50 else "▼ Cooling"
    strength = "Strong" if demand_score > 60 else "Moderate" if demand_score > 30 else "Emerging"
    st.markdown(f"""
    <div class="dp-card dp-insights" style="position:sticky;top:20px">
      <h3>◆ Intelligence Panel</h3>
      <div class="dp-insight-row"><span class="k">Selected Role</span><span class="v">{selected_role}</span></div>
      <div class="dp-insight-row"><span class="k">Selected Location</span><span class="v">{selected_location}</span></div>
      <div class="dp-insight-row"><span class="k">Top Skill</span><span class="v">{top_skill}</span></div>
      <div class="dp-insight-row"><span class="k">Market Strength</span><span class="v" style="color:#00D9FF">{strength}</span></div>
      <div class="dp-insight-row"><span class="k">Average Salary</span><span class="v">₹ {avg_salary:,.0f}</span></div>
      <div class="dp-insight-row"><span class="k">Trend Direction</span><span class="v" style="color:#00D9FF">{trend}</span></div>
      <div class="dp-insight-row"><span class="k">Data Refresh</span><span class="v" style="color:#22ee99">● Live</span></div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
def _logo_b64():
    for p in [ASSETS_DIR / "mini_logo.png"]:
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return ""

logo_b64 = _logo_b64()

footer_logo = f'<img src="data:image/png;base64,{logo_b64}"/>' if logo_b64 else ""
st.markdown(f"""
<div class="dp-footer">
  <div class="brand">
          <div class="dp-footer-brand">
        {footer_logo}
        <div>
    <div>
      <div>DataPilot AI</div>
      <div style="font-size:11px;color:var(--dp-text-dim);font-weight:500">Navigate Your Data Career</div>
    </div>
  </div>
  <div style="color:var(--dp-text-dim);font-size:13px;text-align:center">
    Powered by DataPilot Market Intelligence Engine
  </div>
  <div class="live"><span class="pulse"></span> Live Market Analytics</div>
</div>
""", unsafe_allow_html=True)
