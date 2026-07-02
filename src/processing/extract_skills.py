import pandas as pd
import re
import nltk
import logging
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#    IMPORT DATASET
# ----------------------------------
def load_data(path):
    try:
        df = pd.read_csv(path)
        logging.info("Dataset loaded successfully")
        return df
    except Exception as e:
        logging.error(f"Failed to load dataset: {e}")
        raise



#    COMBINING TEST FEATURES 
# --------------------------------
def combine_text(df):
    df = df.copy()
    df["combined_text"] = (
    df["Standardized_Job_Title"].fillna("") + " " +
    df["Job Description"].fillna("") + " " +
    df["Skills Required"].fillna("")
    )
    return df 


#     REMOVING PUNCTUATIONS
# ----------------------------------
def remove_punctuation(df):
    df = df.copy()
    df["combined_text"] = (df["combined_text"].str.lower()
                       .apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', ' ', x)))
    return df


#     REMOVING EXTRA CHARACTERS (\r,\n,\xa0)
# ------------------------------------------------
def remove_extra_char(df):
    df = df.copy()
    df["combined_text"] = (df['combined_text']
                       .apply(lambda x : re.sub(r'[\r\n\xa0]+' , ' ' , x))
                       .str.strip())   
    return df 


#    REMOVING EXTRA SPACES
# -----------------------------------------
def remove_spaces(df):
    df = df.copy()
    df["combined_text"] = (df['combined_text']
                       .apply(lambda x: re.sub(r'\s+', ' ', x).strip()))
    return df


#   REMOVING IRRELEVANT NUMBERS
# ---------------------------------------
def remove_num(df):
    df = df.copy()
    df['combined_text'] = (df["combined_text"]
                        .apply(lambda x: re.sub(r'\b\d+\b', '', x)))
    return df


#     TOKENIZATION
# -------------------------------------
def word_tokenization(df):
    df = df.copy()
    df['tokens'] = df["combined_text"].apply(word_tokenize)
    return df


#    STOP WORD REMOVAL
# --------------------------------------
def stop_word_remove(tokens):
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

def stopword_processed(df):
    df = df.copy()
    df['filtered_tokens'] = df['tokens'].apply(stop_word_remove)
    return df


#    LEMMATIZATION
# ---------------------------------
def lemmatize_text(df):
    df = df.copy()
    lemmatizer = WordNetLemmatizer()

    df["lemmatized_tokens"] = (df["filtered_tokens"]
                    .apply(lambda tokens: [lemmatizer
                        .lemmatize(token , pos = "v") for token in tokens]))
    return df
    

#   FINAL PROCESSED TEXT
# -----------------------------------
def process_text(df):
    df = df.copy()
    df["processed_text"] = df["lemmatized_tokens"].apply(lambda x: " ".join(x))
    return df


# SKILL EXTRACTION
# -------------------------------------

# Skill List for all Required skills
skills_list = ['python' ,'r','sql','java','scala','c++' ,
               'excel','power bi','tableau' ,'statistics',
               'data visualization','reporting','dashboarding' , 
               'mysql','postgresql','mongodb','snowflake','oracle' ,
               'etl','data warehousing','spark','hadoop','airflow','dbt',
               'machine learning','deep learning','nlp','tensorflow',
               'pytorch','scikit-learn','computer vision','llm' ,
               'aws','azure','gcp','databricks' ,'business analysis',
               'stakeholder management','kpi','forecasting','market research' ,
               'communication','problem solving','leadership','presentation',
               'pandas','numpy','matplotlib','seaborn','plotly','ggplot2',
               'artificial intelligence','big data',
               'data mining','data cleaning', 'data preprocessing',
               'data modeling','data analysis',
               'data storytelling', 'research','analysis','reporting','dashboard' ,
                'structured query language',
               'visualization','google sheets' , 'microsoft excel']

def skill_extractor(text):
    extracted_skills = []
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            extracted_skills.append(skill)
    return list(set(extracted_skills))

def skill_and_count_extract(df):
    df = df.copy()
    df["extracted_skills"] = df["processed_text"].apply(skill_extractor)
    df["skill_count"] = df["extracted_skills"].apply(len)
    return df


#   NORMALIZE SKILLS 
# -------------------------------------------
def skill_normalize(df):
    df = df.copy()
    normalization_dict = {
    "microsoft excel": "excel",
    "structured query language": "sql",
    "visualization": "data visualization",
    "dashboard": "dashboarding"
    }
    df['extracted_skills'] = (df['extracted_skills']
        .apply(lambda skills: [normalization_dict.get(skill, skill) for skill in skills]))
    return df


# SKILL SEPARATION
# ------------------------------------------

#  Separating Skills
def skill_separate(df):
    df = df.copy()
    #technical skills
    technical_skills = [
    # Programming
    'python', 'r', 'sql', 'java', 'scala', 'c++',

    # Data tools
    'excel', 'google sheets', 'microsoft excel',
    'power bi', 'tableau',

    # Statistics & analytics
    'statistics',

    # Databases
    'mysql', 'postgresql', 'mongodb', 'snowflake', 'oracle',

    # Data engineering
    'etl', 'data warehousing', 'spark', 'hadoop',
    'airflow', 'dbt',

    # Machine learning / AI
    'machine learning', 'deep learning', 'nlp',
    'tensorflow', 'pytorch', 'scikit-learn',
    'computer vision', 'llm', 'artificial intelligence',

    # Cloud / infrastructure
    'aws', 'azure', 'gcp', 'databricks',

    # Python libraries
    'pandas', 'numpy', 'matplotlib',
    'seaborn', 'plotly', 'ggplot2',

    # Data-specific processes
    'big data', 'data mining', 'data cleaning',
    'data preprocessing', 'data modeling',
    'data analysis', 'structured query language'
    ]
    
    #soft skills
    soft_skills = [
    'communication',
    'problem solving',
    'leadership',
    'presentation',
    'stakeholder management',
    'research'
    ]
    
    #business terms
    business_terms = [
    'business analysis',
    'kpi',
    'forecasting',
    'market research',
    'data visualization',
    'visualization',
    'reporting',
    'dashboarding',
    'dashboard',
    'data storytelling',
    'analysis'
    ]

    df["technical_skills"]= (df["extracted_skills"]
                .apply(lambda skills: [skill for skill in skills if skill in technical_skills]))   
    
    df["soft_skills"] = (df["extracted_skills"]
                .apply(lambda skills:[skill for skill in skills if skill in soft_skills]))
    
    df['business_skills'] = (df['extracted_skills']
                     .apply(lambda skills: [skill for skill in skills if skill in business_terms]))
    
    return df 


#  SKILL COUNT FREQUENCY
# --------------------------------------
def skill_count_frequency(df):
    all_skills = [
    skill 
    for skill_list in df['extracted_skills'] 
    for skill in skill_list
    ]
    skill_counts = Counter(all_skills)

    #creating dataframe
    skill_freq_df = pd.DataFrame(
    skill_counts.items(),
    columns=["Skill", "Count"]
    ).sort_values(by="Count", ascending=False)

    return skill_freq_df


# ROLE SKILL MAPPING 
# ------------------------------------------
def role_skill_map(df):
    role_skill_data = []
    for role in df["Standardized_Job_Title"].unique():
        role_df = df[df["Standardized_Job_Title"] == role]
        role_skill = [
            skill
            for skills_list in role_df["extracted_skills"]
            for skill in skills_list
        ]
        role_skill_count = Counter(role_skill)
        for skill , count in role_skill_count.items():
            role_skill_data.append({
            "Role": role,
            "Skill": skill,
            "Count": count
            })

    # creating a dataframe for role skill mapping
    role_skill_df = pd.DataFrame(role_skill_data)
    return role_skill_df


# ROLE SKILL MATRIX
# -------------------------------------------
def role_skill_mat(role_skill_df):
    role_skill_df = role_skill_df.copy()
    role_skill_matrix = role_skill_df.pivot_table(
    index = 'Role' , 
    columns = 'Skill' ,
    values = 'Count' , 
    fill_value = 0
    )

    return role_skill_matrix


# MAIN PIPELINE
# ----------------------------------------------
def main():
    # Load
    df = load_data(DATA_DIR / "processed" / "jobs_cleaned.csv")

    # Text Cleaning Pipeline
    df = combine_text(df)
    df = remove_punctuation(df)
    df = remove_extra_char(df)
    df = remove_spaces(df)
    df = remove_num(df)

    # NLP preprocessing
    df = word_tokenization(df)
    df = stopword_processed(df)
    df = lemmatize_text(df)

    #Final Process Text
    df = process_text(df)

    # Skill Extraction
    df = skill_and_count_extract(df)
    df = skill_normalize(df)
    df = skill_separate(df)

    # Skill Count Frequency
    skill_freq_df = skill_count_frequency(df)
    
    #Role Skill Mapping
    role_skill_df = role_skill_map(df)

    #Role Skill Matrix
    role_skill_matrix = role_skill_mat(role_skill_df)

    #Save outputs
    df.to_csv(DATA_DIR / "processed" / "jobs_with_skills.csv", index=False)
    skill_freq_df.to_csv(DATA_DIR / "processed" / "skill_frequencies.csv", index=False)
    role_skill_df.to_csv(DATA_DIR / "processed" / "role_skill_mapping.csv", index=False)
    role_skill_matrix.to_csv(DATA_DIR / "processed" / "role_skill_matrix.csv", index=False)

    logging.info("Data Pipeline Executed Successfully!")


# ENTRY POINT
# ---------------------------------------
if __name__ == "__main__":
    main()
    

