import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd

from src.auth.session_manager import is_authenticated
from src.job_fit.predictor import ROLE_SKILLS, predict_job_fit
from components.sidebar import show_sidebar


st.set_page_config(
    page_title="Career Match Engine · DataPilot AI",
    page_icon="assests/mini_logo.png",
    layout="wide",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

resume_skills = st.session_state.get("resume_skills", [])

# =========================================================
# GLOBAL STYLES
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background:
      radial-gradient(1200px 600px at 10% -10%, rgba(0,200,255,0.15), transparent 60%),
      radial-gradient(900px 500px at 90% 10%, rgba(37,99,235,0.18), transparent 60%),
      radial-gradient(800px 400px at 50% 100%, rgba(14,165,233,0.12), transparent 60%),
      linear-gradient(180deg, #020617 0%, #07112A 50%, #08142F 100%);
    color: #E2E8F0;
}

[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1280px; }

/* Hero */
.dp-hero{
  position:relative;
  border:1px solid var(--border);
  border-radius:24px;
  padding:42px 48px;
  background:
    radial-gradient(600px 280px at 90% 10%, rgba(0,200,255,.18), transparent 60%),
    linear-gradient(135deg, rgba(8,20,47,.85), rgba(7,17,42,.7));
  box-shadow:
    0 0 0 1px rgba(0,200,255,.05) inset,
    0 30px 80px -30px rgba(0,200,255,.25),
    0 0 60px -20px rgba(37,99,235,.35);
  overflow:hidden;
  margin-bottom:28px;
}
.dp-hero::before{
  content:"";position:absolute;inset:-1px;border-radius:24px;
  background:linear-gradient(120deg, rgba(0,200,255,.4), transparent 40%, rgba(37,99,235,.35));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
  -webkit-mask-composite:xor;mask-composite:exclude;padding:1px;pointer-events:none;
}
.dp-hero-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:32px;align-items:center;}
@media (max-width: 980px){.dp-hero-grid{grid-template-columns:1fr;} .dp-hero{padding:28px;}}

.dp-badge{
  display:inline-flex;align-items:center;gap:8px;
  padding:7px 14px;border-radius:999px;
  border:1px solid rgba(0,200,255,.35);
  background:rgba(0,200,255,.08);
  color:#7FE0FF;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
}
.dp-badge .dot{width:7px;height:7px;border-radius:50%;background:#00C8FF;box-shadow:0 0 12px #00C8FF;}

.dp-h1{
  font-size:46px;line-height:1.08;font-weight:800;letter-spacing:-.02em;
  margin:18px 0 14px;color:#F4FAFF;
}
.dp-h1 .grad{
  background:linear-gradient(90deg,#00C8FF,#2563EB);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.dp-sub{color:var(--muted);font-size:16px;line-height:1.6;max-width:560px;}

.dp-pills{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px;}
.dp-pill{
  font-size:12.5px;font-weight:500;color:#CFE6FF;
  padding:8px 14px;border-radius:10px;
  border:1px solid var(--border-soft);
  background:rgba(255,255,255,.03);
  backdrop-filter:blur(6px);
}
.dp-pill span{color:#00C8FF;margin-right:6px;}



/* Card */
.dp-card{
  position:relative;border:1px solid var(--border-soft);border-radius:18px;
  background:linear-gradient(180deg, rgba(8,20,47,.7), rgba(7,17,42,.55));
  padding:22px 24px;backdrop-filter:blur(14px);
  transition:transform .25s ease, border-color .25s ease, box-shadow .25s ease;
}
.dp-card:hover{transform:translateY(-2px);border-color:rgba(0,200,255,.35);
  box-shadow:0 20px 60px -30px rgba(0,200,255,.45);}

.dp-section-title{
  display:flex;align-items:center;gap:10px;margin:32px 0 14px;
  font-size:20px;font-weight:700;color:#F0F8FF;letter-spacing:-.01em;
}
.dp-section-title .bar{width:4px;height:20px;border-radius:3px;
  background:linear-gradient(180deg,#00C8FF,#2563EB);box-shadow:0 0 12px rgba(0,200,255,.6);}
.dp-section-sub{color:var(--muted);font-size:13.5px;margin-top:-8px;margin-bottom:16px;}

/* ===== CTA BUTTON ===== */
div.stButton > button {
    background: linear-gradient(135deg, #00C8FF 0%, #0EA5E9 50%, #2563EB 100%) !important;
    color: #001022 !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 16px 36px !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow:
      0 0 0 1px rgba(0,200,255,0.4) inset,
      0 10px 30px -6px rgba(0,200,255,0.5),
      0 20px 60px -10px rgba(37,99,235,0.4) !important;
    transition: all .25s ease !important;
    letter-spacing: 0.01em !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow:
      0 0 0 1px rgba(0,200,255,0.6) inset,
      0 14px 40px -6px rgba(0,200,255,0.7),
      0 24px 70px -10px rgba(37,99,235,0.55) !important;
}

/* ===== GLASS CARDS ===== */
.dp-card {
    border-radius: 20px;
    background: linear-gradient(160deg, rgba(8,20,47,0.7), rgba(7,17,42,0.45));
    border: 1px solid rgba(0,200,255,0.15);
    padding: 28px;
    backdrop-filter: blur(16px);
    box-shadow: 0 20px 60px -20px rgba(0,0,0,0.5);
    transition: all .3s ease;
}
.dp-card:hover { border-color: rgba(0,200,255,0.35); }

.dp-section-title {
    display:flex; align-items:center; gap:12px;
    font-size: 22px; font-weight:700; color:#F1F5F9;
    margin: 36px 0 18px;
}
.dp-section-title .bar {
    width:4px; height:22px; border-radius:4px;
    background: linear-gradient(180deg,#00C8FF,#2563EB);
    box-shadow: 0 0 12px #00C8FF;
}
.dp-section-title .sub { font-size:13px; font-weight:500; color:#64748B; margin-left:8px;}

/* KPI */
.kpi {
    border-radius: 16px; padding: 20px;
    background: linear-gradient(160deg, rgba(13,28,58,0.8), rgba(7,17,42,0.5));
    border:1px solid rgba(0,200,255,0.18);
    transition: all .25s ease;
}
.kpi:hover { transform: translateY(-3px); border-color: rgba(0,200,255,0.45); box-shadow: 0 12px 40px -10px rgba(0,200,255,0.3);}
.kpi .label { font-size:11px; font-weight:600; color:#64748B; letter-spacing:0.1em; text-transform:uppercase;}
.kpi .value { font-size: 30px; font-weight:800; color:#F1F5F9; margin-top:6px;
   background: linear-gradient(90deg,#00C8FF,#0EA5E9);
   -webkit-background-clip:text; background-clip:text; color:transparent;}
.kpi .hint { font-size:12px; color:#94A3B8; margin-top:4px;}

/* Verdict card */
.dp-verdict {
    border-radius:20px; padding:32px;
    background: linear-gradient(160deg, rgba(0,200,255,0.06), rgba(37,99,235,0.06));
    border:1px solid rgba(0,200,255,0.25);
    position:relative; overflow:hidden;
}
.dp-verdict::before{ content:""; position:absolute; top:-50%; right:-20%; width:400px; height:400px;
   background: radial-gradient(circle, rgba(0,200,255,0.15), transparent 60%); pointer-events:none;}
.dp-verdict h3 { color:#7DD8FF; font-size:14px; letter-spacing:0.1em; text-transform:uppercase; margin:0 0 8px;}
.dp-verdict p { color:#CBD5E1; font-size:15px; line-height:1.7; margin:8px 0;}
.dp-verdict .row { display:flex; gap:10px; align-items:flex-start; margin-top:14px;}
.dp-verdict .row .ic {
   width:28px; height:28px; border-radius:8px; flex-shrink:0;
   background: linear-gradient(135deg,#00C8FF,#2563EB);
   display:flex; align-items:center; justify-content:center; color:#001022; font-weight:800; font-size:13px;
}

/* Skill gap card */
.gap-card {
    border-radius:16px; padding:20px;
    background: linear-gradient(160deg, rgba(13,28,58,0.75), rgba(7,17,42,0.5));
    border:1px solid rgba(0,200,255,0.18);
    transition: all .25s ease; height:100%;
}
.gap-card:hover{ transform: translateY(-3px); border-color: rgba(0,200,255,0.45);}
.gap-card .name { font-size:16px; font-weight:700; color:#F1F5F9; }
.gap-card .meta { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap;}
.gap-card .tag { font-size:11px; font-weight:600; padding:4px 9px; border-radius:6px;
   background: rgba(0,200,255,0.1); color:#7DD8FF; border:1px solid rgba(0,200,255,0.25);}
.gap-card .tag.high { background: rgba(239,68,68,0.1); color:#FCA5A5; border-color: rgba(239,68,68,0.3);}
.gap-card .tag.med  { background: rgba(245,158,11,0.1); color:#FCD34D; border-color: rgba(245,158,11,0.3);}
.gap-card .bar-bg { margin-top:14px; height:6px; border-radius:6px; background: rgba(255,255,255,0.05); overflow:hidden;}
.gap-card .bar-fg { height:100%; border-radius:6px; background: linear-gradient(90deg,#00C8FF,#2563EB); box-shadow: 0 0 10px #00C8FF;}
.gap-card .priority { font-size:11px; color:#64748B; margin-top:8px; letter-spacing:0.08em; text-transform:uppercase;}

/* Skill chips */
.chip {
   display:inline-block; margin:5px; padding:8px 14px;
   border-radius:999px; font-size:13px; font-weight:500;
   background: linear-gradient(135deg, rgba(0,200,255,0.08), rgba(37,99,235,0.08));
   border:1px solid rgba(0,200,255,0.25); color:#CBD5E1;
   transition: all .25s ease;
}
.chip:hover { transform: translateY(-2px); border-color:#00C8FF; color:#7DD8FF;
   box-shadow: 0 8px 20px -6px rgba(0,200,255,0.5);}

/* Timeline */
.tl { position:relative; padding-left: 40px; margin-top:8px;}
.tl::before { content:""; position:absolute; left:14px; top:8px; bottom:8px; width:2px;
   background: linear-gradient(180deg, #00C8FF, #2563EB, transparent);}
.tl-item { position:relative; padding: 16px 20px; margin-bottom:14px;
   border-radius:14px; background: rgba(13,28,58,0.6);
   border:1px solid rgba(0,200,255,0.18);}
.tl-item::before {
   content: attr(data-step); position:absolute; left:-34px; top:14px;
   width:30px; height:30px; border-radius:50%;
   background: linear-gradient(135deg,#00C8FF,#2563EB);
   color:#001022; font-weight:800; font-size:13px;
   display:flex; align-items:center; justify-content:center;
   box-shadow: 0 0 20px rgba(0,200,255,0.6);
}
.tl-item .t { font-size:11px; color:#64748B; letter-spacing:0.1em; text-transform:uppercase; font-weight:600;}
.tl-item .n { font-size:16px; font-weight:700; color:#F1F5F9; margin-top:4px;}
.tl-item .d { font-size:13px; color:#94A3B8; margin-top:4px;}

/* Empty state */
.empty {
   border-radius:24px; padding:60px 40px; text-align:center;
   background: linear-gradient(160deg, rgba(8,20,47,0.6), rgba(7,17,42,0.3));
   border: 1px dashed rgba(0,200,255,0.25);
}
.empty h3 { color:#F1F5F9; font-size:24px; font-weight:700; margin: 20px 0 10px;}
.empty p { color:#94A3B8; font-size:15px; max-width:520px; margin: 0 auto;}
.empty-stats { display:flex; gap:16px; justify-content:center; margin-top:30px; flex-wrap:wrap;}
.empty-stat { padding:14px 22px; border-radius:14px;
   background: rgba(13,28,58,0.6); border:1px solid rgba(0,200,255,0.2); min-width:160px;}
.empty-stat .l { font-size:11px; color:#64748B; letter-spacing:0.1em; text-transform:uppercase;}
.empty-stat .v { font-size:22px; font-weight:800; color:#00C8FF; margin-top:4px;}

.role{
    overflow:hidden;
    white-space:nowrap;
    border-right:3px solid #00C8FF;
    animation: typing 3s steps(14) infinite;
}

@keyframes typing{
    0%{width:0}
    50%{width:14ch}
    100%{width:0}
}

.dp-typewriter{
    display:flex;
    align-items:center;
    gap:10px;
    font-size:1.4rem;
    font-weight:700;
    margin:20px 0;
}

.role-slider{
    height:40px;
    overflow:hidden;
    display:inline-block;
    vertical-align:middle;
}

.role-slider-inner{
    animation: slideRoles 14s infinite;
}

.role-slider-inner div{
    height:40px;
    line-height:40px;
    font-weight:700;
    background: linear-gradient(90deg,#00C8FF,#2563EB);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

@keyframes slideRoles{
    0%,12%   { transform: translateY(0); }
    14%,26%  { transform: translateY(-40px); }
    28%,40%  { transform: translateY(-80px); }
    42%,54%  { transform: translateY(-120px); }
    56%,68%  { transform: translateY(-160px); }
    70%,82%  { transform: translateY(-200px); }
    84%,100% { transform: translateY(-240px); }
}
/* Hide streamlit default success/warn for our context */
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
HERO_SVG = """
<svg viewBox="0 0 480 360" width="100%" height="320" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00C8FF" stop-opacity=".35"/>
      <stop offset="100%" stop-color="#00C8FF" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="lg" x1="0" x2="1">
      <stop offset="0" stop-color="#00C8FF"/>
      <stop offset="1" stop-color="#2563EB"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <circle cx="240" cy="180" r="140" fill="url(#bgGlow)"/>
  <g stroke="url(#lg)" stroke-width="1.2" fill="none" opacity=".8" stroke-dasharray="4 6" style="animation:dash 4s linear infinite">
    <line x1="240" y1="180" x2="90"  y2="80"/>
    <line x1="240" y1="180" x2="400" y2="70"/>
    <line x1="240" y1="180" x2="70"  y2="260"/>
    <line x1="240" y1="180" x2="420" y2="280"/>
    <line x1="240" y1="180" x2="240" y2="40"/>
    <line x1="240" y1="180" x2="240" y2="320"/>
  </g>
  <g fill="#00C8FF" filter="url(#glow)">
    <circle cx="90"  cy="80"  r="6" style="animation:pulseNode 3s infinite"/>
    <circle cx="400" cy="70"  r="6" style="animation:pulseNode 3.4s infinite"/>
    <circle cx="70"  cy="260" r="6" style="animation:pulseNode 2.6s infinite"/>
    <circle cx="420" cy="280" r="6" style="animation:pulseNode 3.8s infinite"/>
    <circle cx="240" cy="40"  r="5" style="animation:pulseNode 2.2s infinite"/>
    <circle cx="240" cy="320" r="5" style="animation:pulseNode 3.1s infinite"/>
  </g>
  <g transform="translate(240,180)">
    <circle r="34" fill="#07112A" stroke="url(#lg)" stroke-width="2"/>
    <circle r="34" fill="none" stroke="#00C8FF" stroke-opacity=".25" stroke-width="14"/>
    <text x="0" y="6" text-anchor="middle" font-family="Inter" font-weight="800" font-size="14" fill="#7FE0FF">DP·AI</text>
  </g>
  <g font-family="Inter" font-size="10" font-weight="600" fill="#9FD8FF">
    <text x="90"  y="68"  text-anchor="middle">ANALYST</text>
    <text x="400" y="58"  text-anchor="middle">SCIENTIST</text>
    <text x="70"  y="280" text-anchor="middle">ENGINEER</text>
    <text x="420" y="300" text-anchor="middle">ML</text>
    <text x="240" y="28"  text-anchor="middle">BI</text>
    <text x="240" y="338" text-anchor="middle">ANALYTICS</text>
  </g>
</svg>
"""

st.markdown(f"""
<div class="dp-hero">
  <div class="dp-hero-grid">
    <div>
      <span class="dp-badge"><span class="dot"></span> AI Career Intelligence</span>
      <div class="dp-h1">Discover Your <span class="grad">Perfect Data Career</span></div>
      <div class="dp-sub">Analyze your resume against real-world industry skill requirements and uncover the career path where you are most likely to succeed.</div>
      <div class="dp-pills">
        <div class="dp-pill"><span>◆</span>Market Intelligence</div>
        <div class="dp-pill"><span>◆</span>Skill Matching</div>
        <div class="dp-pill"><span>◆</span>Career Forecasting</div>
        <div class="dp-pill"><span>◆</span>Gap Detection</div>
      </div>
    </div>
    <div>{HERO_SVG}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# CTA
c1, c2, c3 = st.columns([1,1.2,1])
with c2:
    analyze_clicked = st.button("⚡  Analyze Career Fit", use_container_width=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# =========================================================
# LOGIC (unchanged backend calls)
# =========================================================
predictions = st.session_state.get("job_fit_predictions", {})
missing_skills = st.session_state.get("job_fit_missing_skills", [])
extracted_skills = resume_skills
best_role = st.session_state.get("job_fit_best_role")
best_score = st.session_state.get("job_fit_best_score", 0)

if analyze_clicked:
    if not resume_skills:
        st.error("No resume skills found. Run the Resume Analyzer first to extract skills.")
        st.session_state.pop("job_fit_predictions", None)
        st.session_state.pop("job_fit_missing_skills", None)
        st.session_state.pop("job_fit_best_role", None)
        st.session_state.pop("job_fit_best_score", None)
        predictions = {}
        missing_skills = []
        best_role = None
        best_score = 0
    else:
        predictions = predict_job_fit(resume_skills)
        best_role = next(iter(predictions))
        best_score = predictions[best_role]
        normalized_skills = {s.lower().strip() for s in resume_skills}
        missing_skills = [
            s for s in ROLE_SKILLS.get(best_role, [])
            if s not in normalized_skills
        ]
        st.session_state["job_fit_predictions"] = predictions
        st.session_state["job_fit_missing_skills"] = missing_skills
        st.session_state["job_fit_best_role"] = best_role
        st.session_state["job_fit_best_score"] = best_score

# =========================================================
# EMPTY STATE
# =========================================================
if not predictions:
    skills_count = len(resume_skills)
    resume_status = "Ready" if resume_skills else "Pending"
    readiness = "Detected" if resume_skills else "Awaiting Resume"
    st.markdown(f"""
    <div class="empty">
      <svg width="120" height="120" viewBox="0 0 120 120" style="margin:0 auto;display:block">
        <defs>
          <linearGradient id="eg" x1="0" x2="1">
            <stop offset="0%" stop-color="#00C8FF"/><stop offset="100%" stop-color="#2563EB"/>
          </linearGradient>
        </defs>
        <circle cx="60" cy="60" r="50" fill="none" stroke="url(#eg)" stroke-width="1.5" opacity="0.4"/>
        <circle cx="60" cy="60" r="30" fill="none" stroke="url(#eg)" stroke-width="1.5" opacity="0.6"/>
        <circle cx="60" cy="60" r="8" fill="#00C8FF" style="filter:drop-shadow(0 0 12px #00C8FF)"/>
        <circle cx="20" cy="40" r="4" fill="#00C8FF"/>
        <circle cx="100" cy="50" r="4" fill="#0EA5E9"/>
        <circle cx="30" cy="90" r="4" fill="#2563EB"/>
        <circle cx="95" cy="90" r="4" fill="#00C8FF"/>
        <line x1="60" y1="60" x2="20" y2="40" stroke="url(#eg)" stroke-width="1" opacity="0.6"/>
        <line x1="60" y1="60" x2="100" y2="50" stroke="url(#eg)" stroke-width="1" opacity="0.6"/>
        <line x1="60" y1="60" x2="30" y2="90" stroke="url(#eg)" stroke-width="1" opacity="0.6"/>
        <line x1="60" y1="60" x2="95" y2="90" stroke="url(#eg)" stroke-width="1" opacity="0.6"/>
      </svg>
      <h3>Your AI Career Graph Awaits</h3>
      <p>Analyze your resume and discover where your skills create the strongest market value.</p>
      <div class="empty-stats">
        <div class="empty-stat"><div class="l">Detected Skills</div><div class="v">{skills_count}</div></div>
        <div class="empty-stat"><div class="l">Resume Status</div><div class="v">{resume_status}</div></div>
        <div class="empty-stat"><div class="l">Career Readiness</div><div class="v">{readiness}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# RESULTS
# =========================================================
if predictions:
    # ----- SECTION 1: Scorecard -----
    st.markdown("""<div class="dp-section-title"><span class="bar"></span>Career Match Scorecard<span class="sub">— top role intelligence</span></div>""", unsafe_allow_html=True)

    if best_score >= 80:
        confidence = "Very High"; demand = "Strong"; growth = "Accelerating"; salary = "Premium"
    elif best_score >= 60:
        confidence = "High"; demand = "Healthy"; growth = "Steady"; salary = "Competitive"
    else:
        confidence = "Developing"; demand = "Moderate"; growth = "Emerging"; salary = "Entry"

    k1,k2,k3 = st.columns(3)
    k4,k5,k6 = st.columns(3)
    cards = [
        (k1,"BEST ROLE", best_role, "Top AI match"),
        (k2,"FIT PERCENTAGE", f"{best_score:.1f}%", "Resume alignment"),
        (k3,"CONFIDENCE", confidence, "Model certainty"),
        (k4,"MARKET DEMAND", demand, "Industry signal"),
        (k5,"CAREER GROWTH", growth, "5-yr outlook"),
        (k6,"SALARY POTENTIAL", salary, "Compensation tier"),
    ]
    for col,label,val,hint in cards:
        with col:
            st.markdown(f"""<div class="kpi"><div class="label">{label}</div>
            <div class="value">{val}</div><div class="hint">{hint}</div></div>""", unsafe_allow_html=True)

    # ----- SECTION 2: Chart -----
    st.markdown("""<div class="dp-section-title"><span class="bar"></span>Interactive Career Match<span class="sub">— top 5 roles</span></div>""", unsafe_allow_html=True)

    top_roles = dict(list(predictions.items())[:5])
    roles_list = list(top_roles.keys())
    scores_list = list(top_roles.values())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scores_list, y=roles_list, orientation='h',
        text=[f"{s:.1f}%" for s in scores_list], textposition='outside',
        textfont=dict(color="#7DD8FF", size=13, family="Inter"),
        marker=dict(
            color=scores_list,
            colorscale=[[0,"#0EA5E9"],[0.5,"#00C8FF"],[1,"#2563EB"]],
            line=dict(color="rgba(0,200,255,0.4)", width=1),
        ),
        hovertemplate="<b>%{y}</b><br>Fit Score: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=420,
        margin=dict(l=20,r=40,t=20,b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#CBD5E1"),
        xaxis=dict(showgrid=True, gridcolor="rgba(0,200,255,0.08)", title="Fit Score (%)", range=[0, max(scores_list)*1.15]),
        yaxis=dict(showgrid=False, autorange="reversed"),
        showlegend=False,
        bargap=0.45,
    )
    st.markdown('<div class="dp-card" style="padding:14px 18px;">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ----- SECTION 3: Verdict -----
    st.markdown("""<div class="dp-section-title"><span class="bar"></span>AI Career Verdict<span class="sub">— synthesized insight</span></div>""", unsafe_allow_html=True)

    if best_score >= 80:
        assess = f"Your profile demonstrates strong alignment with {best_role} positions. You're positioned to compete for senior-track opportunities in the current market."
        strength = "Core technical foundations are well established with multiple high-demand skills detected."
        readiness = "Interview-ready. Recommend immediate application to mid-to-senior roles."
        growth_text = "High trajectory — focus on specialization to unlock senior compensation tiers."
        market = "Top quartile candidate. Strong leverage in salary negotiations."
    elif best_score >= 60:
        assess = f"Your profile shows promising alignment with {best_role}. Targeted upskilling will significantly accelerate placement."
        strength = "Solid foundational skills detected with clear room for technical depth."
        readiness = "Application-ready for junior to mid-level positions."
        growth_text = "Moderate-to-high trajectory once core gaps are closed."
        market = "Competitive candidate with strong potential to move upmarket."
    else:
        assess = "Your profile is developing. Strategic skill investment will compound into significant career leverage."
        strength = "Early-stage foundation — primary focus should be building portfolio depth."
        readiness = "Pre-application phase. Recommend 8–12 weeks of focused skill building."
        growth_text = "High long-term potential with disciplined execution on the roadmap below."
        market = "Emerging candidate. Build proof-of-work through projects."

    st.markdown(f"""
    <div class="dp-verdict">
      <h3>AI Career Assessment</h3>
      <p style="font-size:17px;color:#F1F5F9;font-weight:500;">{assess}</p>
      <div class="row"><div class="ic">S</div><div><div style="font-weight:600;color:#7DD8FF;">Strength Analysis</div><p>{strength}</p></div></div>
      <div class="row"><div class="ic">R</div><div><div style="font-weight:600;color:#7DD8FF;">Readiness Level</div><p>{readiness}</p></div></div>
      <div class="row"><div class="ic">G</div><div><div style="font-weight:600;color:#7DD8FF;">Growth Potential</div><p>{growth_text}</p></div></div>
      <div class="row"><div class="ic">M</div><div><div style="font-weight:600;color:#7DD8FF;">Market Position</div><p>{market}</p></div></div>
    </div>
    """, unsafe_allow_html=True)

    # ----- SECTION 4: Skill Gap -----
    st.markdown("""<div class="dp-section-title"><span class="bar"></span>Skill Gap Intelligence<span class="sub">— prioritized learning targets</span></div>""", unsafe_allow_html=True)

    if missing_skills:
        gap_top = missing_skills[:6]
        rows = [st.columns(3), st.columns(3)]
        for idx, skill in enumerate(gap_top):
            col = rows[idx // 3][idx % 3]
            if idx < 2:
                imp, demand_score, prio, cls, prog = "Critical", 95-idx*3, "Priority 1", "high", 92-idx*4
            elif idx < 4:
                imp, demand_score, prio, cls, prog = "High", 82-idx*2, "Priority 2", "med", 75-idx*3
            else:
                imp, demand_score, prio, cls, prog = "Recommended", 68, "Priority 3", "", 55
            with col:
                st.markdown(f"""
                <div class="gap-card">
                  <div class="name">{skill.title()}</div>
                  <div class="meta">
                    <span class="tag {cls}">{imp}</span>
                    <span class="tag">Demand {demand_score}</span>
                  </div>
                  <div class="bar-bg"><div class="bar-fg" style="width:{prog}%"></div></div>
                  <div class="priority">{prio} · Learning Track</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="dp-card" style="text-align:center;">
        <div style="font-size:18px;font-weight:700;color:#7DD8FF;">✓ No critical skill gaps detected</div>
        <div style="color:#94A3B8;margin-top:6px;">Your profile is comprehensively aligned with the target role.</div>
        </div>""", unsafe_allow_html=True)

    # ----- SECTION 5: Detected skills cloud -----
    st.markdown("""<div class="dp-section-title"><span class="bar"></span>Skills Detected<span class="sub">— from your resume</span></div>""", unsafe_allow_html=True)
    chips_html = "".join([f'<span class="chip">{s}</span>' for s in extracted_skills])
    fallback_html = "<span style=\'color:#64748B\'>No skills detected.</span>"
    st.markdown(f'<div class="dp-card">{chips_html or fallback_html}</div>', unsafe_allow_html=True)

    # ----- SECTION 6: Roadmap timeline -----
    st.markdown("""<div class="dp-section-title"><span class="bar"></span>Growth Roadmap<span class="sub">— sequenced execution plan</span></div>""", unsafe_allow_html=True)

    steps_skills = (missing_skills + ["Portfolio Project", "Mock Interview", "Application Sprint", "Negotiation"])[:4]
    step_meta = [
        ("WEEK 1–2", "Foundation", "Establish core competency through guided learning"),
        ("WEEK 3–4", "Application", "Apply skills through hands-on practice projects"),
        ("WEEK 5–6", "Depth", "Build production-grade case studies for your portfolio"),
        ("WEEK 7–8", "Launch", "Refine resume, prepare interviews, begin outreach"),
    ]
    items_html = ""
    for i, skill in enumerate(steps_skills):
        t, n, d = step_meta[i]
        items_html += f"""<div class="tl-item" data-step="{i+1}">
          <div class="t">{t} · {n}</div>
          <div class="n">{skill.title() if isinstance(skill,str) else skill}</div>
          <div class="d">{d}</div>
        </div>"""
    st.markdown(f'<div class="dp-card"><div class="tl">{items_html}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
