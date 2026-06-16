import random
import pandas as pd

from src.job_fit.role_skills import ROLE_SKILLS

COMMON_SKILLS = [
    "communication",
    "problem solving",
    "teamwork",
    "presentation",
    "critical thinking",
    "time management",
    "leadership"
]


def generate_record(role):
    
    role_skills = ROLE_SKILLS[role]

    # choose 60-90% of role skills
    n_skills = random.randint(
        max(4, int(len(role_skills) * 0.6)),
        len(role_skills)
    )

    selected = random.sample(
        role_skills,
        n_skills
    )

    # add random noise skills
    noise_count = random.randint(0, 2)

    selected.extend(
        random.sample(
            COMMON_SKILLS,
            noise_count
        )
    )

    random.shuffle(selected)

    return {
        "skills": ",".join(selected),
        "target_role": role
    }



rows = []
for role in ROLE_SKILLS.keys():

    for _ in range(500):

        rows.append(
            generate_record(role)
        )

df = pd.DataFrame(rows)
print(df.head())
df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

print(df["target_role"].value_counts())

df.to_csv(
    "data/job_fit_dataset.csv",
    index=False
)

