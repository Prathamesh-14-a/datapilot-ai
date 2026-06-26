import os
import time
import base64
import textwrap
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

from src.auth.session_manager import is_authenticated
from components.sidebar import show_sidebar
from src.database.crud import (
    get_analysis_history,
    get_user_resumes,
    save_analysis,
    save_job_fit_history,
    save_resume,
)
from src.job_fit.predictor import ROLE_SKILLS, predict_job_fit
from src.resume_matching.resume_parser import (
    TECHNICAL_SKILLS,
    extract_resume_text,
    extract_skills,
)
from src.ATS.master_pipeline import full_resume_analysis
from src.llm.resume_feedback import generate_resume_feedback
from src.text_to_pdf.text_to_pdf import text_to_pdf


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Resume Analyzer · DataPilot AI",
    page_icon="assets\mini_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# AUTH
# ==========================================================
if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()
user_id = st.session_state["user_id"]


# ==========================================================
# GLOBAL STYLES — DataPilot AI brand system
# ==========================================================
st.markdown(
    """
    <style>
    /* ---------- Tokens ---------- */
    :root {
        --dp-cyan: #00C8FF;
        --dp-sky: #0EA5E9;
        --dp-blue: #2563EB;
        --dp-bg-0: #060B1A;
        --dp-bg-1: #0A1228;
        --dp-bg-2: #0E1A38;
        --dp-text: #E6EEFB;
        --dp-muted: #8FA3C7;
        --dp-border: rgba(148, 184, 255, 0.14);
        --dp-border-strong: rgba(0, 200, 255, 0.35);
        --dp-glass: rgba(15, 26, 56, 0.55);
        --dp-glass-2: rgba(11, 20, 44, 0.75);
        --dp-success: #10B981;
        --dp-warn: #F59E0B;
        --dp-danger: #F43F5E;
        --dp-gradient: linear-gradient(135deg, #00C8FF 0%, #0EA5E9 45%, #2563EB 100%);
        --dp-shadow: 0 10px 40px -10px rgba(0, 200, 255, 0.25);
    }

    /* ---------- App background ---------- */
    .stApp {
        background:
          radial-gradient(1200px 700px at 85% -10%, rgba(14,165,233,0.18), transparent 60%),
          radial-gradient(900px 600px at -10% 20%, rgba(37,99,235,0.18), transparent 55%),
          linear-gradient(180deg, #05091A 0%, #070D22 60%, #05091A 100%);
        color: var(--dp-text);
    }
    .stApp::before {
        content: "";
        position: fixed; inset: 0;
        background-image:
          linear-gradient(rgba(148,184,255,0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(148,184,255,0.05) 1px, transparent 1px);
        background-size: 48px 48px;
        pointer-events: none;
        z-index: 0;
    }
    .block-container { position: relative; z-index: 1; padding-top: 1.2rem; max-width: 1280px; }

    /* ---------- Typography ---------- */
    html, body, [class*="css"] {
        font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--dp-text);
        letter-spacing: -0.005em;
    }
    h1, h2, h3, h4 { color: var(--dp-text); letter-spacing: -0.02em; font-weight: 700; }

    /* Hide default Streamlit chrome */
    #MainMenu {
    visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* ---------- Glass primitives ---------- */
    .dp-glass {
        background: var(--dp-glass);
        border: 1px solid var(--dp-border);
        border-radius: 18px;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
    }
    .dp-glass:hover {
        transform: translateY(-2px);
        border-color: var(--dp-border-strong);
        box-shadow: var(--dp-shadow);
    }

    /* ---------- Hero ---------- */
    .dp-hero {
        position: relative;
        padding: 2.2rem 2.4rem;
        border-radius: 24px;
        background:
          radial-gradient(600px 280px at 90% 10%, rgba(0,200,255,0.18), transparent 60%),
          linear-gradient(135deg, rgba(14,26,56,0.85), rgba(8,16,38,0.85));
        border: 1px solid var(--dp-border);
        overflow: hidden;
        margin-bottom: 1.5rem;
    }
    .dp-hero::after {
        content: "";
        position: absolute; inset: -1px;
        border-radius: 24px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(0,200,255,.5), transparent 40%, rgba(37,99,235,.4));
        -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none;
    }
    .dp-badge {
        display: inline-flex; align-items: center; gap: .5rem;
        padding: .35rem .8rem;
        border-radius: 999px;
        background: rgba(0,200,255,0.10);
        border: 1px solid rgba(0,200,255,0.35);
        color: #7FE3FF;
        font-size: .78rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: .08em;
    }
    .dp-badge .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--dp-cyan);
        box-shadow: 0 0 12px var(--dp-cyan);
        animation: dp-pulse 2s infinite;
    }
    @keyframes dp-pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: .5; transform: scale(1.3); }
    }
    .dp-h1 {
        font-size: clamp(1.8rem, 3vw, 2.6rem);
        font-weight: 800;
        line-height: 1.1;
        margin: 1rem 0 .8rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #BCE6FF 60%, #6BB6FF 100%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .dp-sub { color: var(--dp-muted); font-size: 1.02rem; line-height: 1.6; max-width: 620px; }
    .dp-feat-row { display:flex; flex-wrap:wrap; gap:.5rem; margin-top: 1.2rem; }
    .dp-feat {
        display:inline-flex; align-items:center; gap:.4rem;
        padding:.4rem .8rem; border-radius: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--dp-border);
        color: var(--dp-text); font-size:.82rem; font-weight: 500;
    }
    .dp-feat svg { width: 14px; height: 14px; color: var(--dp-cyan); }

    /* Hero visual */
    .dp-hero-visual {
        position: relative;
        height: 240px;
        border-radius: 18px;
        background:
          radial-gradient(400px 200px at 50% 50%, rgba(0,200,255,0.18), transparent 70%),
          linear-gradient(135deg, rgba(0,200,255,0.08), rgba(37,99,235,0.08));
        border: 1px solid var(--dp-border);
        overflow: hidden;
        display:flex; align-items:center; justify-content:center;
    }
    .dp-scan-doc {
        position: relative; width: 150px; height: 190px;
        background: linear-gradient(180deg, #0E1A38, #0A1228);
        border: 1px solid var(--dp-border-strong);
        border-radius: 10px;
        box-shadow: 0 10px 40px rgba(0,200,255,0.25);
        overflow: hidden;
    }
    .dp-scan-doc::before {
        content:""; position:absolute; left:14px; right:14px; top:18px;
        height: 8px; border-radius: 4px;
        background: rgba(255,255,255,0.15);
        box-shadow:
          0 18px 0 rgba(255,255,255,0.1),
          0 36px 0 rgba(255,255,255,0.1),
          0 54px 0 rgba(255,255,255,0.08),
          0 72px 0 rgba(255,255,255,0.08),
          0 90px 0 rgba(255,255,255,0.06);
    }
    .dp-scan-line {
        position:absolute; left:0; right:0; height: 2px;
        background: linear-gradient(90deg, transparent, var(--dp-cyan), transparent);
        box-shadow: 0 0 18px var(--dp-cyan);
        animation: dp-scan 2.6s linear infinite;
    }
    @keyframes dp-scan {
        0% { top: 0; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { top: 100%; opacity: 0; }
    }
    .dp-particle {
        position:absolute; width: 4px; height: 4px; border-radius: 50%;
        background: var(--dp-cyan); box-shadow: 0 0 10px var(--dp-cyan);
        animation: dp-float 4s ease-in-out infinite;
    }
    @keyframes dp-float {
        0%, 100% { transform: translateY(0); opacity: .3; }
        50% { transform: translateY(-20px); opacity: 1; }
    }

    /* ---------- Floating AI Mentor button ---------- */
    .dp-fab-wrap {
        position: fixed; top: 18px; right: 22px; z-index: 9999;
    }
    .dp-fab {
        display:inline-flex; align-items:center; gap:.55rem;
        padding: .65rem 1.1rem;
        border-radius: 999px;
        background: rgba(8,16,38,0.7);
        border: 1px solid var(--dp-border-strong);
        color: var(--dp-text); font-weight: 600; font-size:.88rem;
        text-decoration: none !important;
        backdrop-filter: blur(14px);
        box-shadow: 0 0 22px rgba(0,200,255,0.35), inset 0 0 0 1px rgba(255,255,255,0.04);
        transition: all .25s ease;
    }
    .dp-fab:hover { transform: translateY(-2px); box-shadow: 0 0 32px rgba(0,200,255,0.55); }
    .dp-fab svg { width: 16px; height: 16px; color: var(--dp-cyan); }

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

    /* ---------- File uploader skin ---------- */
    [data-testid="stFileUploader"] section {
        background: var(--dp-glass) !important;
        border: 1.5px dashed var(--dp-border-strong) !important;
        border-radius: 16px !important;
        padding: 1.4rem !important;
        transition: all .25s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--dp-cyan) !important;
        box-shadow: 0 0 30px rgba(0,200,255,0.20);
    }
    [data-testid="stFileUploader"] section * { color: var(--dp-text) !important; }
    [data-testid="stFileUploader"] button {
        background: var(--dp-gradient) !important;
        color: #001022 !important; border: none !important;
        font-weight: 700 !important;
    }

    /* ---------- Selectbox ---------- */
    [data-baseweb="select"] > div {
        background: var(--dp-glass) !important;
        border: 1px solid var(--dp-border) !important;
        border-radius: 12px !important;
        color: var(--dp-text) !important;
    }
    [data-baseweb="select"] > div:hover { border-color: var(--dp-border-strong) !important; }
    [data-baseweb="popover"] { background: var(--dp-bg-2) !important; }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: var(--dp-gradient) !important;
        color: #00131F !important;
        border: none !important;
        border-radius: 12px !important;
        padding: .75rem 1.4rem !important;
        font-weight: 700 !important;
        letter-spacing: .01em;
        box-shadow: 0 8px 24px -8px rgba(0,200,255,0.55) !important;
        transition: all .2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 32px -8px rgba(0,200,255,0.75) !important;
        filter: brightness(1.08);
    }
    .stDownloadButton > button {
        background: rgba(255,255,255,0.05) !important;
        color: var(--dp-text) !important;
        border: 1px solid var(--dp-border-strong) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }

    /* ---------- Text inputs ---------- */
    .stTextInput > div > div > input {
        background: var(--dp-glass) !important;
        color: var(--dp-text) !important;
        border: 1px solid var(--dp-border) !important;
        border-radius: 10px !important;
    }

    /* ---------- Metric cards ---------- */
    .dp-metric {
        position: relative;
        padding: 1.4rem 1.4rem 1.2rem;
        border-radius: 18px;
        background: linear-gradient(160deg, rgba(14,26,56,0.85), rgba(8,16,38,0.75));
        border: 1px solid var(--dp-border);
        overflow: hidden;
        transition: all .25s ease;
        height: 100%;
    }
    .dp-metric:hover {
        transform: translateY(-3px);
        border-color: var(--dp-border-strong);
        box-shadow: 0 14px 40px -14px rgba(0,200,255,0.4);
    }
    .dp-metric::before {
        content: ""; position: absolute; top: -50%; right: -30%;
        width: 240px; height: 240px; border-radius: 50%;
        background: radial-gradient(circle, rgba(0,200,255,0.18), transparent 65%);
        pointer-events: none;
    }
    .dp-metric .label {
        display:flex; align-items:center; gap:.55rem;
        font-size:.72rem; font-weight: 700; letter-spacing: .12em;
        text-transform: uppercase; color: var(--dp-muted);
    }
    .dp-metric .label svg { width: 14px; height: 14px; color: var(--dp-cyan); }
    .dp-metric .value {
        font-size: 2.4rem; font-weight: 800; line-height: 1;
        margin: .8rem 0 .4rem;
        background: linear-gradient(135deg, #FFFFFF, #7FE3FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .dp-metric .meta { font-size: .82rem; color: var(--dp-muted); }
    .dp-tier {
        display:inline-block; margin-top: .6rem;
        padding: .25rem .6rem; border-radius: 6px;
        font-size:.72rem; font-weight: 700; letter-spacing: .06em;
        text-transform: uppercase;
    }
    .dp-tier.elite { background: rgba(16,185,129,.15); color:#34D399; border:1px solid rgba(16,185,129,.4); }
    .dp-tier.strong { background: rgba(0,200,255,.15); color:#7FE3FF; border:1px solid rgba(0,200,255,.4); }
    .dp-tier.moderate { background: rgba(245,158,11,.15); color:#FBBF24; border:1px solid rgba(245,158,11,.4); }
    .dp-tier.needs { background: rgba(244,63,94,.15); color:#FB7185; border:1px solid rgba(244,63,94,.4); }

    /* ---------- Chips ---------- */
    .dp-chip-row { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:.6rem; }
    .dp-chip {
        display:inline-flex; align-items:center; gap:.4rem;
        padding:.4rem .75rem; border-radius: 8px;
        font-size:.82rem; font-weight: 600;
        border: 1px solid;
    }
    .dp-chip.match { background: rgba(0,200,255,0.10); color:#7FE3FF; border-color: rgba(0,200,255,0.35); }
    .dp-chip.miss  { background: rgba(245,158,11,0.10); color:#FBBF24; border-color: rgba(245,158,11,0.35); }
    .dp-chip.danger{ background: rgba(244,63,94,0.10); color:#FB7185; border-color: rgba(244,63,94,0.35); }
    .dp-chip.strength { background: rgba(16,185,129,0.10); color:#34D399; border-color: rgba(16,185,129,0.35); }
    .dp-chip.focus { background: rgba(245,158,11,0.10); color:#FBBF24; border-color: rgba(245,158,11,0.35); }

    /* ---------- Insight pills ---------- */
    .dp-insight {
        padding: .85rem 1rem; border-radius: 12px;
        border: 1px solid; font-size:.9rem; margin-top:.6rem;
        display:flex; gap:.6rem; align-items:flex-start;
    }
    .dp-insight.good { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.35); color:#A7F3D0; }
    .dp-insight.warn { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.35); color:#FDE68A; }
    .dp-insight.bad  { background: rgba(244,63,94,0.08); border-color: rgba(244,63,94,0.35); color:#FECDD3; }
    .dp-insight svg { width: 18px; height: 18px; flex-shrink: 0; margin-top: 1px; }

    /* ---------- Roadmap ---------- */
    .dp-roadmap { position: relative; padding-left: 1.6rem; margin-top: .6rem; }
    .dp-roadmap::before {
        content:""; position:absolute; left: 14px; top: 6px; bottom: 6px;
        width: 2px; background: linear-gradient(180deg, var(--dp-cyan), rgba(37,99,235,.2));
    }
    .dp-step {
        position: relative; margin-bottom: 1rem;
        background: var(--dp-glass);
        border: 1px solid var(--dp-border);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        transition: all .25s ease;
    }
    .dp-step:hover { border-color: var(--dp-border-strong); transform: translateX(4px); }
    .dp-step .node {
        position: absolute; left: -32px; top: 18px;
        width: 28px; height: 28px; border-radius: 50%;
        display:flex; align-items:center; justify-content:center;
        background: var(--dp-gradient); color:#001022;
        font-weight: 800; font-size:.78rem;
        box-shadow: 0 0 18px rgba(0,200,255,0.5);
    }
    .dp-step .skill { font-weight: 700; color: var(--dp-text); font-size: 1rem; }
    .dp-step .effort {
        margin-top:.35rem; font-size:.8rem; color: var(--dp-muted);
        display:flex; align-items:center; gap:.4rem;
    }
    .dp-icon-small {
        display:inline-flex; align-items:center; justify-content:center;
        width:18px; height:18px;
    }
    .dp-icon-small svg {
        width:100%; height:100%;
    }

    /* ---------- Career card ---------- */
    .dp-career {
        padding: 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(14,26,56,0.85), rgba(8,16,38,0.85));
        border: 1px solid var(--dp-border);
    }
    .dp-readiness-badge {
        display:inline-flex; align-items:center; gap:.5rem;
        padding:.5rem .9rem; border-radius: 999px;
        font-weight: 700; font-size:.85rem;
        border: 1px solid;
    }
    .dp-readiness-badge.lv-elite { background: rgba(16,185,129,.12); color:#34D399; border-color:rgba(16,185,129,.45); }
    .dp-readiness-badge.lv-strong { background: rgba(0,200,255,.12); color:#7FE3FF; border-color:rgba(0,200,255,.45); }
    .dp-readiness-badge.lv-mod { background: rgba(245,158,11,.12); color:#FBBF24; border-color:rgba(245,158,11,.45); }
    .dp-readiness-badge.lv-needs { background: rgba(244,63,94,.12); color:#FB7185; border-color:rgba(244,63,94,.45); }
    .dp-readiness-dot { width:8px; height:8px; border-radius:50%; background: currentColor; box-shadow: 0 0 10px currentColor; }
    .dp-career-summary { color:#CFDDF5; font-size:1rem; line-height:1.65; margin: 1rem 0 0; }

    /* ---------- Progress workflow ---------- */
    .dp-workflow {
        background: var(--dp-glass);
        border: 1px solid var(--dp-border);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
    }
    .dp-wf-step {
        display:flex; align-items:center; gap:.7rem;
        padding:.45rem 0;
        color: var(--dp-muted); font-size:.92rem;
        transition: color .3s ease;
    }
    .dp-wf-step.done { color: var(--dp-text); }
    .dp-wf-step.active { color: var(--dp-cyan); }
    .dp-wf-icon {
        width: 22px; height: 22px; border-radius: 50%;
        display:flex; align-items:center; justify-content:center;
        background: rgba(255,255,255,0.05);
        border: 1px solid var(--dp-border);
        flex-shrink: 0;
    }
    .dp-wf-step.done .dp-wf-icon { background: var(--dp-gradient); border-color: transparent; }
    .dp-wf-step.active .dp-wf-icon {
        border-color: var(--dp-cyan);
        box-shadow: 0 0 12px var(--dp-cyan);
        animation: dp-pulse 1.2s infinite;
    }
    .dp-wf-icon svg { width: 12px; height: 12px; color:#001022; }

    /* ---------- Empty states ---------- */
    .dp-empty {
        text-align: center;
        padding: 2.4rem 1.4rem;
        border: 1px dashed var(--dp-border);
        border-radius: 16px;
        background: var(--dp-glass);
    }
    .dp-empty .ico {
        width: 56px; height: 56px; border-radius: 14px;
        display:inline-flex; align-items:center; justify-content:center;
        background: rgba(0,200,255,0.10);
        border: 1px solid var(--dp-border);
        margin-bottom: .8rem;
    }
    .dp-empty .ico svg { width: 24px; height: 24px; color: var(--dp-cyan); }
    .dp-empty h4 { margin: 0 0 .4rem; }
    .dp-empty p { color: var(--dp-muted); margin: 0; font-size:.92rem; }

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
    .dp-report h1, .dp-report h2, .dp-report h3 { color: #FFFFFF; }

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
    
    /* ---------- Expanders ---------- */
    [data-testid="stExpander"] {
        background: var(--dp-glass) !important;
        border: 1px solid var(--dp-border) !important;
        border-radius: 14px !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary { color: var(--dp-text) !important; font-weight: 600 !important; }

    /* ---------- Tables ---------- */
    .stDataFrame, .stTable { background: transparent !important; }

    /* ---------- Divider tone ---------- */
    hr { border-color: var(--dp-border) !important; }

    /* ---------- Responsive ---------- */
    @media (max-width: 900px) {
        .dp-hero { padding: 1.6rem; }
        .dp-hero-visual { height: 180px; margin-top: 1rem; }
    }
    [data-testid="stHeader"] {
    background: transparent !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    header {
        height: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# SVG helpers
# ==========================================================
SVG = {
    "sparkles": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 4v6c0 5-3.5 9-8 10-4.5-1-8-5-8-10V6l8-4z"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-6"/></svg>',
    "trend": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "user": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "alert": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 1 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M5 22v-2a7 7 0 0 1 14 0v2"/></svg>',
    "rocket": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15 9 22 9 17 14 19 21 12 17 5 21 7 14 2 9 9 9 12 2"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "folder": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "history": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/><polyline points="12 7 12 12 16 14"/></svg>',
}


def icon(name, size=14, color=None):
    style = f"width:{size}px;height:{size}px;" + (f"color:{color};" if color else "")
    return f'<span style="display:inline-flex;{style}">{SVG[name]}</span>'



# ==========================================================
# HERO
# ==========================================================
hero_left, hero_right = st.columns([1.4, 1])

with hero_left:
    st.markdown(
        f"""
        <div class="dp-hero">
            <span class="dp-badge"><span class="dot"></span> Resume Analyzer</span>
            <div class="dp-h1">Transform Your Resume<br/>Into a Market-Ready Asset</div>
            <p class="dp-sub">Analyze ATS performance, identify skill gaps, benchmark against industry standards, and receive AI-powered career guidance.</p>
            <div class="dp-feat-row">
                <span class="dp-feat">{SVG['shield']} ATS Optimized</span>
                <span class="dp-feat">{SVG['ai']} AI Powered</span>
                <span class="dp-feat">{SVG['chart']} Market Intelligence</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown(
        """
        <div class="dp-hero" style="padding:1rem;">
            <div class="dp-hero-visual">
                <div class="dp-particle" style="left:15%; top:30%; animation-delay:0s;"></div>
                <div class="dp-particle" style="left:80%; top:25%; animation-delay:.8s;"></div>
                <div class="dp-particle" style="left:25%; top:75%; animation-delay:1.6s;"></div>
                <div class="dp-particle" style="left:75%; top:70%; animation-delay:2.4s;"></div>
                <div class="dp-scan-doc">
                    <div class="dp-scan-line"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# UPLOAD + ROLE
# ==========================================================
st.markdown(
    f'<div class="dp-section-title"><span class="ico">{SVG["doc"]}</span>Upload & Configure<span class="sub">Step 1 — provide your resume and target role</span></div>',
    unsafe_allow_html=True,
)

up_col, role_col = st.columns([1.2, 1])

with up_col:
    uploaded_file = st.file_uploader(
        "Drag & drop your resume here",
        type=["pdf"],
        help="PDF format · up to 200MB",
    )

    if uploaded_file is not None:
        size_kb = len(uploaded_file.getbuffer()) / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        st.markdown(
            f"""
            <div class="dp-glass" style="padding:1rem 1.2rem; margin-top:.8rem;">
              <div style="display:flex; align-items:center; gap:.9rem;">
                <div style="width:42px;height:42px;border-radius:10px;background:var(--dp-gradient);display:flex;align-items:center;justify-content:center;color:#001022;">
                  {SVG['doc']}
                </div>
                <div style="flex:1; min-width:0;">
                  <div style="font-weight:700; color:var(--dp-text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{uploaded_file.name}</div>
                  <div style="color:var(--dp-muted); font-size:.82rem;">
                    {size_str} · PDF · uploaded {time.strftime('%H:%M')}
                  </div>
                </div>
                <span class="dp-chip match">{SVG['check']} Ready</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with role_col:
    role_options = [
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Engineer",
        "Business Analyst",
        "Analytics",
        "Product Analyst",
    ]
    target_role = st.selectbox("Target Role", role_options, help="Your resume will be scored against this role")

    st.markdown(
        f"""
        <div class="dp-glass" style="padding:.9rem 1rem; margin-top:.6rem;">
          <div style="display:flex;align-items:center;gap:.6rem;color:var(--dp-muted);font-size:.85rem;">
            {SVG['target']}
            <span>Benchmarking against <strong style="color:var(--dp-text);">{target_role}</strong> market standards</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# ANALYZE BUTTON + WORKFLOW
# ==========================================================
st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
analyze_clicked = st.button("Analyze Resume", use_container_width=True, key="dp_analyze")


def render_workflow(active_idx, steps):
    html = '<div class="dp-workflow">'
    for i, s in enumerate(steps):
        cls = "done" if i < active_idx else ("active" if i == active_idx else "")
        ico_inner = SVG["check"] if i < active_idx else ""
        html += f'<div class="dp-wf-step {cls}"><span class="dp-wf-icon">{ico_inner}</span>{s}</div>'
    html += "</div>"
    return html


if analyze_clicked:
    if uploaded_file is None:
        st.error("Please upload a resume first.")
        st.stop()

    os.makedirs("uploads", exist_ok=True)
    save_path = os.path.join("uploads", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    saved_resume = save_resume(
        user_id=user_id,
        resume_name=uploaded_file.name,
        resume_path=save_path,
    )

    steps = [
        "Parsing Resume",
        "Extracting Skills",
        "ATS Evaluation",
        "Career Assessment",
        "Market Benchmarking",
        "AI Recommendations",
    ]
    wf_slot = st.empty()
    for i in range(len(steps)):
        wf_slot.markdown(render_workflow(i, steps), unsafe_allow_html=True)
        time.sleep(0.25)

    # ===== BACKEND CALLS (unchanged) =====
    result = full_resume_analysis(save_path, target_role)
    ats_result = result["ats"]
    save_analysis(
        user_id=user_id,
        resume_id=saved_resume.id,
        ats_score=ats_result.get("ATS Score", 0),
        match_score=ats_result.get("Coverage", 0),
        target_role=target_role,
    )

    st.session_state["analysis_result"] = result
    st.session_state["target_role"] = target_role
    st.session_state["latest_resume_id"] = saved_resume.id

    resume_text = extract_resume_text(save_path)
    resume_skills = extract_skills(resume_text, TECHNICAL_SKILLS)
    st.session_state["resume_skills"] = resume_skills

    job_fit_predictions = predict_job_fit(resume_skills)
    best_role, best_score = next(iter(job_fit_predictions.items()))
    normalized_skills = {s.lower().strip() for s in resume_skills}
    missing_skills = [s for s in ROLE_SKILLS.get(best_role, []) if s not in normalized_skills]

    save_job_fit_history(
        user_id=user_id,
        resume_id=saved_resume.id,
        best_role=best_role,
        best_score=best_score,
        predictions=job_fit_predictions,
        missing_skills=missing_skills,
    )

    wf_slot.markdown(render_workflow(len(steps), steps), unsafe_allow_html=True)


# ==========================================================
# RESULTS
# ==========================================================
if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]
    ats = result["ats"]
    insights = result["insights"]
    roadmap = result["roadmap"]

    matched = ats.get("Matched", []) or []
    missing = ats.get("Missing", []) or []
    total = max(1, len(matched) + len(missing))
    coverage = (len(matched) / total) * 100
    ats_score = float(ats.get("ATS Score", 0))

    # Competitiveness (preserve any existing value if present)
    competitiveness = float(
        ats.get("Competitiveness")
        or ats.get("Competitiveness Index")
        or ((ats_score * 0.6) + (coverage * 0.4))
    )

    def tier(v):
        if v >= 85: return ("Elite", "elite")
        if v >= 70: return ("Strong", "strong")
        if v >= 55: return ("Moderate", "moderate")
        return ("Needs Improvement", "needs")

    ats_tier = tier(ats_score)
    cov_tier = tier(coverage)
    comp_tier = tier(competitiveness)

    # ===== ATS OVERVIEW =====
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["target"]}</span>ATS Overview<span class="sub">How recruiters and parsers score your resume</span></div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class="dp-metric">
              <div class="label">{SVG['shield']} ATS Score</div>
              <div class="value">{ats_score:.1f}%</div>
              <div class="meta">Parser compatibility</div>
              <span class="dp-tier {ats_tier[1]}">{ats_tier[0]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="dp-metric">
              <div class="label">{SVG['check']} Coverage Score</div>
              <div class="value">{coverage:.1f}%</div>
              <div class="meta">{len(matched)} of {len(matched)+len(missing)} role skills</div>
              <span class="dp-tier {cov_tier[1]}">{cov_tier[0]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="dp-metric">
              <div class="label">{SVG['trend']} Competitiveness Index</div>
              <div class="value">{competitiveness:.1f}</div>
              <div class="meta">Weighted market signal</div>
              <span class="dp-tier {comp_tier[1]}">{comp_tier[0]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ===== YOU VS MARKET =====
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["chart"]}</span>You vs Market Average<span class="sub">Benchmarked against {st.session_state.get("target_role","your target role")}</span></div>',
        unsafe_allow_html=True,
    )

    market_ats = 75.0
    market_cov = 68.0

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="You",
        x=["ATS Score", "Coverage Score"],
        y=[ats_score, coverage],
        marker=dict(color="#00C8FF", line=dict(color="#0EA5E9", width=0)),
        text=[f"{ats_score:.1f}%", f"{coverage:.1f}%"],
        textposition="outside",
        textfont=dict(color="#E6EEFB", size=13),
    ))
    fig.add_trace(go.Bar(
        name="Market Avg",
        x=["ATS Score", "Coverage Score"],
        y=[market_ats, market_cov],
        marker=dict(color="rgba(148,184,255,0.35)"),
        text=[f"{market_ats:.0f}%", f"{market_cov:.0f}%"],
        textposition="outside",
        textfont=dict(color="#8FA3C7", size=13),
    ))
    fig.update_layout(
        barmode="group",
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E6EEFB", family="Inter"),
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[0, 110], gridcolor="rgba(148,184,255,0.1)", showline=False),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    delta_ats = ats_score - market_ats
    delta_cov = coverage - market_cov
    if delta_ats >= 5:
        kind, ic = "good", SVG["check"]
        msg = f"Your ATS score is {delta_ats:.1f}% above market average — strong recruiter signal."
    elif delta_ats >= -5:
        kind, ic = "warn", SVG["alert"]
        msg = f"Your ATS score sits within {abs(delta_ats):.1f}% of the market — refine keywords to pull ahead."
    else:
        kind, ic = "bad", SVG["alert"]
        msg = f"Your ATS score is {abs(delta_ats):.1f}% below market — prioritise the missing skills below."
    st.markdown(f'<div class="dp-insight {kind}">{ic}<span>{msg}</span></div>', unsafe_allow_html=True)

    if delta_cov >= 5:
        st.markdown(f'<div class="dp-insight good">{SVG["check"]}<span>Coverage outperforms benchmark by {delta_cov:.1f}%.</span></div>', unsafe_allow_html=True)
    elif delta_cov < -5:
        st.markdown(f'<div class="dp-insight bad">{SVG["alert"]}<span>Coverage trails benchmark by {abs(delta_cov):.1f}% — focus on missing skills to exceed industry standards.</span></div>', unsafe_allow_html=True)

    # ===== SKILL BREAKDOWN =====
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["spark"]}</span>Skill Breakdown<span class="sub">Matched vs missing against role taxonomy</span></div>',
        unsafe_allow_html=True,
    )

    sk_l, sk_r = st.columns(2)

    with sk_l:
        st.markdown(
            f"""
            <div class="dp-glass" style="padding:1.2rem 1.3rem;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem;">
                <div style="display:flex;align-items:center;gap:.6rem;font-weight:700;">{SVG['check']} Matched Skills</div>
                <span class="dp-chip match">{len(matched)}</span>
              </div>
            """,
            unsafe_allow_html=True,
        )
        q_m = st.text_input("Search matched", key="search_match", label_visibility="collapsed", placeholder="Search matched skills…")
        filtered_m = [s for s in matched if q_m.lower() in str(s).lower()] if q_m else matched
        if filtered_m:
            chips = "".join(f'<span class="dp-chip match">{SVG["check"]}{s}</span>' for s in filtered_m)
            st.markdown(f'<div class="dp-chip-row">{chips}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--dp-muted);font-size:.88rem;padding:.4rem 0;">No matches.</div></div>', unsafe_allow_html=True)

    with sk_r:
        st.markdown(
            f"""
            <div class="dp-glass" style="padding:1.2rem 1.3rem;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem;">
                <div style="display:flex;align-items:center;gap:.6rem;font-weight:700;">{SVG['alert']} Missing Skills</div>
                <span class="dp-chip miss">{len(missing)}</span>
              </div>
            """,
            unsafe_allow_html=True,
        )
        q_x = st.text_input("Search missing", key="search_miss", label_visibility="collapsed", placeholder="Search missing skills…")
        filtered_x = [s for s in missing if q_x.lower() in str(s).lower()] if q_x else missing
        if filtered_x:
            chips = "".join(
                f'<span class="dp-chip {"danger" if i < 3 else "miss"}">{SVG["alert"] if i<3 else ""}{s}</span>'
                for i, s in enumerate(filtered_x)
            )
            st.markdown(f'<div class="dp-chip-row">{chips}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--dp-muted);font-size:.88rem;padding:.4rem 0;">No gaps detected.</div></div>', unsafe_allow_html=True)

    # ===== CAREER SUMMARY =====
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["user"]}</span>Career Summary<span class="sub">AI-assessed readiness for your target role</span></div>',
        unsafe_allow_html=True,
    )

    def _norm(v):
        if not v: return []
        if isinstance(v, dict): return [str(x) for x in v.values() if x]
        if isinstance(v, (list, tuple, set)): return [str(x) for x in v if x]
        return [str(v)]

    level = insights.get("Level", "Unknown")
    summary = insights.get("Summary", "")
    strengths = _norm(insights.get("Strengths"))
    focus_areas = _norm(insights.get("Focus Areas"))

    level_cls = {
        "Highly Competitive": "lv-elite",
        "Competitive": "lv-strong",
        "Moderately Competitive": "lv-mod",
        "Needs Improvement": "lv-needs",
    }.get(level, "lv-strong")

    st.markdown(
        f"""
        <div class="dp-career">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.6rem;">
            <div>
              <div style="color:var(--dp-muted);font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;">Career Readiness</div>
              <div style="font-size:1.7rem;font-weight:800;margin-top:.3rem;">{level}</div>
            </div>
            <span class="dp-readiness-badge {level_cls}"><span class="dp-readiness-dot"></span>{level}</span>
          </div>
          <p class="dp-career-summary">{summary}</p>
        </div><br>
        """,
        unsafe_allow_html=True,
    )

    cs_l, cs_r = st.columns(2)
    with cs_l:
        st.markdown(
            f'<div padding:1rem 1.2rem;margin-top:1rem;"><div style="font-weight:700;display:flex;align-items:center;gap:.5rem;">{icon("spark", size=12)} Strengths</div>',
            unsafe_allow_html=True,
        )
        if strengths:
            chips = "".join(f'<span class="dp-chip strength">{s}</span>' for s in strengths)
            st.markdown(f'<div class="dp-chip-row">{chips}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--dp-muted);font-size:.88rem;margin-top:.5rem;">No strengths surfaced yet.</div></div>', unsafe_allow_html=True)

    with cs_r:
        st.markdown(
            f'<div padding:1rem 1.2rem;margin-top:1rem;"><div style="font-weight:700;display:flex;align-items:center;gap:.5rem;">{icon("target", size=12)} Focus Areas</div>',
            unsafe_allow_html=True,
        )
        if focus_areas:
            chips = "".join(f'<span class="dp-chip focus">{s}</span>' for s in focus_areas)
            st.markdown(f'<div class="dp-chip-row">{chips}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--dp-muted);font-size:.88rem;margin-top:.5rem;">No focus areas identified.</div></div>', unsafe_allow_html=True)

    # ===== LEARNING ROADMAP =====
    
    # ===== LEARNING ROADMAP =====
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["rocket"]}</span>Learning Roadmap<span class="sub">Adaptive milestones based on your skill gaps</span></div>',
        unsafe_allow_html=True,
    )

    if roadmap:

        # Handle roadmap if returned as string
        if isinstance(roadmap, str):
            import ast

            try:
                roadmap = ast.literal_eval(roadmap)
            except:
                st.error("Unable to parse roadmap.")
                roadmap = None

        if isinstance(roadmap, dict):

            roadmap_html = ['<div class="dp-roadmap">']

            for idx, (month, details) in enumerate(roadmap.items(), start=1):

                skill = details.get("Skill", "N/A")
                duration = details.get("Duration", "N/A")
                topics = details.get("Topics", [])

                step_html = (
                    f'<div class="dp-step">'
                    f'<div class="node">{idx}</div>'
                    f'<div class="skill">Step {idx} · {month}</div>'
                    f'<div style="margin-top:10px;font-size:20px;font-weight:700;color:#7FE3FF;">{skill.title()}</div>'
                    f'<div class="effort"><span class="dp-icon-small">{SVG["clock"]}</span><span>Duration: {duration}</span></div>'
                    '</div>'
                )

                roadmap_html.append(step_html)

                if topics:
                    topic_html = ''.join(
                        f'<span class="dp-chip focus">{topic}</span>'
                        for topic in topics
                    )
                    roadmap_html.append(
                        f'<div class="dp-chip-row" style="margin-left:35px;margin-bottom:25px;">{topic_html}</div>'
                    )

            roadmap_html.append('</div>')
            st.markdown(''.join(roadmap_html), unsafe_allow_html=True)

        else:
            st.warning("Roadmap format is invalid.")

    else:
        st.markdown(
            f"""
            <div class="dp-empty">
                <div class="ico">{SVG['check']}</div>
                <h4>No Roadmap Available</h4>
                <p>Learning roadmap could not be generated.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    # ===== AI CAREER REPORT ===== 
    st.markdown(
        f'<div class="dp-section-title"><span class="ico">{SVG["ai"]}</span>AI Career Report<span class="sub">Personalised, in-depth analysis</span></div>',
        unsafe_allow_html=True,
    )

    gen = st.button("Generate AI Career Report", use_container_width=True, key="dp_gen_report")
    if gen:
        with st.spinner("Generating detailed AI report…"):
            feedback = generate_resume_feedback(ats, st.session_state["target_role"])
        st.session_state["resume_feedback"] = feedback
        st.session_state["_dp_stream"] = True


# ==========================================================
# AI REPORT DISPLAY
# ==========================================================
if "resume_feedback" in st.session_state:
    feedback = st.session_state["resume_feedback"]

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
                <h3>AI Resume Intelligence</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    report_slot = st.empty()

    if st.session_state.pop("_dp_stream", False):
        buf = ""
        for ch in feedback:
            buf += ch
            if len(buf) % 6 == 0:
                report_slot.markdown(
                    f'<div class="dp-report">{buf}▍</div>',
                    unsafe_allow_html=True
                )
                time.sleep(0.005)

    report_slot.markdown(
        f'<div class="dp-report">{feedback}</div>',
        unsafe_allow_html=True
)

    act1, act2 = st.columns([1, 1])
    with act1:
        b64 = base64.b64encode(feedback.encode()).decode()
        st.markdown(
            f"""
            <a href="data:text/plain;base64,{b64}" download="AI_Career_Report.txt"
               style="display:block;text-align:center;padding:.7rem;border-radius:12px;
                      background:rgba(255,255,255,0.04);border:1px solid var(--dp-border-strong);
                      color:var(--dp-text);text-decoration:none;font-weight:600;">
              Copy / Save Text
            </a>
            """,
            unsafe_allow_html=True,
        )
    
    with act2:
        pdf_data = text_to_pdf(feedback)
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="AI_Career_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ==========================================================
# EMPTY STATE — no analysis yet
# ==========================================================
if "analysis_result" not in st.session_state:
    st.markdown(
        f"""
        <div class="dp-empty" style="margin-top:1.4rem;">
          <div class="ico">{SVG['doc']}</div>
          <h4>No Analysis Yet</h4>
          <p>Upload a resume and pick a target role above to unlock ATS scoring, market benchmarking and AI recommendations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# HISTORY
# ==========================================================
st.markdown(
    f'<div class="dp-section-title"><span class="ico">{SVG["history"]}</span>History<span class="sub">Your past analyses and uploaded resumes</span></div>',
    unsafe_allow_html=True,
)

hist_tab1, hist_tab2 = st.tabs(["Analysis History", "Resume History"])

with hist_tab1:
    analyses = get_analysis_history(user_id)
    if not analyses:
        st.markdown(
            f"""
            <div class="dp-empty">
              <div class="ico">{SVG['chart']}</div>
              <h4>No Analysis Available</h4>
              <p>Run your first analysis to start building a history of insights.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        rows = []
        for a in analyses:
            rows.append({
                "Resume ID": a.resume_id,
                "Target Role": a.target_role,
                "ATS Score": f"{a.ats_score:.2f}%" if a.ats_score is not None else "N/A",
                "Match Score": f"{a.match_score:.2f}%" if a.match_score is not None else "N/A",
                "Analyzed At": a.analysis_date.strftime("%Y-%m-%d %H:%M") if a.analysis_date else "Unknown",
            })
        q = st.text_input("Filter analyses", key="hist_q", placeholder="Search by role…", label_visibility="collapsed")
        if q:
            rows = [r for r in rows if q.lower() in str(r["Target Role"]).lower()]
        st.dataframe(rows, use_container_width=True, hide_index=True)

with hist_tab2:
    resumes = get_user_resumes(user_id)
    if not resumes:
        st.markdown(
            f"""
            <div class="dp-empty">
              <div class="ico">{SVG['folder']}</div>
              <h4>No Resume Uploaded</h4>
              <p>Your uploaded resumes will appear here for quick re-analysis.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        rows = []
        for r in resumes:
            rows.append({
                "Resume": r.resume_name,
                "Uploaded At": r.uploaded_at.strftime("%Y-%m-%d %H:%M") if r.uploaded_at else "Unknown",
            })
        q = st.text_input("Filter resumes", key="res_q", placeholder="Search by name…", label_visibility="collapsed")
        if q:
            rows = [r for r in rows if q.lower() in str(r["Resume"]).lower()]
        st.dataframe(rows, use_container_width=True, hide_index=True)
