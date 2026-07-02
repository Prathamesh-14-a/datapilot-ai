import joblib
import numpy as np
import pandas as pd
from collections import Counter

from src.config.paths import DATA_DIR, MODELS_DIR
from src.salary_prediction.train_salary_model import preprocess_data, feature_engineering
from src.salary_prediction.feature_engeneering import (
    create_skill_features,
    create_skill_count_feature,
    create_premium_skill_count,
    create_experience_skill_interaction,
    create_experience_premium_interaction,
    create_remote_experience_feature,
    create_skill_efficiency,
    create_grouped_skill_features,
    title_exp,
)

RAW_DATA_FILE = DATA_DIR / 'Salary Prediction Data' / 'salary_preprocessed_data.csv'
MODEL_FILE = MODELS_DIR / 'best_salary_model.pkl'


def get_top_skills(df: pd.DataFrame, top_n: int = 25) -> list[str]:
    all_skills = []
    for row in df["Skills"]:
        skills = [
            s.strip().lower()
            for s in str(row).split(",")
            if s.strip()
        ]
        all_skills.extend(skills)

    skill_counts = Counter(all_skills)
    return [skill for skill, _ in skill_counts.most_common(top_n)]


TRAIN_RAW_DF = pd.read_csv(RAW_DATA_FILE)
TOP_SKILLS = get_top_skills(TRAIN_RAW_DF, top_n=25)
TOP_LOCATIONS = list(TRAIN_RAW_DF["Location"].value_counts().head(20).index)
JOB_TITLE_CANONICAL = {
    title.lower(): title
    for title in TRAIN_RAW_DF["Job_Title"].dropna().unique()
}

MODEL = joblib.load(MODEL_FILE)
MODEL_FEATURES = list(getattr(MODEL, "feature_names_", []))


def derive_remote_status(location: str) -> int:
    if not isinstance(location, str):
        return 0
    return int("remote" in location.lower())


def normalize_job_title(job_title: str) -> str:
    if not isinstance(job_title, str):
        return ""
    title = job_title.strip()
    if not title:
        return title
    canonical = JOB_TITLE_CANONICAL.get(title.lower())
    if canonical:
        return canonical
    low = title.lower()
    if "machine learning" in low:
        return "Machine Learning Engineer"
    if "data scientist" in low:
        return "Data Scientist"
    if "data engineer" in low:
        return "Data Engineer"
    if "data analyst" in low:
        return "Data Analyst"
    if "business analyst" in low:
        return "Business Analyst"
    if "analytics" in low:
        return "Analytics Specialist"
    return title.title()


def normalize_location(location: str) -> str:
    if not isinstance(location, str):
        return "Other"
    value = location.strip()
    if not value:
        return "Other"
    lower_value = value.lower()
    if "remote" in lower_value:
        return "Remote"
    canonical = {loc.lower(): loc for loc in TOP_LOCATIONS}
    return canonical.get(lower_value, "Other")


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Job_Title"] = df["Job_Title"].apply(normalize_job_title)
    df["Location"] = df["Location"].apply(normalize_location)
    df["remote_status"] = df["Location"].apply(derive_remote_status)

    df = create_skill_features(df, TOP_SKILLS)
    df = create_skill_count_feature(df)
    df = create_premium_skill_count(df)
    df = create_grouped_skill_features(df)
    df = create_experience_skill_interaction(df)
    df = create_experience_premium_interaction(df)
    df = create_skill_efficiency(df)
    df = create_remote_experience_feature(df)
    df = title_exp(df)
    df = feature_engineering(df)

    X, _ = preprocess_data(df)
    X = X.reindex(columns=MODEL_FEATURES, fill_value=0)
    return X


def master_salary_prediction_pipeline(
    Job_title,
    experience,
    location,
    skills,
    salary: float = 0.0,
) -> float:
    """Return the predicted average salary for the given profile."""
    input_df = pd.DataFrame([
        {
            "Job_Title": Job_title,
            "Experience": experience,
            "Location": location,
            "Skills": skills,
            "Salary": salary,
            "remote_status": derive_remote_status(location),
        }
    ])

    X = build_feature_matrix(input_df)
    prediction_log = MODEL.predict(X)
    prediction_salary = np.expm1(prediction_log)
    return float(f"{prediction_salary[0]:.2f}")


if __name__ == "__main__":
    predicted = master_salary_prediction_pipeline(
        Job_title="Data Scientist",
        experience=4.0,
        location="Remote",
        skills="python, machine learning, sql, deep learning",
    )
    print(f"Predicted average salary: {predicted:.2f}")






