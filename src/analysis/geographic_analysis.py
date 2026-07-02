import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config.paths import DATA_DIR

#--------------------------------------
# CONFIGURATION
# ------------------------------------
DATA_PATH = DATA_DIR / 'processed'

SKILL_FILE = DATA_PATH / 'jobs_with_skills.csv'
SALARY_FILE = DATA_PATH / 'salary_jobs.csv'
JOB_FILE =  DATA_PATH / 'jobs_cleaned.csv'

OUTPUT_ENHANCED_LOCATION = DATA_PATH / 'location_enhanced.csv'
OUTPUT_LOCATION_MATRIX = DATA_PATH / 'location_role_matrix.csv'
OUTPUT_LOCATION_DEEMAND = DATA_PATH / 'location_deemand.csv'
OUTPUT_LOCATION_ROLE_SALARY = DATA_PATH / 'location_role_salary.csv'

# ------------------------------------------
# LOAD DATA
# ------------------------------------------
def load_data():
    try :
        df_job = pd.read_csv(JOB_FILE)
        df_salary = pd.read_csv(SALARY_FILE)
        df_skill = pd.read_csv(SKILL_FILE)

        return df_job , df_skill , df_salary

    except Exception as e:
        logging.error(f'Failed To Load Dataset:{e}')
        raise


# -------------------------------------------
# LOGGING SETUP
# -------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

#--------------------------------------------
# VALID LOCATIONS
# -------------------------------------------
def valid_location(df):
    location_counts = df["Location"].value_counts() 
    valid_locations = location_counts[location_counts >= 3].index 
    df = df[df["Location"].isin(valid_locations)]
    return df


#---------------------------------------------
# LOCATION DEMAND
#---------------------------------------------
def location__demand(df_skill):
    location_demand = df_skill["Location"].value_counts().reset_index()
    location_demand.columns = ["Location", "Job_Count"]

    location_demand["Percentage"] = (
    location_demand["Job_Count"] / len(df_skill) * 100
    )
    return location_demand


# ----------------------------------------------
# LOCATION ROLE ANALYSIS
# ----------------------------------------------
def location_role_matrix(df_skill):
    location_role = (
    df_skill.groupby(["Location", "Standardized_Job_Title"])
    .size()
    .reset_index(name="Count")
    )

    location_role_mat= (
    location_role.pivot_table(
    index = 'Location',
    columns = 'Standardized_Job_Title',
    values = 'Count'
    ).fillna(0)
    )
    return location_role_mat


# ---------------------------------------------
# LOCATION-ROLE-SALARY ANALYSIS
# ---------------------------------------------
def location_role_salary(df_salary):
    location_role_sal = ( 
            df_salary.groupby(["Location", "Standardized_Job_Title"])
            ["salary_avg"] 
            .median() 
            .reset_index()
            )
    return location_role_sal


# ---------------------------------------------
# VISUALIZATION
# ----------------------------------------------
def top_hiring_location(location_demand):
    sns.barplot(data = location_demand,
                    x = 'Location' ,
                    y='Job_Count')
    plt.xticks(rotation = 45)
    plt.title('Top Hiring Location')
    plt.show()


def location_role_heat(location_role_mat):
    sns.heatmap(location_role_mat ,
                cmap='coolwarm' ,
                linecolor='white',
                linewidths=0.2)
    

def location_salary_bar(df_salary):
    location_salary = ( 
            df_salary.groupby(["Location"])
            ["salary_avg"] 
            .median() 
            .sort_values()
            )
    location_salary.plot(kind='barh')
    plt.xlabel('Median Salary')
    plt.ylabel('Location')
    plt.title('Location by salary')


def remote_vs_onsite(df_skill):
    remote_count = df_skill[df_skill['Location'] == 'Remote'].shape[0]
    onsite_count = df_skill[df_skill['Location'] != 'Remote'].shape[0]

    labels = ['Remote', 'On-site']
    sizes = [remote_count, onsite_count]
    colors = ['lightblue', 'lightcoral']
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Remote vs On-site Job Distribution', fontsize=16)
    plt.show()


# ------------------------------------------
# SAVE OUTPUTS
# -------------------------------------------
def save_outputs(df_skill , location_deemand ,location_role_mat , location_role_sal ):
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    df_skill.to_csv(OUTPUT_ENHANCED_LOCATION , index = False)
    location_deemand.to_csv(OUTPUT_LOCATION_DEEMAND , index = False)
    location_role_mat.to_csv(OUTPUT_LOCATION_MATRIX , index= False)
    location_role_sal.to_csv(OUTPUT_LOCATION_ROLE_SALARY , index = False)

    logging.info('Datasets Saved Successfully!')


# ----------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------
def main():
    df_job, df_skill, df_salary = load_data()

    df_skill = valid_location(df_skill)
    df_salary = valid_location(df_salary)
    df_job = valid_location(df_job)

    location_deemand = location__demand(df_skill)
    location_role_mat = location_role_matrix(df_skill)
    location_role_sal = location_role_salary(df_salary)

    top_hiring_location(location_deemand)
    location_salary_bar(df_salary)
    remote_vs_onsite(df_skill)
    location_role_heat(location_role_mat)

    save_outputs(df_skill , location_deemand ,location_role_mat , location_role_sal)


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    main()










