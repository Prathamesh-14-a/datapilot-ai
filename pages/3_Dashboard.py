import streamlit as st
import pandas as pd

from src.auth.session_manager import (
    is_authenticated,
)
from src.dashboard.dashboard_service import build_dashboard_snapshot


st.set_page_config(
    page_title="Dashboard",
    page_icon="🏠",
    layout="wide",
)

if not is_authenticated():
    st.warning("Please login first")
    st.stop()
from components.sidebar import show_sidebar

show_sidebar()

user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("No user profile is loaded for this session.")
    st.stop()

snapshot = build_dashboard_snapshot(user_id)
latest_analysis = snapshot.get("latest_analysis")
latest_prediction = snapshot.get("latest_prediction")
latest_resume = snapshot.get("latest_resume")

if "show_full_history" not in st.session_state:
    st.session_state["show_full_history"] = False


def _format_ts(value):
    if not value:
        return "No history yet"
    return value.strftime("%d %b %Y, %I:%M %p")


def _format_lpa(value):
    if value is None:
        return "No history yet"
    return f"₹{float(value) / 100000:.1f} LPA"


def _render_history_table(rows, empty_message):
    if not rows:
        st.info(empty_message)
        return

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# Header
st.title("🏠 Dashboard")

st.write(
    f"Welcome back, {st.session_state['username']} 👋"
)

st.caption(
    "Your AI Copilot for Data Careers"
)

if latest_resume:
    st.caption(f"Latest resume in your library: {latest_resume.resume_name} • uploaded {_format_ts(getattr(latest_resume, 'uploaded_at', None))}")

# Quick Actions
st.subheader("🚀 Quick Actions")

col1, col2  = st.columns(2)

with col1:

    if st.button(
        "📄 Resume Analyzer",
        use_container_width=True
    ):
        st.switch_page(
            "pages/4_Resume_Analyzer.py"
        )

    if st.button(
        "💰 Salary Predictor",
        use_container_width=True
    ):
        st.switch_page(
            "pages/6_salary_predictor.py"
        )
    
    if st.button(
        "Job Fit Predictor",
        use_container_width=True
    ):
        st.switch_page(
            "pages/8_Job_Fit_predictor.py"
        )

with col2:

    if st.button(
        "🧠 Skill Analysis",
        use_container_width=True
    ):
        st.switch_page(
            "pages/5_Skill_Analysis.py"
        )

    if st.button(
        "🤖 AI Mentor",
        use_container_width=True
    ):
        st.switch_page(
            "pages/7_AI_mentor.py"
        )   
st.divider()

# Metric Section
col1, col2, col3 = st.columns(3)

with col1:
    ats_score = (
        f"{latest_analysis.ats_score:.1f}%"
        if latest_analysis and latest_analysis.ats_score is not None
        else "No history yet"
    )
    st.metric(
        "ATS Score",
        ats_score
    )

with col2:
    skill_match = (
        f"{latest_analysis.match_score:.1f}%"
        if latest_analysis and latest_analysis.match_score is not None
        else "No history yet"
    )
    st.metric(
        "Skill Match",
        skill_match
    )

with col3:
    expected_salary = (
        _format_lpa(latest_prediction.predicted_salary)
        if latest_prediction
        else "No history yet"
    )
    st.metric(
        "Expected Salary",
        expected_salary
    )

col1, col2, col3, col4, col5= st.columns(5)

with col1:
    st.metric("Resumes", snapshot.get("counts", {}).get("resumes", 0))

with col2:
    st.metric("Analyses", snapshot.get("counts", {}).get("analyses", 0))

with col3:
    st.metric("Salary Predictions", snapshot.get("counts", {}).get("predictions", 0))

with col4:
    st.metric("AI Chats", snapshot.get("counts", {}).get("chats", 0))

with col5:
    st.metric("Job Fit Records", snapshot.get("counts", {}).get("job_fit_history", 0))


analysis_trend = pd.DataFrame(snapshot.get("analysis_trend", []))
salary_trend = pd.DataFrame(snapshot.get("salary_trend", []))

st.divider()

if not analysis_trend.empty:
    st.subheader("📈 ATS Trend")
    chart_df = analysis_trend.set_index("date")[ ["ats_score", "match_score"] ]
    st.line_chart(chart_df)

st.divider()

if not salary_trend.empty:
    st.subheader("💹 Salary Trend")
    chart_df = salary_trend.set_index("date")[ ["salary_lpa"] ]
    st.line_chart(chart_df)

st.divider()

# Recent Activity
st.subheader("📜 Recent Activity")

activity_items = snapshot.get("activity_items", [])
show_all_history = st.session_state["show_full_history"]


visible_activity_items = activity_items if show_all_history else activity_items[:5]

if visible_activity_items:
    for item in visible_activity_items:
        st.markdown(
            f"**{item['kind']}** · {item['title']}"
        )
        st.caption(
            f"{item['detail']} • {_format_ts(item['timestamp'])}"
        )
else:
    st.info(
        "No history has been saved yet. Analyze a resume, predict a salary, or start a mentor chat to populate this dashboard."
    )

if st.button(
    "Show all history" if not show_all_history else "Show latest 5",
    use_container_width=False,
):
    st.session_state["show_full_history"] = not show_all_history
    st.rerun()
st.divider()

history_tabs = st.tabs(["Resume Analyses", "Salary Predictions", "Resume Library", "AI Chats", "Job Fit History"])

with history_tabs[0]:
    analysis_rows = [
        {
            "Role": analysis.target_role,
            "ATS Score": f"{analysis.ats_score:.1f}%" if analysis.ats_score is not None else "N/A",
            "Skill Match": f"{analysis.match_score:.1f}%" if analysis.match_score is not None else "N/A",
            "Analyzed At": _format_ts(getattr(analysis, "analysis_date", None)),
        }
        for analysis in snapshot.get("analyses", [])
    ]
    _render_history_table(
        analysis_rows,
        "No analysis history yet. Run the Resume Analyzer to save real results here.",
    )

with history_tabs[1]:
    prediction_rows = [
        {
            "Role": prediction.role,
            "Experience": prediction.experience,
            "Location": prediction.location,
            "Predicted Salary": f"₹{prediction.predicted_salary / 100000:.1f} LPA" if prediction.predicted_salary is not None else "N/A",
            "Predicted At": _format_ts(getattr(prediction, "prediction_date", None)),
        }
        for prediction in snapshot.get("predictions", [])
    ]
    _render_history_table(
        prediction_rows,
        "No salary prediction history yet. Use Salary Predictor to save real market estimates here.",
    )

with history_tabs[2]:
    resume_rows = [
        {
            "Resume": resume.resume_name,
            "Uploaded At": _format_ts(getattr(resume, "uploaded_at", None)),
        }
        for resume in snapshot.get("resumes", [])
    ]
    _render_history_table(
        resume_rows,
        "No resume uploads have been saved yet.",
    )

with history_tabs[3]:
    chat_rows = [
        {
            "Conversation": chat.title,
            "Updated At": _format_ts(getattr(chat, "updated_at", None)),
        }
        for chat in snapshot.get("chat_sessions", [])
    ]
    _render_history_table(
        chat_rows,
        "No AI Mentor chats have been saved yet.",
    )

with history_tabs[4]:
    job_fit_rows = [
        {
            "Best Role": history.best_role,
            "Best Fit": f"{history.best_score:.2f}%" if history.best_score is not None else "N/A",
            "Missing Skills": history.missing_skills or "N/A",
            "Saved At": _format_ts(getattr(history, "created_at", None)),
        }
        for history in snapshot.get("job_fit_histories", [])
    ]
    _render_history_table(
        job_fit_rows,
        "No job fit history yet. Analyze a resume to save job fit results here.",
    )

