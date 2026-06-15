import streamlit as st
from streamlit_tags import st_tags

import src.salary_prediction.salary_predictor as salary_model

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated
from src.database.crud import save_salary_prediction
from src.resume_matching.resume_parser import TECHNICAL_SKILLS
from src.text_to_pdf.text_to_pdf import text_to_pdf
from src.llm.salary_tips import generate_salary_tips


st.set_page_config(
	page_title="Salary Predictor",
	page_icon="💰",
	layout="wide",
)


if not is_authenticated():
	st.warning("Please login first")
	st.stop()


show_sidebar()


st.title("💰 Salary Predictor")
st.caption("Estimate your market salary in LPA using role, experience, location, and skills.")


st.markdown(
	"""
	<style>
	.salary-hero {
		background: linear-gradient(135deg, rgba(14,165,233,0.10), rgba(16,185,129,0.10));
		border: 1px solid rgba(148,163,184,0.25);
		border-radius: 20px;
		padding: 1.2rem 1.3rem;
		box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
		margin-bottom: 1rem;
	}
	.salary-note {
		background: #F8FAFC;
		border-left: 4px solid #0EA5E9;
		padding: 0.95rem 1rem;
		border-radius: 12px;
		color: #334155;
		line-height: 1.65;
	}
	.salary-tip-card {
		background: #0F172A;
		color: #E2E8F0;
		border-radius: 18px;
		padding: 1rem 1.1rem;
		margin-top: 0.9rem;
	}
	.salary-tip-card h4 {
		margin: 0 0 0.6rem 0;
		color: #FFFFFF;
	}
	</style>
	""",
	unsafe_allow_html=True,
)


job_titles = sorted(set(salary_model.JOB_TITLE_CANONICAL.values()))
location_options = ["Remote", *salary_model.TOP_LOCATIONS, "Other"]
location_options = list(dict.fromkeys(location_options))


def evaluate_experience(job_title: str, experience_years: float) -> str:
	if experience_years < 1:
		level = "Entry-level"
		message = "You are likely being evaluated on fundamentals, learning speed, and basic execution."
	elif experience_years < 3:
		level = "Early-career"
		message = "You should already show clear project ownership, practical tooling, and measurable contributions."
	elif experience_years < 6:
		level = "Mid-level"
		message = "Employers usually expect independent delivery, strong domain depth, and visible business impact."
	else:
		level = "Senior"
		message = "Your compensation can rise sharply when you demonstrate leadership, strategy, and mentoring ability."

	return (
		f"For a {job_title} with {experience_years:.1f} years of experience, your profile looks {level.lower()}. {message}"
	)


def split_skills(raw_skills: str) -> str:
	skills = [skill.strip() for skill in raw_skills.split(",") if skill.strip()]
	return ", ".join(skills)


def format_lpa(value: float) -> str:
	return f"{value:.1f} LPA"


if "show_salary_tips" not in st.session_state:
	st.session_state["show_salary_tips"] = False


st.markdown(
	'<div class="salary-hero">Build an estimate based on the current profile inputs, then use the tips panel to improve the next offer.</div>',
	unsafe_allow_html=True,
)


with st.form("salary_prediction_form"):
	col1, col2 = st.columns(2)

	with col1:
		job_title = st.selectbox(
			"Job title",
			job_titles,
			index=job_titles.index("Data Scientist") if "Data Scientist" in job_titles else 0,
			help="Search for a role title before selecting it.",
		)
		experience = st.number_input(
			"Experience (years)",
			min_value=0.0,
			max_value=40.0,
			value=3.0,
			step=0.5,
		)

	with col2:
		location = st.selectbox(
			"Location",
			location_options,
			index=0,
			help="Search for your target work location or choose Remote.",
		)

	st.markdown("### Skills")
	st.caption("Enter at least 5 skills. You can review, edit, and add more skills below.")

	resume_skills = st.session_state.get("resume_skills", [])
	skills = st_tags(
		label="Review and Edit Skills",
		value=resume_skills,
		suggestions=TECHNICAL_SKILLS,
	)

	submit_prediction = st.form_submit_button("Predict Salary", use_container_width=True)


if submit_prediction:
	normalized_skills_list = [skill.strip() for skill in skills if skill.strip()]

	if len(normalized_skills_list) < 5:
		st.error("Please enter at least 5 skills before predicting salary.")
		st.stop()

	normalized_skills = ", ".join(normalized_skills_list)

	with st.spinner("Predicting salary..."):
		predicted_salary = salary_model.master_salary_prediction_pipeline(
			Job_title=job_title,
			experience=float(experience),
			location=location,
			skills=normalized_skills,
		)

	predicted_salary_lpa = predicted_salary / 100000

	user_id = st.session_state.get("user_id")
	if user_id:
		try:
			save_salary_prediction(
				user_id=user_id,
				role=job_title,
				experience=float(experience),
				location=location,
				skills=normalized_skills,
				predicted_salary=predicted_salary,
			)
		except Exception as exc:
			st.warning(f"Salary was predicted, but the history record could not be saved: {exc}")
		else:
			st.session_state["latest_salary_prediction"] = {
				"role": job_title,
				"experience": float(experience),
				"location": location,
				"skills": normalized_skills,
				"predicted_salary": predicted_salary,
			}

	st.success("Salary estimate generated successfully.")

	result_col1, result_col2 = st.columns([1, 2])

	with result_col1:
		st.metric("Predicted Salary", format_lpa(predicted_salary_lpa))

	with result_col2:
		st.markdown(
			f"<div class='salary-note'><strong>Experience review:</strong> {evaluate_experience(job_title, float(experience))}</div>",
			unsafe_allow_html=True,
		)
		st.caption("Note: salary may be more related to your experience level and title than any single skill.")

	st.info(
		"This is an estimate only. Actual salary can vary based on company budget, location policy, interview performance, team size, market timing, negotiated benefits, and internal compensation bands."
	)


# ======================================
# AI FEEDBACK BUTTON
# ======================================

st.divider()
if st.button(
    "🤖 AI tips to increase salary",
    use_container_width=True
):
    with st.spinner(
            "Generating detailed AI report..."
    ):

        feedback = generate_salary_tips(
                job_title , 
				experience ,
				location , 
				skills
		)

        st.session_state["feedback"] = feedback

# ==========================================
# SHOW AI REPORT
# ==========================================

if "feedback" in st.session_state:

    st.divider()

    st.subheader(
        "🤖 AI tips to increase salary"
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
        label="📥 Download AI salary improvement report",
        data=pdf_data,
        file_name="AI_salary_Report.pdf",
        mime="application/pdf"
    )
