# ------------------------------------------
# IMPORTS 
# ------------------------------------------
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config.paths import DATA_DIR


# --------------------------------------------
# CONFIGURATION
# ---------------------------------------------
DATA_PATH = DATA_DIR / "processed"

SALARY_FILE = DATA_PATH / "salary_jobs.csv"
JOB_FILE = DATA_PATH / "jobs_with_skills.csv"

OUTPUT_ENHANCED_SALARY = DATA_PATH / "salary_enhanced.csv"
OUTPUT_PREMIUM_SKILLS = DATA_PATH / "premiun_skill_salary.csv"
OUTPUT_FILTERED_LOCATION = DATA_PATH / "filtered_location_df.csv"

PREMIUM_SKILLS = [
    'tensorflow', 'pytorch', 'nlp', 'llm', 'artificial intelligence',
    'computer vision', 'spark', 'hadoop', 'airflow', 'dbt',
    'databricks', 'snowflake', 'big data',
    'aws', 'azure', 'gcp',
    'scala', 'java'
]

VALID_LOCATIONS = ["Remote", "Bangalore", "Delhi", "Gurgaon", "Noida"]

# -------------------------------------------
# LOGGING SETUP
# -------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ------------------------------------------
# LOAD DATA
# ------------------------------------------
def load_data():
    try :
        df = pd.read_csv(JOB_FILE)
        salary_df = pd.read_csv(SALARY_FILE)

        logging.info(f'Job Data Shape: {df.shape}')
        logging.info(f'Salary Data Shape: {salary_df.shape}')
        return df , salary_df

    except Exception as e:
        logging.error(f'Failed To Load Dataset:{e}')
        raise



# ----------------------------------------------
# PREMIUM SKILL DF
# ----------------------------------------------
def premium_skill(skill_df):
    premium_skills = {}
    for skill in PREMIUM_SKILLS:
        skill_jobs = skill_df[
            skill_df["extracted_skills"].str.contains(skill, na=False)
        ]
    
        premium_skills[skill] = skill_jobs["salary_avg"].dropna().median()

    premium_skill_df = pd.DataFrame(
    premium_skills.items(),
    columns=["Skill", "Median_Salary"]
    )

    premium_skill_df = premium_skill_df.dropna()
    return premium_skill_df


# -----------------------------------------------
# FILTERED LOCATION DF
# ------------------------------------------------
def filtered_skills(salary_df):
    filtered_location_df = salary_df[salary_df["Location"].isin(VALID_LOCATIONS)]
    return filtered_location_df


# -------------------------------------------------
# SALARY BAND
# -------------------------------------------------
def salary_band(salary):
    if salary < 400000:
        return "Low"
    elif salary < 800000:
        return "Mid"
    else:
        return "High"

def apply_salary_band(salary_df):
    salary_df["Salary_Band"] = salary_df["salary_avg"].apply(
        lambda x: salary_band(x) if pd.notnull(x) else "Unknown"
        )
    return salary_df


# -------------------------------------------------
# VISUALIZATION
# -------------------------------------------------
def plot_salary_distribution(salary_df):
    sns.histplot(
    salary_df['salary_avg'], 
    kde = True,
    color='purple',
    element='step'
    )
    plt.title('Distribution Of Salary Average')
    plt.show()


def boxplot_salary(salary_df):
    sns.boxplot(
    salary_df['salary_avg']
    )


def job_role_vs_salary(salary_df):
    salary_job_role = (salary_df.groupby('Standardized_Job_Title')
                   ['salary_avg'].median()
                   .sort_values(ascending=False))

    salary_job_role.sort_values().plot(kind='barh')
    plt.xlabel('Salary LPA (1LPA = 0.1)')
    plt.title('Salary by Job Role')
    plt.show()


def salary_by_location(salary_df):
    salary_location = (salary_df.groupby('Location')
                   ['salary_avg'].median()
                   .sort_values(ascending=False))
    
    salary_location.head(10).plot(kind="bar")
    plt.title("Top Paying Locations")
    plt.show()


def remote_vs_onsite(salary_df):
    remote_salary = salary_df[salary_df["Location"] == "Remote"]["salary_avg"].median()
    onsite_salary = salary_df[salary_df["Location"] != "Remote"]["salary_avg"].median()
    logging.info('Remote Salary :\n' , remote_salary)
    logging.info('Onsite Salary : \n' , onsite_salary)


# ------------------------------------------
# SAVE OUTPUTS
# -------------------------------------------
def save_outputs(salary_df, premium_skill_df , filtered_location_df):
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    salary_df.to_csv(OUTPUT_ENHANCED_SALARY , index = False)
    premium_skill_df.to_csv(OUTPUT_PREMIUM_SKILLS , index = False)
    filtered_location_df.to_csv(OUTPUT_FILTERED_LOCATION , index= False)

    logging.info('Datasets Saved Successfully!')


# ----------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------
def main():
    df , salary_df = load_data()

    premium_skill_df = premium_skill(df)
    filtered_location_df = filtered_skills(salary_df)

    salary_df = apply_salary_band(salary_df)

    plot_salary_distribution(salary_df)
    boxplot_salary(salary_df)
    job_role_vs_salary(salary_df)
    salary_by_location(salary_df)
    remote_vs_onsite(salary_df)

    save_outputs(salary_df, premium_skill_df , filtered_location_df) 


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    main()











