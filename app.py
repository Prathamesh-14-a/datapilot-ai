# app.py
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="DataPilot AI — Navigate Your Data Career",
    page_icon="assets/mini_logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# LOGO LOADER (base64 so it works inside HTML)
# --------------------------------------------------
def load_logo_b64(path: str = "assets/logo.png") -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode()

LOGO_B64 = load_logo_b64()
LOGO_SRC = f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else ""

# --------------------------------------------------
# GLOBAL STYLES
# --------------------------------------------------
st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu, header {visibility: hidden;}
#footer {
    visibility: hidden;
}
.block-container {padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important;}

/* Base */
html, body, [class*="css"] {
    background: #000000 !important;
}

/* Aurora background */
.dp-bg {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;

    background:
        radial-gradient(circle at 15% 15%, rgba(37,99,235,0.12), transparent 30%),
        radial-gradient(circle at 85% 20%, rgba(34,211,238,0.08), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(59,130,246,0.10), transparent 35%),
        linear-gradient(
            180deg,
            #000000 0%,
            #03050a 30%,
            #050914 70%,
            #000000 100%
        );
}
.dp-orb {
    position: absolute; border-radius: 50%; filter: blur(90px); opacity: .45;
    animation: dp-float 22s ease-in-out infinite;
}
.dp-orb.o1 {width:520px;height:520px;background:#2563eb;top:-120px;left:-120px;}
.dp-orb.o2 {width:460px;height:460px;background:#22d3ee;top:30%;right:-140px;animation-delay:-7s;}
.dp-orb.o3 {width:560px;height:560px;background:#6366f1;bottom:-180px;left:25%;animation-delay:-14s;}
@keyframes dp-float {
    0%,100% {transform: translate(0,0) scale(1);}
    50%     {transform: translate(40px,-30px) scale(1.08);}
}

/* Grid overlay */
.dp-grid {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: .35;
    background-image:
        linear-gradient(rgba(148,163,184,.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148,163,184,.06) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
}

/* Content wrapper */
.dp-wrap {position: relative; z-index: 2; padding: 32px 6vw 80px;}

/* Top nav */
.dp-nav {
    display:flex; align-items:center; justify-content:space-between;
    padding: 14px 20px; border-radius: 16px;
    background: rgba(10,15,28,0.55);
    border: 1px solid rgba(148,163,184,0.12);
    backdrop-filter: blur(14px);
    margin-bottom: 64px;
}
.dp-nav-logo {display:flex; align-items:center; gap:12px;}
.dp-nav-logo img {height: 36px;}
.dp-nav-badge {
    font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
    color: #93c5fd; padding: 4px 10px; border-radius: 999px;
    border: 1px solid rgba(59,130,246,0.35); background: rgba(59,130,246,0.08);
}

/* HERO */
.dp-hero {text-align:center; padding: 40px 0 80px;}
.dp-hero-logo {
    display:flex; justify-content:center; margin-bottom: 28px;
    animation: dp-rise .9s ease both; margin-top: -60px;
}
.dp-hero-logo img {
    height: 130px; filter: drop-shadow(0 12px 40px rgba(59,130,246,0.45));
}
.dp-pill {
    display:inline-flex; align-items:center; gap:8px;
    padding: 8px 16px; border-radius: 999px; font-size: 13px;
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.25);
    color: #a5f3fc; margin-bottom: 22px;
}
.dp-pill .dot {width:6px;height:6px;border-radius:50%;background:#22d3ee;box-shadow:0 0 12px #22d3ee;}
.dp-h1 {
    font-size: clamp(40px, 6vw, 76px); line-height: 1.05; font-weight: 800;
    letter-spacing: -0.03em; margin: 8px 0 22px;
    background: linear-gradient(180deg,#ffffff 0%, #93c5fd 60%, #22d3ee 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.dp-sub {
    font-size: clamp(16px, 1.6vw, 20px); color: #94a3b8;
    max-width: 760px; margin: 0 auto 40px; line-height: 1.65;
}
.dp-cta {display:flex; gap:14px; justify-content:center; flex-wrap:wrap;}
.dp-meta {
    margin-top: 28px; display:flex; gap:28px; justify-content:center; flex-wrap:wrap;
    color:#64748b; font-size:13px;
}
.dp-meta span {display:inline-flex; align-items:center; gap:6px;}
.dp-meta i {width:6px;height:6px;border-radius:50%;background:#22d3ee;}

/* Section */
.dp-section {padding: 80px 0;}
.dp-eyebrow {
    text-align:center; font-size:12px; letter-spacing:.22em; text-transform:uppercase;
    color:#22d3ee; margin-bottom: 14px;
}
.dp-h2 {
    text-align:center; font-size: clamp(30px,3.6vw,48px); font-weight:800;
    letter-spacing:-0.02em; margin: 0 0 14px;
    background: linear-gradient(180deg,#ffffff,#cbd5e1);
    -webkit-background-clip:text; background-clip:text; color:transparent;
}
.dp-h2-sub {text-align:center; color:#94a3b8; max-width:680px; margin:0 auto 56px; font-size:16px;}

/* Feature grid */
.dp-grid3 {
    display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 22px;
}
.dp-card {
    position: relative; padding: 28px; border-radius: 20px;
    background: linear-gradient(
        180deg,
        rgba(8,10,15,0.92),
        rgba(3,4,8,0.92)
    );
    border: 1px solid rgba(148,163,184,0.12);
    backdrop-filter: blur(12px);
    transition: transform .35s ease, border-color .35s ease, box-shadow .35s ease;
    overflow: hidden;
}
.dp-card::before {
    content:""; position:absolute; inset:0; border-radius:20px; padding:1px;
    background: linear-gradient(135deg, rgba(59,130,246,0.5), rgba(34,211,238,0.0) 60%);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    opacity: 0; transition: opacity .35s ease;
}
.dp-card:hover {transform: translateY(-4px); border-color: rgba(34,211,238,0.35);
    box-shadow: 0 20px 50px -20px rgba(34,211,238,0.25);}
.dp-card:hover::before {opacity: 1;}
.dp-card .ico {
    width:48px;height:48px;border-radius:14px; display:grid; place-items:center;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.3);
    margin-bottom: 18px; color:#60a5fa;
}
.dp-card h3 {font-size:19px; font-weight:700; margin:0 0 8px; color:#e6edf7;}
.dp-card p {color:#94a3b8; font-size:14.5px; line-height:1.6; margin:0 0 14px;}
.dp-card ul {list-style:none; padding:0; margin:0;}
.dp-card li {
    color:#cbd5e1; font-size:13.5px; padding: 6px 0 6px 22px; position:relative;
}
.dp-card li::before {
    content:""; position:absolute; left:0; top:12px; width:12px; height:2px;
    background: linear-gradient(90deg,#3b82f6,#22d3ee); border-radius:2px;
}

/* Steps */
.dp-steps {
    display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:20px;
    position: relative;
}
.dp-step {
    padding: 26px; border-radius: 18px;
    background: linear-gradient(180deg, rgba(15,23,42,0.65), rgba(10,15,28,0.5));
    border: 1px solid rgba(148,163,184,0.12);
    backdrop-filter: blur(10px);
    transition: transform .3s ease, border-color .3s ease;
}
.dp-step:hover {transform: translateY(-3px); border-color: rgba(59,130,246,0.35);}
.dp-step .num {
    font-size:13px; letter-spacing:.2em; color:#22d3ee; margin-bottom:14px;
}
.dp-step h4 {font-size:18px; font-weight:700; margin:0 0 8px; color:#e6edf7;}
.dp-step p {color:#94a3b8; font-size:13.5px; line-height:1.6; margin:0;}

/* Built-for chips */
.dp-chips {display:flex; flex-wrap:wrap; gap:12px; justify-content:center;}
.dp-chip {
    padding: 12px 20px; border-radius: 999px; font-size:14px; color:#cbd5e1;
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(148,163,184,0.15);
    backdrop-filter: blur(10px);
    transition: all .25s ease;
}
.dp-chip:hover {
    color:#fff; border-color: rgba(34,211,238,0.5);
    box-shadow: 0 0 24px rgba(34,211,238,0.18);
    transform: translateY(-2px);
}

/* Final CTA */
.dp-cta-box {
    position: relative; padding: 56px 32px; border-radius: 28px; text-align:center;
    background:
        radial-gradient(600px 300px at 50% 0%, rgba(34,211,238,0.18), transparent 70%),
        linear-gradient(180deg, rgba(15,23,42,0.85), rgba(10,15,28,0.7));
    border: 1px solid rgba(59,130,246,0.25);
    overflow: hidden;
}
.dp-cta-box h2 {
    font-size: clamp(28px,3.4vw,44px); font-weight:800; margin:0 0 14px;
    background: linear-gradient(180deg,#ffffff,#93c5fd);
    -webkit-background-clip:text; background-clip:text; color:transparent;
}
.dp-cta-box p {color:#94a3b8; max-width:560px; margin: 0 auto 28px;}

/* Footer */
.dp-footer {
    margin-top: 80px; padding: 36px 0 24px;
    border-top: 1px solid rgba(148,163,184,0.1);
    display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;
    color: #cbd5e1; font-size:13px;
}
.dp-footer img {height:28px; opacity:.9;}
.dp-foot-brand {display:flex; align-items:center; gap:12px;}
.dp-footer {
    position: relative;
    z-index: 9999;
}
/* Reveal */
.dp-reveal {opacity:0; transform: translateY(20px); animation: dp-rise .9s ease forwards;}
.dp-reveal.d1 {animation-delay:.1s;}
.dp-reveal.d2 {animation-delay:.25s;}
.dp-reveal.d3 {animation-delay:.4s;}
@keyframes dp-rise {to {opacity:1; transform: translateY(0);}}

/* Streamlit buttons -> premium */
div.stButton > button {
    width: 100%;
    padding: 14px 26px !important;
    border-radius: 14px !important;
    font-weight: 600 !important; font-size: 15px !important;
    border: 1px solid rgba(59,130,246,0.4) !important;
    background: linear-gradient(135deg,#2563eb,#22d3ee) !important;
    color: #ffffff !important;
    box-shadow: 0 10px 30px -10px rgba(34,211,238,0.55) !important;
    transition: transform .2s ease, box-shadow .2s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 18px 40px -12px rgba(34,211,238,0.75) !important;
}
div[data-testid="column"]:nth-of-type(2) div.stButton > button {
    background: rgba(15,23,42,0.7) !important;
    border: 1px solid rgba(148,163,184,0.25) !important;
    box-shadow: none !important;
}
div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {
    border-color: rgba(34,211,238,0.5) !important;
    background: rgba(15,23,42,0.9) !important;
}
</style>

<div class="dp-bg">
    <div class="dp-orb o1"></div>
    <div class="dp-orb o2"></div>
    <div class="dp-orb o3"></div>
</div>
<div class="dp-grid"></div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ---------- MAGNETIC GRADIENT BORDER on cards ---------- */
.dp-card, .dp-feature {
    position: relative;
    isolation: isolate;
}
.dp-card::before, .dp-feature::before {
    content: "";
    position: absolute; inset: -1px;
    border-radius: inherit;
    padding: 1px;
    background: conic-gradient(from var(--angle, 0deg),
        rgba(34,211,238,0.0) 0deg,
        rgba(34,211,238,0.55) 90deg,
        rgba(168,85,247,0.55) 180deg,
        rgba(34,211,238,0.0) 270deg);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    opacity: 0; transition: opacity 0.4s ease;
    animation: dp-spin 6s linear infinite;
    z-index: -1;
}
.dp-card:hover::before, .dp-feature:hover::before { opacity: 1; }
@property --angle { syntax: "<angle>"; initial-value: 0deg; inherits: false; }
@keyframes dp-spin { to { --angle: 360deg; } }

/* ---------- TEXT GRADIENT SWEEP on hover ---------- */
.dp-hover-text {
    background: linear-gradient(90deg, #e2e8f0 0%, #22d3ee 50%, #a855f7 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    background-position: 0% center;
    transition: background-position 0.6s ease;
}
.dp-hover-text:hover { background-position: 100% center; }

/* ---------- MAGNETIC BUTTON PULSE ---------- */
.stButton > button {
    transform: translateZ(0);
    transition: transform 0.25s cubic-bezier(.2,.8,.2,1),
                box-shadow 0.25s ease, filter 0.25s ease;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    filter: brightness(1.08);
    box-shadow: 0 12px 40px rgba(34,211,238,0.35),
                0 0 0 1px rgba(34,211,238,0.4) inset;
}
.stButton > button:active { transform: translateY(0) scale(0.98); }

/* ---------- INPUT GLOW RING ---------- */
.stTextInput input, .stPassword input {
    transition: box-shadow 0.3s ease, border-color 0.3s ease, transform 0.2s ease;
}
.stTextInput input:focus, .stPassword input:focus {
    box-shadow: 0 0 0 3px rgba(34,211,238,0.25),
                0 0 30px rgba(34,211,238,0.25);
    transform: translateY(-1px);
}

/* ---------- BADGE / CHIP RIPPLE ---------- */
.dp-chip {
    position: relative; overflow: hidden;
    transition: transform 0.25s ease, background 0.3s ease;
}
.dp-chip:hover { transform: translateY(-2px); background: rgba(34,211,238,0.15); }
.dp-chip::after {
    content:""; position:absolute; inset:0;
    background: radial-gradient(circle at var(--x,50%) var(--y,50%),
        rgba(34,211,238,0.35), transparent 40%);
    opacity:0; transition: opacity 0.4s ease;
}
.dp-chip:hover::after { opacity: 1; }

/* ---------- SCROLL-REVEAL ---------- */
.dp-scroll {
    opacity: 0; transform: translateY(30px);
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(.2,.8,.2,1);
}
.dp-scroll.dp-in { opacity: 1; transform: translateY(0); }

/* ---------- FLOATING LOGO ---------- */
.dp-logo, .dp-logo-mark {
    animation: dp-floaty 5s ease-in-out infinite;
}
@keyframes dp-floaty {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-6px); }
}

/* ---------- GRADIENT HEADLINE SHIMMER LOOP ---------- */
.dp-headline {
    background-size: 200% auto;
    animation: dp-shine 4s linear infinite;
}
@keyframes dp-shine {
    0%   { background-position: 0% center; }
    100% { background-position: 200% center; }
}
</style>
""", unsafe_allow_html=True)

#---------------------------------------------
# JS
#---------------------------------------------

components.html("""
<script>
const doc = window.parent.document;

/* Magnetic buttons (subtle pull toward cursor) */
doc.querySelectorAll('.stButton > button').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width/2;
        const y = e.clientY - r.top - r.height/2;
        btn.style.transform = `translate(${x*0.12}px, ${y*0.18}px) scale(1.03)`;
    });
    btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
});

/* Ripple position for chips */
doc.querySelectorAll('.dp-chip').forEach(el => {
    el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty('--x', (e.clientX - r.left) + 'px');
        el.style.setProperty('--y', (e.clientY - r.top) + 'px');
    });
});

/* Scroll-reveal observer */
const io = new IntersectionObserver((entries) => {
    entries.forEach(en => { if (en.isIntersecting) en.target.classList.add('dp-in'); });
}, { threshold: 0.12 });
doc.querySelectorAll('.dp-scroll, .dp-card, .dp-feature').forEach(el => {
    el.classList.add('dp-scroll'); io.observe(el);
});

/* Parallax aurora orbs follow cursor */
doc.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 20;
    const y = (e.clientY / window.innerHeight - 0.5) * 20;
    doc.querySelectorAll('.dp-orb').forEach((orb, i) => {
        const k = (i+1) * 0.6;
        orb.style.translate = `${x*k}px ${y*k}px`;
    });
});

/* Tilt-on-hover for any .dp-tilt element */
doc.querySelectorAll('.dp-card, .dp-tilt').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        card.style.transform = `perspective(900px) rotateX(${(0.5-py)*6}deg) rotateY(${(px-0.5)*8}deg) translateY(-2px)`;
    });
    card.addEventListener('mouseleave', () => { card.style.transform=''; });
});
</script>
""", height=0)
# --------------------------------------------------
# SVG ICONS
# --------------------------------------------------
def svg(name):
    icons = {
        "resume": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h4"/></svg>',
        "skill":  '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/></svg>',
        "salary": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 6v12M9 9h4.5a2 2 0 0 1 0 4H10a2 2 0 0 0 0 4h5"/></svg>',
        "mentor": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z"/></svg>',
        "fit":    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
        "market": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg>',
    }
    return icons.get(name, "")

# --------------------------------------------------
# NAV
# --------------------------------------------------
st.markdown(f"""
<div class="dp-wrap">
  <div class="dp-nav dp-reveal dp-scroll">
    <div class="dp-nav-logo ">
      {f'<img src="{LOGO_SRC}" class="dp-logo" alt="DataPilot AI"/>' if LOGO_SRC else '<strong style="color:#fff">DataPilot AI</strong>'}
    </div>
    <div class="dp-nav-badge">AI Career Platform · v1.0</div>
  </div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HERO
# --------------------------------------------------
st.markdown(f"""
  <section class="dp-hero">
    <div class="dp-hero-logo">
      {f'<img src="{LOGO_SRC}" class="dp-logo" alt="DataPilot AI"/>' if LOGO_SRC else ''}
    </div>
    <div class="dp-pill dp-reveal d1" class="dp-chip"><span class="dot"></span> Built for Data, Analytics & ML professionals</div>
    <h1 class="dp-h1 dp-reveal d1">Navigate Your Data Career<br/>With AI</h1>
    <center><p class="dp-sub dp-reveal d2">
      From resume to dream job — DataPilot AI gives you personalized roadmaps,
      real-time skill gap analysis, salary intelligence, and interview prep
      crafted for Data Analysts, Scientists, Engineers, and ML professionals.
    </p></center>
  </section>
""", unsafe_allow_html=True)

# CTA buttons (preserve st.switch_page)
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c2:
    if st.button("Get Started Free", use_container_width=True, key="cta_signup"):
        st.switch_page("pages/2_Signup.py")
with c3:
    if st.button("Sign In", use_container_width=True, key="cta_login"):
        st.switch_page("pages/1_Login.py")

st.markdown("""
  <div class="dp-meta dp-reveal d3">
    <span><i></i> No credit card required</span>
    <span><i></i> AI-powered insights</span>
    <span><i></i> Trusted by data professionals</span>
  </div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FEATURES
# --------------------------------------------------
st.markdown(f"""
<section class="dp-section">
  <div class="dp-eyebrow">Capabilities</div>
  <h2 class="dp-h2 dp-hover-text">Everything you need to grow your data career</h2>
  <center><p class="dp-h2-sub">Six AI-powered modules working together to take you from where you are to where you want to be.</p></center>

  <div class="dp-grid3">
    <div class="dp-card">
      <div class="ico">{svg("resume")}</div>
      <h3 class="dp-hover-text">Resume Analyzer</h3>
      <p>Deep ATS analysis and recruiter-grade scoring for data-focused resumes.</p>
      <ul>
        <li>ATS compatibility analysis</li>
        <li>Resume scoring & feedback</li>
        <li>Keyword optimization</li>
        <li>Recruiter readiness check</li>
      </ul>
    </div>
    <div class="dp-card">
      <div class="ico">{svg("skill")}</div>
      <h3 class="dp-hover-text">Skill Gap Analysis</h3>
      <p>Compare your profile against live job market requirements in seconds.</p>
      <ul>
        <li>Detect missing skills</li>
        <li>Benchmark against target roles</li>
        <li>Personalized learning roadmap</li>
        <li>Priority-ranked next steps</li>
      </ul>
    </div>
    <div class="dp-card">
      <div class="ico">{svg("salary")}</div>
      <h3 class="dp-hover-text">Salary Predictor</h3>
      <p>Know your market value before you ever sit down at the negotiation table.</p>
      <ul>
        <li>Estimated market salary</li>
        <li>Location-based insights</li>
        <li>Experience-based predictions</li>
        <li>Role and skill multipliers</li>
      </ul>
    </div>
    <div class="dp-card">
      <div class="ico">{svg("mentor")}</div>
      <h3 class="dp-hover-text">AI Career Mentor</h3>
      <p>A 24/7 career coach trained on the patterns of top data professionals.</p>
      <ul>
        <li>Personalized career guidance</li>
        <li>Interview preparation</li>
        <li>Long-term career planning</li>
        <li>Actionable weekly goals</li>
      </ul>
    </div>
    <div class="dp-card">
      <div class="ico">{svg("fit")}</div>
      <h3 class="dp-hover-text">Job Role Fit Predictor</h3>
      <p>Match your profile to real job descriptions with explainable confidence scores.</p>
      <ul>
        <li>Resume to role matching</li>
        <li>Confidence scoring</li>
        <li>Alternative career suggestions</li>
        <li>Strength & weakness breakdown</li>
      </ul>
    </div>
    <div class="dp-card">
      <div class="ico">{svg("market")}</div>
      <h3 class="dp-hover-text">Market Intelligence</h3>
      <p>Stay ahead with live analytics on what the data industry is hiring for.</p>
      <ul>
        <li>Trending skills</li>
        <li>Salary trends</li>
        <li>Industry demand analytics</li>
        <li>Hiring velocity by role</li>
      </ul>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HOW IT WORKS
# --------------------------------------------------
st.markdown("""
<section class="dp-section">
  <div class="dp-eyebrow">How it works</div>
  <h2 class="dp-h2 dp-hover-text">From resume to dream role in four steps</h2>
  <center><p class="dp-h2-sub">A guided, AI-powered workflow that compounds your career momentum.</p></center>

  <div class="dp-steps">
    <div class="dp-step dp-feature" >
      <div class="num">STEP 01</div>
      <h4 class="dp-hover-text">Upload Resume</h4>
      <p>Drop your resume and let DataPilot AI parse your skills, experience, and trajectory.</p>
    </div>
    <div class="dp-step dp-feature">
      <div class="num">STEP 02</div>
      <h4 class="dp-hover-text">Analyze Skills</h4>
      <p>Get instant gap analysis against the data roles you're targeting today.</p>
    </div>
    <div class="dp-step dp-feature">
      <div class="num">STEP 03</div>
      <h4 class="dp-hover-text">Discover Opportunities</h4>
      <p>Match to roles, see salary ranges, and uncover paths you didn't know existed.</p>
    </div>
    <div class="dp-step dp-feature">
      <div class="num">STEP 04</div>
      <h4 class="dp-hover-text">Land Your Dream Role</h4>
      <p>Interview prep, tailored coaching, and a roadmap to close every offer.</p>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# --------------------------------------------------
# BUILT FOR
# --------------------------------------------------
st.markdown("""
<section class="dp-section">
  <div class="dp-eyebrow">Built for</div>
  <h2 class="dp-h2 dp-hover-text">Every role in the modern data stack</h2>
  <center><p class="dp-h2-sub">Purpose-built guidance for the people shaping data-driven companies.</p></center>
  <div class="dp-chips">
    <div class="dp-chip">Data Analysts</div>
    <div class="dp-chip">Data Scientists</div>
    <div class="dp-chip">Data Engineers</div>
    <div class="dp-chip">Machine Learning Engineers</div>
    <div class="dp-chip">BI Analysts</div>  
    <div class="dp-chip">Analytics Engineers</div>
    <div class="dp-chip">Business Analysts</div>
  </div>
</section>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FINAL CTA
# --------------------------------------------------
st.markdown("""
<section class="dp-section">
  <div class="dp-cta-box dp-tilt">
    <h2>Ready to Accelerate Your Data Career?</h2>
    <p>Join data professionals using DataPilot AI to navigate their next move with confidence.</p>
  </div>
</section>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c2:
    if st.button("Get Started", use_container_width=True, key="final_signup"):
        st.switch_page("pages/2_Signup.py")
with c3:
    if st.button("Sign In ", use_container_width=True, key="final_login"):
        st.switch_page("pages/1_Login.py")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(f"""
  <footer class="dp-footer">
    <div class="dp-foot-brand">
      {f'<img src="{LOGO_SRC}"  alt="DataPilot AI"/>' if LOGO_SRC else '<strong>DataPilot AI</strong>'}
      <span>Navigate Your Data Career.</span>
    </div>
    <div>© 2026 DataPilot AI · v1.0</div>
  </footer>
</div>
""", unsafe_allow_html=True)
