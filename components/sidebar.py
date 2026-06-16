import streamlit as st
from src.auth.session_manager import logout

def show_sidebar():

    with st.sidebar:

        st.title("🚀 DataPilot AI")

        st.caption(
            "Navigate Your Data Career with AI"
        )

        st.divider()

        st.write(
            f"👤 {st.session_state['username']}"
        )

        st.divider()

        # Navigation
        if st.button("📄 Resume Analyzer", key="nav_resume", use_container_width=True):
            st.experimental_set_query_params()
            st.switch_page("pages/4_Resume_Analyzer.py")

        if st.button("🎯 Job Fit Predictor", key="nav_jobfit", use_container_width=True):
            st.experimental_set_query_params()
            st.switch_page("pages/8_Job_Fit_Predictor")

        if st.button("💰 Salary Predictor", key="nav_salary", use_container_width=True):
            st.experimental_set_query_params()
            st.switch_page("pages/6_salary_predictor.py")

        if st.button("🧠 Skill Analysis", key="nav_skill", use_container_width=True):
            st.experimental_set_query_params()
            st.switch_page("pages/5_Skill_Analysis.py")

        if st.button(
            "🚪 Logout",
            key="sidebar_logout",
            use_container_width=True
        ):
            logout()
            st.switch_page("pages/1_Login.py")