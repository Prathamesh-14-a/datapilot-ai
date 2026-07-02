import ast
import logging

import pandas as pd

from src.config.paths import DATA_DIR


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ----------------------------------------------
# CONFIG
# ----------------------------------------------
DATA_PATH = DATA_DIR / 'processed'

SKILL_FILE = DATA_PATH / 'jobs_with_skills.csv'

OUTPUT_BENCHMARK_FILE = DATA_PATH / 'top_skills_by_role.csv'


# -----------------------------------------------
# IMPORT DATASET
# -----------------------------------------------
def load_data():
    try:
        df = pd.read_csv(SKILL_FILE)

    except FileNotFoundError:
        logging.error('File Not Found')

    except Exception as e:
        logging.error(f'File Loading Eroor : {e}')

    return df


#-------------------------------------------------
# BASIC VALIDATION
# -----------------------------------------------
def validate_data(df):

    #validating datarows
    if df.empty:

        raise ValueError(
        'DataFrame is empty'
        )
    
    # required columns
    required_columns = [
    "Standardized_Job_Title",
    "extracted_skills"
    ]
    # missing columns
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
        ]
    
    if missing_columns:
         raise ValueError(
             f'missing column  : {missing_columns}'
         )
    
    return df


# ------------------------------------------
# CLEANING DATA
# ------------------------------------------
def cleaning_data(df):
    # droping nulls
    df = df.dropna(
        subset = [
             "Standardized_Job_Title",
            "extracted_skills"
        ]
    )

    # removing duplicate
    df = df.drop_duplicates()

    #reset index
    df = df.reset_index(drop=True)

    return df


# -----------------------------------------
#  BENCHMARK DATAFRAME
# -----------------------------------------
def benchmark_data(df):
    #extracting subset
    benchmark_df = df[[
    "Standardized_Job_Title",
        "extracted_skills"
    ]].copy()

    # converting string into actual list
    benchmark_df['extracted_skills'] = benchmark_df['extracted_skills'].apply(
    ast.literal_eval
    )

    #exploding skills 
    benchmark_df = benchmark_df.explode(
    "extracted_skills"
    )

    # cleaning skill noise
    exclude_skills = [
    "analysis",
    "research",
    "data analysis",
    "communication" , 
    "data visualization" , 
    "leadership" , 
    "presentation"
    ]
    benchmark_df = (benchmark_df[~benchmark_df['extracted_skills']
                                 .isin(exclude_skills)].copy())
    
    # renaming column
    benchmark_df = benchmark_df.rename(
    columns={
        "extracted_skills": "Skill"
    }
    )

    #reset index
    benchmark_df = benchmark_df.reset_index(
    drop=True
    )

    return benchmark_df

# ----------------------------------------------
# ROLE SKILLS COUNT DATAFRAME
# -----------------------------------------------
def role_skill_count_df(benchmark_df):

    # group by benchmark_df by job role and skill and counted frequency

    role_skill_counts = (
    benchmark_df
    .groupby(
        [
            "Standardized_Job_Title",
            "Skill"
        ]
    )
    .size()
    .reset_index(name="Count")
    )

    # sorting values 
    role_skill_counts = (
    role_skill_counts.sort_values(
        by = ['Standardized_Job_Title' , 'Count'] ,
        ascending = [True ,False ]
    )
    )

    # reset index
    role_skill_counts = role_skill_counts.reset_index(drop=True)

    return role_skill_counts

# ----------------------------------------------------
# TOP ROLE SKILL DATAFRAME
# ----------------------------------------------------
def top_role_skill_df(role_skill_counts):

    # taking top 10 skills for each job role
    TOP_N = 10
    top_role_skill = (
        role_skill_counts.groupby(
        'Standardized_Job_Title'
        )
    ).head(TOP_N)

    # reset index
    top_role_skill = top_role_skill.reset_index(drop = True)

    return top_role_skill

# -------------------------------------------------------
# PRINTING PREVIEWS
# -------------------------------------------------------
def print_preview(benchmark_df , role_skill_counts , top_role_skill):
    print('Benchmark DF Shape:\n')
    print(benchmark_df.shape)
    print('Benchmark DF Preview : \n ')
    print(benchmark_df.head())

    print('Role Skill Counts DF Shape:\n')
    print(role_skill_counts.shape)
    print('Role Skill Counts DF Preview : \n ')
    print(role_skill_counts.head())
    print("Role Skill Count For Data Analyst : \n")
    print(
    role_skill_counts[
        role_skill_counts[
            "Standardized_Job_Title"
        ] == "Data Analyst"
    ])
    print('Highest Frequency Skils: \n')
    print(
    role_skill_counts
    .sort_values(
        by="Count",
        ascending=False
    )
    .head(20)
    )

    print('Top Role Skill DF Shape:\n')
    print(top_role_skill.shape)
    print('Top Role Skill DF Preview : \n ')
    print(top_role_skill.head(20))
    print("Top Role Skill Count For Data Analyst : \n")
    print(
    top_role_skill[
       top_role_skill[
            "Standardized_Job_Title"
        ] == "Data Analyst"
    ])
    

# ----------------------------------------------------
# SAVE OUTPUT
# -----------------------------------------------------
def save_output(top_role_skill):
    top_role_skill.to_csv(
        OUTPUT_BENCHMARK_FILE , 
         index = False
    )


# -----------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------
def main():
    df = load_data()

    df = validate_data(df)

    df = cleaning_data(df)

    benchmark_df = benchmark_data(df)
    
    role_skill_counts = role_skill_count_df(benchmark_df)

    top_role_skill = top_role_skill_df(role_skill_counts)

    print_preview(benchmark_df , role_skill_counts , top_role_skill)

    save_output(top_role_skill)
    print('Dataset saved Successfully')

# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    main()








    




