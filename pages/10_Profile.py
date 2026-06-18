from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated, logout
from src.dashboard.dashboard_service import build_dashboard_snapshot
from src.database.crud import get_user


st.set_page_config(
    page_title="Profile",
    page_icon=":bust_in_silhouette:",
    layout="wide",
)


if not is_authenticated():
    st.warning("Please login first")
    st.stop()


show_sidebar()


user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("No user profile is loaded for this session.")
    st.stop()


user = get_user(user_id)
snapshot = build_dashboard_snapshot(user_id)


def _format_ts(value):
    if not value:
        return "Not available"

    return value.strftime("%d %b %Y, %I:%M %p")


def _format_lpa(value):
    if value is None:
        return "No prediction yet"

    return f"Rs. {float(value) / 100000:.1f} LPA"


def _initials(name):
    parts = [part for part in str(name or "User").split() if part]
    if not parts:
        return "U"

    return "".join(part[0].upper() for part in parts[:2])


def _profile_defaults():
    return {
        "full_name": st.session_state.get("username", ""),
        "headline": "Aspiring Data Professional",
        "phone": "",
        "location": "",
        "portfolio": "",
        "linkedin": "",
        "github": "",
        "target_role": "",
        "experience_level": "Fresher",
        "availability": "Open to opportunities",
        "preferred_location": "Remote / Hybrid",
        "expected_salary": "",
        "bio": "",
        "skills": "",
        "career_goals": "",
        "email_updates": True,
        "resume_reminders": True,
        "mentor_tips": True,
        "profile_visibility": "Private",
    }


def _get_profile():
    key = f"profile_details_{user_id}"
    if key not in st.session_state:
        st.session_state[key] = _profile_defaults()

    return st.session_state[key]


def _render_avatar(name):
    st.markdown(
        f"""
        <div class="profile-avatar">{escape(_initials(name))}</div>
        """,
        unsafe_allow_html=True,
    )


def _render_activity_table(activity_items):
    if not activity_items:
        st.info(
            "No activity yet. Analyze a resume, predict salary, or start an AI Mentor chat to build your profile history."
        )
        return

    rows = [
        {
            "Activity": item["kind"],
            "Title": item["title"],
            "Details": item["detail"],
            "Date": _format_ts(item["timestamp"]),
        }
        for item in activity_items[:8]
    ]

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


def _render_resume_table(resumes):
    if not resumes:
        st.info("No resumes uploaded yet.")
        return

    rows = [
        {
            "Resume": resume.resume_name or "Untitled resume",
            "Uploaded At": _format_ts(getattr(resume, "uploaded_at", None)),
        }
        for resume in sorted(
            resumes,
            key=lambda item: getattr(item, "uploaded_at", datetime.min) or datetime.min,
            reverse=True,
        )
    ]

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


st.markdown(
    """
    <style>
    .profile-avatar {
        width: 92px;
        height: 92px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #1f77b4;
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
    }
    .profile-name {
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }
    .profile-headline {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 0.75rem;
    }
    .profile-pill {
        display: inline-block;
        padding: 0.35rem 0.65rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        border-radius: 999px;
        background: #eef2f7;
        color: #263238;
        font-size: 0.86rem;
        font-weight: 650;
    }
    .profile-section-note {
        color: #64748b;
        margin-top: -0.4rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


profile = _get_profile()
latest_analysis = snapshot.get("latest_analysis")
latest_prediction = snapshot.get("latest_prediction")
latest_resume = snapshot.get("latest_resume")
counts = snapshot.get("counts", {})


st.title("Profile")
st.caption("Manage your account, career details, activity, preferences, and saved profile information.")


top_left, top_right = st.columns([1, 3])

with top_left:
    _render_avatar(profile.get("full_name") or st.session_state.get("username"))

with top_right:
    display_name = profile.get("full_name") or st.session_state.get("username")
    st.markdown(
        f"""
        <div class="profile-name">{escape(display_name)}</div>
        <div class="profile-headline">{escape(profile.get("headline") or "Career profile")}</div>
        """,
        unsafe_allow_html=True,
    )

    for value in [
        profile.get("target_role"),
        profile.get("experience_level"),
        profile.get("availability"),
        profile.get("preferred_location"),
    ]:
        if value:
            st.markdown(
                f'<span class="profile-pill">{escape(value)}</span>',
                unsafe_allow_html=True,
            )


st.divider()


metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.metric("Resumes", counts.get("resumes", 0))

with metric_col2:
    st.metric("Analyses", counts.get("analyses", 0))

with metric_col3:
    st.metric("Salary Predictions", counts.get("predictions", 0))

with metric_col4:
    st.metric("AI Chats", counts.get("chats", 0))

with metric_col5:
    st.metric("Job Fit Records", counts.get("job_fit_history", 0))


st.divider()


overview_tab, edit_tab, resume_tab, activity_tab, settings_tab = st.tabs(
    [
        "Overview",
        "Edit Profile",
        "Resume & Career",
        "Activity",
        "Settings",
    ]
)


with overview_tab:
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Account Information")
        st.write(f"**Username:** {st.session_state.get('username', 'Not available')}")
        st.write(f"**Email:** {st.session_state.get('email', 'Not available')}")
        st.write(f"**Member Since:** {_format_ts(getattr(user, 'created_at', None))}")
        st.write(f"**Profile Visibility:** {profile.get('profile_visibility', 'Private')}")

        st.subheader("Contact")
        st.write(f"**Phone:** {profile.get('phone') or 'Not added'}")
        st.write(f"**Location:** {profile.get('location') or 'Not added'}")
        st.write(f"**Portfolio:** {profile.get('portfolio') or 'Not added'}")
        st.write(f"**LinkedIn:** {profile.get('linkedin') or 'Not added'}")
        st.write(f"**GitHub:** {profile.get('github') or 'Not added'}")

    with right_col:
        st.subheader("Career Snapshot")
        st.write(f"**Target Role:** {profile.get('target_role') or 'Not selected'}")
        st.write(f"**Experience Level:** {profile.get('experience_level') or 'Not selected'}")
        st.write(f"**Availability:** {profile.get('availability') or 'Not selected'}")
        st.write(f"**Preferred Location:** {profile.get('preferred_location') or 'Not added'}")
        st.write(f"**Expected Salary:** {profile.get('expected_salary') or 'Not added'}")

        if latest_analysis:
            st.write(f"**Latest ATS Score:** {latest_analysis.ats_score:.1f}%")
            st.write(f"**Latest Skill Match:** {latest_analysis.match_score:.1f}%")
            st.write(f"**Latest Target Role:** {latest_analysis.target_role or 'Not available'}")
        else:
            st.info("Run the Resume Analyzer to see your latest ATS and match scores here.")

        if latest_prediction:
            st.write(f"**Latest Salary Estimate:** {_format_lpa(latest_prediction.predicted_salary)}")

    st.subheader("About")
    st.write(profile.get("bio") or "No bio added yet.")

    st.subheader("Skills")
    skills = [
        skill.strip()
        for skill in profile.get("skills", "").split(",")
        if skill.strip()
    ]
    if skills:
        for skill in skills:
            st.markdown(
                f'<span class="profile-pill">{escape(skill)}</span>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No skills added yet.")


with edit_tab:
    st.subheader("Edit Personal Details")
    st.markdown(
        '<div class="profile-section-note">These details are saved for your current app session.</div>',
        unsafe_allow_html=True,
    )

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
            headline = st.text_input("Profile Headline", value=profile.get("headline", ""))
            phone = st.text_input("Phone", value=profile.get("phone", ""))
            location = st.text_input("Location", value=profile.get("location", ""))
            portfolio = st.text_input("Portfolio Website", value=profile.get("portfolio", ""))

        with col2:
            linkedin = st.text_input("LinkedIn URL", value=profile.get("linkedin", ""))
            github = st.text_input("GitHub URL", value=profile.get("github", ""))
            target_role = st.text_input("Target Role", value=profile.get("target_role", ""))
            experience_level = st.selectbox(
                "Experience Level",
                [
                    "Fresher",
                    "Entry Level",
                    "Mid Level",
                    "Senior",
                    "Lead / Manager",
                ],
                index=[
                    "Fresher",
                    "Entry Level",
                    "Mid Level",
                    "Senior",
                    "Lead / Manager",
                ].index(profile.get("experience_level", "Fresher"))
                if profile.get("experience_level", "Fresher")
                in [
                    "Fresher",
                    "Entry Level",
                    "Mid Level",
                    "Senior",
                    "Lead / Manager",
                ]
                else 0,
            )
            availability = st.selectbox(
                "Availability",
                [
                    "Open to opportunities",
                    "Actively applying",
                    "Interviewing",
                    "Not looking",
                ],
                index=[
                    "Open to opportunities",
                    "Actively applying",
                    "Interviewing",
                    "Not looking",
                ].index(profile.get("availability", "Open to opportunities"))
                if profile.get("availability", "Open to opportunities")
                in [
                    "Open to opportunities",
                    "Actively applying",
                    "Interviewing",
                    "Not looking",
                ]
                else 0,
            )

        preferred_location = st.text_input(
            "Preferred Job Location",
            value=profile.get("preferred_location", ""),
        )
        expected_salary = st.text_input(
            "Expected Salary",
            value=profile.get("expected_salary", ""),
        )
        skills = st.text_area(
            "Skills",
            value=profile.get("skills", ""),
            help="Enter skills separated by commas.",
        )
        bio = st.text_area("Bio", value=profile.get("bio", ""), height=120)
        career_goals = st.text_area(
            "Career Goals",
            value=profile.get("career_goals", ""),
            height=120,
        )

        saved = st.form_submit_button("Save Profile", use_container_width=True)

    if saved:
        profile.update(
            {
                "full_name": full_name,
                "headline": headline,
                "phone": phone,
                "location": location,
                "portfolio": portfolio,
                "linkedin": linkedin,
                "github": github,
                "target_role": target_role,
                "experience_level": experience_level,
                "availability": availability,
                "preferred_location": preferred_location,
                "expected_salary": expected_salary,
                "skills": skills,
                "bio": bio,
                "career_goals": career_goals,
            }
        )
        st.success("Profile updated successfully.")


with resume_tab:
    st.subheader("Resume Library")
    if latest_resume:
        st.info(
            f"Latest resume: {latest_resume.resume_name or 'Untitled resume'} "
            f"uploaded {_format_ts(getattr(latest_resume, 'uploaded_at', None))}"
        )

    _render_resume_table(snapshot.get("resumes", []))

    st.subheader("Career Goals")
    st.write(profile.get("career_goals") or "No career goals added yet.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Analyze Resume", use_container_width=True):
            st.switch_page("pages/4_Resume_Analyzer.py")
    with col2:
        if st.button("Predict Salary", use_container_width=True):
            st.switch_page("pages/6_salary_predictor.py")
    with col3:
        if st.button("Open AI Mentor", use_container_width=True):
            st.switch_page("pages/7_AI_mentor.py")


with activity_tab:
    st.subheader("Recent Activity")
    _render_activity_table(snapshot.get("activity_items", []))

    st.subheader("Latest Results")
    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        ats_score = (
            f"{latest_analysis.ats_score:.1f}%"
            if latest_analysis and latest_analysis.ats_score is not None
            else "No result yet"
        )
        st.metric("ATS Score", ats_score)

    with result_col2:
        match_score = (
            f"{latest_analysis.match_score:.1f}%"
            if latest_analysis and latest_analysis.match_score is not None
            else "No result yet"
        )
        st.metric("Skill Match", match_score)

    with result_col3:
        salary = (
            _format_lpa(latest_prediction.predicted_salary)
            if latest_prediction
            else "No result yet"
        )
        st.metric("Salary Estimate", salary)


with settings_tab:
    st.subheader("Preferences")

    email_updates = st.checkbox(
        "Email updates",
        value=profile.get("email_updates", True),
    )
    resume_reminders = st.checkbox(
        "Resume improvement reminders",
        value=profile.get("resume_reminders", True),
    )
    mentor_tips = st.checkbox(
        "AI Mentor tips",
        value=profile.get("mentor_tips", True),
    )
    profile_visibility = st.selectbox(
        "Profile Visibility",
        ["Private", "Visible to mentors", "Visible to recruiters"],
        index=["Private", "Visible to mentors", "Visible to recruiters"].index(
            profile.get("profile_visibility", "Private")
        )
        if profile.get("profile_visibility", "Private")
        in ["Private", "Visible to mentors", "Visible to recruiters"]
        else 0,
    )

    if st.button("Save Preferences", use_container_width=True):
        profile.update(
            {
                "email_updates": email_updates,
                "resume_reminders": resume_reminders,
                "mentor_tips": mentor_tips,
                "profile_visibility": profile_visibility,
            }
        )
        st.success("Preferences saved.")

    st.divider()
    st.subheader("Security")
    st.write(f"Signed in as **{st.session_state.get('email', 'Not available')}**")
    st.caption("Password changes are handled from the authentication flow.")

    if st.button("Logout", use_container_width=True):
        logout()
        st.switch_page("pages/1_Login.py")
