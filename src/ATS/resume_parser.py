import pdfplumber
import re
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from src.resume_matching.resume_parser import (extract_resume_text , 
                                               extract_with_ocr , 
                                               clean_resume_text , 
                                               text_validation , 
                                               extract_skills )

SKILLS_DB = [

    # Programming Languages
    "python",
    "r",
    "sql",
    "java",
    "scala",
    "c++",
    "matlab",
    "sas",

    # Python Libraries
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "plotly",
    "bokeh",
    "scipy",
    "statsmodels",
    "scikit-learn",
    "sklearn",
    "tensorflow",
    "keras",
    "pytorch",
    "xgboost",
    "lightgbm",
    "opencv",
    "nltk",
    "spacy",

    # Data Analysis
    "data analysis",
    "data cleaning",
    "data wrangling",
    "data preprocessing",
    "exploratory data analysis",
    "eda",
    "feature engineering",
    "statistical analysis",

    # Machine Learning
    "machine learning",
    "supervised learning",
    "unsupervised learning",
    "classification",
    "regression",
    "clustering",
    "decision trees",
    "random forest",
    "gradient boosting",
    "support vector machine",
    "svm",
    "ensemble learning",

    # Deep Learning
    "deep learning",
    "neural networks",
    "cnn",
    "rnn",
    "lstm",
    "transformers",

    # NLP
    "natural language processing",
    "nlp",
    "text mining",
    "sentiment analysis",
    "tokenization",

    # Statistics & Math
    "statistics",
    "probability",
    "hypothesis testing",
    "a/b testing",
    "linear algebra",
    "calculus",

    # Databases
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",
    "oracle",
    "nosql",

    # BI / Visualization Tools
    "power bi",
    "tableau",
    "excel",
    "google sheets",
    "looker",
    "qlikview",

    # Data Engineering
    "etl",
    "elt",
    "data pipelines",
    "apache spark",
    "hadoop",
    "airflow",
    "kafka",

    # Cloud Platforms
    "aws",
    "azure",
    "gcp",
    "google cloud",

    # Big Data
    "big data",
    "distributed computing",

    # Deployment / MLOps
    "docker",
    "kubernetes",
    "mlops",
    "model deployment",
    "flask",
    "fastapi",
    "streamlit",

    # Version Control
    "git",
    "github",

    # Spreadsheet Skills
    "pivot tables",
    "vlookup",
    "dashboarding",

    # Business / Analytics
    "business intelligence",
    "data visualization",
    "reporting",
    "dashboard development",
    "kpi analysis",

    # AI / Advanced
    "artificial intelligence",
    "computer vision",
    "recommendation systems",
    "time series analysis"
]

def process_resume(path:str) -> str:

    
    # trying normal extraction
    resume_text = extract_resume_text(path)

    if not text_validation(resume_text):

        
        resume_text = extract_with_ocr(path)
    
    return resume_text

    
def cleaned_resume_text(resume_text:str) -> str:
    # clean text
    cleaned_text = clean_resume_text(resume_text)
    return cleaned_text

    

resume = r"d:\Startup\Project\ai-career-coach\data\resume\Pratham_Resume_Updated.pdf"



class SectionParser:

    SECTION_PATTERNS = {
        "summary": r"(professional summary|summary|profile)",
        "skills": r"(technical skills|skills|core competencies)",
        "projects": r"(projects|project experience)",
        "education": r"(education|academic background)",
        "experience": r"(experience|work experience|professional experience)",
        "certifications": r"(certifications|licenses)"
    }

    def extract_sections(self, text):
        """
        Extract structured resume sections
        """

        sections = {}

        lower_text = text.lower()

        matches = []

        for section, pattern in self.SECTION_PATTERNS.items():
            match = re.search(pattern, lower_text)

            if match:
                matches.append((match.start(), section))

        matches.sort()

        for i in range(len(matches)):
            start_pos, section_name = matches[i]

            if i + 1 < len(matches):
                end_pos = matches[i + 1][0]
            else:
                end_pos = len(text)

            sections[section_name] = text[start_pos:end_pos].strip()

        return sections

result_text = process_resume(resume)
cleaned_text = cleaned_resume_text(result_text)
section_parser = SectionParser()

sections = section_parser.extract_sections(cleaned_text)

# for section, content in sections.items():
#     print(f"\n{'='*60}")
#     print(f"{section.upper()}")
#     print(f"{'='*60}")
#     print(content[:700])

skill_section = sections.get("skills" , "")
project_section = sections.get("projects" , "")

skills_from_skills = extract_skills(skill_section , SKILLS_DB)
skills_from_projects = extract_skills(project_section , SKILLS_DB)

# print("\nSkills Section Matches:")
# print(skills_from_skills)

# print("\nProjects Section Matches:")
# print(skills_from_projects)

# print("\nCombined Unique Skills:")
# print(sorted(set(skills_from_skills + skills_from_projects)))



# testing on 10 resumes
# for i in range(1 , 18):
    # resume = Path((rf"d:\Startup\Project\ai-career-coach\data\resume\resume_{i}.pdf"))
   
    # print(f'\nResume Skill Extraction For Resume No. {i}\n')
    # result_text = process_resume(resume)
    # cleaned_text = cleaned_resume_text(result_text)
    # section_parser = SectionParser()

    # sections = section_parser.extract_sections(cleaned_text)

    # for section, content in sections.items():
    #     print(f"\n{'='*60}")
    #     print(f"{section.upper()}")
    #     print(f"{'='*60}")
    #     print(content[:700])
