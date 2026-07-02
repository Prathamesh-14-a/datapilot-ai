from src.llm.gemini_client import generate_response

import pandas as pd
from src.resume_matching.resume_parser import (
    extract_resume_text ,
    extract_skills
    
)
from src.ATS.resume_parser import(
    SKILLS_DB
)
from src.ATS.ats_match import (
    get_role_skills,
    calculated_weighted_score,
)
from src.config.paths import DATA_DIR


#---------------------------------------------------
# GENERATE RESUME FEEDBACK
#--------------------------------------------------
def generate_resume_feedback(
       ats_result ,
       role = 'Data Analyst'
):
    prompt = f"""
    You are an experienced Data Science Career Coach.

    Target Role:
    {role}

    Readiness Score:
    {ats_result['ATS Score']}

    Strengths:
    {', '.join(ats_result['Matched'])}

    Missing Skills:
    {', '.join(ats_result['Missing'])}

    Provide:

    1. Overall Assessment

    2. Key Strengths

    3. Weaknesses

    4. Resume Improvements

    5. Project Recommendations

    6. Learning Recommendations

    Keep the advice practical and actionable and precise.
    """
    response = generate_response(prompt)

    return response

#---------------------------------------------------
# Main
#---------------------------------------------------
def main():
    resume_file = DATA_DIR / "resume" / "Pratham_Resume_Updated.pdf"
    resume_text = extract_resume_text(resume_file)
    resume_skills = extract_skills(resume_text, SKILLS_DB)


    da_skills = get_role_skills('Data Analyst')

    ats_result = calculated_weighted_score(resume_skills , da_skills)
    feedback = generate_resume_feedback(ats_result, role='Data Analyst')
    print(feedback)

if __name__ == "__main__":
    main()