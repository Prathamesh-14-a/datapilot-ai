import os
import streamlit as st

from src.auth.session_manager import is_authenticated
from components.sidebar import show_sidebar

from src.ATS.master_pipeline import full_resume_analysis
from src.llm.resume_feedback import generate_resume_feedback

# ==========================================
# AUTHENTICATION
# ==========================================

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

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

    with st.spinner(
        "Analyzing your resume..."
    ):

        result = full_resume_analysis(
            save_path,
            target_role
        )

    # Save results for later use
    st.session_state["analysis_result"] = result
    st.session_state["target_role"] = target_role

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

    st.markdown(
        "### 🔥 Priority Skills"
    )

    for skill in ats["Priority"]:
        st.info(skill)

    # ======================================
    # CAREER SUMMARY CARD
    # ======================================

    st.divider()

    st.subheader(
        "📈 Career Summary"
    )

    st.write(insights)

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

        st.session_state["feedback"] = feedback

# ==========================================
# SHOW AI REPORT
# ==========================================

if "feedback" in st.session_state:

    st.divider()

    st.subheader(
        "🤖 AI Career Report"
    )

    with st.expander(
        "View Detailed AI Feedback",
        expanded=True
    ):
        st.markdown(
            st.session_state["feedback"]
        )