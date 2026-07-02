import pandas as pd
from src.resume_matching.resume_parser import (
    extract_resume_text ,
    extract_skills
    
)
from src.ATS.resume_parser import(
    SKILLS_DB
)
from src.ATS.ats_match import (
    get_role_skills ,
    calculated_weighted_score
)
from src.llm.resume_feedback import generate_resume_feedback

from src.ATS.skill_recommender import career_insights 
from src.ATS.roadmap_generator import generate_roadmap

def analyze_ats(resume_file, target_role):

    resume_text = extract_resume_text(resume_file)
    resume_skills = extract_skills(resume_text, SKILLS_DB)


    da_skills = get_role_skills(target_role)

    ats_result = calculated_weighted_score(resume_skills , da_skills)
    print("ATS Result:", ats_result)

    return ats_result




def analyze_resume(resume_file, target_role):

    resume_text = extract_resume_text(resume_file)
    resume_skills = extract_skills(resume_text, SKILLS_DB)


    da_skills = get_role_skills(target_role)

    ats_result = calculated_weighted_score(resume_skills , da_skills)
    feedback = generate_resume_feedback(ats_result, target_role)
    print(feedback)


def full_resume_analysis(
    resume_file,
    target_role
):
    ats_result = analyze_ats(
        resume_file,
        target_role
    )

    insights = career_insights(
        ats_result
    )

    roadmap = generate_roadmap(
        ats_result
    )

    feedback = generate_resume_feedback(
        ats_result,
        target_role
    )

    return {
        "ats": ats_result,
        "insights": insights,
        "roadmap": roadmap,
        "feedback": feedback
    }

# def main():
#     ats_result = analyze_ats(
#         DATA_DIR / "resume" / "Pratham_Resume_Updated.pdf",
#         "Data Analyst",
#     )

#     career_insights_result = career_insights(ats_result)
#     print(career_insights_result)

#     roadmap = generate_roadmap(ats_result)
#     print(roadmap)

#     AI_feedback = generate_resume_feedback(ats_result, "Data Analyst")
#     print(AI_feedback)


# if __name__ == "__main__":
#     main()

