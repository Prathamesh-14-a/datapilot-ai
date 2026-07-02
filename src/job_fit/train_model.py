import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config.paths import DATA_DIR, MODELS_DIR
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score 


df = pd.read_csv(
    DATA_DIR / 'job_fit_dataset.csv'
)

all_skills = set()

for skills in df["skills"]:

    for skill in skills.split(","):
        all_skills.add(skill.strip())

all_skills = sorted(list(all_skills))
print("Total Skills:", len(all_skills))

#Multi Hot Encoding 
def encode_skills(skill_string):

    skill_set = set(
        s.strip()
        for s in skill_string.split(",")
    )

    return [
        1 if skill in skill_set else 0
        for skill in all_skills
    ]

# input vallues
X = df["skills"].apply(
    encode_skills
)

X = pd.DataFrame(
    X.tolist(),
    columns=all_skills
)

#label encoding
label_encoder = LabelEncoder()

y = label_encoder.fit_transform(
    df["target_role"]
)


for i, role in enumerate(label_encoder.classes_):
    print(i, role)


# Train Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

#Train Model
def train_random_classi(X_train , y_train):
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    return model

def evaluate(model):
    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

def encode_resume_skills(
    resume_skills,
    all_skills
):
    
    skill_set = {
        skill.lower().strip()
        for skill in resume_skills
    }

    return [
        1 if skill in skill_set else 0
        for skill in all_skills
    ]


model = train_random_classi(X_train , y_train)
evaluate(model)
resume_skills = [
   'python'
]

vector = encode_resume_skills(
    resume_skills,
    all_skills
)

X_input = pd.DataFrame(
    [vector],
    columns=all_skills
)

prediction = model.predict(
    X_input
)
print(prediction)


probabilities = model.predict_proba(
    [vector]
)[0]
for role, prob in zip(
    label_encoder.classes_,
    probabilities
):
    print(
        role,
        round(prob * 100, 2)
    )


joblib.dump(model, MODELS_DIR / 'job_model.pkl')
joblib.dump(label_encoder, MODELS_DIR / 'label_encoder.pkl')
joblib.dump(all_skills, MODELS_DIR / 'skill_vocab.pkl')