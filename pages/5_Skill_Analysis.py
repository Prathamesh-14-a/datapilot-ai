# pages/Skill_Analyzer.py
import streamlit as st
import time
import html
import re
import base64

from src.auth.session_manager import is_authenticated
from components.sidebar import show_sidebar
from streamlit_tags import st_tags
from src.resume_matching.resume_parser import TECHNICAL_SKILLS
from src.resume_matching.master_career_intelligent import career_intelligence_pipeline
from src.llm.skill_improvement import generate_skill_feedback
from src.text_to_pdf.text_to_pdf import text_to_pdf
from src.ATS.ats_match import get_role_skills, calculated_weighted_score

# ----------------------------------------------------------------------
# AUTH + SHELL
# ----------------------------------------------------------------------
if not is_authenticated():
    st.warning("Please login first")
    st.stop()

st.set_page_config(page_title="Skill Analyzer · DataPilot AI", 
                  page_icon="assets\mini_logo.png",
                  layout="wide",
                  initial_sidebar_state="expanded")
show_sidebar()

# ----------------------------------------------------------------------
# GLOBAL STYLES — DataPilot AI design system
# ----------------------------------------------------------------------
st.markdown("""
<style>
:root{
  --dp-cyan:#00C8FF;
  --dp-sky:#0EA5E9;
  --dp-blue:#2563EB;
  --dp-bg-0:#03060f;
  --dp-bg-1:#070d1f;
  --dp-bg-2:#0b1430;
  --dp-text:#e6efff;
  --dp-muted:#8aa0c7;
  --dp-border:rgba(120,170,255,0.14);
  --dp-glow:0 0 40px rgba(0,200,255,0.18);
}

/* App background */
.stApp{
  background:
    radial-gradient(1200px 600px at 80% -10%, rgba(0,200,255,0.10), transparent 60%),
    radial-gradient(900px 500px at -10% 20%, rgba(37,99,235,0.18), transparent 60%),
    linear-gradient(180deg, var(--dp-bg-0), var(--dp-bg-1) 60%, var(--dp-bg-0));
  color:var(--dp-text);
}
.block-container{padding-top:1.2rem; max-width:1280px;}

/* Kill default streamlit chrome noise */

#MainMenu,header ,footer{visibility:hidden;}

/* Generic glass card */
.dp-card{
  position:relative;
  background:linear-gradient(160deg, rgba(14,22,48,0.85), rgba(8,14,32,0.75));
  border:1px solid var(--dp-border);
  border-radius:18px;
  padding:22px 24px;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 10px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
}
.dp-card:hover{
  transform:translateY(-2px);
  border-color:rgba(0,200,255,0.35);
  box-shadow: 0 14px 50px rgba(0,0,0,0.55), 0 0 30px rgba(0,200,255,0.10);
}

/* Hero */
.dp-hero{
  display:grid; grid-template-columns: 1.3fr 1fr; gap:28px;
  padding:34px 36px; border-radius:24px;
  background:
    radial-gradient(600px 220px at 90% 10%, rgba(0,200,255,0.18), transparent 60%),
    linear-gradient(160deg, rgba(10,18,44,0.95), rgba(5,9,24,0.85));
  border:1px solid var(--dp-border);
  box-shadow: var(--dp-glow);
  overflow:hidden; position:relative;
}
@media (max-width: 980px){ .dp-hero{ grid-template-columns:1fr; } }

.dp-badge{
  display:inline-flex; align-items:center; gap:8px;
  padding:6px 12px; border-radius:999px;
  background:rgba(0,200,255,0.08);
  border:1px solid rgba(0,200,255,0.3);
  color:#9be8ff; font-size:12px; letter-spacing:.04em; font-weight:600;
}
.dp-badge .dot{
  width:6px; height:6px; border-radius:50%;
  background:var(--dp-cyan); box-shadow:0 0 10px var(--dp-cyan);
  animation:dp-pulse 2s infinite;
}
@keyframes dp-pulse{0%,100%{opacity:1}50%{opacity:.4}}

.dp-h1{
  font-size:44px; line-height:1.08; font-weight:800; margin:14px 0 10px;
  background:linear-gradient(90deg,#ffffff 0%,#bcd9ff 60%,#7cd6ff 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  letter-spacing:-0.02em;
}
.dp-sub{ color:var(--dp-muted); font-size:16px; max-width:560px; line-height:1.6;}

.dp-feature-row{ display:flex; gap:10px; margin-top:18px; flex-wrap:wrap;}
.dp-chip{
  padding:7px 13px; border-radius:10px;
  background:rgba(255,255,255,0.03);
  border:1px solid var(--dp-border);
  color:#cfe1ff; font-size:12.5px; font-weight:500;
}

/* Animated network illustration (pure CSS/SVG) */
.dp-viz{ position:relative; min-height:240px;}
.dp-viz svg{ width:100%; height:100%; }
.dp-orb{
  position:absolute; border-radius:50%;
  filter:blur(30px); opacity:.7;
}
.dp-orb.a{ width:160px;height:160px; background:#0EA5E9; top:10%; right:20%; animation:dp-float 7s ease-in-out infinite;}
.dp-orb.b{ width:120px;height:120px; background:#00C8FF; bottom:5%; right:45%; animation:dp-float 9s ease-in-out infinite reverse;}
@keyframes dp-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-18px)}}

/* Metric cards */
.dp-metric{
  border-radius:18px; padding:22px 24px;
  background:linear-gradient(160deg, rgba(14,22,48,0.9), rgba(8,14,32,0.75));
  border:1px solid var(--dp-border); position:relative; overflow:hidden;
}
.dp-metric::before{
  content:""; position:absolute; inset:0; border-radius:18px; padding:1px;
  background:linear-gradient(135deg, rgba(0,200,255,0.55), rgba(37,99,235,0.0) 60%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude; pointer-events:none;
}
.dp-metric .lbl{ color:var(--dp-muted); font-size:12px; letter-spacing:.12em; text-transform:uppercase; font-weight:600;}
.dp-metric .val{
  font-size:38px; font-weight:800; margin-top:6px;
  background:linear-gradient(90deg,#fff,#7cd6ff);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.dp-metric .ico{
  width:38px;height:38px;border-radius:10px; display:flex;align-items:center;justify-content:center;
  background:rgba(0,200,255,0.10); border:1px solid rgba(0,200,255,0.25);
  margin-bottom:14px;
}

/* Skill chips */
.dp-skill{
  display:inline-flex; align-items:center; gap:6px;
  padding:6px 12px; margin:4px; border-radius:999px;
  font-size:13px; font-weight:500;
  background:rgba(0,200,255,0.08);
  border:1px solid rgba(0,200,255,0.3);
  color:#bfeaff;
  transition:.2s;
}
.dp-skill:hover{ transform:translateY(-1px); box-shadow:0 0 14px rgba(0,200,255,0.35); }
.dp-skill.miss{
  background:rgba(255,120,80,0.08);
  border-color:rgba(255,140,90,0.35);
  color:#ffd4c2;
}
.dp-skill.miss:hover{ box-shadow:0 0 14px rgba(255,140,90,0.35); }

/* Section heading */
.dp-section-h{
  display:flex; align-items:center; gap:10px; margin: 28px 0 14px;
}
.dp-section-h .bar{ width:4px; height:22px; border-radius:2px; background:linear-gradient(180deg,var(--dp-cyan),var(--dp-blue));}
.dp-section-h h2{ font-size:22px; font-weight:700; margin:0; color:#eaf3ff;}
.dp-section-h .sh-sub{ color:var(--dp-muted); font-size:13px; margin-left:8px;}

/* Streamlit input restyles */
div[data-baseweb="select"] > div{
  background:rgba(10,18,44,0.7)!important;
  border:1px solid var(--dp-border)!important;
  border-radius:12px!important;
}
.stTextInput input, .stTextArea textarea{
  background:rgba(10,18,44,0.7)!important;
  border:1px solid var(--dp-border)!important;
  color:var(--dp-text)!important; border-radius:12px!important;
}

/* Primary buttons */
.stButton > button{
  background:linear-gradient(135deg,#2563EB 0%, #0EA5E9 55%, #00C8FF 100%)!important;
  color:white!important; border:0!important; border-radius:14px!important;
  padding:12px 18px!important; font-weight:600!important;
  box-shadow: 0 10px 30px rgba(0,200,255,0.25)!important;
  transition: transform .15s ease, box-shadow .25s ease!important;
}
.stButton > button:hover{
  transform:translateY(-2px)!important;
  box-shadow: 0 16px 40px rgba(0,200,255,0.45)!important;
}
.stDownloadButton > button{
  background:rgba(0,200,255,0.10)!important;
  border:1px solid rgba(0,200,255,0.35)!important;
  color:#bfeaff!important; border-radius:12px!important;
}


/* Timeline */
.dp-mile{
  display:flex; gap:14px; align-items:flex-start;
  padding:14px 16px; border-radius:14px;
  background:rgba(10,18,44,0.65); border:1px solid var(--dp-border);
  margin-bottom:10px;
}
.dp-mile .num{
  width:34px;height:34px;border-radius:10px; flex:none;
  background:linear-gradient(135deg,#2563EB,#00C8FF); color:white;
  display:flex;align-items:center;justify-content:center; font-weight:700;
}
.dp-mile .name{ font-weight:600; color:#eaf3ff;}
.dp-mile .meta{ color:var(--dp-muted); font-size:12.5px; margin-top:2px;}
.dp-diff{ padding:3px 9px; border-radius:8px; font-size:11px; font-weight:600;}
.dp-diff.easy{ background:rgba(34,197,94,.12); color:#7ef0a8; border:1px solid rgba(34,197,94,.3);}
.dp-diff.med{  background:rgba(0,200,255,.12); color:#9be8ff; border:1px solid rgba(0,200,255,.3);}
.dp-diff.hard{ background:rgba(168,85,247,.14); color:#d6b4ff; border:1px solid rgba(168,85,247,.35);}

/* Priority matrix */
.dp-pri-col{ border-radius:18px; padding:18px; border:1px solid var(--dp-border);
  background:linear-gradient(160deg, rgba(14,22,48,0.9), rgba(8,14,32,0.75)); height:100%;}
.dp-pri-h{ display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;}
.dp-pri-h .ttl{ font-weight:700; color:#eaf3ff;}
.dp-pri-badge{ font-size:11px; font-weight:700; padding:4px 9px; border-radius:8px;}
.dp-pri.green .dp-pri-badge{ background:rgba(34,197,94,.14); color:#7ef0a8; border:1px solid rgba(34,197,94,.35);}
.dp-pri.blue  .dp-pri-badge{ background:rgba(0,200,255,.14); color:#9be8ff; border:1px solid rgba(0,200,255,.35);}
.dp-pri.purple .dp-pri-badge{ background:rgba(168,85,247,.16); color:#d6b4ff; border:1px solid rgba(168,85,247,.4);}

/* Status badges */
.dp-status{ display:inline-flex; padding:6px 12px; border-radius:999px; font-weight:700; font-size:12px;}
.dp-status.elite{ background:rgba(0,200,255,.14); color:#9be8ff; border:1px solid rgba(0,200,255,.4);}
.dp-status.strong{ background:rgba(34,197,94,.14); color:#7ef0a8; border:1px solid rgba(34,197,94,.4);}
.dp-status.moderate{ background:rgba(245,158,11,.14); color:#ffd789; border:1px solid rgba(245,158,11,.4);}
.dp-status.needs{ background:rgba(239,68,68,.14); color:#ffb1b1; border:1px solid rgba(239,68,68,.4);}

/* Loading timeline */
.dp-step{ display:flex; align-items:center; gap:10px; padding:8px 0; color:#cfe1ff;}
.dp-step .tick{
  width:20px;height:20px;border-radius:50%;
  background:linear-gradient(135deg,#00C8FF,#2563EB);
  display:flex;align-items:center;justify-content:center; color:white; font-size:12px;
  box-shadow:0 0 14px rgba(0,200,255,.5);
}
.dp-step.pending{ color:#5d749e;}
.dp-step.pending .tick{ background:rgba(255,255,255,0.05); box-shadow:none;}

/* Fade-in */
.dp-fade{ animation:dpFade .6s ease both;}
@keyframes dpFade{ from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:translateY(0);}

/* ---------- AI report container ---------- */
.dp-report {
background: linear-gradient(160deg, rgba(14,26,56,0.85), rgba(8,16,38,0.85));
        border: 1px solid var(--dp-border-strong);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 14px 40px -14px rgba(0,200,255,0.35);
        color: #DCE7FA;
        line-height: 1.7;
    }
.dp-report h1, .dp-report h2, .dp-report h3 { color: #FFFFFF; } }

/* ---------- Section title ---------- */
    .dp-section-title {
        display:flex; align-items:center; gap:.6rem;
        margin: 1.8rem 0 1rem;
        font-size: 1.25rem; font-weight: 700;
    }
    .dp-section-title .ico {
        width: 32px; height: 32px; border-radius: 9px;
        display:inline-flex; align-items:center; justify-content:center;
        background: rgba(0,200,255,0.10);
        border: 1px solid var(--dp-border);
    }
    .dp-section-title .ico svg { width: 16px; height: 16px; color: var(--dp-cyan); }
    .dp-section-title .sub { color: var(--dp-muted); font-size:.85rem; font-weight: 500; margin-left:.4rem; }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------
st.markdown("""
<div class="dp-hero dp-fade">
  <div>
    <span class="dp-badge"><span class="dot"></span> AI SKILL INTELLIGENCE</span>
    <div class="dp-h1">Understand Your<br/>Market Readiness</div>
    <div class="dp-sub">
      Benchmark your skills against industry requirements, discover gaps,
      and generate an AI-powered growth roadmap tailored to your target role.
    </div>
    <div class="dp-feature-row">
      <span class="dp-chip">◆ Market Aligned</span>
      <span class="dp-chip">◆ AI Powered</span>
      <span class="dp-chip">◆ Skill Intelligence</span>
    </div>
  </div>
  <div class="dp-viz">
    <div class="dp-orb a"></div>
    <div class="dp-orb b"></div>
    <svg viewBox="0 0 400 260" preserveAspectRatio="xMidYMid meet">
      <defs>
        <linearGradient id="ln" x1="0" x2="1">
          <stop offset="0" stop-color="#00C8FF" stop-opacity=".8"/>
          <stop offset="1" stop-color="#2563EB" stop-opacity=".2"/>
        </linearGradient>
      </defs>
      <g stroke="url(#ln)" stroke-width="1" fill="none" opacity=".85">
        <line x1="200" y1="130" x2="80"  y2="60"/>
        <line x1="200" y1="130" x2="320" y2="60"/>
        <line x1="200" y1="130" x2="60"  y2="200"/>
        <line x1="200" y1="130" x2="340" y2="200"/>
        <line x1="200" y1="130" x2="200" y2="30"/>
        <line x1="200" y1="130" x2="200" y2="230"/>
      </g>
      <g fill="#00C8FF">
        <circle cx="200" cy="130" r="10"><animate attributeName="r" values="10;13;10" dur="2.5s" repeatCount="indefinite"/></circle>
        <circle cx="80"  cy="60"  r="5"/>
        <circle cx="320" cy="60"  r="5"/>
        <circle cx="60"  cy="200" r="5"/>
        <circle cx="340" cy="200" r="5"/>
        <circle cx="200" cy="30"  r="5"/>
        <circle cx="200" cy="230" r="5"/>
      </g>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)

SVG = {"ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 1 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M5 22v-2a7 7 0 0 1 14 0v2"/></svg>'}


# ----------------------------------------------------------------------
# ROLE SELECTION (premium look around native selectbox)
# ----------------------------------------------------------------------
ROLE_META = {
    "Data Analyst": "Insights, dashboards, and business reporting",
    "Data Scientist": "Modeling, statistics, and experimentation",
    "Machine Learning Engineer": "Production ML systems and pipelines",
    "Data Engineer": "Data platforms, pipelines, and warehousing",
    "Business Analyst": "Process, requirements, and stakeholder insight",
    "Product Analyst": "Product metrics, funnels, and experimentation",
    "Analytics": "Cross-functional analytics and decision science",
}

st.markdown('<div class="dp-section-h"><div class="bar"></div><h2>Target Role</h2><span class="sh-sub">Choose your benchmark role</span></div>', unsafe_allow_html=True)

col_r1, col_r2 = st.columns([1.2, 1])
with col_r1:
    target_role = st.selectbox(
        "Target Role",
        list(ROLE_META.keys()),
        label_visibility="collapsed",
    )
with col_r2:
    st.markdown(
        f"""<div class="dp-card" style="padding:14px 18px;">
          <div style="color:var(--dp-muted); font-size:11px; letter-spacing:.12em; font-weight:700;">SELECTED ROLE</div>
          <div style="font-size:18px;font-weight:700;margin-top:4px;color:#eaf3ff;">{html.escape(target_role)}</div>
          <div style="color:var(--dp-muted); font-size:13px; margin-top:4px;">{html.escape(ROLE_META[target_role])}</div>
        </div>""",
        unsafe_allow_html=True,
    )

# Keep session compatibility
st.session_state["target_role"] = target_role

# ----------------------------------------------------------------------
# SKILL INPUT
# ----------------------------------------------------------------------
st.markdown('<div class="dp-section-h"><div class="bar"></div><h2>Your Skills</h2><span class="sh-sub">Review and refine your detected skills</span></div>', unsafe_allow_html=True)

resume_skills = st.session_state.get("resume_skills", [])

skills = st_tags(
    label="",
    value=resume_skills,
    suggestions=TECHNICAL_SKILLS,
)

st.markdown(
    f"""<div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
      <span class="dp-badge"><span class="dot"></span> {len(skills)} Skills Detected</span>
      <span style="color:var(--dp-muted);font-size:12.5px;">Add or remove skills to better reflect your expertise</span>
    </div>""",
    unsafe_allow_html=True,
)

# Compute ATS (unchanged backend)
da_skills = get_role_skills(target_role)
ats = calculated_weighted_score(skills, da_skills)

# ----------------------------------------------------------------------
# ANALYZE BUTTON
# ----------------------------------------------------------------------
st.write("")
analyze = st.button("Analyze Skills", use_container_width=True, key="dp_analyze")

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
QUICK_WINS = {"excel","sql joins","power bi","tableau","data cleaning","powerbi","pivot tables","vlookup","etl basics","sql","reporting"}
GROWTH = {"advanced sql","python","pandas","numpy","dashboard","statistics","feature engineering","data visualization","airflow","dbt","matplotlib","seaborn"}
ADVANCED = {"machine learning","deep learning","mlops","kubernetes","spark","kafka","aws","gcp","azure","generative ai","llm","nlp","computer vision","data engineering"}

def _norm(s): return re.sub(r"\s+"," ", s.strip().lower())

def classify(skill):
    n = _norm(skill)
    for kw in QUICK_WINS:
        if kw in n: return "quick"
    for kw in ADVANCED:
        if kw in n: return "advanced"
    for kw in GROWTH:
        if kw in n: return "growth"
    return "growth"

EFFORT = {"quick":"~1-2 weeks", "growth":"~3-6 weeks", "advanced":"~2-4 months"}
DIFF_CLASS = {"quick":"easy", "growth":"med", "advanced":"hard"}
DIFF_LABEL = {"quick":"Beginner", "growth":"Intermediate", "advanced":"Advanced"}

def status_for(score):
    try: s = float(score)
    except: s = 0
    if s >= 85: return ("Elite","elite")
    if s >= 70: return ("Strong","strong")
    if s >= 50: return ("Moderate","moderate")
    return ("Needs Improvement","needs")

# ----------------------------------------------------------------------
# ANALYZE FLOW
# ----------------------------------------------------------------------
if analyze:
    steps = [
        "Reading Skills",
        "Matching Industry Requirements",
        "Evaluating Market Readiness",
        "Detecting Skill Gaps",
        "Generating Intelligence",
        "Building Recommendations",
    ]
    holder = st.empty()
    for i in range(len(steps)+1):
        rows = ""
        for j, s in enumerate(steps):
            done = j < i
            cls = "" if done else "pending"
            tick = "✓" if done else "•"
            rows += f'<div class="dp-step {cls}"><div class="tick">{tick}</div>{s}</div>'
        holder.markdown(f'<div class="dp-card">{rows}</div>', unsafe_allow_html=True)
        time.sleep(0.35)
    holder.empty()
    st.session_state["dp_analyzed"] = True

# ----------------------------------------------------------------------
# RESULTS
# ----------------------------------------------------------------------
if st.session_state.get("dp_analyzed"):
    coverage = ats.get("Coverage", 0)
    matched = ats.get("Matched", []) or []
    missing = ats.get("Missing", []) or []

    # METRICS
    st.markdown('<div class="dp-section-h dp-fade"><div class="bar"></div><h2>Skill Match Overview</h2></div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    metric_cards = [
        (m1, "SKILL MATCH SCORE", f"{coverage}%" if isinstance(coverage,(int,float)) else str(coverage),
         '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00C8FF" stroke-width="2"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-6"/></svg>'),
        (m2, "MATCHED SKILLS", str(len(matched)),
         '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7ef0a8" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>'),
        (m3, "MISSING SKILLS", str(len(missing)),
         '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffb1b1" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg>'),
    ]
    for col, lbl, val, ico in metric_cards:
        with col:
            st.markdown(f"""
              <div class="dp-metric dp-fade">
                <div class="ico">{ico}</div>
                <div class="lbl">{lbl}</div>
                <div class="val">{html.escape(str(val))}</div>
              </div>
            """, unsafe_allow_html=True)

    # SKILL GAP ANALYSIS
    st.markdown('<div class="dp-section-h dp-fade"><div class="bar"></div><h2>Skill Gap Analysis</h2></div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(f'<div class="dp-card dp-fade"><div style="display:flex;justify-content:space-between;align-items:center;"><strong style="color:#eaf3ff;">Matched Skills</strong><span class="dp-badge">{len(matched)}</span></div>', unsafe_allow_html=True)
        q1 = st.text_input("Search matched", key="search_matched", placeholder="Filter matched skills…", label_visibility="collapsed")
        filtered = [s for s in matched if q1.lower() in str(s).lower()] if q1 else matched
        chips = "".join([f'<span class="dp-skill">{html.escape(str(s))}</span>' for s in filtered]) or '<span style="color:var(--dp-muted);">No matches</span>'
        st.markdown(f'<div style="margin-top:10px;">{chips}</div></div>', unsafe_allow_html=True)
    with g2:
        st.markdown(f'<div class="dp-card dp-fade"><div style="display:flex;justify-content:space-between;align-items:center;"><strong style="color:#eaf3ff;">Missing Skills</strong><span class="dp-badge" style="background:rgba(255,140,90,0.10); border-color:rgba(255,140,90,0.35); color:#ffd4c2;">{len(missing)}</span></div>', unsafe_allow_html=True)
        q2 = st.text_input("Search missing", key="search_missing", placeholder="Filter missing skills…", label_visibility="collapsed")
        filtered = [s for s in missing if q2.lower() in str(s).lower()] if q2 else missing
        chips = "".join([f'<span class="dp-skill miss">{html.escape(str(s))}</span>' for s in filtered]) or '<span style="color:var(--dp-muted);">None — strong coverage</span>'
        st.markdown(f'<div style="margin-top:10px;">{chips}</div></div>', unsafe_allow_html=True)

    # PRIORITY MATRIX
    st.markdown('<div class="dp-section-h dp-fade"><div class="bar"></div><h2>Skill Gap Priority Matrix</h2><span class="sh-sub">Classified by impact and effort</span></div>', unsafe_allow_html=True)
    buckets = {"quick":[], "growth":[], "advanced":[]}
    for s in missing:
        buckets[classify(s)].append(s)

    p1, p2, p3 = st.columns(3)
    cols_meta = [
        (p1, "quick",    "green",  "Quick Wins",            "Quick Win"),
        (p2, "growth",   "blue",   "Growth Accelerators",   "Growth Accelerator"),
        (p3, "advanced", "purple", "Long-Term Investments", "Long-Term Investment"),
    ]
    for col, key, tone, title, badge in cols_meta:
        items = buckets[key]
        rows = ""
        for s in items:
            rows += f'<div class="dp-skill" style="display:flex;justify-content:space-between;width:100%;margin:6px 0;"><span>{html.escape(str(s))}</span><span style="color:var(--dp-muted);font-size:11px;">{EFFORT[key]}</span></div>'
        if not items:
            rows = '<div style="color:var(--dp-muted);font-size:13px;">No items in this bucket.</div>'
        with col:
            st.markdown(f"""
              <div class="dp-pri-col dp-pri {tone} dp-fade">
                <div class="dp-pri-h">
                  <div class="ttl">{title}</div>
                  <div class="dp-pri-badge">{badge}</div>
                </div>
                <div>{rows}</div>
              </div>
            """, unsafe_allow_html=True)

    # Recommended Learning Order
    order = buckets["quick"] + buckets["growth"] + buckets["advanced"]
    if order:
        steps_html = " <span style='color:var(--dp-muted)'>→</span> ".join(
            [f'<span class="dp-skill">{html.escape(str(s))}</span>' for s in order[:8]]
        )
        st.markdown(f"""
        <div class="dp-card dp-fade" style="margin-top:14px;">
          <div style="color:var(--dp-muted);font-size:12px;letter-spacing:.12em;font-weight:700;">RECOMMENDED LEARNING ORDER</div>
          <div style="margin-top:10px; line-height:2;">{steps_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # MARKET READINESS
    label, cls = status_for(coverage)
    insights = career_intelligence_pipeline(ats)
    st.markdown('<div class="dp-section-h dp-fade"><div class="bar"></div><h2>Market Readiness</h2></div>', unsafe_allow_html=True)
    st.markdown(f"""
      <div class="dp-card dp-fade">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <span class="dp-status {cls}">{label}</span>
          <span style="color:var(--dp-muted);font-size:13px;">Based on coverage of {target_role} market skills</span>
        </div>
        <div style="color:#dbe7ff; line-height:1.65; white-space:pre-wrap;">{html.escape(str(insights))}</div>
      </div>
    """, unsafe_allow_html=True)

    # ROADMAP
    if missing:
        st.markdown('<div class="dp-section-h dp-fade"><div class="bar"></div><h2>Skill Roadmap</h2><span class="sh-sub">Dynamically built from your missing skills</span></div>', unsafe_allow_html=True)
        mile_html = ""
        for i, s in enumerate(missing, 1):
            k = classify(s)
            mile_html += f"""
              <div class="dp-mile dp-fade">
                <div class="num">{i}</div>
                <div style="flex:1;">
                  <div class="name">{html.escape(str(s))}</div>
                  <div class="meta">Estimated effort: {EFFORT[k]}</div>
                </div>
                <span class="dp-diff {DIFF_CLASS[k]}">{DIFF_LABEL[k]}</span>
              </div>
            """
        st.markdown(mile_html, unsafe_allow_html=True)

    # ===== AI CAREER REPORT =====
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["ai"]}</span>AI Improvement Plan</div>',
        unsafe_allow_html=True,
    )

    gen = st.button("Generate Skill Improvemetn Plan", use_container_width=True, key="dp_gen_report")
    if gen:
        with st.spinner("Generating detailed AI report…"):
            feedback = generate_skill_feedback(ats, st.session_state["target_role"])
        st.session_state["skill_feedback"] = feedback
        st.session_state["_dp_stream"] = True


# ==========================================================
# AI REPORT DISPLAY
# ==========================================================
if "skill_feedback" in st.session_state:
    feedback = st.session_state["skill_feedback"]

    st.markdown('<div class="dp-report">', unsafe_allow_html=True)
    report_slot = st.empty()

    if st.session_state.pop("_dp_stream", False):
        # Streaming reveal for fresh generations
        buf = ""
        for ch in feedback:
            buf += ch
            if len(buf) % 6 == 0:
                report_slot.markdown(buf + "▍")
                time.sleep(0.005)
        report_slot.markdown(feedback)
    else:
        report_slot.markdown(feedback)

    st.markdown("</div>", unsafe_allow_html=True)

    act1, act2, act3 = st.columns([1, 1, 1])
    with act1:
        b64 = base64.b64encode(feedback.encode()).decode()
        st.markdown(
            f"""
            <a href="data:text/plain;base64,{b64}" download="AI_skill_Report.txt"
               style="display:block;text-align:center;padding:.7rem;border-radius:12px;
                      background:rgba(255,255,255,0.04);border:1px solid var(--dp-border-strong);
                      color:var(--dp-text);text-decoration:none;font-weight:600;">
              Copy / Save Text
            </a>
            """,
            unsafe_allow_html=True,
        )
    with act2:
        with st.expander("Expand Report", expanded=False):
            st.markdown(feedback)
    with act3:
        pdf_data = text_to_pdf(feedback)
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="AI_dkillr_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ----------------------------------------------------------------------
# EMPTY STATE
# ----------------------------------------------------------------------
if not skills and not st.session_state.get("dp_analyzed"):
    st.markdown("""
    <div class="dp-card dp-fade" style="text-align:center;padding:40px;">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#00C8FF" stroke-width="1.5" style="margin-bottom:12px;">
        <path d="M12 2a10 10 0 1 0 10 10"/>
        <path d="M22 2 12 12"/>
      </svg>
      <div style="font-size:18px;font-weight:700;color:#eaf3ff;">Ready when you are</div>
      <div style="color:var(--dp-muted);margin-top:6px;">Add your skills and select a target role to discover your market readiness.</div>
    </div>
    """, unsafe_allow_html=True)
