import streamlit as st
import streamlit.components.v1 as components
from src.auth.auth_service import login
from src.auth.session_manager import create_session, is_authenticated

import base64
import os

def load_logo(path="assets/logo.png"):
    try:
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        mime = "svg+xml" if ext == "svg" else ext  # handle svg too
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/{mime};base64,{data}"
    except FileNotFoundError:
        return ""  # fallback compass icon shows automatically

LOGO_BASE64 = load_logo("assets/logo.png")
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Login — DataPilot AI",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='14' fill='%232563EB'/></svg>",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if is_authenticated():
    st.switch_page("pages/3_Dashboard.py")

# --------------------------------------------------
# GLOBAL CSS — page shell + right-col form styling
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: #0B1020 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    color: #F8FAFC !important;
    margin: 0 !important; padding: 0 !important;
}
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important; max-width: 100% !important; min-height: 100vh !important;
}
#MainMenu, header, footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stSidebar"],
.stDeployButton { display: none !important; }

[data-testid="stHorizontalBlock"] {
    gap: 0 !important; padding: 0 !important;
    min-height: 100vh !important; align-items: stretch !important;
    background: #0B1020 !important;
}
[data-testid="stHorizontalBlock"] > div:first-child {
    padding: 0 !important; min-height: 100vh !important;
    flex: 1 1 55% !important; background: #0B1020 !important;
    border-right: 1px solid #1F2937 !important; overflow: hidden !important;
}
[data-testid="stHorizontalBlock"] > div:last-child {
    background: #0B1020 !important; padding: 0 !important;
    min-height: 100vh !important; flex: 0 0 45% !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlock"] {
    padding: 0 !important; gap: 0 !important; height: 100% !important;
}
[data-testid="stHorizontalBlock"] > div:first-child iframe {
    border: none !important; display: block !important;
}

/* ── Right panel card shell ── */
.dp-right-wrap {
    width: 100%; max-width: 420px; margin: 0 auto;
    padding: 48px 0; box-sizing: border-box;
}
.dp-card-shell {
    position: relative;
    background: rgba(17,24,39,0.82);
    border: 1px solid #1F2937; border-radius: 20px;
    padding: 40px 36px 32px;
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 0 0 1px rgba(37,99,235,0.07), 0 24px 64px rgba(0,0,0,0.55), 0 4px 16px rgba(0,0,0,0.3);
    /* JS will animate this in */
    opacity: 0; transform: translateY(20px);
    animation: cardSlideIn 0.6s cubic-bezier(0.16,1,0.3,1) 0.2s forwards;
}
@keyframes cardSlideIn {
    to { opacity: 1; transform: translateY(0); }
}
.dp-card-shell::before {
    content: ''; position: absolute;
    top: 0; left: 22px; right: 22px; height: 1px;
    background: linear-gradient(90deg,transparent,rgba(37,99,235,.5),rgba(34,211,238,.5),transparent);
}
.dp-card-title {
    font-size: 1.25rem; font-weight: 700; color: #F8FAFC;
    letter-spacing: -0.02em; margin: 0 0 4px; font-family: 'Inter', sans-serif;
}
.dp-card-sub {
    font-size: 0.8125rem; color: #4B5563; margin: 0 0 4px; font-family: 'Inter', sans-serif;
}
.dp-field-label {
    display: block; font-size: 10.5px; font-weight: 600; color: #6B7280;
    letter-spacing: 0.09em; text-transform: uppercase;
    margin: 20px 0 7px; font-family: 'Inter', sans-serif;
}
.dp-divider-line {
    display: flex; align-items: center; gap: 10px;
    margin: 20px 0 16px; font-size: 10px; letter-spacing: 0.1em;
    text-transform: uppercase; color: #374151; font-family: 'Inter', sans-serif;
}
.dp-divider-line::before, .dp-divider-line::after {
    content: ''; flex: 1; height: 1px; background: #1F2937;
}

/* ── Input overrides ── */
.stTextInput > div > div > input {
    background: rgba(11,16,32,0.9) !important;
    border: 1px solid #1F2937 !important; border-radius: 10px !important;
    color: #F8FAFC !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.9375rem !important; padding: 12px 15px !important;
    height: auto !important; transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important; outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #374151 !important; }
.stTextInput > label { display: none !important; }

/* ── Shake animation for validation error ── */
@keyframes shake {
    0%,100%{transform:translateX(0)}
    20%{transform:translateX(-6px)}
    40%{transform:translateX(6px)}
    60%{transform:translateX(-4px)}
    80%{transform:translateX(4px)}
}
.stTextInput.dp-shake > div > div > input {
    animation: shake 0.4s ease !important;
    border-color: #EF4444 !important;
    box-shadow: 0 0 0 3px rgba(239,68,68,0.15) !important;
}

/* ── Primary button ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg,#2563EB 0%,#1D4ED8 55%,#1E40AF 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    padding: 13px 20px !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.9375rem !important; font-weight: 600 !important;
    cursor: pointer !important; height: auto !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.38) !important;
    transition: all 0.2s !important; letter-spacing: 0.01em !important; margin-top: 4px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#3B82F6 0%,#2563EB 55%,#1D4ED8 100%) !important;
    box-shadow: 0 6px 24px rgba(37,99,235,0.52) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: scale(0.98) translateY(0) !important; }

/* Secondary button */
.dp-signup-wrap .stButton > button {
    background: transparent !important; border: 1px solid #1F2937 !important;
    color: #22D3EE !important; box-shadow: none !important;
    font-size: 0.875rem !important; font-weight: 500 !important; margin-top: 0 !important;
}
.dp-signup-wrap .stButton > button:hover {
    border-color: #22D3EE !important; background: rgba(34,211,238,0.05) !important;
    box-shadow: none !important; transform: none !important;
}

/* Alerts */
.stAlert { background: rgba(17,24,39,0.9) !important; border-radius: 10px !important; font-family: 'Inter', sans-serif !important; }

/* ── Page-level JS-driven interactions on right col ── */
/* Cursor follow glow — injected via JS */
.dp-cursor-glow {
    position: fixed; width: 320px; height: 320px; border-radius: 50%;
    background: radial-gradient(circle, rgba(37,99,235,0.06) 0%, transparent 70%);
    pointer-events: none; transform: translate(-50%,-50%);
    transition: left 0.08s ease, top 0.08s ease;
    z-index: 0;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LEFT PANEL — full HTML + JS inside components.html iframe
# --------------------------------------------------
LEFT_PANEL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#0B1020;font-family:'Inter',system-ui,sans-serif;color:#F8FAFC;overflow:hidden;}

.panel{
    display:flex;flex-direction:column;justify-content:center;
    padding:72px 64px;min-height:100vh;position:relative;overflow:hidden;
}

/* Grid bg */
.grid{
    position:absolute;inset:0;
    background-image:
        linear-gradient(rgba(31,41,55,.38) 1px,transparent 1px),
        linear-gradient(90deg,rgba(31,41,55,.38) 1px,transparent 1px);
    background-size:48px 48px;pointer-events:none;
    transition:background-position 0.1s ease;
}

/* Ambient glows */
.g1{position:absolute;top:-160px;left:-160px;width:560px;height:560px;
    background:radial-gradient(circle,rgba(37,99,235,.2) 0%,transparent 70%);
    border-radius:50%;pointer-events:none;transition:transform 0.15s ease;}
.g2{position:absolute;bottom:-120px;right:-60px;width:400px;height:400px;
    background:radial-gradient(circle,rgba(34,211,238,.12) 0%,transparent 70%);
    border-radius:50%;pointer-events:none;transition:transform 0.15s ease;}

/* Mouse-follow spotlight */
.spotlight{
    position:absolute;width:600px;height:600px;border-radius:50%;
    background:radial-gradient(circle,rgba(37,99,235,.07) 0%,transparent 65%);
    pointer-events:none;transform:translate(-50%,-50%);
    transition:left .12s ease,top .12s ease;z-index:0;
}

/* Canvas for floating particles */
#particles{position:absolute;inset:0;pointer-events:none;z-index:0;}

.inner{position:relative;z-index:1;max-width:500px;}

/* Logo */
.logo-wrap{margin-bottom:48px;opacity:0;transform:translateY(-12px);animation:fadeUp .5s cubic-bezier(.16,1,.3,1) .1s forwards;}
.logo-img{height:44px;width:auto;object-fit:contain;display:block;}

/* Eyebrow with typing cursor */
.eyebrow{
    font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
    color:#22D3EE;margin-bottom:13px;
    opacity:0;animation:fadeUp .5s cubic-bezier(.16,1,.3,1) .25s forwards;
}

/* Headline */
.headline{
    font-size:clamp(1.7rem,2.8vw,2.75rem);font-weight:700;line-height:1.15;
    color:#F8FAFC;letter-spacing:-.025em;margin-bottom:16px;
    opacity:0;animation:fadeUp .6s cubic-bezier(.16,1,.3,1) .35s forwards;
}
.grad{
    background:linear-gradient(135deg,#2563EB 0%,#22D3EE 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}

/* Sub */
.sub{
    font-size:.9375rem;color:#64748B;line-height:1.7;margin-bottom:32px;
    opacity:0;animation:fadeUp .6s cubic-bezier(.16,1,.3,1) .45s forwards;
}

/* Role pills — stagger in */
.roles{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:40px;}
.pill{
    display:inline-flex;align-items:center;gap:7px;
    padding:6px 13px;border-radius:999px;
    border:1px solid #1F2937;background:rgba(17,24,39,.65);
    font-size:12px;font-weight:500;color:#94A3B8;
    cursor:default;
    opacity:0;transform:translateY(8px);
    transition:border-color .2s, background .2s, color .2s, transform .2s;
}
.pill:hover{
    border-color:#2563EB;background:rgba(37,99,235,.12);
    color:#E2E8F0;transform:translateY(-2px);
}
.pill.active{
    border-color:#22D3EE;background:rgba(34,211,238,.1);color:#22D3EE;
}
.dot{width:6px;height:6px;border-radius:50%;background:linear-gradient(135deg,#2563EB,#22D3EE);flex-shrink:0;}

/* Proof */
.proof{
    display:flex;align-items:center;gap:14px;
    padding-top:26px;border-top:1px solid #1F2937;
    opacity:0;animation:fadeUp .6s cubic-bezier(.16,1,.3,1) 1.1s forwards;
}
.avs{display:flex;}
.av{
    width:28px;height:28px;border-radius:50%;border:2px solid #0B1020;
    margin-right:-8px;display:flex;align-items:center;justify-content:center;
    font-size:10px;font-weight:700;color:#fff;
    transition:transform .2s, margin .2s;
}
.avs:hover .av{margin-right:2px;}
.av1{background:linear-gradient(135deg,#2563EB,#3B82F6);}
.av2{background:linear-gradient(135deg,#7C3AED,#A855F7);}
.av3{background:linear-gradient(135deg,#059669,#10B981);}
.av4{background:linear-gradient(135deg,#DC2626,#F87171);}
.proof-txt{font-size:12px;color:#4B5563;line-height:1.5;padding-left:6px;}
.proof-txt strong{color:#94A3B8;font-weight:500;}

/* Counter animation */
.counter{display:inline;font-weight:500;color:#94A3B8;}

@keyframes fadeUp{to{opacity:1;transform:translateY(0);}}
</style>
</head>
<body>

<canvas id="particles"></canvas>

<div class="panel">
  <div class="grid" id="grid"></div>
  <div class="g1" id="g1"></div>
  <div class="g2" id="g2"></div>
  <div class="spotlight" id="spotlight"></div>

  <div class="inner">

    <!-- Logo -->
    <div class="logo-wrap">
      <img src="LOGO_SRC_PLACEHOLDER" class="logo-img" alt="DataPilot AI"
        onerror="this.onerror=null;this.style.display='none';document.getElementById('logo-fallback').style.display='flex'"/>
      <div id="logo-fallback" style="display:none;align-items:center;gap:10px;">
        <div style="width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,#2563EB,#22D3EE);display:flex;align-items:center;justify-content:center;">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="7" stroke="white" stroke-width="1.5"/>
            <path d="M10 3 L10 10 L15 6" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="10" cy="10" r="1.5" fill="white"/>
          </svg>
        </div>
        <span style="font-size:20px;font-weight:700;color:#F8FAFC;letter-spacing:-.02em;">DataPilot <span style="color:#22D3EE;">AI</span></span>
      </div>
    </div>

    <p class="eyebrow">AI-Powered Career Intelligence</p>

    <h1 class="headline">
      Navigate Your<br>
      <span class="grad">Data Career.</span>
    </h1>

    <p class="sub">
      Personalized career guidance for Data, Analytics, and Machine Learning
      professionals — from first role to senior leadership.
    </p>

    <div class="roles" id="roles">
      <div class="pill"><div class="dot"></div>Data Analyst</div>
      <div class="pill"><div class="dot"></div>Data Scientist</div>
      <div class="pill"><div class="dot"></div>Data Engineer</div>
      <div class="pill"><div class="dot"></div>ML Engineer</div>
      <div class="pill"><div class="dot"></div>BI Analyst</div>
      <div class="pill"><div class="dot"></div>Analytics Engineer</div>
    </div>

    <div class="proof">
      <div class="avs" id="avs">
        <div class="av av1">A</div>
        <div class="av av2">R</div>
        <div class="av av3">S</div>
        <div class="av av4">K</div>
      </div>
      <div class="proof-txt">
        <span class="counter" id="counter">0</span>+ professionals<br>navigating their data careers
      </div>
    </div>

  </div>
</div>

<script>
// ── 1. MOUSE PARALLAX — spotlight + glow drift ──
const spotlight = document.getElementById('spotlight');
const g1 = document.getElementById('g1');
const g2 = document.getElementById('g2');

document.addEventListener('mousemove', e => {
    const x = e.clientX, y = e.clientY;
    const w = window.innerWidth, h = window.innerHeight;
    const dx = (x / w - 0.5), dy = (y / h - 0.5);

    spotlight.style.left = x + 'px';
    spotlight.style.top  = y + 'px';

    g1.style.transform = `translate(${dx * 18}px, ${dy * 18}px)`;
    g2.style.transform = `translate(${-dx * 12}px, ${-dy * 12}px)`;
});

// ── 2. PILL STAGGER-IN ANIMATION ──
document.querySelectorAll('.pill').forEach((pill, i) => {
    pill.style.animation = `fadeUp 0.5s cubic-bezier(.16,1,.3,1) ${0.55 + i * 0.07}s forwards`;
});

// ── 3. PILL AUTO-CYCLE HIGHLIGHT ──
const pills = document.querySelectorAll('.pill');
let activePill = -1;
function cyclePill() {
    if (activePill >= 0) pills[activePill].classList.remove('active');
    activePill = (activePill + 1) % pills.length;
    pills[activePill].classList.add('active');
}
setTimeout(() => { cyclePill(); setInterval(cyclePill, 1800); }, 1400);

// Click to highlight
pills.forEach(p => {
    p.addEventListener('click', () => {
        pills.forEach(x => x.classList.remove('active'));
        p.classList.add('active');
    });
});

</script>
</body>
</html>
"""
LEFT_PANEL_HTML = LEFT_PANEL_HTML.replace("LOGO_SRC_PLACEHOLDER", LOGO_BASE64)
# --------------------------------------------------
# RIGHT PANEL — JS interactions injected via st.markdown
# --------------------------------------------------
RIGHT_JS = """
<script>
(function() {
    // Run after Streamlit finishes rendering
    function init() {
        // ── Cursor glow that follows mouse on right panel ──
        let glow = document.querySelector('.dp-cursor-glow');
        if (!glow) {
            glow = document.createElement('div');
            glow.className = 'dp-cursor-glow';
            document.body.appendChild(glow);
        }
        document.addEventListener('mousemove', e => {
            glow.style.left = e.clientX + 'px';
            glow.style.top  = e.clientY + 'px';
        });

        // ── Input focus ripple effect ──
        document.querySelectorAll('.stTextInput input').forEach(inp => {
            inp.addEventListener('focus', function() {
                this.closest('.stTextInput').style.transition = 'transform 0.15s ease';
                this.closest('.stTextInput').style.transform = 'scale(1.01)';
            });
            inp.addEventListener('blur', function() {
                this.closest('.stTextInput').style.transform = 'scale(1)';
            });

            // ── Live email validation indicator ──
            if (inp.type === 'email' || inp.placeholder.includes('company')) {
                inp.addEventListener('input', function() {
                    const valid = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(this.value);
                    if (this.value.length > 3) {
                        this.style.borderColor = valid ? '#22D3EE' : '#F59E0B';
                        this.style.boxShadow   = valid
                            ? '0 0 0 3px rgba(34,211,238,0.12)'
                            : '0 0 0 3px rgba(245,158,11,0.12)';
                    } else {
                        this.style.borderColor = '';
                        this.style.boxShadow   = '';
                    }
                });
            }
        });

        // ── Button click ripple ──
        document.querySelectorAll('.stButton > button').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const circle = document.createElement('span');
                const d = Math.max(this.offsetWidth, this.offsetHeight);
                const rect = this.getBoundingClientRect();
                circle.style.cssText = [
                    'position:absolute','border-radius:50%','pointer-events:none',
                    `width:${d}px`, `height:${d}px`,
                    `left:${e.clientX - rect.left - d/2}px`,
                    `top:${e.clientY - rect.top  - d/2}px`,
                    'background:rgba(255,255,255,0.18)',
                    'transform:scale(0)',
                    'animation:ripple 0.55s linear',
                ].join(';');
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(circle);
                setTimeout(() => circle.remove(), 600);
            });
        });

        // ── Password strength meter ──
        const passInputs = document.querySelectorAll('.stTextInput input[type="password"]');
        if (passInputs.length) {
            const pass = passInputs[0];

            // Create meter bar
            let meter = document.getElementById('dp-strength-meter');
            if (!meter) {
                meter = document.createElement('div');
                meter.id = 'dp-strength-meter';
                meter.style.cssText = [
                    'height:3px','border-radius:3px','margin-top:6px',
                    'background:#1F2937','overflow:hidden','transition:all .3s',
                    'opacity:0',
                ].join(';');
                meter.innerHTML = '<div id="dp-strength-bar" style="height:100%;width:0;border-radius:3px;transition:width .35s ease,background .35s ease;"></div>';
                pass.closest('.stTextInput').appendChild(meter);
            }

            pass.addEventListener('input', function() {
                const v = this.value;
                let score = 0;
                if (v.length >= 8)  score++;
                if (/[A-Z]/.test(v)) score++;
                if (/[0-9]/.test(v)) score++;
                if (/[^A-Za-z0-9]/.test(v)) score++;

                const bar = document.getElementById('dp-strength-bar');
                meter.style.opacity = v.length ? '1' : '0';

                const configs = [
                    {w:'20%', bg:'#EF4444'},
                    {w:'45%', bg:'#F59E0B'},
                    {w:'70%', bg:'#3B82F6'},
                    {w:'100%',bg:'#22D3EE'},
                ];
                const c = configs[Math.max(0, score - 1)] || configs[0];
                bar.style.width      = v.length ? c.w  : '0';
                bar.style.background = v.length ? c.bg : 'transparent';
            });
        }
    }

    // Inject ripple keyframe once
    if (!document.getElementById('dp-ripple-style')) {
        const s = document.createElement('style');
        s.id = 'dp-ripple-style';
        s.textContent = '@keyframes ripple{to{transform:scale(3);opacity:0}}';
        document.head.appendChild(s);
    }

    // Delay to let Streamlit render its widgets
    if (document.readyState === 'complete') {
        setTimeout(init, 400);
    } else {
        window.addEventListener('load', () => setTimeout(init, 400));
    }
    // Also re-run on Streamlit rerenders
    setTimeout(init, 800);
    setTimeout(init, 1800);
})();
</script>
"""

# --------------------------------------------------
# TWO-COLUMN LAYOUT
# --------------------------------------------------
col_left, col_right = st.columns([55, 45])

with col_left:
    components.html(LEFT_PANEL_HTML, height=900, scrolling=False)

with col_right:
    st.markdown("""
<div class="dp-right-wrap">
  <div class="dp-card-shell">
    <p class="dp-card-title">Welcome back</p>
    <p class="dp-card-sub">Sign in to your DataPilot AI account</p>
    <span class="dp-field-label">Login with Email Address</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<span class="dp-field-label">Email</span>', unsafe_allow_html=True)
    email = st.text_input(
        "Email",
        placeholder="you@company.com",
        label_visibility="collapsed"
    )

    st.markdown('<span class="dp-field-label">Password</span>', unsafe_allow_html=True)

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    login_btn = st.button("Sign in to DataPilot AI", use_container_width=True)

    # ── LOGIN LOGIC — untouched ──
    if login_btn:
        if not email or not password:
            st.warning("Please enter your email and password.")
        else:
            try:
                user = login(email=email, password=password)
                create_session(user)
                st.success("Signed in successfully.")
                st.switch_page("pages/3_Dashboard.py")
            except Exception as e:
                st.error(str(e))

    st.markdown('<div class="dp-divider-line">or</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="dp-signup-wrap">', unsafe_allow_html=True)
        if st.button("Create a free account", use_container_width=True):
            st.switch_page("pages/2_Signup.py")
        st.markdown('</div>', unsafe_allow_html=True)

    # Inject right-panel JS interactions
    st.markdown(RIGHT_JS, unsafe_allow_html=True)