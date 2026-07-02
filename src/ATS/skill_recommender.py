from src.ATS.ats_match import (
    get_role_skills , 
    calculated_weighted_score)
import pandas as pd
from src.resume_matching.resume_parser import (
    extract_resume_text ,
    extract_skills
    
)
from src.ATS.resume_parser import SKILLS_DB
from src.config.paths import DATA_DIR



# resume_file = DATA_DIR / "resume" / "Pratham_Resume_Updated.pdf"
# resume_text = extract_resume_text(resume_file)
# resume_skills = extract_skills(resume_text, SKILLS_DB)


# da_skills = get_role_skills('Data Analyst')

# ATS_score = calculated_weighted_score(resume_skills , da_skills)


def generate_recommendation(ats_result):
    ats_result = ats_result or {}
    priority_skills = ats_result.get('Priority') or []
    high_priority = priority_skills[:2]

    medium_priority = priority_skills[2:5]

    low_priority = priority_skills[5:]

    return {
        'High Priority Skills' : high_priority , 
        'Medium Priority Skills' : medium_priority ,
        'Low Priority Skills' : low_priority
    }


#---------------------------------------------------------------
# GET LEVEL
#---------------------------------------------------------------

def get_level(ats_score):
    if ats_score >= 85:
        return 'Highly Competitive'
    
    elif ats_score >= 70:
        return 'Competitive'
    
    elif ats_score >= 50:
        return "Moderately Competitive"
    
    else:
        return "Needs Improvement"
    

#-------------------------------------------------
# GET SUMMARY
#-------------------------------------------------

def get_summary(ats_score):
    if ats_score >= 85:
        return 'Your resume is well-aligned with the job requirements, showcasing a strong match between your skills and the desired qualifications. You are likely to be highly competitive in the applicant pool.'
    
    elif ats_score >= 70:
        return 'Your resume demonstrates a good alignment with the job requirements, indicating that you possess many of the key skills and qualifications sought by employers. You are likely to be competitive in the applicant pool.'
    
    elif ats_score >= 50:
        return "Your resume shows some alignment with the job requirements, but there may be areas where your skills or qualifications could be further strengthened to better match what employers are looking for. You may be moderately competitive in the applicant pool."
    
    else:
        return "Your resume may not be fully aligned with the job requirements, suggesting that there are significant gaps in your skills or qualifications compared to what employers are seeking. It may be beneficial to focus on improving these areas to enhance your competitiveness in the applicant pool."


#-----------------------------------------------------------------
# GENERATE CAREER INSIGHTS
#-----------------------------------------------------------------

def career_insights(ats_result):
    ats_result = ats_result or {}
    score = ats_result.get('ATS Score', ats_result.get('ATS score', 0))
    level = get_level(score)
    summary = get_summary(score)
    strengths = (ats_result.get("Matched") or [])[:3]
    recommendations = generate_recommendation(ats_result)
    focus_areas = (
        recommendations['High Priority Skills'] + 
        recommendations['Medium Priority Skills']
    )
    return {
    "Level": level,
    "Summary": summary,
    "Strengths": strengths,
    "Focus Areas": focus_areas
    }


#-----------------------------------------------------
# MAIN
#-----------------------------------------------------
def main():
    resume_file = DATA_DIR / "resume" / "Pratham_Resume_Updated.pdf"
    resume_text = extract_resume_text(resume_file)
    resume_skills = extract_skills(resume_text, SKILLS_DB)


    da_skills = get_role_skills('Data Analyst')

    ats_result = calculated_weighted_score(resume_skills , da_skills)
    insightd = career_insights(ats_result)
    print(insightd)

if __name__ == "__main__":
    main()