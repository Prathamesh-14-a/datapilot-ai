import pandas as pd
from src.resume_matching.resume_parser import (
    extract_resume_text ,
    extract_skills
    
)
from src.ATS.resume_parser import(
    SKILLS_DB
)



# Job description as string input
job_description = """
Looking for a Data Analyst skilled in Python, SQL, Power BI,
Excel, ETL pipelines, machine learning, pandas,
data visualization, and statistical analysis.
"""

# Extract JD skills
job_description_skills = extract_skills(job_description, SKILLS_DB)

# Extract Resume skills
resume_file = r"d:\Startup\Project\ai-career-coach\data\resume\Pratham_Resume_Updated.pdf"
resume_text = extract_resume_text(resume_file)
resume_skills = extract_skills(resume_text, SKILLS_DB)

# Match
matched_skills = sorted(
    set(resume_skills).intersection(job_description_skills)
)

score = (len(matched_skills) / len(job_description_skills)) * 100


# print("=" * 50)
# print("ATS MATCH REPORT")
# print("=" * 50)

# print("\nJob Description Skills:")
# print(job_description_skills)

# print("\nResume Skills:")
# print(resume_skills)

# # print("\nMatched Skills:")
# # print(matched_skills)

# print(f"\nATS Score: {score:.2f}%")

BENCHMARK_DF = r'd:\Startup\Project\ai-career-coach\data\processed\top_skill_by_role_cleaned.csv'

#    IMPORT DATASET
# ----------------------------------
def load_data(path):
    try:
        df = pd.read_csv(path)
    
        return df
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        raise

benchmark_df = load_data(BENCHMARK_DF)


def get_role_skills(role):
    role_df = (
        benchmark_df[benchmark_df['Standardized_Job_Title'].str.lower() == role.lower()]
    )

    role_df["weight"] = (
    role_df["Count"] /
    role_df["Count"].max()
    ) * 10

    return dict(
        zip(
            role_df['Skill'].str.lower(),
            role_df['weight']
        )
    )

role_skills = get_role_skills('Data Analyst')



def calculated_weighted_score(
        resume_skills , 
        role_skills , 
        
):
    total_weight = sum(role_skills.values())

    matched_weight = 0

    matched = []
    missing = []

    for skill , count in role_skills.items():

        if skill in resume_skills:
            matched_weight += count
            matched.append(skill)
        else:
            missing.append(skill)

    score = round(
        (matched_weight / total_weight) * 100,
        2
    )

    #prioritize missing skills based on their weight in the role
    role_df = pd.DataFrame(list(role_skills.items()), columns=['Skill', 'Count'])
    priority_skills = (
    role_df[role_df["Skill"].isin(missing)]
    [["Skill", "Count"]]
    .sort_values("Count", ascending=False )
    .reset_index(drop=True)
    )
    priority = priority_skills["Skill"].tolist()


    #coverage of matched skills
    coverage = round(
    (len(matched) / len(role_skills)) * 100,
    2
    )

    return {'ATS Score': score, 
            'Matched': matched, 
            'Missing': missing, 
            'Priority': priority, 
            'Coverage': coverage}

#-----------------------------------------------------
# MAIN
#-----------------------------------------------------
def main():
    resume_file = r"d:\Startup\Project\ai-career-coach\data\resume\Pratham_Resume_Updated.pdf"
    resume_text = extract_resume_text(resume_file)
    resume_skills = extract_skills(resume_text, SKILLS_DB)


    da_skills = get_role_skills('Data Analyst')

    ats_result = calculated_weighted_score(resume_skills , da_skills)
    print(ats_result)

if __name__ == "__main__":
    main()

