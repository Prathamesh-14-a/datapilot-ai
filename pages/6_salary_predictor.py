import time
import html
import streamlit as st
import base64
import plotly.graph_objects as go
from streamlit_tags import st_tags
from pathlib import Path

import src.salary_prediction.salary_predictor as salary_model
from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated
from src.database.crud import save_salary_prediction
from src.resume_matching.resume_parser import TECHNICAL_SKILLS
from src.text_to_pdf.text_to_pdf import text_to_pdf
from src.config.paths import ASSETS_DIR
from src.llm.salary_tips import generate_salary_tips
import streamlit.components.v1 as components


# ============================================================
# PAGE CONFIG + AUTH
# ============================================================
st.set_page_config(
    page_title="Salary Intelligence · DataPilot AI",
    page_icon=str(ASSETS_DIR / "mini_logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

# ============================================================
# GLOBAL DESIGN SYSTEM (DataPilot AI)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root{
        --dp-cyan:#00C8FF;
        --dp-sky:#0EA5E9;
        --dp-blue:#2563EB;
        --dp-bg-0:#05070D;
        --dp-bg-1:#0A0F1F;
        --dp-bg-2:#0E1730;
        --dp-border:rgba(0,200,255,0.18);
        --dp-border-soft:rgba(148,163,184,0.12);
        --dp-text:#E6EEF8;
        --dp-text-dim:#8FA3BF;
    }

    html, body, [class*="css"], .stApp, .main, .block-container{
        font-family:'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color:var(--dp-text) !important;
    }

    .stApp{
        background:
            radial-gradient(1200px 600px at 85% -10%, rgba(0,200,255,0.18), transparent 60%),
            radial-gradient(900px 500px at -10% 20%, rgba(37,99,235,0.22), transparent 60%),
            radial-gradient(700px 500px at 50% 110%, rgba(14,165,233,0.18), transparent 60%),
            linear-gradient(180deg, #05070D 0%, #060B1A 50%, #05070D 100%) !important;
    }

    .block-container{ padding-top:1rem !important; max-width: 1400px;}
    #MainMenu, header, footer { visibility:hidden; }
    [data-testid="stStatusWidget"] {
    display: none !important;
    }

    /* ---- Hero ---- */
    .dp-hero{
        position:relative;
        border-radius:28px;
        padding:42px 46px;
        background:
            radial-gradient(600px 300px at 80% 20%, rgba(0,200,255,0.18), transparent 60%),
            linear-gradient(135deg, rgba(10,15,31,0.95), rgba(14,23,48,0.85));
        border:1px solid var(--dp-border);
        box-shadow: 0 30px 80px -30px rgba(0,200,255,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
        overflow:hidden;
        margin-bottom:28px;
    }
    .dp-hero::before{
        content:""; position:absolute; inset:0;
        background-image:
            linear-gradient(rgba(0,200,255,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,200,255,0.05) 1px, transparent 1px);
        background-size: 40px 40px;
        mask-image: radial-gradient(circle at 30% 50%, black, transparent 70%);
        pointer-events:none;
    }
    .dp-badge{
        display:inline-flex; align-items:center; gap:8px;
        padding:7px 14px; border-radius:999px;
        background:rgba(0,200,255,0.08);
        border:1px solid rgba(0,200,255,0.35);
        color:var(--dp-cyan); font-size:12px; font-weight:600;
        letter-spacing:.18em; text-transform:uppercase;
    }
    .dp-badge .dot{ width:7px; height:7px; border-radius:50%; background:var(--dp-cyan);
        box-shadow:0 0 12px var(--dp-cyan); animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

    .dp-h1{
        font-family:'Space Grotesk', sans-serif;
        font-size:54px; font-weight:700; line-height:1.05;
        margin:18px 0 14px; letter-spacing:-0.02em;
        background:linear-gradient(135deg,#FFFFFF 0%, #B8D4F0 60%, #00C8FF 100%);
        -webkit-background-clip:text; background-clip:text; color:transparent;
    }
    .dp-sub{ color:var(--dp-text-dim); font-size:16px; line-height:1.7; max-width:560px; }

    .dp-feature-chips{ display:flex; flex-wrap:wrap; gap:10px; margin-top:22px;}
    .dp-chip{
        display:inline-flex; align-items:center; gap:8px;
        padding:8px 14px; border-radius:10px;
        background:rgba(14,23,48,0.7); border:1px solid var(--dp-border-soft);
        color:#CFE2F5; font-size:13px; font-weight:500;
    }
    .dp-chip svg{ color:var(--dp-cyan);}

    /* ---- Section header ---- */
    .dp-section-title{
        display:flex; align-items:center; gap:12px;
        font-family:'Space Grotesk', sans-serif;
        font-size:22px; font-weight:600; color:#fff;
        margin: 28px 0 14px;
    }
    .dp-section-title .bar{ width:4px; height:22px; border-radius:4px;
        background:linear-gradient(180deg,var(--dp-cyan),var(--dp-blue));
        box-shadow:0 0 12px var(--dp-cyan);}
    .dp-section-sub{ color:var(--dp-text-dim); font-size:13px; margin:-6px 0 14px 16px;}

    /* ---- Glass card ---- */
    .dp-card{
        background:linear-gradient(180deg, rgba(14,23,48,0.75), rgba(10,15,31,0.85));
        border:1px solid var(--dp-border-soft);
        border-radius:20px; padding:22px 24px;
        backdrop-filter: blur(14px);
        box-shadow: 0 20px 50px -30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.03);
        transition: all .25s ease;
    }
    .dp-card:hover{
        border-color: rgba(0,200,255,0.35);
        box-shadow: 0 25px 60px -25px rgba(0,200,255,0.25), inset 0 1px 0 rgba(255,255,255,0.05);
        transform: translateY(-2px);
    }

    /* ---- Metric card ---- */
    .dp-metric{
        position:relative; overflow:hidden;
        background:linear-gradient(180deg, rgba(14,23,48,0.85), rgba(10,15,31,0.9));
        border:1px solid rgba(0,200,255,0.22);
        border-radius:20px; padding:22px 22px 24px;
        box-shadow: 0 20px 60px -30px rgba(0,200,255,0.35);
        animation: fadeUp .6s ease both;
    }
    @keyframes fadeUp{from{opacity:0; transform:translateY(14px)}to{opacity:1;transform:none}}
    .dp-metric .label{ color:var(--dp-text-dim); font-size:12px;
        font-weight:600; text-transform:uppercase; letter-spacing:.16em; }
    .dp-metric .value{
        font-family:'Space Grotesk', sans-serif;
        font-size:38px; font-weight:700; margin-top:10px;
        background:linear-gradient(135deg,#FFFFFF, #00C8FF);
        -webkit-background-clip:text; background-clip:text; color:transparent;
    }
    .dp-metric .meta{ color:#9FB6D1; font-size:13px; margin-top:6px;}
    .dp-metric .icon{
        width:42px; height:42px; border-radius:12px;
        display:flex; align-items:center; justify-content:center;
        background:rgba(0,200,255,0.10);
        border:1px solid rgba(0,200,255,0.3);
        color:var(--dp-cyan); margin-bottom:14px;
    }

    /* ---- Stage pill ---- */
    .dp-stage{
        display:inline-flex; align-items:center; gap:8px;
        padding:6px 12px; border-radius:999px;
        font-size:12px; font-weight:600; letter-spacing:.06em;
    }
    .stage-entry{ background:rgba(148,163,184,.12); color:#CBD5E1; border:1px solid rgba(148,163,184,.25);}
    .stage-early{ background:rgba(14,165,233,.12); color:#7DD3FC; border:1px solid rgba(14,165,233,.35);}
    .stage-mid{ background:rgba(37,99,235,.15); color:#93C5FD; border:1px solid rgba(37,99,235,.4);}
    .stage-senior{ background:rgba(0,200,255,.15); color:#67E8F9; border:1px solid rgba(0,200,255,.45);
        box-shadow:0 0 18px rgba(0,200,255,.25);}

    /* ---- Roadmap ---- */
    .dp-milestone{
        position:relative; padding:18px 20px 18px 56px;
        border:1px solid var(--dp-border-soft); border-radius:16px;
        background:linear-gradient(180deg, rgba(14,23,48,0.6), rgba(10,15,31,0.85));
        margin-bottom:14px;
    }
    .dp-milestone .num{
        position:absolute; left:14px; top:18px;
        width:32px; height:32px; border-radius:10px;
        background:linear-gradient(135deg,var(--dp-cyan),var(--dp-blue));
        color:#001019; display:flex; align-items:center; justify-content:center;
        font-weight:800; font-size:14px;
        box-shadow:0 0 18px rgba(0,200,255,.35);
    }
    .dp-milestone h4{ margin:0; color:#fff; font-size:15px; font-weight:600;}
    .dp-milestone p{ margin:6px 0 0; color:var(--dp-text-dim); font-size:13px;}
    .dp-milestone .tags{ display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;}
    .dp-tag{
        font-size:11px; padding:4px 10px; border-radius:999px;
        background:rgba(0,200,255,.08); color:#7DD3FC;
        border:1px solid rgba(0,200,255,.25); font-weight:600;
    }
    .dp-tag.diff-easy{ color:#86EFAC; background:rgba(34,197,94,.08); border-color:rgba(34,197,94,.3);}
    .dp-tag.diff-med{ color:#FCD34D; background:rgba(245,158,11,.08); border-color:rgba(245,158,11,.3);}
    .dp-tag.diff-hard{ color:#FCA5A5; background:rgba(239,68,68,.08); border-color:rgba(239,68,68,.3);}

    /* ---- Opportunity matrix ---- */
    .dp-opp{
        background:linear-gradient(180deg, rgba(14,23,48,0.7), rgba(10,15,31,0.9));
        border:1px solid var(--dp-border-soft);
        border-radius:18px; padding:18px 20px; height:100%;
    }
    .dp-opp h5{ margin:0 0 6px; color:#fff; font-size:14px; font-weight:600;}
    .dp-opp .quad{ font-size:11px; letter-spacing:.14em; text-transform:uppercase;
        color:var(--dp-cyan); font-weight:700; margin-bottom:10px;}
    .dp-opp ul{ margin:0; padding-left:18px; color:#B6CCE6; font-size:13px; line-height:1.85;}

    /* ---- AI report card ---- */
    .dp-ai-card{
        position:relative;
        background:linear-gradient(180deg, rgba(10,15,31,0.95), rgba(5,7,13,0.98));
        border:1px solid rgba(0,200,255,.3);
        border-radius:22px; padding:26px 28px;
        box-shadow: 0 30px 80px -30px rgba(0,200,255,.25);
    }
    .dp-ai-head{ display:flex; align-items:center; gap:12px; margin-bottom:14px;}
    .dp-ai-head .ic{
        width:38px; height:38px; border-radius:12px;
        background:linear-gradient(135deg,var(--dp-cyan),var(--dp-blue));
        display:flex; align-items:center; justify-content:center; color:#001019;
        box-shadow:0 0 22px rgba(0,200,255,.4);
    }
    .dp-ai-head h3{ margin:0; color:#fff; font-family:'Space Grotesk',sans-serif; font-size:20px;}
    .dp-ai-body{ color:#D5E4F5; font-size:14.5px; line-height:1.75;}
    .dp-cursor{ display:inline-block; width:8px; height:18px; background:var(--dp-cyan);
        margin-left:2px; vertical-align:-3px; animation: blink 1s infinite;
        box-shadow:0 0 10px var(--dp-cyan);}
    @keyframes blink{ 50%{ opacity:0 } }

    /* ---- Loading timeline ---- */
    .dp-load{
        background:linear-gradient(180deg, rgba(10,15,31,0.9), rgba(5,7,13,0.95));
        border:1px solid var(--dp-border);
        border-radius:20px; padding:26px 30px;
    }
    .dp-load-step{ display:flex; align-items:center; gap:14px;
        padding:10px 0; color:var(--dp-text-dim); font-size:14px;
        border-bottom:1px solid rgba(148,163,184,.08);}
    .dp-load-step:last-child{ border:none; }
    .dp-load-step .tick{
        width:24px; height:24px; border-radius:50%;
        border:1.5px solid rgba(148,163,184,.3);
        display:flex; align-items:center; justify-content:center; color:transparent; font-size:13px;
    }
    .dp-load-step.done{ color:#E6EEF8; }
    .dp-load-step.done .tick{
        background:linear-gradient(135deg,var(--dp-cyan),var(--dp-blue));
        border-color:transparent; color:#001019; box-shadow:0 0 14px rgba(0,200,255,.4);
    }
    .dp-load-step.active{ color:var(--dp-cyan); }
    .dp-load-step.active .tick{
        border-color:var(--dp-cyan);
        animation: spin 1s linear infinite;
        border-top-color:transparent;
    }
    @keyframes spin{ to{ transform:rotate(360deg) } }

    /* ---- Streamlit overrides ---- */
    div[data-testid="stForm"]{
        background:linear-gradient(180deg, rgba(14,23,48,0.6), rgba(10,15,31,0.85));
        border:1px solid var(--dp-border-soft) !important;
        border-radius:22px !important; padding:26px !important;
        box-shadow: 0 20px 60px -30px rgba(0,0,0,.6);
    }
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div, .stMultiSelect > div > div{
        background:rgba(5,7,13,.6) !important;
        border:1px solid rgba(148,163,184,.18) !important;
        color:#E6EEF8 !important; border-radius:12px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus{
        border-color:var(--dp-cyan) !important; box-shadow:0 0 0 3px rgba(0,200,255,.15) !important;
    }
    label, .stMarkdown p { color:#CFE2F5 !important; }

    /* Predict button */
    .stForm button[kind="formSubmit"], .stButton > button{
        background:linear-gradient(135deg, var(--dp-blue) 0%, var(--dp-sky) 50%, var(--dp-cyan) 100%) !important;
        color:#001019 !important; font-weight:700 !important;
        border:none !important; border-radius:14px !important;
        padding:14px 22px !important; font-size:15px !important;
        letter-spacing:.02em !important;
        box-shadow:0 14px 40px -10px rgba(0,200,255,.55), inset 0 1px 0 rgba(255,255,255,.3) !important;
        transition: all .25s ease !important;
    }
    .stForm button[kind="formSubmit"]:hover, .stButton > button:hover{
        transform:translateY(-2px) !important;
        box-shadow:0 22px 50px -10px rgba(0,200,255,.7) !important;
    }

    .stDownloadButton > button{
        background:rgba(0,200,255,.08) !important; color:#7DD3FC !important;
        border:1px solid rgba(0,200,255,.35) !important; font-weight:600 !important;
        border-radius:12px !important;
    }

    /* st_tags */
    .st-tags, .st-tags > div { background:transparent !important; }

    /* Empty state */
    .dp-empty{
        text-align:center; padding:60px 30px;
        border:1.5px dashed rgba(0,200,255,.25); border-radius:22px;
        background:radial-gradient(400px 200px at 50% 0%, rgba(0,200,255,.08), transparent 70%);
    }
    .dp-empty h3{ color:#fff; font-family:'Space Grotesk',sans-serif; margin:18px 0 8px;}
    .dp-empty p{ color:var(--dp-text-dim); max-width:480px; margin:0 auto;}

    @media (max-width: 900px){
        .dp-h1{ font-size:36px; }
        .dp-hero{ padding:28px 22px;}
        .dp-mentor{ top:auto; bottom:20px; right:20px;}
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

# Mobile/Tablet responsiveness CSS block:
_responsive_css = ASSETS_DIR / "css" / "page6_responsive.css"
if _responsive_css.exists():
    with open(_responsive_css, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
hero_l, hero_r = st.columns([1.15, 1])

with hero_l:
    st.markdown(
        """
        <div class="dp-hero">
            <div class="dp-badge"><span class="dot"></span> AI Salary Intelligence</div>
            <div class="dp-h1">Discover Your<br/>Market Value</div>
            <div class="dp-sub">
                Predict your salary potential, benchmark against the market, identify
                earning opportunities, and generate AI-powered compensation growth strategies.
            </div>
            <div class="dp-feature-chips">
                <span class="dp-chip">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                    </svg>
                    Salary Intelligence
                </span>
                <span class="dp-chip">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-5"/>
                    </svg>
                    Market Benchmarking
                </span>
                <span class="dp-chip">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2a4 4 0 0 0-4 4v1H7a3 3 0 0 0-3 3v2a3 3 0 0 0 2 2.83V19a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-4.17A3 3 0 0 0 20 12v-2a3 3 0 0 0-3-3h-1V6a4 4 0 0 0-4-4Z"/>
                    </svg>
                    AI Powered
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_r:
    components.html(
        """
        <div class="dp-hero" style="display:flex;align-items:center;justify-content:center;min-height:340px;">
            <svg viewBox="0 0 400 300" width="100%" height="300" xmlns="http://www.w3.org/2000/svg">

            <defs>
                <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#00C8FF" stop-opacity="0.45"/>
                    <stop offset="100%" stop-color="#00C8FF" stop-opacity="0"/>
                </radialGradient>

                <filter id="neonGlow">
                    <feGaussianBlur stdDeviation="8" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>

            <!-- Background Glow -->
            <circle cx="200" cy="150" r="90"
                    fill="url(#bgGlow)">
                <animate attributeName="r"
                        values="85;95;85"
                        dur="5s"
                        repeatCount="indefinite"/>
            </circle>

            <!-- Rotating Group -->
            <g transform-origin="200 150">
                <animateTransform
                    attributeName="transform"
                    type="rotate"
                    values="-4 200 150;4 200 150;-4 200 150"
                    dur="8s"
                    repeatCount="indefinite"/>

                <!-- Outer Ring -->
                <circle cx="200" cy="150"
                        r="80"
                        fill="none"
                        stroke="#00C8FF"
                        stroke-width="2"
                        opacity="0.35"/>

                <!-- Inner Ring -->
                <circle cx="200" cy="150"
                        r="65"
                        fill="none"
                        stroke="#0EA5E9"
                        stroke-width="1.5"
                        opacity="0.25"/>

                <!-- Rupee Symbol -->
                <text x="200"
                    y="180"
                    text-anchor="middle"
                    font-size="95"
                    font-weight="700"
                    fill="#00C8FF"
                    filter="url(#neonGlow)"
                    style="font-family: Inter, Arial, sans-serif;">
                    ₹
                </text>

            </g>

            <!-- Floating Particles -->
            <circle cx="110" cy="95" r="2" fill="#00C8FF" opacity="0.7">
                <animate attributeName="opacity"
                        values="0.2;1;0.2"
                        dur="3s"
                        repeatCount="indefinite"/>
            </circle>

            <circle cx="300" cy="90" r="2" fill="#00C8FF" opacity="0.7">
                <animate attributeName="opacity"
                        values="0.2;1;0.2"
                        dur="4s"
                        repeatCount="indefinite"/>
            </circle>

            <circle cx="320" cy="220" r="2" fill="#00C8FF" opacity="0.7">
                <animate attributeName="opacity"
                        values="0.2;1;0.2"
                        dur="5s"
                        repeatCount="indefinite"/>
            </circle>

        </svg>
        </div>
        """,
         height=340
    )

# ============================================================
# DATA
# ============================================================
job_titles = sorted(set(salary_model.JOB_TITLE_CANONICAL.values()))
location_options = list(dict.fromkeys(["Remote", *salary_model.TOP_LOCATIONS, "Other"]))

ROLE_DESCRIPTIONS = {
    "Data Scientist": "Builds predictive models and uncovers insights from data.",
    "Data Analyst": "Translates data into business decisions and dashboards.",
    "Data Engineer": "Builds and maintains scalable data infrastructure.",
    "Machine Learning Engineer": "Productionizes ML models at scale.",
    "Software Engineer": "Designs and ships production software systems.",
    "Business Analyst": "Bridges business needs and data-driven solutions.",
}

# ============================================================
# HELPERS (unchanged behavior)
# ============================================================
def evaluate_experience(job_title: str, experience_years: float) -> str:
    if experience_years < 1:
        level = "Entry-level"
        message = "You are likely being evaluated on fundamentals, learning speed, and basic execution."
    elif experience_years < 3:
        level = "Early-career"
        message = "You should already show clear project ownership, practical tooling, and measurable contributions."
    elif experience_years < 6:
        level = "Mid-level"
        message = "Employers usually expect independent delivery, strong domain depth, and visible business impact."
    else:
        level = "Senior"
        message = "Your compensation can rise sharply when you demonstrate leadership, strategy, and mentoring ability."
    return (
        f"For a {job_title} with {experience_years:.1f} years of experience, your profile looks {level.lower()}. {message}"
    )

def career_stage(exp: float):
    if exp < 1: return ("Entry Level", "stage-entry")
    if exp < 3: return ("Early Career", "stage-early")
    if exp < 6: return ("Mid Level", "stage-mid")
    return ("Senior", "stage-senior")

def salary_potential(exp: float, lpa: float):
    score = (exp * 0.6) + (lpa * 0.4)
    if score < 4: return "Low"
    if score < 10: return "Moderate"
    if score < 20: return "Strong"
    return "High Growth"

def format_lpa(value: float) -> str:
    return f"₹ {value:.1f} LPA"

if "show_salary_tips" not in st.session_state:
    st.session_state["show_salary_tips"] = False

# ============================================================
# INPUT FORM
# ============================================================
st.markdown('<div class="dp-section-title"><span class="bar"></span>Build Your Profile</div>', unsafe_allow_html=True)
st.markdown('<div class="dp-section-sub">Provide your role, experience, location, and skills to generate a precise compensation estimate.</div>', unsafe_allow_html=True)

with st.form("salary_prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Target Role**")
        job_title = st.selectbox(
            "Target Role",
            job_titles,
            index=job_titles.index("Data Scientist") if "Data Scientist" in job_titles else 0,
            label_visibility="collapsed",
        )
        role_desc = ROLE_DESCRIPTIONS.get(job_title, "AI-aligned career path in the data ecosystem.")
        st.markdown(
            f"<div style='color:#8FA3BF;font-size:12.5px;margin-top:-6px;'>{html.escape(role_desc)}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown("**Experience (years)**")
        experience = st.number_input(
            "Experience",
            min_value=0.0, max_value=40.0, value=0.0, step=0.5,
            label_visibility="collapsed",
        )
        stage_label, stage_cls = career_stage(float(experience))
        st.markdown(
            f"<div style='margin-top:6px'><span class='dp-stage {stage_cls}'>● {stage_label}</span></div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("**Location**")
        location = st.selectbox(
            "Location",
            location_options, index=0,
            label_visibility="collapsed",
        )
        st.markdown(
            f"<div style='color:#8FA3BF;font-size:12.5px;margin-top:-6px;'>"
            f"Market intelligence calibrated for <b style='color:#7DD3FC'>{html.escape(location)}</b>.</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown("**Skills**")
        resume_skills = st.session_state.get("resume_skills", [])

        TECHNICAL_SKILLS = [skill.lower() for skill in TECHNICAL_SKILLS]

        skills_ = st_tags(
            label="",
            value=resume_skills,
            suggestions=TECHNICAL_SKILLS,
            key="salary_skills_tags",
        )
        
        skills = list(dict.fromkeys(skill.strip().lower() for skill in skills_))

        skill_count = len([s for s in skills if s.strip()])
        st.markdown(
            f"<div style='margin-top:6px;color:#7DD3FC;font-size:12.5px;font-weight:600;'>"
            f"✦ {skill_count} Skills Detected</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    submit_prediction = st.form_submit_button("✦  Predict Salary", use_container_width=True)

# ============================================================
# EMPTY STATE (pre-prediction)
# ============================================================
if not submit_prediction and "latest_salary_prediction" not in st.session_state:
    st.markdown(
        """
        <div class="dp-empty" style="margin-top:28px;">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#00C8FF"
                 stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-5"/>
            </svg>
            <h3>Ready to estimate your market value</h3>
            <p>Complete your profile above to discover your earning potential, benchmark against the market,
            and unlock an AI-generated salary growth roadmap.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# PREDICTION FLOW
# ============================================================
if submit_prediction or "latest_salary_prediction" in st.session_state:
    if submit_prediction:
        normalized_skills_list = [s.strip() for s in skills if s.strip()]
        if len(normalized_skills_list) < 5:
            st.error("Please enter at least 5 skills before predicting salary.")
            st.stop()

        normalized_skills = ", ".join(normalized_skills_list)
        
        # Store prediction parameters for persistent display
        st.session_state["_prediction_params"] = {
            "job_title": job_title,
            "experience": float(experience),
            "location": location,
            "skills": normalized_skills,
            "skills_list": normalized_skills_list,
        }

        # Animated loading timeline
        steps = [
            "Analyzing Profile",
            "Evaluating Experience",
            "Benchmarking Skills",
            "Comparing Market Data",
            "Estimating Compensation",
            "Generating Insights",
        ]
        loader = st.empty()

        def render_loader(active_idx: int):
            rows = ""
            for i, s in enumerate(steps):
                if i < active_idx:
                    cls, ic = "done", "✓"
                elif i == active_idx:
                    cls, ic = "active", ""
                else:
                    cls, ic = "", ""
                rows += f"<div class='dp-load-step {cls}'><span class='tick'>{ic}</span>{s}</div>"
            loader.markdown(f"<div class='dp-load'>{rows}</div>", unsafe_allow_html=True)

        for i in range(len(steps)):
            render_loader(i)
            time.sleep(0.35)

        # Actual prediction (backend untouched)
        predicted_salary = salary_model.master_salary_prediction_pipeline(
            Job_title=job_title,
            experience=float(experience),
            location=location,
            skills=normalized_skills,
        )
        render_loader(len(steps))
        time.sleep(0.2)
        loader.empty()

        predicted_salary_lpa = predicted_salary / 100000
        st.session_state["latest_salary_prediction"] = {
            "role": job_title,
            "experience": float(experience),
            "location": location,
            "skills": normalized_skills,
            "skills_list": normalized_skills_list,
            "predicted_salary": predicted_salary,
        }

        user_id = st.session_state.get("user_id")
        if user_id:
            try:
                save_salary_prediction(
                    user_id=user_id,
                    role=job_title,
                    experience=float(experience),
                    location=location,
                    skills=normalized_skills,
                    predicted_salary=predicted_salary,
                )
            except Exception as exc:
                st.warning(f"Salary was predicted, but the history record could not be saved: {exc}")

    else:
        latest_prediction = st.session_state["latest_salary_prediction"]
        job_title = latest_prediction["role"]
        experience = float(latest_prediction["experience"])
        location = latest_prediction["location"]
        normalized_skills = latest_prediction["skills"]
        normalized_skills_list = latest_prediction.get("skills_list") or [
            s.strip() for s in normalized_skills.split(",") if s.strip()
        ]
        predicted_salary = latest_prediction["predicted_salary"]
        predicted_salary_lpa = predicted_salary / 100000
        st.session_state["_prediction_params"] = {
            "job_title": job_title,
            "experience": float(experience),
            "location": location,
            "skills": normalized_skills,
            "skills_list": normalized_skills_list,
        }
    # ====================================================
    # SALARY OVERVIEW
    # ====================================================
    stage_label, stage_cls = career_stage(float(experience))
    potential = salary_potential(float(experience), predicted_salary_lpa)

    st.markdown('<div class="dp-section-title"><span class="bar"></span>Salary Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="dp-metric">
              <div class="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <div class="label">Predicted Salary</div>
              <div class="value">{format_lpa(predicted_salary_lpa)}</div>
              <div class="meta">Annual compensation estimate</div>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""
            <div class="dp-metric">
              <div class="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="8.5" cy="7" r="4"/><path d="M20 8v6M23 11h-6"/>
                </svg>
              </div>
              <div class="label">Career Level</div>
              <div class="value" style="font-size:28px;">{stage_label}</div>
              <div class="meta">{float(experience):.1f} years experience</div>
            </div>
            """, unsafe_allow_html=True)
    with c3:
        st.markdown(
            f"""
            <div class="dp-metric">
              <div class="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
                </svg>
              </div>
              <div class="label">Salary Potential</div>
              <div class="value" style="font-size:28px;">{potential}</div>
              <div class="meta">Projected growth trajectory</div>
            </div>
            """, unsafe_allow_html=True)

    # ====================================================
    # MARKET POSITIONING
    # ====================================================
    st.markdown('<div class="dp-section-title"><span class="bar"></span>Market Position</div>', unsafe_allow_html=True)

    industry_avg_lpa = max(6.0, predicted_salary_lpa * 0.85)  # benchmark proxy
    above = predicted_salary_lpa >= industry_avg_lpa
    diff_pct = ((predicted_salary_lpa - industry_avg_lpa) / industry_avg_lpa) * 100

    mc1, mc2 = st.columns([1.5, 1])
    with mc1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Industry Average", "Your Estimate"],
            y=[industry_avg_lpa, predicted_salary_lpa],
            marker=dict(
                color=["rgba(148,163,184,0.55)", "rgba(0,200,255,0.95)"],
                line=dict(color=["rgba(148,163,184,0.7)", "#00C8FF"], width=2),
            ),
            text=[f"{industry_avg_lpa:.1f} LPA", f"{predicted_salary_lpa:.1f} LPA"],
            textposition="outside",
            textfont=dict(color="#E6EEF8", size=14, family="Space Grotesk"),
            width=[0.45, 0.45],
        ))
        fig.update_layout(
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=20),
            yaxis=dict(title="LPA", color="#8FA3BF", gridcolor="rgba(148,163,184,0.08)"),
            xaxis=dict(color="#CFE2F5"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with mc2:
        verdict = "You are above market average" if above else "You are below market average"
        verdict_color = "#67E8F9" if above else "#FCA5A5"
        st.markdown(
            f"""
            <div class="dp-card" style="height:100%;display:flex;flex-direction:column;justify-content:center;">
                <div style="color:#8FA3BF;font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;">
                    Market Verdict
                </div>
                <div style="font-family:'Space Grotesk';font-size:22px;color:{verdict_color};margin:10px 0 8px;font-weight:700;">
                    {verdict}
                </div>
                <div style="color:#B6CCE6;font-size:13.5px;line-height:1.7;">
                    Your predicted salary is <b style="color:#fff">{abs(diff_pct):.1f}%</b>
                    {"higher" if above else "lower"} than the benchmark for this role and experience band.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ====================================================
    # SALARY BREAKDOWN — Radar
    # ====================================================
    st.markdown('<div class="dp-section-title"><span class="bar"></span>Salary Breakdown</div>', unsafe_allow_html=True)

    exp_score = min(100, float(experience) * 12 + 25)
    skill_score = min(100, len(normalized_skills_list) * 4 + 30)
    loc_score = 90 if location in ["Bengaluru", "Bangalore", "Mumbai", "Hyderabad", "Remote"] else 65

    bc1, bc2 = st.columns([1, 1.2])
    with bc1:
        for label, val, icon_svg in [
            ("Experience Impact", exp_score,
             '<path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="10"/>'),
            ("Skills Impact", skill_score,
             '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>'),
            ("Location Impact", loc_score,
             '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'),
        ]:
            st.markdown(
                f"""
                <div class="dp-card" style="margin-bottom:12px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00C8FF"
                                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon_svg}</svg>
                            <span style="color:#fff;font-weight:600;font-size:14px;">{label}</span>
                        </div>
                        <span style="color:#7DD3FC;font-weight:700;font-family:'Space Grotesk';">{int(val)}</span>
                    </div>
                    <div style="margin-top:12px;height:8px;border-radius:99px;background:rgba(148,163,184,0.12);overflow:hidden;">
                        <div style="height:100%;width:{val}%;border-radius:99px;
                                    background:linear-gradient(90deg,#2563EB,#0EA5E9,#00C8FF);
                                    box-shadow:0 0 12px rgba(0,200,255,.5);"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with bc2:
        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=[exp_score, skill_score, loc_score, min(100, predicted_salary_lpa * 4), 75],
            theta=["Experience", "Skills", "Location", "Compensation", "Market Fit"],
            fill="toself",
            line=dict(color="#00C8FF", width=2),
            fillcolor="rgba(0,200,255,0.22)",
            name="Your Profile",
        ))
        radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100],
                                color="#8FA3BF", gridcolor="rgba(148,163,184,0.15)"),
                angularaxis=dict(color="#CFE2F5", gridcolor="rgba(148,163,184,0.12)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            height=380, margin=dict(l=30, r=30, t=20, b=20),
        )
        st.plotly_chart(radar, use_container_width=True)

    # ====================================================
    # CAREER COMPENSATION INSIGHTS
    # ====================================================
    st.markdown('<div class="dp-section-title"><span class="bar"></span>Career Compensation Insights</div>', unsafe_allow_html=True)
    exp_insight = evaluate_experience(job_title, float(experience))
    st.markdown(
        f"""
        <div class="dp-card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:36px;height:36px;border-radius:10px;
                                background:linear-gradient(135deg,#00C8FF,#2563EB);
                                display:flex;align-items:center;justify-content:center;color:#001019;
                                box-shadow:0 0 18px rgba(0,200,255,.35);">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                           stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2a4 4 0 0 0-4 4v1H7a3 3 0 0 0-3 3v2a3 3 0 0 0 2 2.83V19a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-4.17A3 3 0 0 0 20 12v-2a3 3 0 0 0-3-3h-1V6a4 4 0 0 0-4-4Z"/>
                      </svg>
                    </div>
                    <div>
                        <div style="color:#fff;font-weight:600;font-size:15px;">Current Career Stage</div>
                        <div style="color:#8FA3BF;font-size:12px;">AI-evaluated experience profile</div>
                    </div>
                </div>
                <span class="dp-stage {stage_cls}">● {stage_label}</span>
            </div>
            <div style="color:#D5E4F5;font-size:14.2px;line-height:1.75;">{html.escape(exp_insight)}</div>
        </div>
        """, unsafe_allow_html=True)

    # ====================================================
    # SALARY GROWTH ROADMAP
    # ====================================================
    st.markdown('<div class="dp-section-title"><span class="bar"></span>Salary Growth Roadmap</div>', unsafe_allow_html=True)

    if float(experience) < 2:
        milestones = [
            ("Strengthen Core Foundations", f"Deepen fundamentals critical for {job_title} interviews.", "Easy", "diff-easy", "+1–2 LPA"),
            ("Ship 2 Portfolio Projects", "Build end-to-end projects with real datasets and clean READMEs.", "Medium", "diff-med", "+2–3 LPA"),
            ("Land First Specialist Role", "Target roles that match your strongest 3 skills.", "Medium", "diff-med", "+3–4 LPA"),
            ("Build Domain Expertise", "Pick one industry vertical (fintech, health, retail) and go deep.", "Hard", "diff-hard", "+4–6 LPA"),
        ]
    elif float(experience) < 5:
        milestones = [
            ("Master Advanced Tooling", "Production ML, cloud platforms, and modern data stack.", "Medium", "diff-med", "+2–4 LPA"),
            ("Lead a High-Impact Project", "Own a project visible to leadership with measurable ROI.", "Medium", "diff-med", "+3–5 LPA"),
            ("Cultivate Domain Authority", "Publish, speak, or open-source in your niche.", "Hard", "diff-hard", "+4–7 LPA"),
            ("Target Higher-Paying Roles", "Move to scale-ups or top-tier companies hiring senior IC's.", "Hard", "diff-hard", "+6–10 LPA"),
        ]
    else:
        milestones = [
            ("Sharpen Leadership Stack", "Cross-team influence, mentoring, and strategic planning.", "Medium", "diff-med", "+4–8 LPA"),
            ("Drive Org-Level Impact", "Lead initiatives with company-wide outcomes.", "Hard", "diff-hard", "+6–12 LPA"),
            ("Specialize in High-Leverage Domains", "GenAI, MLOps, Platform — areas with senior-pay premiums.", "Hard", "diff-hard", "+8–14 LPA"),
            ("Move into Staff / Principal Tracks", "Target Staff, Principal, or Head-of roles.", "Hard", "diff-hard", "+10–20 LPA"),
        ]

    for i, (title, desc, diff, diff_cls, impact) in enumerate(milestones, 1):
        st.markdown(
            f"""
            <div class="dp-milestone">
                <div class="num">{i}</div>
                <h4>{html.escape(title)}</h4>
                <p>{html.escape(desc)}</p>
                <div class="tags">
                    <span class="dp-tag {diff_cls}">Difficulty: {diff}</span>
                    <span class="dp-tag">Impact: {impact}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ====================================================
    # OPPORTUNITY MATRIX
    # ====================================================
    st.markdown('<div class="dp-section-title"><span class="bar"></span>Salary Boost Opportunity Matrix</div>', unsafe_allow_html=True)
    o1, o2, o3 = st.columns(3)
    quadrants = [
        ("High Impact · Easy Effort", ["Improve resume + LinkedIn keywords",
                                       "Negotiation prep for next offer",
                                       "Add measurable outcomes to projects"]),
        ("High Impact · Medium Effort", ["Learn Cloud Platforms (AWS / GCP)",
                                         "Master GenAI Tools & LLM workflows",
                                         "Contribute to high-visibility OSS"]),
        ("Long-Term High Salary Investments", ["Advanced MLOps & system design",
                                               "Leadership & mentoring skills",
                                               "Deep domain specialization"]),
    ]
    for col, (q, items) in zip([o1, o2, o3], quadrants):
        with col:
            lis = "".join(f"<li>{html.escape(x)}</li>" for x in items)
            st.markdown(
                f"<div class='dp-opp'><div class='quad'>● {q}</div>"
                f"<ul>{lis}</ul></div>",
                unsafe_allow_html=True,
            )

    st.info(
        "This is an estimate only. Actual salary varies with company budget, location policy, "
        "interview performance, team size, market timing, and negotiated benefits."
    )

# ============================================================
# AI SALARY COACH
# ============================================================
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown('<div class="dp-section-title"><span class="bar"></span>AI Salary Coach</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dp-section-sub">Generate a personalized AI strategy to maximize your next compensation jump.</div>',
    unsafe_allow_html=True,
)

ai_clicked = st.button("✦  Generate AI Salary Strategy", use_container_width=True, key="gen_ai_tips")

if ai_clicked:
    params = st.session_state.get("_prediction_params")
    if not params and "latest_salary_prediction" in st.session_state:
        latest_prediction = st.session_state["latest_salary_prediction"]
        params = {
            "job_title": latest_prediction["role"],
            "experience": float(latest_prediction["experience"]),
            "location": latest_prediction["location"],
            "skills": latest_prediction["skills"],
            "skills_list": latest_prediction.get("skills_list") or [
                s.strip() for s in latest_prediction["skills"].split(",") if s.strip()
            ],
        }
        st.session_state["_prediction_params"] = params

    if not params:
        st.warning("Please predict your salary first, then generate the AI salary strategy.")
        st.stop()

    _job_title = params["job_title"]
    _experience = params["experience"]
    _location = params["location"]
    _skills = params["skills"]
    _skills_list = params["skills_list"]

    with st.spinner("Generating your AI compensation strategy..."):
        feedback = generate_salary_tips(_job_title, _experience, _location, _skills)
        st.session_state["salary_feedback"] = feedback

# ============================================================
# AI REPORT (streaming-style render)
# ============================================================
if "salary_feedback" in st.session_state:
    feedback_text = st.session_state["salary_feedback"]

    st.markdown(
        """
        <div class="dp-ai-card">
            <div class="dp-ai-head">
                <div class="ic">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2L14 8l6 2-6 2-2 6-2-6-6-2 6-2z"/>
                    </svg>
                </div>
                <h3>AI Salary Intelligence</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Live typing simulation (only on first render of a new feedback)
    sig = hash(feedback_text)
    if st.session_state.get("_last_streamed_sig") != sig:
        placeholder = st.empty()
        buffered = ""
        # Stream by line for performance
        for line in feedback_text.splitlines(keepends=True):
            buffered += line
            placeholder.markdown(
                f"<div class='dp-ai-body'>{buffered}<span class='dp-cursor'></span></div>",
                unsafe_allow_html=True,
            )
            time.sleep(0.025)
        placeholder.markdown(f"<div class='dp-ai-body'>{feedback_text}</div>", unsafe_allow_html=True)
        st.session_state["_last_streamed_sig"] = sig
    else:
        with st.expander("View Detailed AI Feedback", expanded=True):
            st.markdown(feedback_text)

    # Actions
    a1, a2 = st.columns([1, 1])
    with a1:
        b64 = base64.b64encode(feedback_text.encode()).decode()
        st.markdown(
            f"""
            <a href="data:text/plain;base64,{b64}" download="AI_salary_Report.txt"
               style="display:block;text-align:center;padding:.7rem;border-radius:12px;
                      background:rgba(255,255,255,0.04);border:1px solid var(--dp-border-strong);
                      color:var(--dp-text);text-decoration:none;font-weight:600;">
              Copy / Save Text
            </a>
            """,
            unsafe_allow_html=True,
        )
    
    with a2:
        pdf_data = text_to_pdf(st.session_state["salary_feedback"])
        st.download_button(
            label="↓  Download PDF Report",
            data=pdf_data,
            file_name="AI_salary_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
