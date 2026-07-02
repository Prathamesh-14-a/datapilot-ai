import ast

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config.paths import DATA_DIR


# -------------------- LOAD DATA --------------------
def load_data():
    df_skill = pd.read_csv(DATA_DIR / 'processed' / 'jobs_with_skills.csv')
    df_enha = pd.read_csv(DATA_DIR / 'processed' / 'Enhanced_skills_dataset.csv')
    return df_skill, df_enha


# -------------------- CLEAN DATA --------------------
def preprocess(df_skill):
    df_skill["extracted_skills"] = df_skill["extracted_skills"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    df_exp = df_skill.explode("extracted_skills")
    df_exp = df_exp.rename(columns={"extracted_skills": "Skill"})

    generic_terms = ["analysis", "research", "data analysis", "communication"]
    df_exp = df_exp[~df_exp["Skill"].isin(generic_terms)]

    return df_exp

# -------------------- ANALYSIS --------------------
def create_role_skill(df_exp):
    role_skill = (
        df_exp
        .groupby(["Standardized_Job_Title", "Skill"])
        .size()
        .reset_index(name="Count")
    )
    return role_skill


def get_top_skills(role_skill):
    return (
        role_skill
        .sort_values(["Standardized_Job_Title", "Count"], ascending=[True, False])
        .groupby("Standardized_Job_Title")
        .head(10)
    )


def create_matrix(role_skill):
    matrix = role_skill.pivot_table(
        index="Standardized_Job_Title",
        columns="Skill",
        values="Count",
        fill_value=0
    )
    return matrix


def normalize_skills(role_skill, df_skill):
    role_counts = df_skill["Standardized_Job_Title"].value_counts()

    role_skill["Normalized"] = role_skill.apply(
        lambda x: x["Count"] / role_counts[x["Standardized_Job_Title"]],
        axis=1
    )
    return role_skill


# -------------------- VISUALIZATION --------------------
def plot_heatmap(matrix):
    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix, linewidth=0.2, linecolor='white')
    plt.title("Role vs Skill Matrix")
    plt.show()


def plot_top_skills(top_skills, role):
    subset = top_skills[top_skills["Standardized_Job_Title"] == role]

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=subset.sort_values("Count", ascending=False),
        x="Count",
        y="Skill",
        hue="Skill",
        palette="viridis"
    )
    plt.title(f"Top Skills for {role}")
    plt.show()


def plot_normalized(role_skill, role):
    subset = (
        role_skill[role_skill["Standardized_Job_Title"] == role]
        .sort_values("Normalized", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=subset,
        x="Normalized",
        y="Skill",
        hue="Skill",
        palette="plasma"
    )
    plt.title(f"Normalized Skill Importance for {role}")
    plt.show()


# -------------------- MAIN --------------------
def main():
    df_skill, df_enha = load_data()

    df_exp = preprocess(df_skill)
    role_skill = create_role_skill(df_exp)

    top_skills = get_top_skills(role_skill)
    matrix = create_matrix(role_skill)

    matrix.to_csv(
        DATA_DIR / 'processed' / 'role_skill_matrix.csv',
        index=False
    )

    top_skills.to_csv(
        DATA_DIR / 'processed' / 'top_skill_by_role_cleaned.csv',
        index=False
    )

    role_skill.to_csv(
        DATA_DIR / 'processed' / 'role_skills_insights.csv',
        index=False
    )

    role_skill = normalize_skills(role_skill, df_skill)

    # Example usage
    role = top_skills["Standardized_Job_Title"].iloc[0]

    plot_top_skills(top_skills, role)
    plot_normalized(role_skill, role)
    plot_heatmap(matrix)



if __name__ == "__main__":
    main()