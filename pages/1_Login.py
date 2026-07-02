# pages/1_Login.py
import base64
from pathlib import Path

import streamlit as st

from src.auth.auth_service import login
from src.auth.session_manager import create_session, is_authenticated
from src.config.paths import ASSETS_DIR, PAGES_DIR


def load_logo(path: Path | None = None):
    try:
        target = path or (ASSETS_DIR / "logo.png")
        ext = target.suffix.lower().replace(".", "")
        mime = "svg+xml" if ext == "svg" else ext
        with target.open("rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/{mime};base64,{data}"
    except Exception:
        return ""

LOGO_B64 = load_logo(ASSETS_DIR / "logo.png")
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="DataPilot AI — Login",
    page_icon=str(ASSETS_DIR / "mini_logo.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# REDIRECT IF ALREADY LOGGED IN
# --------------------------------------------------
if is_authenticated():
    st.switch_page(str(PAGES_DIR / "3_Dashboard.py"))

# --------------------------------------------------
# GLOBAL CSS (Design System)
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg: #0B1020;
    --bg-2: #111827;
    --border: #1F2937;
    --primary: #2563EB;
    --accent: #22D3EE;
    --text: #F8FAFC;
    --muted: #94A3B8;
    --radius: 16px;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"], .stApp {
    background: radial-gradient(1200px 600px at 10% -10%, rgba(37,99,235,0.18), transparent 60%),
                radial-gradient(900px 500px at 100% 0%, rgba(34,211,238,0.10), transparent 55%),
                var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

#MainMenu, footer, header {visibility: hidden;}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {display:none !important;}
[data-testid="stHeader"] {background: transparent;}
            
.block-container {
    padding: 4rem 3rem 3rem 1rem !important;
    max-width: 1280px !important;
}

/* ---------------- LEFT SIDE ---------------- */
.dp-brand {
    display:flex; align-items:center; gap:12px; margin-bottom:48px; margin-left: -16px;
}
.dp-logo {
    width:44px; height:44px; border-radius:12px;
    background: linear-gradient(135deg, #2563EB 0%, #22D3EE 100%);
    display:flex; align-items:center; justify-content:center;
    box-shadow: 0 8px 24px rgba(37,99,235,0.35);
}
.dp-logo svg { width:24px; height:24px; }
.dp-brand-name {
    font-size: 20px; font-weight: 700; letter-spacing:-0.01em; color: var(--text);
}
.dp-brand-name span {
    background: linear-gradient(135deg, #2563EB, #22D3EE);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.dp-headline {
    font-size: clamp(36px, 4.5vw, 56px);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin: 0 0 24px 0;
    background: linear-gradient(180deg, #F8FAFC 0%, #94A3B8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.dp-sub {
    font-size: 17px; line-height: 1.65; color: var(--muted);
    max-width: 460px; margin-bottom: 40px;
}
.dp-features { display:flex; flex-direction:column; gap:18px; max-width:460px;}
.dp-feature { display:flex; align-items:flex-start; gap:14px; }
.dp-feat-ico {
    width:36px; height:36px; border-radius:10px; flex-shrink:0;
    background: rgba(34,211,238,0.08); border:1px solid rgba(34,211,238,0.18);
    display:flex; align-items:center; justify-content:center;
}
.dp-feat-ico svg { width:18px; height:18px; stroke:#22D3EE; }
.dp-feat-text { font-size:14px; color: var(--text); font-weight:500; line-height:1.5;}
.dp-feat-text small { display:block; color: var(--muted); font-weight:400; margin-top:2px;}

/* ---------------- RIGHT SIDE CARD ---------------- */
.dp-card {
    background: linear-gradient(180deg, rgba(17,24,39,0.7) 0%, rgba(11,16,32,0.7) 100%);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: var(--radius);
    padding: 40px 36px;
    box-shadow:
        0 30px 80px -20px rgba(0,0,0,0.5),
        0 0 0 1px rgba(37,99,235,0.05),
        inset 0 1px 0 rgba(255,255,255,0.04);
    margin-top: 12px;
}
.dp-card h2 {
    font-size: 24px; font-weight: 700; letter-spacing:-0.02em;
    margin:0 0 6px 0; color: var(--text);
}
.dp-card p.lead {
    font-size: 14px; color: var(--muted); margin:0 0 28px 0;
}

/* Inputs */
.stTextInput > label {
    font-size: 13px !important; font-weight: 500 !important;
    color: var(--text) !important; margin-bottom: 6px !important;
}
.stTextInput > div > div > input {
    background: rgba(11,16,32,0.6) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    height: 46px !important;
}
.stTextInput > div > div > input::placeholder { color: #4B5563 !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.18) !important;
    outline: none !important;
}
.stTextInput > div > div {
    background: transparent !important; border: none !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2563EB 0%, #22D3EE 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.01em !important;
    padding: 12px 20px !important;
    height: 46px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 10px 24px -8px rgba(37,99,235,0.5) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 16px 32px -10px rgba(34,211,238,0.5) !important;
    filter: brightness(1.05) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary (sign up) button */
.dp-secondary .stButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    box-shadow: none !important;
}
.dp-secondary .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(34,211,238,0.04) !important;
}

/* Divider */
.dp-divider {
    display:flex; align-items:center; gap:12px;
    margin: 24px 0 16px 0; color: var(--muted); font-size:12px;
}
.dp-divider::before, .dp-divider::after {
    content:""; flex:1; height:1px; background: var(--border);
}

.dp-signup-row {
    text-align:center; color: var(--muted); font-size:13px; margin-top: 8px;
}

/* Alerts */
.stAlert {
    background: rgba(17,24,39,0.8) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

/* Footer note */
.dp-foot {
    text-align:center; color:#4B5563; font-size:12px; margin-top:32px;
}

@media (max-width:768px){
  html,body,[class*="css"],[data-testid="stAppViewContainer"],.stApp{overflow-x:hidden !important;}

  .block-container{padding:2rem 1rem 2rem 1rem !important;max-width:100% !important;}

  [data-testid="column"]{width:100% !important;flex:1 1 100% !important;min-width:100% !important;}
  [data-testid="stHorizontalBlock"]{flex-direction:column !important;gap:0 !important;}

  .dp-aurora{overflow:hidden !important;}
  .dp-orb.o1{width:260px;height:260px;top:-80px;left:-80px;}
  .dp-orb.o2{width:220px;height:220px;bottom:-60px;right:-60px;}
  .dp-orb.o3{width:180px;height:180px;opacity:0.15;}
  .dp-orb{animation-duration:24s !important;filter:blur(60px) !important;}

  #dp-stars{width:100vw !important;max-width:100vw !important;overflow:hidden !important;}

  .dp-brand{justify-content:center !important;margin-left:0 !important;margin-bottom:28px !important;}
  .dp-brand img{max-width:400px !important;height:auto !important;}

  .dp-headline{font-size:34px !important;text-align:center !important;margin-bottom:16px !important;letter-spacing:-0.02em !important;}

  .dp-sub{font-size:15px !important;text-align:center !important;margin:0 auto 28px auto !important;max-width:100% !important;}

  .dp-features{max-width:100% !important;gap:14px !important;}
  .dp-feature{width:100% !important;padding:12px !important;background:rgba(34,211,238,0.04);border:1px solid rgba(34,211,238,0.1);border-radius:12px;}
  .dp-feature:hover{transform:none !important;}

  .dp-card{padding:24px 18px !important;margin-top:28px !important;width:100% !important;box-sizing:border-box !important;transform:none !important;}
  .dp-card:hover::before{opacity:0 !important;}
  .dp-card h2{font-size:20px !important;}
  .dp-card p.lead{font-size:13px !important;}

  .stTextInput>label{font-size:13px !important;}
  .stTextInput>div>div>input{font-size:14px !important;height:48px !important;padding:12px 14px !important;width:100% !important;box-sizing:border-box !important;}

  .stButton>button{width:100% !important;font-size:15px !important;height:48px !important;padding:12px 16px !important;box-sizing:border-box !important;}
  .stButton>button::after{display:none !important;}

  .dp-divider{margin:18px 0 12px 0 !important;font-size:12px !important;}

  .dp-signup-row{font-size:13px !important;}
  .dp-foot{font-size:11px !important;margin-top:20px !important;}

  .dp-feat-ico{width:32px !important;height:32px !important;flex-shrink:0 !important;}
  .dp-feat-ico svg{width:16px !important;height:16px !important;}
  .dp-feat-text{font-size:13px !important;}
  .dp-feat-text small{font-size:12px !important;}

  .dp-brand-name{font-size:18px !important;}

  [data-testid="stStatusWidget"] {
    display: none !important;
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
""", unsafe_allow_html=True)


# --------------------------------------------------
# JS + MOTION EFFECTS
# --------------------------------------------------
st.markdown("""
<style>
/* Animated aurora orbs */
.dp-aurora {
    position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;
}
.dp-orb {
    position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.45;
    animation: dp-float 18s ease-in-out infinite;
}
.dp-orb.o1 { width: 480px; height: 480px; background: #2563EB; top: -120px; left: -120px;}
.dp-orb.o2 { width: 380px; height: 380px; background: #22D3EE; bottom: -100px; right: -80px; animation-delay: -6s;}
.dp-orb.o3 { width: 300px; height: 300px; background: #4F46E5; top: 40%; left: 45%; opacity: 0.25; animation-delay: -12s;}

@keyframes dp-float {
    0%,100% { transform: translate(0,0) scale(1); }
    33%     { transform: translate(40px,-30px) scale(1.08); }
    66%     { transform: translate(-30px,40px) scale(0.95); }
}

/* Constellation canvas */
#dp-stars {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: 0.55;
}

/* Make Streamlit content sit above effects */
[data-testid="stAppViewContainer"] > .main { position: relative; z-index: 2; }
.block-container { position: relative; z-index: 2; }

/* Reveal on load */
.dp-reveal { opacity: 0; transform: translateY(14px); animation: dp-rise 0.9s cubic-bezier(.2,.7,.2,1) forwards; }
.dp-reveal.d1 { animation-delay: 0.05s; }
.dp-reveal.d2 { animation-delay: 0.18s; }
.dp-reveal.d3 { animation-delay: 0.32s; }
@keyframes dp-rise { to { opacity: 1; transform: translateY(0); } }

/* Logo subtle pulse */
.dp-logo { animation: dp-glow 3.5s ease-in-out infinite; }
@keyframes dp-glow {
    0%,100% { box-shadow: 0 8px 24px rgba(37,99,235,0.35); }
    50%     { box-shadow: 0 12px 40px rgba(34,211,238,0.55); }
}

/* Headline shimmer */
.dp-headline {
    background-size: 200% 100% !important;
    animation: dp-shimmer 6s linear infinite;
}
@keyframes dp-shimmer {
    0%   { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

/* Card tilt + glow on hover (via JS variables) */
.dp-card {
    transform: perspective(1200px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
    transition: transform 0.25s ease, box-shadow 0.3s ease;
    position: relative; overflow: hidden;
}
.dp-card::before {
    content:""; position:absolute; inset:0; border-radius:inherit; pointer-events:none;
    background: radial-gradient(600px circle at var(--mx,50%) var(--my,50%),
                rgba(34,211,238,0.12), transparent 40%);
    opacity: 0; transition: opacity 0.3s ease;
}
.dp-card:hover::before { opacity: 1; }

/* Input focus ring upgrade */
.stTextInput > div > div > input:focus {
    box-shadow: 0 0 0 3px rgba(37,99,235,0.25),
                0 0 24px rgba(34,211,238,0.25) !important;
}

/* Button shine sweep */
.stButton > button { position: relative; overflow: hidden; }
.stButton > button::after {
    content:""; position:absolute; top:0; left:-120%; width:60%; height:100%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.35), transparent);
    transform: skewX(-20deg); transition: left 0.7s ease;
}
.stButton > button:hover::after { left: 130%; }

/* Feature card hover lift */
.dp-feature { transition: transform 0.3s ease; }
.dp-feature:hover { transform: translateX(6px); }
.dp-feature:hover .dp-feat-ico {
    background: rgba(34,211,238,0.18);
    border-color: rgba(34,211,238,0.4);
}
</style>

<div class="dp-aurora">
    <div class="dp-orb o1"></div>
    <div class="dp-orb o2"></div>
    <div class="dp-orb o3"></div>
</div>
<canvas id="dp-stars"></canvas>

<script>
(function(){
    const doc = window.parent.document;

    // ---- Constellation canvas ----
    const canvas = doc.getElementById('dp-stars');
    if (canvas && !canvas.dataset.init) {
        canvas.dataset.init = '1';
        const ctx = canvas.getContext('2d');
        let w, h, pts = [];
        const COUNT = 70;
        function resize(){
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }
        function init(){
            pts = Array.from({length: COUNT}, () => ({
                x: Math.random()*w, y: Math.random()*h,
                vx: (Math.random()-0.5)*0.25, vy: (Math.random()-0.5)*0.25,
                r: Math.random()*1.4 + 0.4
            }));
        }
        function draw(){
            ctx.clearRect(0,0,w,h);
            for (let p of pts){
                p.x += p.vx; p.y += p.vy;
                if (p.x<0||p.x>w) p.vx*=-1;
                if (p.y<0||p.y>h) p.vy*=-1;
                ctx.beginPath();
                ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
                ctx.fillStyle = 'rgba(148,197,255,0.7)';
                ctx.fill();
            }
            for (let i=0;i<pts.length;i++){
                for (let j=i+1;j<pts.length;j++){
                    const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y;
                    const d2 = dx*dx+dy*dy;
                    if (d2 < 14000){
                        const a = 1 - d2/14000;
                        ctx.strokeStyle = `rgba(34,211,238,${a*0.18})`;
                        ctx.lineWidth = 0.6;
                        ctx.beginPath();
                        ctx.moveTo(pts[i].x,pts[i].y);
                        ctx.lineTo(pts[j].x,pts[j].y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(draw);
        }
        window.addEventListener('resize', () => { resize(); init(); });
        resize(); init(); draw();
    }

    // ---- Card tilt + spotlight ----
    function bindCard(){
        const card = doc.querySelector('.dp-card');
        if (!card || card.dataset.bound) return;
        card.dataset.bound = '1';
        card.addEventListener('mousemove', e => {
            const r = card.getBoundingClientRect();
            const x = e.clientX - r.left, y = e.clientY - r.top;
            const rx = ((y / r.height) - 0.5) * -4;
            const ry = ((x / r.width)  - 0.5) *  4;
            card.style.setProperty('--rx', rx + 'deg');
            card.style.setProperty('--ry', ry + 'deg');
            card.style.setProperty('--mx', x + 'px');
            card.style.setProperty('--my', y + 'px');
        });
        card.addEventListener('mouseleave', () => {
            card.style.setProperty('--rx','0deg');
            card.style.setProperty('--ry','0deg');
        });
    }

    // ---- Reveal classes ----
    function bindReveal(){
        const brand = doc.querySelector('.dp-brand');
        const head  = doc.querySelector('.dp-headline');
        const sub   = doc.querySelector('.dp-sub');
        const feats = doc.querySelector('.dp-features');
        const card  = doc.querySelector('.dp-card');
        [brand, head].forEach(el => el && el.classList.add('dp-reveal','d1'));
        [sub, card].forEach(el => el && el.classList.add('dp-reveal','d2'));
        feats && feats.classList.add('dp-reveal','d3');
    }

    const tryBind = () => { bindCard(); bindReveal(); };
    tryBind();
    new MutationObserver(tryBind).observe(doc.body, {childList:true, subtree:true});
})();
</script>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
left, spacer, right = st.columns([1.1, 0.1, 0.9])

# ---------- LEFT ----------
with left:
    st.markdown("""
    <div class="dp-brand">
    <img src="LOGO_PLACEHOLDER" style="height:110px;width:auto;object-fit:contain;" alt="DataPilot AI"/>
    </div>

    <h1 class="dp-headline">Navigate Your<br/>Data Career.</h1>
    <p class="dp-sub">
        AI-powered career guidance for Data, Analytics, and Machine Learning
        professionals. Personalized roadmaps, skill gap analysis, and interview prep.
    </p>

    <div class="dp-features">
        <div class="dp-feature">
            <div class="dp-feat-ico">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-5"/>
                </svg>
            </div>
            <div class="dp-feat-text">Personalized Career Roadmaps
                <small>Built for Data Analysts, Scientists, Engineers, and ML roles.</small>
            </div>
        </div>
        <div class="dp-feature">
            <div class="dp-feat-ico">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                </svg>
            </div>
            <div class="dp-feat-text">Real-Time Skill Gap Analysis
                <small>Compare your profile against market-ready job requirements.</small>
            </div>
        </div>
        <div class="dp-feature">
            <div class="dp-feat-ico">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                </svg>
            </div>
            <div class="dp-feat-text">AI Feedback
                <small>Get AI generated professional feedbacks.</small>
            </div>
        </div>
    </div>
    """.replace("LOGO_PLACEHOLDER", LOGO_B64), unsafe_allow_html=True)

# ---------- RIGHT ----------
with right:
    st.markdown("""
    <div class="dp-card">
        <h2>Welcome back</h2>
        <p class="lead">Sign in to continue to your DataPilot AI workspace.</p>
    </div><br>
    """, unsafe_allow_html=True)


    # Streamlit form rendered after the heading card
    email = st.text_input("Email address", placeholder="you@company.com", key="dp_email")
    password = st.text_input("Password", type="password", placeholder="••••••••••", key="dp_pw")

    login_btn = st.button("Sign in", use_container_width=True, key="dp_login")

    #st.page_link("pages/11_Forget_Password.py", label="Forgot password?")

    st.markdown('<div class="dp-divider">or</div>', unsafe_allow_html=True)

    st.markdown('<div class="dp-secondary">', unsafe_allow_html=True)
    signup_btn = st.button("Create a new account", use_container_width=True, key="dp_signup")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="dp-foot">By signing in you agree to our Terms & Privacy Policy.</div>',
        unsafe_allow_html=True
    )

# --------------------------------------------------
# LOGIC (unchanged)
# --------------------------------------------------
if login_btn:
    if not email or not password:
        st.warning("Please fill all fields")
    else:
        try:
            user = login(email=email, password=password)
            create_session(user)
            st.success("Login Successful")
            st.switch_page("pages/3_Dashboard.py")
        except Exception as e:
            st.error(str(e))



if signup_btn:
    st.switch_page("pages/2_Signup.py")
