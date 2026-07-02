import pandas as pd 
from src.resume_matching.resume_parser import (
    extract_resume_text,
    extract_skills
)
from src.ATS.resume_parser import(
    SKILLS_DB
)

from src.ATS.ats_match import get_role_skills, calculated_weighted_score
from src.config.paths import DATA_DIR


SKILL_ROADMAP = {
    "big data": {
        "duration": "4 weeks",
        "resources": [
            "Data Warehousing",
            "Distributed Systems",
            "Batch and Streaming Processing",
            "Hadoop Ecosystem",
            "NoSQL Databases"
        ]
    },
    "presentation": {
        "duration": "2 weeks",
        "resources": [
            "Slide Layout",
            "Storytelling",
            "Audience Engagement",
            "Visual Design",
            "Public Speaking"
        ]
    },
    "power bi": {
        "duration": "3 weeks",
        "resources": [
            "Power Query",
            "DAX",
            "Dashboard Design",
            "Data Modeling",
            "Power BI Service"
        ]
    },
    "r": {
        "duration": "3 weeks",
        "resources": [
            "R Syntax",
            "Data Wrangling with dplyr",
            "Visualization with ggplot2",
            "Statistical Modeling",
            "R Markdown"
        ]
    },
    "excel": {
        "duration": "2 weeks",
        "resources": [
            "Formulas and Functions",
            "Pivot Tables",
            "Data Analysis Toolpak",
            "VBA Basics",
            "Advanced Charts"
        ]
    },
    "data visualization": {
        "duration": "2 weeks",
        "resources": [
            "Visualization Principles",
            "Charts and Graphs",
            "Storytelling with Data",
            "Dashboard Design",
            "Interactive Visuals"
        ]
    },
    "spark": {
        "duration": "4 weeks",
        "resources": [
            "Spark Core",
            "Spark SQL",
            "Spark Streaming",
            "DataFrame API",
            "Cluster Tuning"
        ]
    },
    "tensorflow": {
        "duration": "4 weeks",
        "resources": [
            "TensorFlow Basics",
            "Neural Networks",
            "Model Deployment",
            "TensorBoard",
            "Keras API"
        ]
    },
    "artificial intelligence": {
        "duration": "5 weeks",
        "resources": [
            "AI Concepts",
            "Search and Optimization",
            "Ethics in AI",
            "Machine Learning Foundations",
            "AI Applications"
        ]
    },
    "market research": {
        "duration": "3 weeks",
        "resources": [
            "Customer Segmentation",
            "Competitive Analysis",
            "Survey Design",
            "Market Sizing",
            "Trend Analytics"
        ]
    },
    "statistics": {
        "duration": "2 weeks",
        "resources": [
            "Descriptive Statistics",
            "Probability",
            "Hypothesis Testing",
            "Regression Analysis",
            "Statistical Inference"
        ]
    },
    "snowflake": {
        "duration": "3 weeks",
        "resources": [
            "Cloud Data Warehousing",
            "Snowflake Architecture",
            "Data Sharing",
            "Secure Data Access",
            "Performance Tuning"
        ]
    },
    "data preprocessing": {
        "duration": "3 weeks",
        "resources": [
            "Data Cleaning",
            "Feature Engineering",
            "Normalization and Scaling",
            "Missing Value Handling",
            "Encoding Categorical Variables"
        ]
    },
    "business analysis": {
        "duration": "3 weeks",
        "resources": [
            "Requirements Gathering",
            "Process Mapping",
            "Stakeholder Communication",
            "Use Case Development",
            "Business Case Analysis"
        ]
    },
    "dashboarding": {
        "duration": "3 weeks",
        "resources": [
            "Dashboard Layout",
            "KPIs and Metrics",
            "Interactivity",
            "Data Storytelling",
            "Performance Optimization"
        ]
    },
    "sql": {
        "duration": "3 weeks",
        "resources": [
            "Joins",
            "Window Functions",
            "CTEs",
            "Query Optimization",
            "Indexing"
        ]
    },
    "nlp": {
        "duration": "4 weeks",
        "resources": [
            "Text Preprocessing",
            "Language Models",
            "Named Entity Recognition",
            "Sentiment Analysis",
            "Topic Modeling"
        ]
    },
    "tableau": {
        "duration": "3 weeks",
        "resources": [
            "Tableau Basics",
            "Calculated Fields",
            "Dashboard Building",
            "Data Blending",
            "Storytelling in Tableau"
        ]
    },
    "gcp": {
        "duration": "4 weeks",
        "resources": [
            "BigQuery",
            "Dataflow",
            "Vertex AI",
            "Cloud Storage",
            "IAM and Security"
        ]
    },
    "python": {
        "duration": "4 weeks",
        "resources": [
            "Pandas",
            "NumPy",
            "Data Cleaning",
            "Scripting and Automation",
            "API Integration"
        ]
    },
    "numpy": {
        "duration": "2 weeks",
        "resources": [
            "Array Operations",
            "Linear Algebra",
            "Broadcasting",
            "Performance Optimization",
            "Random Number Generation"
        ]
    },
    "pandas": {
        "duration": "3 weeks",
        "resources": [
            "DataFrames",
            "Data Manipulation",
            "Time Series",
            "GroupBy Operations",
            "Data Cleaning Workflows"
        ]
    },
    "aws": {
        "duration": "4 weeks",
        "resources": [
            "AWS Core Services",
            "S3 and EC2",
            "IAM and Security",
            "Lambda and Serverless",
            "AWS Analytics"
        ]
    },
    "airflow": {
        "duration": "3 weeks",
        "resources": [
            "DAG Design",
            "Task Scheduling",
            "Operators and Sensors",
            "Monitoring and Logging",
            "Airflow Best Practices"
        ]
    },
    "llm": {
        "duration": "4 weeks",
        "resources": [
            "Transformer Architecture",
            "Prompt Engineering",
            "Fine-Tuning",
            "Evaluation Metrics",
            "In-context Learning"
        ]
    },
    "leadership": {
        "duration": "3 weeks",
        "resources": [
            "Team Communication",
            "Decision Making",
            "Mentoring",
            "Conflict Resolution",
            "Strategic Planning"
        ]
    },
    "azure": {
        "duration": "4 weeks",
        "resources": [
            "Azure Data Services",
            "Azure Synapse",
            "Azure ML",
            "Azure Storage",
            "Security and Governance"
        ]
    },
    "pytorch": {
        "duration": "4 weeks",
        "resources": [
            "PyTorch Tensors",
            "Model Training",
            "Custom Layers",
            "Autograd and Optimization",
            "Deployment with TorchServe"
        ]
    },
    "etl": {
        "duration": "3 weeks",
        "resources": [
            "Extract Processes",
            "Transform Techniques",
            "Load Strategies",
            "Pipeline Orchestration",
            "Data Quality Checks"
        ]
    },
    "dbt": {
        "duration": "3 weeks",
        "resources": [
            "dbt Models",
            "Testing and Documentation",
            "Deployment",
            "Data Lineage",
            "Version Control"
        ]
    }
}


def generate_roadmap(ats_result):

    priority_skills = ats_result['Priority']

    roadmap = {}

    month = 1

    for skill in priority_skills:

        if skill in SKILL_ROADMAP:

            roadmap[f"Month {month}"] = {
                "Skill": skill,
                "Duration":
                SKILL_ROADMAP[skill]["duration"],

                "Topics":
                SKILL_ROADMAP[skill]["resources"]
            }

            month += 1

    return roadmap


#-----------------------------------------------------
# MAIN
#-----------------------------------------------------
def main():
    resume_file = DATA_DIR / "resume" / "Pratham_Resume_Updated.pdf"
    resume_text = extract_resume_text(resume_file)
    resume_skills = extract_skills(resume_text, SKILLS_DB)


    da_skills = get_role_skills('Data Analyst')

    ats_result = calculated_weighted_score(resume_skills , da_skills)
    roadmap = generate_roadmap(ats_result)
    print(roadmap)


if __name__ == "__main__":
    main()
