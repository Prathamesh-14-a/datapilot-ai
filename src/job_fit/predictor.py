
import joblib
import pandas as pd
from pathlib import Path
from src.job_fit.role_skills import ROLE_SKILLS


BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(
    BASE_DIR / "models" / "job_model.pkl"
)

label_encoder = joblib.load(
    BASE_DIR / "models" / "label_encoder.pkl"
)

skill_vocab = joblib.load(
    BASE_DIR / "models" / "skill_vocab.pkl"
)

def encode_resume_skills(
    resume_skills
):

    skill_set = {
        skill.lower().strip()
        for skill in resume_skills
    }

    return [
        1 if skill in skill_set else 0
        for skill in skill_vocab
    ]

def predict_job_fit(resume_skills):
    vector = encode_resume_skills(
    resume_skills
    )

    X_input = pd.DataFrame(
    [vector],
    columns=skill_vocab
    )

    probabilities = model.predict_proba(
    X_input
    )[0]

    results = {}

    for role, prob in zip(
        label_encoder.classes_,
        probabilities
    ):
        results[role] = float(
    round(prob * 100, 2)
    )

    results = dict(
    sorted(
        results.items(),
        key=lambda x: x[1],
        reverse=True
    )
    )

    return results



resume_skills = [
    "python",
    "sql",
    "power bi",
    "excel"
]

predictions = predict_job_fit(
    resume_skills
)

print(predictions)



def get_top_roles(
    resume_skills,
    top_n=3
):

    predictions = predict_job_fit(
        resume_skills
    )

    return list(
        predictions.items()
    )[:top_n]

print(
    get_top_roles(
        resume_skills
    )
)

required = ROLE_SKILLS[
    "Data Analyst"
]

missing = [
    skill
    for skill in required
    if skill not in resume_skills
]
print(missing)