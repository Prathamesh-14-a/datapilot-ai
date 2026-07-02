from collections import Counter

import numpy as np
import pandas as pd

from src.config.paths import DATA_DIR

#------------------------------------------------------
# PATH
#------------------------------------------------------
DATA_PATH = DATA_DIR / 'Salary Prediction Data'

SALARY_DATA_FILE = DATA_PATH / 'salary_preprocessed_data.csv'
FEATURE_DATA = DATA_PATH / "salary_feature_data.csv"


#------------------------------------------------------
# LOAD DATA
#------------------------------------------------------
def load_data():
    try:
        df = pd.read_csv(SALARY_DATA_FILE)

        print("Data Loaded Successfully")
        print(df.shape)

        return df

    except FileNotFoundError:
        print("File Not Found")

    except Exception as e:
        print(f"File Loading Error: {e}")

    return None


#------------------------------------------------------
# EXTRACT TOP SKILLS
#------------------------------------------------------
def extract_top_skills(df, top_n=25):

    all_skills = []

    for row in df["Skills"]:
        skills = [
            s.strip().lower()
            for s in str(row).split(",")
            if s.strip()
        ]
        all_skills.extend(skills)

    skill_counts = Counter(all_skills)

    top_skills = [
        skill
        for skill, count in skill_counts.most_common(top_n)
    ]

    return top_skills


#------------------------------------------------------
# CREATE BINARY SKILL FEATURES (FIXED)
#------------------------------------------------------
def create_skill_features(df, top_skills):

    for skill in top_skills:
        df[skill] = df["Skills"].apply(
            lambda x: 1 if skill in [
                s.strip().lower()
                for s in str(x).split(",")
            ] else 0
        )

    return df


#------------------------------------------------------
# REDUCE LOCATION
#------------------------------------------------------
def reduce_location_categories(df, top_n=20):

    top_locations = df["Location"].value_counts().head(top_n).index

    df["Location"] = df["Location"].apply(
        lambda x: x if x in top_locations else "Other"
    )

    return df


#------------------------------------------------------
# SKILL COUNT
#------------------------------------------------------
def create_skill_count_feature(df):

    df["Skill_Count"] = df["Skills"].apply(
        lambda x: len([
            s for s in str(x).split(",")
            if s.strip()
        ])
    )

    return df


#------------------------------------------------------
# PREMIUM SKILL COUNT
#------------------------------------------------------
def create_premium_skill_count(df):

    premium_skills = [
        "aws",
        "spark",
        "hadoop",
        "deep learning",
        "machine learning",
        "natural language processing"
    ]

    for skill in premium_skills:
        if skill not in df.columns:
            df[skill] = df["Skills"].apply(
                lambda x: 1 if skill in [
                    s.strip().lower()
                    for s in str(x).split(",")
                ] else 0
            )

    df["Premium_Skill_Count"] = df[premium_skills].sum(axis=1)

    return df


#------------------------------------------------------
# EXPERIENCE × SKILL
#------------------------------------------------------
def create_experience_skill_interaction(df):

    df["Exp_X_SkillCount"] = (
        df["Experience"] * df["Skill_Count"]
    )

    return df


#------------------------------------------------------
# EXPERIENCE × PREMIUM SKILL
#------------------------------------------------------
def create_experience_premium_interaction(df):

    df["Exp_X_PremiumSkill"] = (
        df["Experience"] * df["Premium_Skill_Count"]
    )

    return df


#------------------------------------------------------
# REMOTE × EXPERIENCE
#------------------------------------------------------
def create_remote_experience_feature(df):

    df["Remote_Experience"] = (
        df["remote_status"] * df["Experience"]
    )

    return df


#------------------------------------------------------
# SKILL EFFICIENCY
#------------------------------------------------------
def create_skill_efficiency(df):

    df["Skill_Efficiency"] = (
        df["Skill_Count"] / (df["Experience"] + 1)
    )

    return df

#------------------------------------------------------
# GROUPED SKILL FEATURES
#------------------------------------------------------
def create_grouped_skill_features(df):

    skill_groups = {
        "Programming_Skills": [
            "python", "r", "java", "c++"
        ],
        "ML_Skills": [
            "machine learning",
            "deep learning",
            "natural language processing"
        ],
        "Cloud_Skills": [
            "aws", "azure", "gcp"
        ],
        "Database_Skills": [
            "sql", "mongodb", "postgresql"
        ],
        "BigData_Skills": [
            "spark", "hadoop"
        ]
    }

    for group_name, skills in skill_groups.items():

        available = [
            skill for skill in skills
            if skill in df.columns
        ]

        if available:
            df[group_name] = df[available].sum(axis=1)
        else:
            df[group_name] = 0

    return df


#------------------------------------------------------
# ENCODE
#------------------------------------------------------
def encoding_categorical(df):

    categorical_columns = [
        "Job_Title",
        "Location",
    ]

    df = pd.get_dummies(
        df,
        columns=categorical_columns,
        drop_first=True,
        dtype=int
    )

    print("\nEncoded Categorical Features")

    return df

def title_exp(df):

    df['DS_Experience'] = (
        (df['Job_Title'] == 'Data Scientist').astype(int)
        * df['Experience']
    )

    df['DE_Experience'] = (
        (df['Job_Title'] == 'Data Engineer').astype(int)
        * df['Experience']
    )

    df['DA_Experience'] = (
        (df['Job_Title'] == 'Data Analyst').astype(int)
        * df['Experience']
    )

    df['ML_Experience'] = (
        (df['Job_Title'] == 'Machine Learning Engineer').astype(int)
        * df['Experience']
    )

    df['BA_Experience'] = (
        (df['Job_Title'] == 'Business Analyst').astype(int)
        * df['Experience']
    )

    df['Analytics_Experience'] = (
        (df['Job_Title'] == 'Analytics Specialist').astype(int)
        * df['Experience']
    )

    return df


#-------------------------------------------------------
#CLIP SALARY OUTLIERS
#-------------------------------------------------------
def clip_salary_outliers(df):
    q1 = df['Salary'].quantile(0.01)
    q99 = df['Salary'].quantile(0.99)

    df = df[
        (df['Salary'] >= q1) &
        (df['Salary'] <= q99)
    ]

    return df

#------------------------------------------------------
# SPLIT
#------------------------------------------------------
def split_features_target(df):

    X = df.drop(columns=["Salary"])
    y = df["Salary"]

    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target shape: {y.shape}")

    return X, y


#------------------------------------------------------
# SAVE
#------------------------------------------------------
def save_feature_data(df):

    df.to_csv(FEATURE_DATA, index=False)

    print("\nFeature Engineered Data Saved")


#------------------------------------------------------
# MAIN
#------------------------------------------------------
def main():

    df = load_data()

    if df is None:
        return

    top_skills = extract_top_skills(df)

    df = create_skill_features(df, top_skills)
    df = reduce_location_categories(df)
    df = create_skill_count_feature(df)
    df = create_premium_skill_count(df)

    df = create_grouped_skill_features(df)

    df = create_experience_skill_interaction(df)
    df = create_experience_premium_interaction(df)

    df = create_skill_efficiency(df)

    df = clip_salary_outliers(df)

    df = create_remote_experience_feature(df)
    df = title_exp(df)
    df = encoding_categorical(df)

    print(df.columns)

    df =  df.drop(columns=["Skills"])

    save_feature_data(df)

    X, y = split_features_target(df)

    print(df.columns)
    


#------------------------------------------------------
# ENTRY
#------------------------------------------------------
if __name__ == "__main__":
    main()