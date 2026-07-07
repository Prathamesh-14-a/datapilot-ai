# pages/2_Signup.py

import base64
from pathlib import Path

import streamlit as st

from src.auth.auth_service import signup
from src.auth.session_manager import create_session, is_authenticated
from src.config.paths import ASSETS_DIR, ROOT_DIR


def image_to_base64(path: Path):
    with path.open("rb") as img:
        return base64.b64encode(img.read()).decode()

skill_icon = image_to_base64(
    ASSETS_DIR / "icons" / "brain-circuit.png"
)
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="DataPilot AI — Sign Up",
    page_icon=str(ASSETS_DIR / "mini_logo.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# REDIRECT IF ALREADY LOGGED IN
# --------------------------------------------------
if is_authenticated():
    st.switch_page("pages/3_Dashboard.py")


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def _logo_data_uri() -> str:
    """Return logo as base64 data URI (falls back to empty string)."""
    for candidate in [ASSETS_DIR / "logo.png", ROOT_DIR / "static" / "logo.png", ROOT_DIR / "logo.png"]:
        if candidate.exists():
            b64 = base64.b64encode(candidate.read_bytes()).decode()
            return f"data:image/png;base64,{b64}"
    return ""


LOGO_URI = _logo_data_uri()


# --------------------------------------------------
# GLOBAL STYLES  (Linear / Stripe / Vercel inspired)
# --------------------------------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

      /* Hide Streamlit chrome */
      #MainMenu, footer, header {visibility: hidden;}
      [data-testid="stToolbar"], [data-testid="stDecoration"],
      [data-testid="stStatusWidget"], [data-testid="stSidebarNav"],
      [data-testid="collapsedControl"] {display: none !important;}

      /* App background */
      html,
        body,
        [data-testid="stAppViewContainer"],
        .stApp {

        background:
            radial-gradient(circle at 10% 20%, rgba(37,99,235,0.28), transparent 35%),
            radial-gradient(circle at 90% 15%, rgba(6,182,212,0.15), transparent 30%),
            radial-gradient(circle at 50% 80%, rgba(29,78,216,0.12), transparent 35%),
            linear-gradient(
                135deg,
                #020617 0%,
                #050816 30%,
                #071329 70%,
                #030712 100%
            );

        color: #e6ecf5;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

      .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1280px;
      }

      /* ------------- LEFT BRAND PANEL ------------- */
      .dp-brand { animation: dpFadeUp 0.7s ease both; }
      .dp-brand{
    position:relative;
}

.dp-brand::before{
    content:"";

    position:absolute;

    width:500px;
    height:500px;

    top:-150px;
    left:-150px;

    border-radius:50%;

    background:
    radial-gradient(
      circle,
      rgba(37,99,235,.25),
      transparent 70%
    );

    filter:blur(80px);

    z-index:-1;
}
      .dp-logo {
        display: flex; align-items: center; gap: 14px; margin-bottom: 56px;
      }
      .dp-logo img { height: 120px; width: auto; filter: drop-shadow(0 6px 24px rgba(37,99,235,0.45)); }
      .dp-badge{
        display:inline-flex;
        align-items:center;
        padding:8px 16px;
        margin-bottom:24px;

        background:rgba(37,99,235,.12);

        border:1px solid rgba(59,130,246,.25);

        border-radius:999px;

        color:#7dd3fc;

        font-size:13px;

        font-weight:600;
        }
      .dp-headline {
        font-size: 72px; line-height: .95; font-weight: 800;
        letter-spacing: -0.03em; margin: 0 0 18px 0;
        background: linear-gradient(180deg, #ffffff 0%, #b8c4d6 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent;
      }
      .dp-sub {
        font-size: 16px; line-height: 1.65; color: #8a96ad;
        max-width: 480px; margin-bottom: 44px;
      }

      .dp-features { display: flex; flex-direction: column; gap: 14px; max-width: 520px; }
      .dp-feature {
        display: flex; align-items: flex-start; gap: 14px;
        padding: 14px 16px;
        background: rgba(9,14,25,.85);
        backdrop-filter: blur(14px);
        border:1px solid rgba(59,130,246,.12);
        border-radius: 12px;
        transition: all .25s ease;
        animation: dpFadeUp 0.6s ease both;
      }
      .dp-feature:hover{
     transform:translateY(-4px);
     border-color:rgba(59,130,246,.35);
     background:rgba(12,18,32,.95); 
     box-shadow:
     0 15px 40px rgba(37,99,235,.15);
        }
      .dp-feature:nth-child(1){animation-delay:.05s}
      .dp-feature:nth-child(2){animation-delay:.12s}
      .dp-feature:nth-child(3){animation-delay:.19s}
      .dp-feature:nth-child(4){animation-delay:.26s}
      .dp-feature:nth-child(5){animation-delay:.33s}

      .dp-ico {
        flex: 0 0 38px; height: 38px; border-radius: 10px;
        display: grid; place-items: center;
        background: linear-gradient(135deg, rgba(37,99,235,0.22), rgba(34,211,238,0.16));
        border: 1px solid rgba(59,130,246,0.35);
        color: #7cc4ff;
      }
      .dp-ftitle { font-weight: 600; color: #eaf0fa; font-size: 14.5px; }
      .dp-fdesc { color: #8a96ad; font-size: 13px; margin-top: 2px; }

      /* ------------- RIGHT GLASS CARD ------------- */
      .dp-card-wrap { display: flex; justify-content: center; align-items: flex-start; }
      .dp-trust{
        margin-bottom:20px;

        padding:14px 20px;

        background:rgba(255,255,255,.03);

        border:1px solid rgba(255,255,255,.06);

        border-radius:16px;

        color:#94a3b8;
    }
      .dp-card {
        width: 100%; max-width: 460px;
        background: linear-gradient(180deg, rgba(15,20,32,0.78), rgba(10,14,24,0.78));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 36px 34px 30px;
        backdrop-filter: blur(18px) saturate(140%);
        -webkit-backdrop-filter: blur(18px) saturate(140%);
        box-shadow:
        0 0 0 1px rgba(59,130,246,.08),
        0 30px 80px rgba(0,0,0,.6),
        0 0 120px rgba(37,99,235,.12);
      }
      .dp-card::before {
        content:""; position:absolute; inset:-1px;
        background: linear-gradient(135deg, rgba(59,130,246,0.35), transparent 40%, rgba(34,211,238,0.25));
        border-radius: 20px; padding:1px; -webkit-mask:
          linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude; pointer-events:none; opacity:.55;
      }
      .dp-card h2 {
        font-size: 26px; font-weight: 700; letter-spacing: -0.02em;
        color: #f3f6fb; margin: 0 0 8px;
      }
      .dp-card p.lead { color: #8a96ad; font-size: 14px; margin: 0 0 22px; line-height: 1.6; }

      /* Inputs */
      .stTextInput > label, .stPasswordInput > label {
        color: #c8d2e4 !important; font-size: 13px !important;
        font-weight: 500 !important; margin-bottom: 6px !important;
      }
      .stTextInput input, .stPasswordInput input,
      [data-baseweb="input"] input {
        background: rgba(10,14,24,0.7) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        color: #eef2f8 !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        transition: all .2s ease !important;
      }
      [data-baseweb="input"] {
        background: transparent !important;
        border-radius: 10px !important;
        border: none !important;
      }
      .stTextInput input:focus, .stPasswordInput input:focus,
      [data-baseweb="input"]:focus-within input {
        border-color: rgba(59,130,246,0.7) !important;
        box-shadow: 0 0 0 4px rgba(59,130,246,0.15) !important;
        outline: none !important;
      }
      .stTextInput input::placeholder { color: #5b6678 !important; }

      /* Primary button */
      .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #22d3ee 100%) !important;
        color: #ffffff !important;
        border: 0 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        padding: 12px 18px !important;
        letter-spacing: 0.01em;
        box-shadow: 0 10px 28px -10px rgba(37,99,235,0.7);
        transition: transform .15s ease, box-shadow .2s ease, filter .2s ease !important;
      }
      .stButton > button:hover {
        transform: translateY(-3px);
        filter: brightness(1.06);
       box-shadow:
        0 0 30px rgba(34,211,238,.35),
        0 15px 45px rgba(37,99,235,.35);
            }
      .stButton > button:active { transform: translateY(0); }

      /* Secondary (login) ghost button */
    
      .dp-secondary .stButton > button:hover {
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(59,130,246,0.45) !important;
        color: #ffffff !important;
      }

      /* Password strength */
      .dp-strength {
        margin-top: -6px; margin-bottom: 6px;
      }
      .dp-strength-track {
        height: 4px; width: 100%; border-radius: 999px;
        background: rgba(255,255,255,0.06); overflow: hidden;
      }
      .dp-strength-bar {
        height: 100%; width: 0%;
        background: linear-gradient(90deg,#ef4444,#f59e0b,#22d3ee,#22c55e);
        background-size: 300% 100%;
        transition: width .35s ease, background-position .35s ease;
        border-radius: 999px;
      }
      .dp-strength-label {
        font-size: 12px; color: #8a96ad; margin-top: 6px;
        display:flex; justify-content: space-between;
      }

      .dp-divider {
        display:flex; align-items:center; gap:12px;
        color:#5b6678; font-size:12px; margin: 18px 0 12px;
      }
      .dp-divider::before, .dp-divider::after {
        content:""; flex:1; height:1px; background: rgba(255,255,255,0.08);
      }

      .dp-foot {
        text-align: center; color:#8a96ad; font-size: 13px; margin-top: 14px;
      }

      /* Streamlit alert tweaks */
      .stAlert {
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(15,20,32,0.7) !important;
      }

      /* Animation */
      @keyframes dpFadeUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
      }

      @media (max-width:768px){
        html,body,[data-testid="stAppViewContainer"],.stApp{overflow-x:hidden !important;}

        .block-container{padding-top:1.5rem !important;padding-left:1rem !important;padding-right:1rem !important;max-width:100% !important;}

        [data-testid="stHorizontalBlock"]{flex-direction:column !important;gap:0 !important;}
        [data-testid="column"]{width:100% !important;flex:1 1 100% !important;min-width:100% !important;}

        .dp-brand{text-align:center !important;}
        .dp-brand::before{width:280px !important;height:280px !important;top:-80px !important;left:50% !important;transform:translateX(-50%) !important;}

        .dp-logo{justify-content:center !important;margin-bottom:24px !important;}
        .dp-logo img{max-width:400px !important;height:auto !important;}

        .dp-badge{font-size:12px !important;padding:6px 14px !important;margin-bottom:16px !important;display:inline-flex !important;}

        .dp-headline{font-size:36px !important;text-align:center !important;letter-spacing:-0.025em !important;margin-bottom:14px !important;}

        .dp-sub{font-size:15px !important;text-align:center !important;max-width:100% !important;margin-bottom:28px !important;}

        .dp-features{max-width:100% !important;gap:10px !important;}
        .dp-feature{padding:12px 14px !important;width:100% !important;box-sizing:border-box !important;}
        .dp-feature:hover{transform:none !important;}
        .dp-ico{flex:0 0 34px !important;height:34px !important;}
        .dp-ico svg{width:16px !important;height:16px !important;}
        .dp-ftitle{font-size:13.5px !important;}
        .dp-fdesc{font-size:12px !important;}

        .dp-trust{font-size:12px !important;padding:10px 14px !important;margin-top:24px !important;text-align:center !important;}

        .dp-card{width:100% !important;max-width:100% !important;padding:24px 18px 22px !important;border-radius:16px !important;box-sizing:border-box !important;}
        .dp-card h2{font-size:21px !important;}
        .dp-card p.lead{font-size:13px !important;margin-bottom:18px !important;}

        .stTextInput>label,.stPasswordInput>label{font-size:13px !important;}
        .stTextInput input,.stPasswordInput input,[data-baseweb="input"] input{font-size:14px !important;padding:11px 13px !important;width:100% !important;box-sizing:border-box !important;}

        .stProgress{width:100% !important;}
        [data-testid="stProgress"]>div{border-radius:999px !important;}

        .stButton>button{width:100% !important;font-size:15px !important;padding:12px 16px !important;box-sizing:border-box !important;}

        .dp-divider{margin:14px 0 10px !important;font-size:12px !important;}

        .dp-foot{font-size:12px !important;margin-top:12px !important;}

        [data-testid="stAppViewContainer"]>section>div{overflow-x:hidden !important;}

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
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
left, right = st.columns([1.05, 1], gap="large")

# ---------- LEFT: BRAND ----------
with left:
    logo_html = (
        f'<img src="{LOGO_URI}" alt="DataPilot AI"/>' if LOGO_URI else
        '<span style="font-size:22px;font-weight:700;color:#fff;">DataPilot <span style="color:#22d3ee;">AI</span></span>'
    )

    st.markdown(
        f"""
        <div class="dp-brand">
          <div class="dp-logo">{logo_html}</div>
          <div class="dp-badge">
            AI Career Copilot for Data Professionals
            </div>
          <h1 class="dp-headline">Start Your<br/>Data Career Journey.</h1>
          <p class="dp-sub">
            Build job-ready skills, discover opportunities, and grow with
            AI-powered career guidance designed for Data and ML professionals.
          </p>

          <div class="dp-features">

        <div class="dp-feature">
            <div class="dp-ico">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 3v18h18"/>
                    <path d="M7 14l4-4 4 4 5-6"/>
                </svg>
            </div>
            <div>
                <div class="dp-ftitle">Personalized Career Roadmaps</div>
                <div class="dp-fdesc">Tailored paths for Analysts, Scientists, Engineers, and ML roles.</div>
            </div>
        </div>

        <div class="dp-feature">
            <div class="dp-ico"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain-circuit-icon lucide-brain-circuit"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M9 13a4.5 4.5 0 0 0 3-4"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M12 13h4"/><path d="M12 18h6a2 2 0 0 1 2 2v1"/><path d="M12 8h8"/><path d="M16 8V5a2 2 0 0 1 2-2"/><circle cx="16" cy="13" r=".5"/><circle cx="18" cy="3" r=".5"/>
            <circle cx="20" cy="21" r=".5"/><circle cx="20" cy="8" r=".5"/></svg></div>
            <div>
                <div class="dp-ftitle">Skill Gap Analysis</div>
                <div class="dp-fdesc">
                    Benchmark your profile against real job requirements.
                </div>
            </div>
        </div>

        <div class="dp-feature">
            <div class="dp-ico">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20"/>
                </svg>
            </div>
            <div>
                <div class="dp-ftitle">Market Intelligence</div>
                <div class="dp-fdesc">
                    Live insights on roles, salaries, and in-demand skills across data.
                </div>
            </div>
        </div>

        <div class="dp-feature">
            <div class="dp-ico">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a4 4 0 01-4 4H8l-5 3V6a4 4 0 014-4h10a4 4 0 014 4z"/>
                </svg>
            </div>
            <div>
                <div class="dp-ftitle">AI Career Mentor</div>
                <div class="dp-fdesc">
                    On-demand guidance, interview prep, and feedback from your AI mentor.
                </div>
            </div>
        </div>

        <div class="dp-feature">
            <div class="dp-ico">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                    <path d="M14 2v6h6M9 13h6M9 17h6M9 9h2"/>
                </svg>
            </div>
            <div>
                <div class="dp-ftitle">Resume Optimization</div>
                <div class="dp-fdesc">
                    Polish your resume with ATS-aware suggestions tuned for data roles.
                </div>
            </div>
        </div>


        </div>

        """,
        unsafe_allow_html=True
    )

# ---------- RIGHT: SIGNUP CARD ----------
with right:
    st.markdown('<div class="dp-trust">Trusted by aspiring Data Professionals</div>', unsafe_allow_html=True)
   
    st.markdown(
        """
        <h2>Create Your Account</h2>
        <p class="lead">Join DataPilot AI and start building your future in Data and AI.</p>
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input("Username", placeholder="yourname", key="su_username")
    email = st.text_input("Email address", placeholder="you@company.com", key="su_email")
    

    # Password strength meter (pure CSS/JS, no logic change)
    password = st.text_input(
    "Password",
    type="password",
    placeholder="Create a password"
    )

    # Password Strength Meter
    if password:

        strength = 0

        if len(password) >= 8:
            strength += 1

        if any(c.isupper() for c in password):
            strength += 1

        if any(c.isdigit() for c in password):
            strength += 1

        if any(not c.isalnum() for c in password):
            strength += 1

        st.progress(strength / 4)

        if strength <= 1:
            st.markdown(
            "<span style='color:#ef4444;'>Weak Password</span>",
            unsafe_allow_html=True
            )

        elif strength <= 3:
            st.markdown(
                "<span style='color:#f59e0b;'>Medium Password</span>",
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                "<span style='color:#22c55e;'>Strong Password</span>",
                unsafe_allow_html=True
            )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm your password"
        )

    signup_btn = st.button("Create Account", use_container_width=True, key="su_submit")

    st.markdown('<div class="dp-divider">or</div>', unsafe_allow_html=True)

    
    st.markdown(
    """
    <div style="text-align:center; margin-top:15px;">
        <span style="color:#94a3b8;">
            Already have an account?
        </span>
    </div>
    """,
    unsafe_allow_html=True
    )

    login_btn = st.button(
        "Sign In",
        use_container_width=True,
        key="login_btn"
    )
    

    st.markdown(
        '<div class="dp-foot">By creating an account, you agree to our Terms & Privacy Policy.</div>',
        unsafe_allow_html=True,
    )



# --------------------------------------------------
# SIGNUP LOGIC  (unchanged)
# --------------------------------------------------
if signup_btn:
    if not username or not email or not password or not confirm_password:
        st.warning("Please fill all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match.")
    elif len(password) < 8:
        st.error("Password must be at least 8 characters.")
    else:
        try:
            user = signup(username, email, password)
            create_session(user)
            st.write(st.session_state)
            st.success("Account created successfully!")
            st.switch_page("pages/3_Dashboard.py")
            st.rerun()
        except Exception as e:
            st.error(str(e))

if login_btn:
    st.switch_page("pages/1_Login.py")
