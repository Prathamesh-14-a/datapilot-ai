import os
import streamlit as st

from src.auth.session_manager import is_authenticated
from components.sidebar import show_sidebar
from src.database.crud import (
    get_analysis_history,
    get_job_fit_history,
    get_user_resumes,
    save_analysis,
    save_job_fit_history,
    save_resume,
)
from src.job_fit.predictor import (
    ROLE_SKILLS,
    predict_job_fit,
)
from src.resume_matching.resume_parser import (
    TECHNICAL_SKILLS,
    extract_resume_text,
    extract_skills,
)

from src.ATS.master_pipeline import full_resume_analysis
from src.llm.resume_feedback import generate_resume_feedback
from src.text_to_pdf.text_to_pdf import text_to_pdf



def _normalize_items(value):
    if not value:
        return []

    if isinstance(value, dict):
        return [str(item) for item in value.values() if item]

    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item]

    return [str(value)]


def _render_chip(text, kind="neutral"):
    palette = {
        "neutral": "#E8EEF6",
        "success": "#D9FBE8",
        "warning": "#FFF1D6",
        "danger": "#FDE2E1",
        "info": "#DDEBFF",
    }

    color = palette.get(kind, palette["neutral"])

    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:0.35rem 0.7rem;
            margin:0.2rem 0.35rem 0.2rem 0;
            border-radius:999px;
            background:{color};
            color:#1F2937;
            font-size:0.88rem;
            font-weight:600;
            line-height:1.2;
        ">{text}</span>
        """,
        unsafe_allow_html=True,
    )


def render_career_summary(insights):
    level = insights.get("Level", "Unknown")
    summary = insights.get("Summary", "")
    strengths = _normalize_items(insights.get("Strengths"))
    focus_areas = _normalize_items(insights.get("Focus Areas"))

    level_style = {
        "Highly Competitive": ("success", "🟢", "#DCFCE7"),
        "Competitive": ("info", "🔵", "#DBEAFE"),
        "Moderately Competitive": ("warning", "🟠", "#FEF3C7"),
        "Needs Improvement": ("danger", "🔴", "#FEE2E2"),
    }
    level_kind, level_icon, level_bg = level_style.get(level, ("neutral", "⚪", "#E2E8F0"))

    st.markdown(
        """
        <style>
        .career-card {
            background: linear-gradient(135deg, rgba(14,165,233,0.08), rgba(16,185,129,0.08));
            border: 1px solid rgba(148,163,184,0.25);
            border-radius: 18px;
            padding: 1.25rem;
            box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }
        .career-label {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            font-weight: 700;
            margin-bottom: 0.85rem;
        }
        .career-summary-text {
            color: #334155;
            font-size: 1rem;
            line-height: 1.65;
            margin-bottom: 0;
        }
        .section-title {
            margin: 0 0 0.5rem 0;
            font-size: 0.95rem;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="career-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="career-label" style="background:{level_bg}; color:#0f172a;">{level_icon} {level}</div>',
        unsafe_allow_html=True,
    )

    if level == "Needs Improvement":
        st.warning(
            "This resume needs stronger alignment for the selected role. Focus on the skills below to improve your match."
        )

    left_col, right_col = st.columns([1, 2])

    with left_col:
        if level == "Needs Improvement":
            st.markdown(
                """
                <div style="margin-bottom:0.35rem; font-size:0.9rem; color:#94A3B8; font-weight:600;">
                    Career Readiness
                </div>
                <div style="font-size:1.8rem; font-weight:700; line-height:1.15; color:#F43F5E;">
                    Needs Improvement
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif level == "Moderately Competitive":
            st.markdown(
                """
                <div style="margin-bottom:0.35rem; font-size:0.9rem; color:#94A3B8; font-weight:600;">
                    Career Readiness
                </div>
                <div style="font-size:1.8rem; font-weight:700; line-height:1.15; color: #FFA500;">
                    Moderately Competitive
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif level == "Competitive":
            st.markdown(
                """
                <div style="margin-bottom:0.35rem; font-size:0.9rem; color:#94A3B8; font-weight:600;">
                    Career Readiness
                </div>
                <div style="font-size:1.8rem; font-weight:700; line-height:1.15; color:#FFFF00;">
                    Competitive
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif level == "Highly Competitive":
            st.markdown(
                """
                <div style="margin-bottom:0.35rem; font-size:0.9rem; color:#94A3B8; font-weight:600;">
                    Career Readiness
                </div>
                <div style="font-size:1.8rem; font-weight:700; line-height:1.15; color:#008000;">
                    Highly Competitive
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.metric("Career Readiness", level)
        st.caption("Your resume is being evaluated against the selected role.")

    with right_col:
        st.markdown(
            f'<p class="career-summary-text" style="color:#F5FDFD;">{summary}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    skills_left, skills_right = st.columns(2)

    with skills_left:
        st.markdown("### ✨ Strengths")
        if strengths:
            for skill in strengths:
                _render_chip(skill, "success")
        else:
            st.caption("No matched strengths were detected yet.")

    with skills_right:
        st.markdown("### 🎯 Focus Areas")
        if focus_areas:
            for skill in focus_areas:
                _render_chip(skill, "warning")
        else:
            st.caption("No focus areas were identified.")

    with st.expander("See raw insight data", expanded=False):
        st.json(insights)


def render_analysis_history(analyses):
    st.subheader("🗂 Analysis History")

    if not analyses:
        st.info("No analysis records have been saved yet.")
        return

    history_rows = []

    for analysis in analyses:
        history_rows.append(
            {
                "Resume ID": analysis.resume_id,
                "Target Role": analysis.target_role,
                "ATS Score": (
                    f"{analysis.ats_score:.2f}%"
                    if analysis.ats_score is not None
                    else "N/A"
                ),
                "Match Score": (
                    f"{analysis.match_score:.2f}%"
                    if analysis.match_score is not None
                    else "N/A"
                ),
                "Analyzed At": (
                    analysis.analysis_date.strftime("%Y-%m-%d %H:%M")
                    if analysis.analysis_date
                    else "Unknown"
                ),
            }
        )

    st.table(history_rows)


# ==========================================
# AUTHENTICATION
# ==========================================

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

user_id = st.session_state["user_id"]

# ==========================================
# PAGE HEADER
# ==========================================

st.title("📄 Resume Analyzer")

st.caption(
    "Upload your resume and receive ATS insights, career guidance, and an AI-powered improvement report."
)

# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"]
)

# ==========================================
# TARGET ROLE
# ==========================================

target_role = st.selectbox(
    
    "Select Target Role",
    
    [
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Engineer",
        "Business Analyst",
        "Analytics" ,
        "Product Analyst"
    ]
)

# ==========================================
# ANALYZE RESUME BUTTON
# ==========================================

if st.button(
    "🔍 Analyze Resume",
    use_container_width=True
):

    if uploaded_file is None:
        st.error("Please upload a resume first.")
        st.stop()

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    save_path = os.path.join(
        "uploads",
        uploaded_file.name
    )

    with open(save_path, "wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )

    saved_resume = save_resume(
        user_id=user_id,
        resume_name=uploaded_file.name,
        resume_path=save_path,
    )

    st.success(
        f"Saved {saved_resume.resume_name} to your resume library."
    )

    with st.spinner(
        "Analyzing your resume..."
    ):

        result = full_resume_analysis(
            save_path,
            target_role
        )

    ats_result = result["ats"]
    save_analysis(
        user_id=user_id,
        resume_id=saved_resume.id,
        ats_score=ats_result.get("ATS Score", 0),
        match_score=ats_result.get("Coverage", 0),
        target_role=target_role,
    )

    # Save results for later use
    st.session_state["analysis_result"] = result
    st.session_state["target_role"] = target_role
    st.session_state["latest_resume_id"] = saved_resume.id
    resume_text = extract_resume_text(save_path)

    resume_skills = extract_skills(
        resume_text,
        TECHNICAL_SKILLS
    )
    st.session_state["resume_skills"] = resume_skills

    # compute job fit for the resume skills and save history
    job_fit_predictions = predict_job_fit(resume_skills)
    best_role, best_score = next(iter(job_fit_predictions.items()))
    normalized_skills = {skill.lower().strip() for skill in resume_skills}
    missing_skills = [
        skill
        for skill in ROLE_SKILLS.get(best_role, [])
        if skill not in normalized_skills
    ]

    save_job_fit_history(
        user_id=user_id,
        resume_id=saved_resume.id,
        best_role=best_role,
        best_score=best_score,
        predictions=job_fit_predictions,
        missing_skills=missing_skills,
    )

    st.success("Analysis saved to your history.")

st.divider()


# ==========================================
# SHOW ANALYSIS RESULTS
# ==========================================

if "analysis_result" in st.session_state:

    result = st.session_state["analysis_result"]

    ats = result["ats"]
    insights = result["insights"]
    roadmap = result["roadmap"]

    # ======================================
    # ATS READINESS CARD
    # ======================================

    st.divider()

    st.subheader("🎯 ATS Readiness")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "ATS Score",
            f"{ats['ATS Score']}%"
        )

    with col2:
        coverage = (
            len(ats["Matched"])
            /
            (
                len(ats["Matched"])
                +
                len(ats["Missing"])
            )
        ) * 100

        st.metric(
            "Coverage",
            f"{coverage:.1f}%"
        )

    st.progress(
        ats["ATS Score"] / 100
    )
    # ======================================
    # SKILL BREAKDOWN
    # ======================================

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "### ✅ Matched Skills"
        )

        for skill in ats["Matched"]:
            st.success(skill)

    with col2:
        st.markdown(
            "### ❌ Missing Skills"
        )

        for skill in ats["Missing"]:
            st.warning(skill)

    # ======================================
    # CAREER SUMMARY CARD
    # ======================================

    st.divider()

    st.subheader(
        "📈 Career Summary"
    )

    render_career_summary(insights)

    # ======================================
    # LEARNING ROADMAP
    # ======================================

    st.divider()

    st.subheader(
        "🗺 Learning Roadmap"
    )

    st.write(roadmap)



    # ======================================
    # AI FEEDBACK BUTTON
    # ======================================

    st.divider()

    if st.button(
        "🤖 Generate AI Feedback",
        use_container_width=True
    ):

        with st.spinner(
            "Generating detailed AI report..."
        ):

            feedback = generate_resume_feedback(
                ats,
                st.session_state["target_role"]
            )

        st.session_state["resume_feedback"] = feedback

# ==========================================
# SHOW AI REPORT
# ==========================================

if "resume_feedback" in st.session_state:

    st.divider()

    st.subheader(
        "🤖 AI Career Report"
    )

    with st.expander(
        "View Detailed AI Feedback",
        expanded=True
    ):
        st.markdown(
            st.session_state["resume_feedback"]
        )

if "resume_feedback" in st.session_state:

    pdf_data = text_to_pdf(st.session_state["resume_feedback"])

    st.download_button(
        label="📥 Download AI Career Report",
        data=pdf_data,
        file_name="AI_Career_Report.pdf",
        mime="application/pdf"
    )

def render_resume_history(resumes):
    st.subheader("🗂 Resume History")

    if not resumes:
        st.info("No resumes have been uploaded yet.")
        return

    resume_rows = []

    for resume in resumes:
        resume_rows.append(
            {
                "Resume": resume.resume_name,
                "Uploaded At": (
                    resume.uploaded_at.strftime("%Y-%m-%d %H:%M")
                    if resume.uploaded_at
                    else "Unknown"
                ),
            }
        )

    st.table(resume_rows)

with st.expander(
        "View Analysis History",
        expanded=False
    ):
    render_analysis_history(get_analysis_history(user_id))

with st.expander(
        "View Resume History",
        expanded=False
    ):
    render_resume_history(get_user_resumes(user_id))

