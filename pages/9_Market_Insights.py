import streamlit as st
import pandas as pd
import plotly.express as px

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Market Insights",
    page_icon="📈",
    layout="wide"
)

# --------------------------------------------------
# AUTH
# --------------------------------------------------

if not is_authenticated():
    st.warning("Please login first")
    st.stop()

show_sidebar()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

skill_df = pd.read_csv(
    "d:/Startup/Project/ai-career-coach/data/processed/top_skill_by_role_cleaned.csv"
)

location_df = pd.read_csv(
    "d:/Startup/Project/ai-career-coach/data/processed/location_distribution.csv"
)

salary_df = pd.read_csv(
    "d:/Startup/Project/ai-career-coach/data/processed/salary_jobs.csv"
)

jobs_df = pd.read_csv(
    "d:/Startup/Project/ai-career-coach/data/processed/jobs_with_skills.csv"
)
exp_df = pd.read_csv(
    "d:/Startup/Project/ai-career-coach/data/Salary Prediction Data/salary_final_data.csv"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📈 Market Insights")
st.caption(
    "Explore hiring trends, salaries, skills, and market demand."
)

# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.subheader("🎯 Filters")

col1, col2 = st.columns(2)

with col1:

    selected_role = st.selectbox(
        "Select Role",
        sorted(
            exp_df["Standardized_Job_Title"].unique()
        )
    )

with col2:

    selected_location = st.selectbox(
        "Select Location",
        ["All"] +
        sorted(
            location_df["Location"].unique().tolist()
        )
    )

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

skill_filtered = skill_df[
    skill_df["Standardized_Job_Title"]
    == selected_role
]

salary_filtered = salary_df[
    salary_df["Standardized_Job_Title"]
    == selected_role
]

job_filtered = jobs_df[
    jobs_df["Standardized_Job_Title"]
    == selected_role
]


if selected_location == "All":

    exp_filtered = exp_df[
        exp_df["Standardized_Job_Title"]
        == selected_role
    ]

else:

    exp_filtered = exp_df[
        (exp_df["Standardized_Job_Title"]
         == selected_role)
        &
        (exp_df["Location"]
         == selected_location)
    ]


if selected_location != "All":

    location_filtered = exp_df[
        exp_df["Location"]
        == selected_location
    ]

else:

    location_filtered = location_df

st.divider()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📊 Market Overview")

col1, col2, col3 = st.columns(3)

with col1:

    avg_salary = (
        exp_filtered["salary_avg"].mean()
        if not salary_filtered.empty
        else 0
    )

    st.metric(
        "Average Salary",
        f"₹ {avg_salary:,.0f}"
    )

with col2:

    max_salary = (
        exp_filtered["salary_avg"].max()
        if not exp_filtered.empty
        else 0
    )

    st.metric(
        "Highest Salary",
        f"₹ {max_salary:,.0f}"
    )

with col3:

    if not skill_filtered.empty:

        top_skill = (
            skill_filtered
            .sort_values(
                "Count",
                ascending=False
            )
            .iloc[0]["Skill"]
        )

    else:
        top_skill = "N/A"

    st.metric(
        "Top Skill",
        top_skill
    )



st.divider()

# --------------------------------------------------
# TOP SKILLS
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        skill_filtered.head(15),
        x="Count",
        y="Skill",
        orientation="h",
        title=f"🔥 Top Skills for {selected_role}"
    )

    fig.update_layout(
        height=500,
        yaxis={
            "categoryorder":
            "total ascending"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# SALARY ANALYSIS
# --------------------------------------------------
exp_filtered["Exp_Group"] = pd.cut(
    exp_filtered["Experience_Years"],
    bins=[0,2,5,8,12,20],
    labels=[
        "0-2",
        "2-5",
        "5-8",
        "8-12",
        "12+"
    ]
)

salary_chart = (
    exp_filtered
    .groupby("Exp_Group")
    ["salary_avg"]
    .median()
    .reset_index()
)

with col2:

    fig = px.bar(
    salary_chart,
    x="Exp_Group",
    y="salary_avg",
    text_auto=".2s",
    title="💰 Median Salary by Experience Group"
)

    st.plotly_chart(
    fig,
    use_container_width=True
)
# --------------------------------------------------
# LOCATION DISTRIBUTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    top_locations = (
    location_df
    .sort_values(
        "count",
        ascending=False
    )
    .head(10)
    )

    fig = px.pie(
        top_locations,
        names="Location",
        values="count",
        title="📍 Top Hiring Locations"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# SKILL TREEMAP
# --------------------------------------------------

with col2:

    fig = px.treemap(
        skill_filtered,
        path=["Skill"],
        values="Count",
        title="🌳 Skill Demand Treemap"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# --------------------------------------------------
# MARKET OPPORTUNITIES
# --------------------------------------------------

st.subheader("🚀 Market Opportunities")

user_skills = st.session_state.get(
    "resume_skills",
    []
)

market_skills = (
    skill_filtered
    .sort_values(
        "Count",
        ascending=False
    )["Skill"]
    .head(10)
    .tolist()
)

missing_skills = [

    skill

    for skill in market_skills

    if skill.lower()
    not in [
        s.lower()
        for s in user_skills
    ]
]

if len(user_skills) == 0:

    st.info(
        "Upload and analyze a resume to see personalized skill recommendations."
    )

else:

    if missing_skills:

        for skill in missing_skills:

            st.warning(
                f"📌 Learn {skill}"
            )

    else:

        st.success(
            "🎉 Your skills are strongly aligned with market demand."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Powered by DataPilot AI Market Intelligence Engine"
)