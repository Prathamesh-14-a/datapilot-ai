import pandas as pd
import re
import numpy as np
from src.config.paths import DATA_DIR


# -------------------------------
# LOAD DATA
# -------------------------------
def load_data(path):
    return pd.read_csv(path)


# -------------------------------
# BASIC CLEANING
# -------------------------------
def clean_basic(df):
    df["Location"].fillna("Not Specified", inplace=True)
    df["Experience Required"].fillna("Not Specified", inplace=True)
    return df


# -------------------------------
# JOB TITLE STANDARDIZATION
# -------------------------------
def standardize_job_title(title):
    title = str(title).lower()

    if "data analyst" in title:
        return "Data Analyst"
    elif "data scientist" in title:
        return "Data Scientist"
    elif "business analyst" in title:
        return "Business Analyst"
    elif "machine learning" in title:
        return "Machine Learning Engineer"
    elif "data engineer" in title:
        return "Data Engineer"
    elif "product analyst" in title:
        return "Product Analyst"
    elif "analytics" in title:
        return "Analytics"
    else:
        return "Other"


def process_job_title(df):
    df["Standardized_Job_Title"] = df["Job Title"].apply(standardize_job_title)
    return df


# -------------------------------
# POSTING DATE NORMALIZATION
# -------------------------------
def normalize_posting_date(date_str):
    date_str = str(date_str).lower()

    if 'few' in date_str or 'hour' in date_str or 'today' in date_str:
        return 0
    elif 'day' in date_str:
        num = re.search(r'\d+', date_str)
        return int(num.group()) if num else 1
    elif 'week' in date_str:
        num = re.search(r'\d+', date_str)
        return int(num.group()) * 7 if num else 7
    elif 'month' in date_str:
        num = re.search(r'\d+', date_str)
        return int(num.group()) * 30 if num else 30
    elif "30+" in date_str:
        return 30
    else:
        return np.nan


def process_dates(df):
    df["days_sinced_posted"] = df["Posted Date"].apply(normalize_posting_date)
    return df


# -------------------------------
# SALARY CLEANING
# -------------------------------
def clean_salary(salary_text):
    salary_text = str(salary_text).strip()

    if "competitive" in salary_text.lower() or salary_text == "nan":
        return pd.Series([np.nan, np.nan, np.nan])

    cleaned = salary_text.replace("₹", "").replace(",", "").strip()

    if "-" in cleaned:
        parts = cleaned.split("-")

        try:
            salary_min = int(parts[0].strip())
            salary_max = int(parts[1].strip())
            salary_avg = (salary_min + salary_max) / 2
            return pd.Series([salary_min, salary_max, salary_avg])
        except:
            return pd.Series([np.nan, np.nan, np.nan])
    else:
        try:
            salary_value = int(cleaned.strip())
            return pd.Series([salary_value, salary_value, salary_value])
        except:
            return pd.Series([np.nan, np.nan, np.nan])


def process_salary(df):
    df[["salary_min", "salary_max", "salary_avg"]] = df["Salary"].apply(clean_salary)
    return df


def create_salary_subset(df):
    salary_df = df[df["salary_avg"].notnull()].copy()
    salary_df.reset_index(drop=True, inplace=True)
    return salary_df


# -------------------------------
# LOCATION STANDARDIZATION
# -------------------------------
def standardize_location(df):
    location_mapping = {
        "Work from home": "Remote",
        "Nanakramguda": "Hyderabad",
        "Yalahanka": "Bangalore"
    }

    df["Location"] = df["Location"].replace(location_mapping)
    return df


# -------------------------------
# EXPERIENCE EXTRACTION
# -------------------------------
def extract_experience_years(exp_text):
    exp_text = str(exp_text).lower()

    if "no experience required" in exp_text:
        return 0
    else:
        match = re.search(r'\d+', exp_text)
        return int(match.group()) if match else np.nan


def process_experience(df):
    df["Experience_Years"] = df["Experience Required"].apply(extract_experience_years)
    return df


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    # Load
    df = load_data(DATA_DIR / "processed" / "jobs_filtered.csv")

    # Cleaning Pipeline
    df = clean_basic(df)
    df = process_job_title(df)
    df = process_dates(df)
    df = process_salary(df)
    df = standardize_location(df)
    df = process_experience(df)

    # Salary subset
    salary_df = create_salary_subset(df)

    # Save outputs
    df.to_csv(DATA_DIR / "processed" / "jobs_cleaned.csv", index=False)
    salary_df.to_csv(DATA_DIR / "processed" / "salary_jobs.csv", index=False)

    print("Data pipeline executed successfully!")


# ------------------------------- 
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    main()