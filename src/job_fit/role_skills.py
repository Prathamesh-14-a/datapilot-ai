ROLE_SKILLS = {

    "Data Analyst": [
        "sql",
        "excel",
        "power bi",
        "tableau",
        "python",
        "statistics",
        "pandas",
        "data visualization",
        "reporting",
        "dashboarding"
    ],

    "Data Scientist": [
        "python",
        "machine learning",
        "deep learning",
        "statistics",
        "numpy",
        "pandas",
        "scikit-learn",
        "data visualization",
        "feature engineering",
        "model deployment"
    ],

    "Data Engineer": [
        "python",
        "sql",
        "etl",
        "spark",
        "hadoop",
        "airflow",
        "data warehouse",
        "aws",
        "azure",
        "database design"
    ],

    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "mlops",
        "docker",
        "kubernetes",
        "model deployment",
        "api development"
    ],

    "Business Analyst": [
        "excel",
        "sql",
        "power bi",
        "tableau",
        "business analysis",
        "stakeholder management",
        "requirements gathering",
        "reporting",
        "data visualization",
        "communication"
    ],

    "BI Analyst": [
        "sql",
        "power bi",
        "tableau",
        "excel",
        "dashboarding",
        "reporting",
        "data visualization",
        "business intelligence",
        "data modeling",
        "kpi analysis"
    ],

    "Analytics Engineer": [
        "sql",
        "python",
        "dbt",
        "data modeling",
        "etl",
        "data warehouse",
        "snowflake",
        "bigquery",
        "airflow",
        "analytics engineering"
    ]
}

ALL_SKILLS = set()

for skills in ROLE_SKILLS.values():
    ALL_SKILLS.update(skills)

ALL_SKILLS = sorted(list(ALL_SKILLS))
print(len(ALL_SKILLS))
print(ALL_SKILLS)


SKILL_MAPPING = {

    "powerbi": "power bi",
    "microsoft power bi": "power bi",

    "ms excel": "excel",
    "microsoft excel": "excel",

    "sklearn": "scikit-learn",

    "pyspark": "spark",

    "amazon web services": "aws"
}