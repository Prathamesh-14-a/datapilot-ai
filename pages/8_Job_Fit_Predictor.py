import streamlit as st
import plotly.express as px
import pandas as pd

from src.auth.session_manager import is_authenticated
from src.job_fit.predictor import ROLE_SKILLS, predict_job_fit
from components.sidebar import show_sidebar

st.set_page_config(
	page_title="AI Job Fit Predictor",
	page_icon="🤖",
	layout="wide",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

resume_skills = st.session_state.get("resume_skills", [])
extracted_skills = resume_skills
predictions = {}
missing_skills = []


st.markdown("""
# 🎯 Career Role Fit Analyzer

Find out which data career role best matches your resume.

Our AI-powered engine analyzes the skills detected in your resume and compares them against industry-standard skill requirements for:

- Data Analyst
- Data Scientist
- Data Engineer
- Machine Learning Engineer
- BI Analyst
- Business Analyst
- Analytics Engineer

The tool provides:

✅ Best career match

✅ Role fit scores

✅ Skill gap analysis

✅ Personalized learning recommendations
""")


if st.button(
    "🔍 See Best Job Role Fit According to Your Resume",
    use_container_width=True
):

    if not resume_skills:
        st.error("No resume skills found. Run the Resume Analyzer first to extract skills.")
    else:
        predictions = predict_job_fit(resume_skills)
        extracted_skills = resume_skills
        best_role = next(iter(predictions))
        best_score = predictions[best_role]
        normalized_skills = {skill.lower().strip() for skill in resume_skills}
        missing_skills = [
            skill
            for skill in ROLE_SKILLS.get(best_role, [])
            if skill not in normalized_skills
        ]

        # ==========================================
        # BAR CHART
        # ==========================================

        top_roles = dict(list(predictions.items())[:5])

        chart_df = pd.DataFrame({
            "Role": list(top_roles.keys()),
            "Fit Score": list(top_roles.values())
        })

        st.markdown("## 📊 Job Role Fit Scores")

        fig = px.bar(
            chart_df,
            x="Role",
            y="Fit Score",
            text="Fit Score",
            title="Top Career Matches"
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        fig.update_layout(
            yaxis_title="Fit Score (%)",
            xaxis_title="Career Role",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==========================================
        # BEST MATCH
        # ==========================================

        st.success(
            f"🏆 Best Career Match: {best_role} ({best_score:.1f}%)"
        )

        # ==========================================
        # CAREER INSIGHT
        # ==========================================

        st.markdown("## 📝 Career Insight")

        if best_score >= 80:
            st.success(
                f"Your profile is strongly aligned with {best_role} positions."
            )
        elif best_score >= 60:
            st.warning(
                f"Your profile shows good alignment with {best_role}. "
                "A few additional skills can significantly improve your chances."
            )
        else:
            st.info(
                "Your profile is still developing. Focus on the skill gaps below."
            )

        # ==========================================
        # SKILL GAP ANALYSIS
        # ==========================================

        st.markdown("## 📈 Skill Gap Analysis")

        if missing_skills:
            st.write(
                f"To strengthen your profile for **{best_role}**, consider learning:"
            )
            for skill in missing_skills[:5]:
                st.markdown(
                    f"✅ **{skill.title()}**"
                )
        else:
            st.success(
                "Excellent! No major skill gaps detected."
            )

        # ==========================================
        # SKILLS DETECTED
        # ==========================================

        st.markdown("## 🛠️ Skills Detected From Resume")

        cols = st.columns(4)
        for idx, skill in enumerate(extracted_skills):
            with cols[idx % 4]:
                st.caption(f"🔹 {skill}")

        # ==========================================
        # LEARNING ROADMAP
        # ==========================================

        st.markdown("## 🚀 Recommended Learning Roadmap")

        if missing_skills:
            for i, skill in enumerate(
                missing_skills[:3],
                start=1
            ):
                st.write(
                    f"{i}. Learn **{skill.title()}**"
                )
            st.info(
                "Complete these skills and re-analyze your resume to improve your fit score."
            )

        # ==========================================
        # INFO SECTION
        # ==========================================

        with st.expander(
            "ℹ️ How does this work?"
        ):
            st.write("""
            The Job Fit Analyzer uses a machine learning model trained on
            industry-specific skill profiles.

            It compares the skills detected in your resume with the
            requirements of different data roles and predicts the
            roles that best match your current profile.

            The Skill Gap Analysis identifies important skills
            that can help improve your alignment with your target role.
            """)
