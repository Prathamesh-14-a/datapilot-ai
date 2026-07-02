import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import os
from pathlib import Path
import sys
from src.config.paths import DATA_DIR

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.processing.clean_jobs import standardize_job_title

#-----------------------------------------------
# HEADERS FOR WEB SCRAPING
#-----------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# -----------------------------------------------
# SCRAPPING JOBS FOR SALARIES
#-----------------------------------------------

def scrape_jobs(role, pages):

    all_jobs = []

    # convert role to url format
    role_url = role.lower().replace(" ", "-")

    for page in range(1, pages + 1):

        url = f"https://www.ambitionbox.com/jobs/{role_url}-jobs-prf?page={page}"

        print(f"Scraping Page {page}")

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            response.raise_for_status()

        except requests.exceptions.Timeout:
            print("Request timed out")
            continue

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.find_all("div", class_="jobInfoCard")

        for card in cards:

            # TITLE
            title_tag = card.find("a", class_="title noclick")

            job_title = (
                title_tag.text.strip()
                if title_tag else None
            )

            # EXPERIENCE
            exp_div = card.find(
                "div",
                title=lambda x: x and "year" in x.lower()
            )

            experience = (
                exp_div.get("title")
                if exp_div else None
            )

            # LOCATION
            loc_div = card.find(
                "div",
                class_=lambda x: x and "loc" in x
            )

            location = (
                loc_div.get("title")
                if loc_div else None
            )

            # SALARY
            salary_div = card.find(
                "div",
                title=lambda x: x and "L/yr" in x
            )

            salary = (
                salary_div.get("title")
                if salary_div else None
            )

            # SKILLS
            skills = None

            skill_divs = card.find_all("div", title=True)

            for div in skill_divs:

                skill_title = div.get("title")

                # skills usually contain commas
                if skill_title and "," in skill_title:

                    skills = [
                        skill.strip()
                        for skill in skill_title.split(",")
                    ]

                    break

            # STORE DATA
            all_jobs.append({
                "role": role,
                "job_title": job_title,
                "experience": experience,
                "location": location,
                "salary": salary,
                "skills": skills
            })

    # dataframe
    df = pd.DataFrame(all_jobs)

    return df


def extract_avg_exp(exp):    
    if pd.isna(exp):
        return None

    exp = str(exp).lower().strip()

    # extract all numbers
    nums = re.findall(r'\d+', exp)

    if len(nums) >= 2:
        min_exp = int(nums[0])
        max_exp = int(nums[1])

        return (min_exp + max_exp) / 2

    elif len(nums) == 1:
        return int(nums[0])

    else:
        return None

    
def extract_avg_salary(sal):    
    if pd.isna(sal):
        return None

    sal = str(sal).lower().strip()

    # extract all numbers
    nums = re.findall(r'\d+', sal)

    if len(nums) >= 2:
        min_exp = int(nums[0])
        max_exp = int(nums[1])

        return ((min_exp + max_exp) / 2 ) * 100000

    elif len(nums) == 1:
        return int(nums[0]) * 100000

    else:
        return None

# ------------------------------------------------------
# CLEANING DATA
# ------------------------------------------------------
def cleaning_scrape_data(df):
    df['Standardized_Job_Title'] = df['job_title'].apply(standardize_job_title)
    df['avg_experience'] = df['experience'].apply(extract_avg_exp)
    df['avg_salary'] = df['salary'].apply(extract_avg_salary)
    return df

# ------------------------------------------------------
# MAIN PIPELINE
#------------------------------------------------------
def main():
    data_analyst_df = scrape_jobs("data analyst" , 45)
    data_analyst_df = cleaning_scrape_data(data_analyst_df)
    print(data_analyst_df.head())
    print(data_analyst_df.shape)
    data_analyst_df.to_csv(DATA_DIR / "Salary Prediction Data" / "data_analyst_jobs.csv", index=False)

    data_scientist_df = scrape_jobs("data scientist" , 50)
    data_scientist_df = cleaning_scrape_data(data_scientist_df)
    print(data_scientist_df.head())
    print(data_scientist_df.shape)
    data_scientist_df.to_csv(DATA_DIR / "Salary Prediction Data" / "data_scientist_jobs.csv", index=False)

    data_engineer_df = scrape_jobs("data engineer" , 70)
    data_engineer_df = cleaning_scrape_data(data_engineer_df)
    print(data_engineer_df.head())
    print(data_engineer_df.shape)
    data_engineer_df.to_csv(DATA_DIR / "Salary Prediction Data" / "data_engineer_jobs.csv", index=False)

    ml_df = scrape_jobs("machine learning engineer" , 30)
    ml_df = cleaning_scrape_data(ml_df)
    print(ml_df.head())
    print(ml_df.shape)
    ml_df.to_csv(DATA_DIR / "Salary Prediction Data" / "ml_engineer_jobs.csv", index=False)


    business_df = scrape_jobs("business analyst" , 40)
    business_df = cleaning_scrape_data(business_df)
    print(business_df.head())
    print(business_df.shape)
    business_df.to_csv(DATA_DIR / "Salary Prediction Data" / "business_analyst_jobs.csv", index=False)

    


if __name__ == "__main__":
    main()






