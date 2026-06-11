import streamlit as st

from src.auth.session_manager import is_authenticated
from components.sidebar import show_sidebar
from streamlit_tags import st_tags
from src.resume_matching.resume_parser import TECHNICAL_SKILLS
from src.resume_matching.master_career_intelligent import career_intelligence_pipeline
from src.llm.skill_improvement import generate_skill_feedback
from src.text_to_pdf.text_to_pdf import text_to_pdf

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

st.title("🧠 Skill Analyzer")

st.caption(
    "Analyze your skills against industry requirements"
)

target_role = st.selectbox(
    "Target Role",
    [
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Engineer",
        "Business Analyst" ,
        "Product Analyst",
        "Analytics"
    ]
)

resume_skills = st.session_state.get(
    "resume_skills",
    []
)

skills = st_tags(
    label="Review and Edit Skills",
    value=resume_skills,
    suggestions=
        TECHNICAL_SKILLS
)

st.caption("Add or remove skills to better reflect your expertise")

analysis_result = st.session_state.get(
    "analysis_result"
)
ats = analysis_result['ats']

st.write(
    'Skills will be matched to market trend skills as per role'
)
if st.button(
    "🔍 Analyze Skills",
    use_container_width=True
):
    st.write(
        'Match Score :' ,  ats['Coverage']   
    )
    st.write(
        "Matched Skills To Industry Requirement : " , ats['Matched']
    )
    st.write(
        'Missing Skills As Per Industry Requirement :' , ats['Missing']
    )

    st.subheader(
        "Insights"
    )
    st.write(
        career_intelligence_pipeline(ats)
    )

# ======================================
# AI FEEDBACK BUTTON
# ======================================

st.divider()
if st.button(
    "🤖 Generate Skill Improvement Plan",
    use_container_width=True
):
    with st.spinner(
            "Generating detailed AI report..."
    ):

        feedback = generate_skill_feedback(
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
        "🤖 AI Skill Improvement Report"
    )

    with st.expander(
        "View Detailed AI Feedback",
        expanded=True
    ):
        st.markdown(
            st.session_state["feedback"]
        )

if "feedback" in st.session_state:

    pdf_data = text_to_pdf(st.session_state["feedback"])

    st.download_button(
        label="📥 Download AI Skill Improvement Report",
        data=pdf_data,
        file_name="AI_skill_Report.pdf",
        mime="application/pdf"
    )