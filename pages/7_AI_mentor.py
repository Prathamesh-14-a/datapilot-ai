import streamlit as st
import json
import time
import html
from datetime import datetime

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated
from src.database.crud import (
    get_ai_chat_sessions,
    save_ai_chat_session,
)
from src.llm.career_chat import ask_career_ai


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Mentor · DataPilot AI",
    page_icon="assets/mini_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

# Keep the original sidebar mounted but collapsed by default (handled above).
show_sidebar()


# ============================================================
# PROMPT LIBRARY  (unchanged data)
# ============================================================
PROMPT_BATCHES = [
    [
        "How can I become a Data Scientist?",
        "Is Data Analytics a good career in 2026?",
        "What skills do I need for a Data Engineer role?",
        "Should I learn Data Science or Data Analytics first?",
        "What is the career roadmap for Machine Learning Engineer?",
    ],
    [
        "Create a 6-month Data Analyst roadmap",
        "What should I learn after Python and SQL?",
        "Build a roadmap for becoming a Data Scientist",
        "How can I learn Machine Learning from scratch?",
        "What projects should I build to get hired?",
    ],
    [
        "Common Data Analyst interview questions",
        "SQL interview questions for freshers",
        "Python interview questions for Data Science",
        "How should I answer \"Tell me about yourself\"?",
        "Mock interview for Data Analyst role",
    ],
    [
        "How can I improve my ATS score?",
        "What skills should I add to my resume?",
        "How should I describe my projects?",
        "What mistakes should I avoid in my resume?",
        "Review my resume for Data Analyst jobs",
    ],
    [
        "What salary can I expect as a Data Analyst?",
        "Which data roles pay the most?",
        "How do I negotiate salary?",
        "What are the highest-paying skills in Data Science?",
        "Which companies hire freshers in Data Analytics?",
    ],
    [
        "Suggest beginner Data Analytics projects",
        "Suggest intermediate Machine Learning projects",
        "How can I make my GitHub portfolio stand out?",
        "What projects should I add to my resume?",
        "Give me a real-world data science project idea",
    ],
    [
        "Which data skills are most in demand?",
        "Is Power BI still worth learning?",
        "Should I learn Tableau or Power BI?",
        "What are the latest trends in AI and ML?",
        "Which tools are recruiters looking for?",
    ],
]

PROMPT_META = {
    0: ("Career Intelligence", "Strategic guidance for your next move"),
    1: ("Learning Roadmaps", "Structured paths from beginner to hired"),
    2: ("Interview Coaching", "Practice rounds and high-signal answers"),
    3: ("Resume Studio", "ATS-grade resume tuning and storytelling"),
    4: ("Salary Insights", "Compensation benchmarks and negotiation"),
    5: ("Project Lab", "Portfolio ideas recruiters actually notice"),
    6: ("Market Trends", "What hiring managers are searching for"),
}


# ============================================================
# BACKEND HELPERS (UNCHANGED LOGIC)
# ============================================================
def _load_chat_messages(chat_session):
    try:
        return json.loads(chat_session.messages_json)
    except Exception:
        return []


def _get_chat_title(messages, fallback_question=""):
    for message in messages:
        if message.get("role") == "user" and message.get("content"):
            return message["content"][:70]
    return fallback_question[:70]


def _ensure_state():
    defaults = {
        "mentor_messages": [],
        "mentor_chat_session_id": None,
        "mentor_prompt_batch": 0,
        "mentor_pending_question": None,
        "mentor_search_query": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _load_recent_history():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return []
    return get_ai_chat_sessions(user_id)[:30]


def _reset_chat():
    st.session_state["mentor_messages"] = []
    st.session_state["mentor_chat_session_id"] = None
    st.session_state["mentor_pending_question"] = None


def _rotate_prompt_batch():
    st.session_state["mentor_prompt_batch"] = (
        st.session_state["mentor_prompt_batch"] + 1
    ) % len(PROMPT_BATCHES)


def _queue_question(question):
    st.session_state["mentor_pending_question"] = question


def _load_chat_session(chat_session):
    st.session_state["mentor_messages"] = _load_chat_messages(chat_session)
    st.session_state["mentor_chat_session_id"] = chat_session.id
    st.session_state["mentor_pending_question"] = None


def _save_current_chat(user_id, fallback_question):
    if not st.session_state["mentor_messages"]:
        return
    title = _get_chat_title(st.session_state["mentor_messages"], fallback_question)
    chat_session = save_ai_chat_session(
        user_id=user_id,
        title=title,
        messages=st.session_state["mentor_messages"],
        chat_session_id=st.session_state.get("mentor_chat_session_id"),
    )
    st.session_state["mentor_chat_session_id"] = chat_session.id


# ============================================================
# GLOBAL STYLES — DataPilot AI design system
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root{
        --dp-bg-0:#020617;
        --dp-bg-1:#07112A;
        --dp-bg-2:#08142F;
        --dp-primary:#00C8FF;
        --dp-secondary:#0EA5E9;
        --dp-accent:#2563EB;
        --dp-text:#E2E8F0;
        --dp-muted:#94A3B8;
        --dp-border:rgba(148,184,255,0.12);
        --dp-glass:rgba(8,20,47,0.55);
        --dp-glow:0 0 40px rgba(0,200,255,0.25);
    }

    html, body, [class*="css"], .stApp{
        font-family:'Inter', sans-serif !important;
        color:var(--dp-text) !important;
    }

    /* Ambient background */
    .stApp{
        background:
            radial-gradient(1200px 600px at 10% -10%, rgba(37,99,235,0.25), transparent 60%),
            radial-gradient(900px 500px at 90% 10%, rgba(14,165,233,0.22), transparent 60%),
            radial-gradient(800px 800px at 50% 110%, rgba(0,200,255,0.12), transparent 60%),
            linear-gradient(180deg, #020617 0%, #07112A 60%, #08142F 100%) !important;
        background-attachment: fixed !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header {visibility:hidden;}
    .block-container{padding-top:1.2rem !important; padding-bottom:8rem !important; max-width:1400px;}

    /* Sidebar (mentor) */
    section[data-testid="stSidebar"]{
        background:linear-gradient(180deg, rgba(2,6,23,0.95), rgba(7,17,42,0.95)) !important;
        border-right:1px solid var(--dp-border) !important;
        backdrop-filter: blur(18px);
    }
    section[data-testid="stSidebar"] *{color:var(--dp-text) !important;}

    .dp-sb-brand{
        display:flex; align-items:center; gap:10px;
        padding:14px 6px 18px 6px;
        border-bottom:1px solid var(--dp-border);
        margin-bottom:14px;
    }
    .dp-sb-brand-mark{
        width:34px;height:34px;border-radius:10px;
        background:linear-gradient(135deg,#00C8FF,#2563EB);
        box-shadow:0 0 18px rgba(0,200,255,0.45);
        display:flex;align-items:center;justify-content:center;
        font-weight:800;color:#001022;font-family:'Space Grotesk';
    }
    .dp-sb-brand-title{font-family:'Space Grotesk';font-weight:700;font-size:1.05rem;letter-spacing:.3px;}
    .dp-sb-brand-sub{font-size:.7rem;color:var(--dp-muted);margin-top:-2px;}

    .dp-sb-section{font-size:.7rem;letter-spacing:.18em;color:var(--dp-muted);text-transform:uppercase;margin:14px 4px 8px;}

    /* New chat button */
    section[data-testid="stSidebar"] .stButton>button{
        background:linear-gradient(135deg, rgba(0,200,255,0.12), rgba(37,99,235,0.18)) !important;
        border:1px solid rgba(0,200,255,0.35) !important;
        color:var(--dp-text) !important;
        border-radius:12px !important;
        padding:10px 12px !important;
        font-weight:500 !important;
        text-align:left !important;
        transition: all .25s ease;
        box-shadow: 0 0 0 rgba(0,200,255,0);
    }
    section[data-testid="stSidebar"] .stButton>button:hover{
        border-color:var(--dp-primary) !important;
        box-shadow:0 0 18px rgba(0,200,255,0.35);
        transform: translateY(-1px);
    }

    /* Hero */
    .dp-hero{
        position:relative;
        border-radius:24px;
        padding:38px 44px;
        margin: 6px 0 22px 0;
        background:
            radial-gradient(600px 200px at 20% 0%, rgba(0,200,255,0.18), transparent 70%),
            linear-gradient(180deg, rgba(8,20,47,0.7), rgba(7,17,42,0.5));
        border:1px solid var(--dp-border);
        backdrop-filter: blur(14px);
        overflow:hidden;
    }
    .dp-hero::before{
        content:"";position:absolute;inset:0;
        background-image:
            linear-gradient(rgba(0,200,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,200,255,0.06) 1px, transparent 1px);
        background-size: 42px 42px;
        mask-image: radial-gradient(circle at 30% 50%, black, transparent 70%);
        pointer-events:none;
    }
    .dp-hero-grid{display:grid;grid-template-columns: 1.4fr 1fr;gap:36px;align-items:center;position:relative;z-index:1;}
    .dp-badge{
        display:inline-flex;align-items:center;gap:8px;
        padding:6px 14px;border-radius:999px;
        background:rgba(0,200,255,0.08);
        border:1px solid rgba(0,200,255,0.35);
        color:#7FE3FF;font-size:.78rem;font-weight:500;
    }
    .dp-badge .dot{width:7px;height:7px;border-radius:50%;background:var(--dp-primary);box-shadow:0 0 10px var(--dp-primary);}
    .dp-hero h1{
        font-family:'Space Grotesk';
        font-size: clamp(2rem, 3.4vw, 3rem);
        line-height:1.08;
        margin:16px 0 12px;
        background: linear-gradient(120deg, #FFFFFF 0%, #BCE7FF 55%, #00C8FF 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        font-weight:700;
    }
    .dp-hero p{color:var(--dp-muted);font-size:1.02rem;line-height:1.65;max-width:560px;}
    .dp-pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;}
    .dp-pill{
        font-size:.76rem;padding:6px 12px;border-radius:999px;
        background:rgba(255,255,255,0.03);border:1px solid var(--dp-border);
        color:#CBD5E1;
    }

    /* Neural illustration */
    .dp-neural{display:flex;justify-content:center;align-items:center;}
    @keyframes float {0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
    @keyframes pulseGlow{0%,100%{opacity:.4}50%{opacity:1}}
    .dp-neural svg{animation: float 6s ease-in-out infinite;}
    .dp-neural circle.node{animation: pulseGlow 3s ease-in-out infinite;}

    /* Section header */
    .dp-section-title{
        font-family:'Space Grotesk';font-weight:600;
        font-size:1.05rem;color:#E2E8F0;
        display:flex;align-items:center;gap:10px;
        margin: 8px 0 14px;
    }
    .dp-section-title .bar{width:3px;height:16px;border-radius:2px;background:linear-gradient(180deg,#00C8FF,#2563EB);box-shadow:0 0 10px #00C8FF;}
    .dp-section-sub{color:var(--dp-muted);font-size:.86rem;margin-bottom:14px;}

    /* Prompt cards = themed buttons */
    div[data-testid="stHorizontalBlock"] .stButton>button{
        width:100%;
        background:linear-gradient(160deg, rgba(8,20,47,0.65), rgba(7,17,42,0.4)) !important;
        border:1px solid var(--dp-border) !important;
        color:#E2E8F0 !important;
        border-radius:16px !important;
        padding:18px 18px !important;
        text-align:left !important;
        font-size:.92rem !important;
        font-weight:500 !important;
        min-height:78px;
        backdrop-filter: blur(10px);
        transition: all .25s ease;
        position:relative;
    }
    div[data-testid="stHorizontalBlock"] .stButton>button:hover{
        border-color: rgba(0,200,255,0.55) !important;
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,200,255,0.18), 0 0 0 1px rgba(0,200,255,0.25) inset;
        background:linear-gradient(160deg, rgba(0,200,255,0.10), rgba(37,99,235,0.10)) !important;
    }

    /* More prompts button */
    .dp-more .stButton>button{
        background:transparent !important;
        border:1px dashed rgba(0,200,255,0.35) !important;
        color:#7FE3FF !important;
        border-radius:12px !important;
        padding:10px 18px !important;
        font-weight:500 !important;
    }
    .dp-more .stButton>button:hover{
        background:rgba(0,200,255,0.06) !important;
        border-color:var(--dp-primary) !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"]{
        background: transparent !important;
        border:none !important;
        padding: 6px 0 !important;
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"]{
        border-radius:18px !important;
        padding:14px 18px !important;
        font-size:.96rem;
        line-height:1.65;
        max-width: 820px;
    }
    /* Assistant */
    [data-testid="stChatMessage"]:has(img[alt="assistant"]) [data-testid="stChatMessageContent"],
    div.stChatMessage.st-emotion-cache-assistant [data-testid="stChatMessageContent"]{
        background: linear-gradient(180deg, rgba(8,20,47,0.85), rgba(7,17,42,0.7)) !important;
        border:1px solid var(--dp-border) !important;
        color:#E5EEFB !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.25);
        backdrop-filter: blur(14px);
    }
    /* User */
    [data-testid="stChatMessage"]:has(img[alt="user"]) [data-testid="stChatMessageContent"]{
        background: linear-gradient(135deg, #2563EB, #0EA5E9) !important;
        color:#FFFFFF !important;
        border:1px solid rgba(0,200,255,0.4) !important;
        box-shadow: 0 12px 30px rgba(37,99,235,0.35), 0 0 24px rgba(0,200,255,0.2);
        margin-left:auto !important;
    }
    [data-testid="stChatMessage"]:has(img[alt="user"]){
        flex-direction: row-reverse !important;
    }

    /* Chat input dock */
    [data-testid="stChatInput"]{
        background: linear-gradient(180deg, rgba(8,20,47,0.85), rgba(7,17,42,0.85)) !important;
        border:1px solid rgba(0,200,255,0.35) !important;
        border-radius:18px !important;
        box-shadow: 0 0 40px rgba(0,200,255,0.18), 0 12px 50px rgba(0,0,0,0.45) !important;
        backdrop-filter: blur(18px);
    }
    [data-testid="stChatInput"] textarea{
        color:#E2E8F0 !important;
        font-size:.98rem !important;
    }
    [data-testid="stChatInput"]:focus-within{
        border-color:var(--dp-primary) !important;
        box-shadow: 0 0 0 3px rgba(0,200,255,0.18), 0 0 60px rgba(0,200,255,0.25) !important;
    }
    [data-testid="stBottomBlockContainer"]{
        background: transparent !important;
    }

    /* Divider */
    hr{border-color: var(--dp-border) !important; opacity:.6;}

    /* History items */
    .dp-history-item{
        display:block;padding:10px 12px;border-radius:10px;
        border:1px solid transparent;cursor:pointer;
        transition: all .2s ease;
    }
    .dp-history-item:hover{
        background:rgba(0,200,255,0.06);
        border-color:rgba(0,200,255,0.25);
    }
    .dp-history-active{
        background: linear-gradient(135deg, rgba(0,200,255,0.14), rgba(37,99,235,0.14));
        border:1px solid rgba(0,200,255,0.5);
        box-shadow: 0 0 18px rgba(0,200,255,0.25);
    }

    /* Thinking pulse */
    .dp-thinking{
        display:flex;align-items:center;gap:12px;
        padding:14px 18px;border-radius:16px;
        background: linear-gradient(180deg, rgba(8,20,47,0.85), rgba(7,17,42,0.7));
        border:1px solid var(--dp-border);
        color:#CBD5E1;font-size:.92rem;
        max-width:520px;
    }
    .dp-thinking .ring{
        width:14px;height:14px;border-radius:50%;
        border:2px solid rgba(0,200,255,0.25);
        border-top-color: var(--dp-primary);
        animation: spin 1s linear infinite;
    }
    @keyframes spin{to{transform:rotate(360deg)}}
    .dp-think-steps{display:flex;flex-direction:column;gap:4px;}
    .dp-think-step{font-size:.82rem;color:var(--dp-muted);opacity:.6;}
    .dp-think-step.active{color:#7FE3FF;opacity:1;}

    /* Insights panel */
    .dp-insights{
        position:sticky;top:14px;
        border-radius:20px;padding:20px;
        background: linear-gradient(180deg, rgba(8,20,47,0.7), rgba(7,17,42,0.5));
        border:1px solid var(--dp-border);
        backdrop-filter: blur(14px);
    }
    .dp-insights h4{
        font-family:'Space Grotesk';font-size:.95rem;
        color:#E2E8F0;margin:0 0 14px;
        display:flex;align-items:center;gap:8px;
    }
    .dp-insight-row{
        display:flex;justify-content:space-between;align-items:center;
        padding:10px 0;border-bottom:1px solid var(--dp-border);
    }
    .dp-insight-row:last-child{border-bottom:none;}
    .dp-insight-label{font-size:.78rem;color:var(--dp-muted);text-transform:uppercase;letter-spacing:.1em;}
    .dp-insight-value{font-size:.92rem;color:#E2E8F0;font-weight:600;}

    /* Empty state */
    .dp-empty{
        text-align:center;padding:50px 20px;
        color:var(--dp-muted);
    }

    /* Cursor blink */
    .dp-cursor::after{
        content:"▍";color:var(--dp-primary);
        animation: blink 1s steps(2,start) infinite;
        margin-left:2px;
    }
    @keyframes blink{to{visibility:hidden}}

    /* Streamlit text input */
    .stTextInput input{
        background: rgba(8,20,47,0.7) !important;
        border:1px solid var(--dp-border) !important;
        color:#E2E8F0 !important;
        border-radius:10px !important;
    }
    .stTextInput input:focus{
        border-color: var(--dp-primary) !important;
        box-shadow: 0 0 0 2px rgba(0,200,255,0.2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MENTOR SIDEBAR
# ============================================================
def _format_ts(ts):
    try:
        if isinstance(ts, datetime):
            return ts.strftime("%b %d, %H:%M")
        return str(ts)[:16]
    except Exception:
        return ""


def _render_mentor_sidebar(conversations):
    with st.sidebar:
        st.markdown(
            """
            <div class="dp-sb-brand">
                <div class="dp-sb-brand-mark">D</div>
                <div>
                    <div class="dp-sb-brand-title">DataPilot AI</div>
                    <div class="dp-sb-brand-sub">AI Career Mentor</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("＋  New Chat", use_container_width=True, key="dp_new_chat"):
            _reset_chat()
            st.rerun()

        st.markdown('<div class="dp-sb-section">Search</div>', unsafe_allow_html=True)
        query = st.text_input(
            "Search chats",
            value=st.session_state.get("mentor_search_query", ""),
            label_visibility="collapsed",
            placeholder="Search conversations…",
            key="dp_search_input",
        )
        st.session_state["mentor_search_query"] = query

        st.markdown('<div class="dp-sb-section">Recent Conversations</div>', unsafe_allow_html=True)

        if not conversations:
            st.markdown(
                '<div style="color:#64748B;font-size:.85rem;padding:10px 4px;">No conversations yet. Start your first chat.</div>',
                unsafe_allow_html=True,
            )
            return

        active_id = st.session_state.get("mentor_chat_session_id")
        q = (query or "").lower().strip()

        for cs in conversations:
            title = cs.title or "Untitled chat"
            if q and q not in title.lower():
                continue
            label = title if len(title) <= 38 else title[:38] + "…"
            ts = _format_ts(getattr(cs, "updated_at", None) or getattr(cs, "created_at", None))
            is_active = active_id == cs.id

            # Use button with prefix for active state
            btn_label = ("● " if is_active else "")  + label
            if st.button(
                btn_label,
                key=f"dp_hist_{cs.id}",
                use_container_width=True,
                help=title,
            ):
                _load_chat_session(cs)
                st.rerun()
            if ts:
                st.markdown(
                    f'<div style="font-size:.7rem;color:#64748B;margin:-6px 4px 8px 6px;">{html.escape(ts)}</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# HERO + NEURAL SVG
# ============================================================
NEURAL_SVG = """
<svg viewBox="0 0 420 320" width="100%" height="280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="g1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00C8FF" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#2563EB" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="line" x1="0" x2="1">
      <stop offset="0" stop-color="#00C8FF" stop-opacity="0.7"/>
      <stop offset="1" stop-color="#2563EB" stop-opacity="0.2"/>
    </linearGradient>
  </defs>
  <circle cx="210" cy="160" r="120" fill="url(#g1)" opacity="0.35"/>
  <g stroke="url(#line)" stroke-width="1.2" fill="none" opacity="0.7">
    <line x1="60" y1="80" x2="210" y2="160"/>
    <line x1="60" y1="240" x2="210" y2="160"/>
    <line x1="360" y1="80" x2="210" y2="160"/>
    <line x1="360" y1="240" x2="210" y2="160"/>
    <line x1="210" y1="40" x2="210" y2="160"/>
    <line x1="210" y1="280" x2="210" y2="160"/>
    <line x1="120" y1="60" x2="300" y2="260"/>
    <line x1="120" y1="260" x2="300" y2="60"/>
  </g>
  <g fill="#00C8FF">
    <circle class="node" cx="210" cy="160" r="10"/>
    <circle class="node" cx="60" cy="80" r="5"/>
    <circle class="node" cx="60" cy="240" r="5"/>
    <circle class="node" cx="360" cy="80" r="5"/>
    <circle class="node" cx="360" cy="240" r="5"/>
    <circle class="node" cx="210" cy="40" r="4"/>
    <circle class="node" cx="210" cy="280" r="4"/>
    <circle class="node" cx="120" cy="60" r="3"/>
    <circle class="node" cx="300" cy="260" r="3"/>
    <circle class="node" cx="120" cy="260" r="3"/>
    <circle class="node" cx="300" cy="60" r="3"/>
  </g>
</svg>
"""


def _render_hero():
    st.markdown(
        f"""
        <div class="dp-hero">
            <div class="dp-hero-grid">
                <div>
                    <span class="dp-badge"><span class="dot"></span> AI Career Mentor</span>
                    <h1>Your Personal Data Career Copilot</h1>
                    <p>Get personalized guidance for careers, interviews, resumes, projects,
                    salary growth, and learning roadmaps — crafted for Data, Analytics & ML professionals.</p>
                    <div class="dp-pills">
                        <span class="dp-pill">Career Intelligence</span>
                        <span class="dp-pill">Interview Coaching</span>
                        <span class="dp-pill">Salary Insights</span>
                        <span class="dp-pill">Skill Roadmaps</span>
                    </div>
                </div>
                <div class="dp-neural">{NEURAL_SVG}</div>
            </div>
        </div>
        <p>• Scroll down the sidebar to access previous chats.</p>
        """,
        unsafe_allow_html=True,
    )



# ============================================================
# PROMPT CARDS
# ============================================================
def _render_prompt_cards(prompts):
    rows = [prompts[i:i + 2] for i in range(0, len(prompts), 2)]
    for row_index, row in enumerate(rows):
        cols = st.columns(len(row))
        for col, prompt in zip(cols, row):
            with col:
                st.button(
                    prompt,
                    key=f"prompt_{st.session_state['mentor_prompt_batch']}_{row_index}_{prompt}",
                    use_container_width=True,
                    on_click=_queue_question,
                    args=(prompt,),
                )


# ============================================================
# INSIGHTS PANEL
# ============================================================
def _render_insights():
    msgs = st.session_state["mentor_messages"]
    user_msgs = [m for m in msgs if m["role"] == "user"]
    ai_msgs = [m for m in msgs if m["role"] == "assistant"]
    batch_idx = st.session_state["mentor_prompt_batch"]
    focus, _ = PROMPT_META.get(batch_idx, ("Career Intelligence", ""))
    last_user = user_msgs[-1]["content"][:40] + "…" if user_msgs else "—"
    avg_len = int(sum(len(m["content"]) for m in ai_msgs) / max(len(ai_msgs), 1)) if ai_msgs else 0

    st.markdown(
        f"""
        <div class="dp-insights">
            <h4>◆ AI Insights</h4>
            <div class="dp-insight-row">
                <span class="dp-insight-label">Career Focus</span>
                <span class="dp-insight-value">{html.escape(focus)}</span>
            </div>
            <div class="dp-insight-row">
                <span class="dp-insight-label">Current Topic</span>
                <span class="dp-insight-value">{html.escape(last_user)}</span>
            </div>
            <div class="dp-insight-row">
                <span class="dp-insight-label">Messages</span>
                <span class="dp-insight-value">{len(msgs)}</span>
            </div>
            <div class="dp-insight-row">
                <span class="dp-insight-label">Avg Response</span>
                <span class="dp-insight-value">{avg_len} chars</span>
            </div>
            <div class="dp-insight-row">
                <span class="dp-insight-label">Session</span>
                <span class="dp-insight-value">{"Active" if msgs else "Idle"}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MESSAGES + STREAMING
# ============================================================
def _render_messages():
    for message in st.session_state["mentor_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _stream_answer(placeholder, full_text):
    """Word-by-word streaming effect into a placeholder."""
    words = full_text.split(" ")
    buf = ""
    for i, w in enumerate(words):
        buf += w + " "
        if i % 2 == 0 or i == len(words) - 1:
            placeholder.markdown(
                f'<div class="dp-cursor">{buf}</div>',
                unsafe_allow_html=True,
            )
            time.sleep(0.015)
    placeholder.markdown(full_text)


def _render_thinking(slot):
    steps = [
        "Analyzing career context",
        "Reviewing market trends",
        "Generating recommendations",
        "Building personalized response",
    ]
    items = "".join(
        f'<div class="dp-think-step" id="s{i}">› {s}</div>' for i, s in enumerate(steps)
    )
    slot.markdown(
        f"""
        <div class="dp-thinking">
            <div class="ring"></div>
            <div class="dp-think-steps">
                <div style="color:#7FE3FF;font-weight:500;">DataPilot AI is thinking…</div>
                {items}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RENDER
# ============================================================
_ensure_state()
recent_history = _load_recent_history()
_render_mentor_sidebar(recent_history)

main_col, side_col = st.columns([3, 1], gap="large")

with main_col:
    has_messages = bool(st.session_state["mentor_messages"])

    if not has_messages:
        _render_hero()

        batch_idx = st.session_state["mentor_prompt_batch"]
        title, subtitle = PROMPT_META.get(batch_idx, ("Suggested Prompts", ""))
        st.markdown(
            f'<div class="dp-section-title"><span class="bar"></span>{html.escape(title)}</div>'
            f'<div class="dp-section-sub">{html.escape(subtitle)} — tap a card to start.</div>',
            unsafe_allow_html=True,
        )

        _render_prompt_cards(PROMPT_BATCHES[batch_idx])

        st.markdown('<div class="dp-more" style="margin-top:14px;">', unsafe_allow_html=True)
        if st.button("→  Show more prompts", use_container_width=False, key="dp_more"):
            _rotate_prompt_batch()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="dp-section-title"><span class="bar"></span>Conversation</div>',
            unsafe_allow_html=True,
        )
        _render_messages()

with side_col:
    _render_insights()


# ============================================================
# CHAT INPUT  (LOGIC UNCHANGED)
# ============================================================
pending_question = st.session_state.get("mentor_pending_question")
user_input = st.chat_input("Ask anything about your data career...")
question_to_answer = pending_question or user_input

if question_to_answer:
    st.session_state["mentor_pending_question"] = None
    st.session_state["mentor_messages"].append(
        {"role": "user", "content": question_to_answer}
    )

    with main_col:
        with st.chat_message("user"):
            st.markdown(question_to_answer)

        with st.chat_message("assistant"):
            think_slot = st.empty()
            _render_thinking(think_slot)
            answer = ask_career_ai(
                question_to_answer,
                conversation_history=st.session_state["mentor_messages"],
            )
            think_slot.empty()
            stream_slot = st.empty()
            _stream_answer(stream_slot, answer)

    st.session_state["mentor_messages"].append(
        {"role": "assistant", "content": answer}
    )

    user_id = st.session_state.get("user_id")
    if user_id:
        _save_current_chat(user_id, question_to_answer)

    st.rerun()
