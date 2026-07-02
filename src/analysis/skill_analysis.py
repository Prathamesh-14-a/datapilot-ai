# =========================================
# IMPORTS
# =========================================
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

from src.config.paths import DATA_DIR, REPORTS_DIR


# =========================================
# CONFIGURATION
# =========================================
DATA_PATH = DATA_DIR / "processed"
REPORT_PATH = REPORTS_DIR / "dashboard_images"

SKILL_FILE = DATA_PATH / "skill_frequencies.csv"
ROLE_FILE = DATA_PATH / "role_skill_mapping.csv"

OUTPUT_ENHANCED = DATA_PATH / "Enhanced_skills_dataset.csv"
OUTPUT_ROLE_FILTERED = DATA_PATH / "role_df_filtered.csv"

WORDCLOUD_PATH = REPORT_PATH / "skill_wordcloud.png"

EXCLUDE_SKILLS = ["analysis", "research", "data analysis", "communication"]

PREMIUM_SKILLS = [
    'tensorflow', 'pytorch', 'nlp', 'llm', 'artificial intelligence',
    'computer vision', 'spark', 'hadoop', 'airflow', 'dbt',
    'databricks', 'snowflake', 'big data',
    'aws', 'azure', 'gcp',
    'scala', 'java'
]


# =========================================
# LOGGING SETUP
# =========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================================
# LOAD DATA
# =========================================
def load_data():
    if not SKILL_FILE.exists():
        raise FileNotFoundError(f"{SKILL_FILE} not found")

    if not ROLE_FILE.exists():
        raise FileNotFoundError(f"{ROLE_FILE} not found")

    df = pd.read_csv(SKILL_FILE)
    role_df = pd.read_csv(ROLE_FILE)

    logging.info(f"Skill Data Shape: {df.shape}")
    logging.info(f"Role Data Shape: {role_df.shape}")

    return df, role_df


# =========================================
# FILTERING
# =========================================
def filter_skills(df):
    if 'Skill' not in df.columns:
        raise ValueError("Missing 'Skill' column")

    return df[~df['Skill'].isin(EXCLUDE_SKILLS)].copy()


# =========================================
# CATEGORY MAPPING
# =========================================
def category_skill(skill):
    if skill in ['python', 'sql', 'r', 'java', 'scala']:
        return 'Programming'
    elif skill in ['power bi', 'tableau', 'excel']:
        return 'BI'
    elif skill in ['aws', 'gcp', 'azure']:
        return 'Cloud'
    elif skill in ['tensorflow', 'sckit-learn', 'pytorch', 'machine learning']:
        return 'Machine Learning'
    elif skill in ['communication', 'problem solving', 'presentation', 'leadership']:
        return 'Soft Skills'
    elif skill in ['postgresql', 'oracle', 'mysql', 'mongodb']:
        return 'DataBase'
    elif skill in ['data preprocessing', 'pandas']:
        return 'Data Cleaning'
    elif skill in ['etl', 'hadoop', 'databricks', 'dbt', 'spark', 'big data', 'snowflake', 'airflow']:
        return 'Data Engineering'
    elif skill in ['nlp', 'llm', 'artificial intelligence']:
        return 'Artificial Intelligence'
    elif skill in ['ggplot2', 'matplotlib', 'data visualization', 'seaborn', 'dashboarding']:
        return 'Data Visualization'
    elif skill in ["analysis", "research", "data analysis"]:
        return 'Generic Terms'
    else:
        return 'Other'


# =========================================
# FEATURE ENGINEERING
# =========================================
def demand_level(count):
    if count >= 40:
        return 'High'
    elif count >= 15:
        return 'Medium'
    return 'Low'


def enrich_skills(df, role_df_filtered):
    if 'Count' not in df.columns:
        raise ValueError("Missing 'Count' column")

    df['category'] = df['Skill'].apply(category_skill)
    df['demand_level'] = df['Count'].apply(demand_level)

    df['percentage_of_jobs'] = df['Count'] / len(role_df_filtered) * 100

    df["Rank"] = df["Count"].rank(
        ascending=False,
        method="dense"
    )

    df['premium_skill'] = df['Skill'].apply(
        lambda skill: 'Yes' if skill in PREMIUM_SKILLS else 'No'
    )

    return df



# =========================================
# STANDARDIZED SKILLS
# =========================================
def standard_skill(df):
    skill_standardization_map = {
    # Programming Languages
    'python': 'Python',
    'r': 'R',
    'sql': 'SQL',
    'java': 'Java',
    'scala': 'Scala',

    # Data Analysis / Visualization
    'excel': 'Excel',
    'power bi': 'Power BI',
    'tableau': 'Tableau',
    'data visualization': 'Data Visualization',
    'dashboarding': 'Dashboarding',
    'matplotlib': 'Matplotlib',
    'seaborn': 'Seaborn',
    'ggplot2': 'GGPlot2',
    'kpi': 'KPI Analysis',

    # Databases
    'mysql': 'MySQL',
    'postgresql': 'PostgreSQL',
    'mongodb': 'MongoDB',
    'oracle': 'Oracle Database',
    'snowflake': 'Snowflake',

    # Data Engineering / Big Data
    'etl': 'ETL',
    'big data': 'Big Data',
    'spark': 'Apache Spark',
    'hadoop': 'Hadoop',
    'airflow': 'Apache Airflow',
    'dbt': 'dbt',
    'databricks': 'Databricks',

    # Cloud Platforms
    'aws': 'Amazon Web Services (AWS)',
    'azure': 'Microsoft Azure',
    'gcp': 'Google Cloud Platform (GCP)',

    # Machine Learning / AI
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'nlp': 'Natural Language Processing (NLP)',
    'llm': 'Large Language Models (LLMs)',
    'artificial intelligence': 'Artificial Intelligence (AI)',
    'computer vision': 'Computer Vision',

    # Statistics / Data Science
    'statistics': 'Statistics',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'data preprocessing': 'Data Preprocessing',

    # Business / Soft Skills
    'business analysis': 'Business Analysis',
    'market research': 'Market Research',
    'stakeholder management': 'Stakeholder Management',
    'leadership': 'Leadership',
    'presentation': 'Presentation Skills'
    }
    df['standardized_skills'] = df['Skill'].map(skill_standardization_map)
    return df


# =========================================
# VISUALIZATIONS
# =========================================
def plot_top_skills(df):
    top_skills = df.sort_values(by='Count', ascending=False).head(20)

    plt.figure(figsize=(12, 6))
    plt.bar(
        x=top_skills['Skill'],
        height=top_skills['Count'],
        color='yellow',
        alpha=0.7,
        edgecolor='black'
    )
    plt.xticks(rotation=90)
    plt.title('Top 20 Skills')
    plt.tight_layout()
    plt.show()


def plot_category_distribution(df):
    category_counts = df.groupby('category')['Count'].sum().sort_values()

    category_counts.plot(
        kind='barh',
        color=sns.color_palette('viridis', len(category_counts))
    )
    plt.title("Skill Demand by Category")
    plt.tight_layout()
    plt.show()


def generate_wordcloud(df):
    skill_count_dict = dict(zip(df['Skill'], df['Count']))

    wc = WordCloud(
        width=1200,
        height=600,
        background_color="white"
    ).generate_from_frequencies(skill_count_dict)

    plt.figure(figsize=(15, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

    # Ensure directory exists
    WORDCLOUD_PATH.parent.mkdir(parents=True, exist_ok=True)
    wc.to_file(WORDCLOUD_PATH)


def plot_heatmap(role_df):
    pivot = role_df.pivot_table(
        index='Role',
        columns='Skill',
        values='Count',
        fill_value=0
    )

    plt.figure(figsize=(12, 6))
    sns.heatmap(
        pivot,
        cmap='coolwarm',
        linewidths=0.1,
        linecolor='white'
    )
    plt.tight_layout()
    plt.show()


# =========================================
# SAVE OUTPUTS
# =========================================
def save_outputs(df, role_df_filtered):
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_ENHANCED, index=False)
    role_df_filtered.to_csv(OUTPUT_ROLE_FILTERED, index=False)

    logging.info("Datasets saved successfully!")


# =========================================
# MAIN PIPELINE
# =========================================
def main():
    df, role_df = load_data()

    filtered_skill_df = filter_skills(df)
    role_df_filtered = filter_skills(role_df)

    filtered_skill_df = enrich_skills(filtered_skill_df, role_df_filtered)

    filtered_skill_df = standard_skill(filtered_skill_df)

    plot_top_skills(filtered_skill_df)
    plot_category_distribution(filtered_skill_df)
    generate_wordcloud(filtered_skill_df)
    plot_heatmap(role_df_filtered)


    # save_outputs(filtered_skill_df, role_df_filtered)


# =========================================
# ENTRY POINT
# =========================================
if __name__ == "__main__":
    main()