import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from src.config.paths import DATA_DIR


#Scrapping Data from the Internshala Job portal
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

job_titles = []
company_names= []
locations = []
salary = []
experience_list = []
skills_required= []
job_description = []
posted_dates = []
job_links = []

for j in range(1,16):
    url = f"https://internshala.com/jobs/analytics,data-science,machine-learning-jobs/page-{j}/"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
    soup = BeautifulSoup(response.text , "html.parser")
      
    #extracting job titles
    for title in soup.find_all("a" , class_ = "job-title-href"):
        job_titles.append(title.text.strip())
    
    #extracting company names
    for company in soup.find_all("p" , class_ = "company-name"):
        company_names.append(company.text.strip())  
    
    #extracting locations
    for loc in soup.find_all("div", class_="individual_internship"):
        location_tag = loc.select_one("p.row-1-item.locations span a")
        if location_tag:
            locations.append(location_tag.get_text(strip=True)) 
        else:
            locations.append(None)
    
    #extracting salary
    for job in soup.find_all("div", class_="individual_internship"):
        salary_tag = job.select_one("i.ic-16-money + span")
    
        if salary_tag:
            salary.append(salary_tag.get_text(strip=True))
        else:
            salary.append(None)
       
    #extracting experience
    for exp in soup.find_all("div", class_="individual_internship_details"):
        exp_tag = exp.select_one("i.ic-16-briefcase + span")
        if exp_tag:
            experience = exp_tag.get_text(strip=True)
            experience_list.append(experience)
        else:
            experience_list.append(None)
    
    #extracting skills required
    for job in soup.find_all("div", class_="individual_internship"):
        skill_tags = job.select("div.job_skills div.job_skill")
        skills = [skill.get_text(strip=True) for skill in skill_tags]
        skills_required.append(skills)
    
    #extracting job description
    for des in soup.find_all("div", class_="individual_internship_details"):
        des_tag = des.select_one("div.about_job div.text")
        if des_tag:
            description = des_tag.get_text(strip=True)
        job_description.append(description)
    
    #extracting posted dates
    for job in soup.find_all("div", class_="internship_meta"):
        date = job.select_one("div.detail-row-2 div.color-labels span")
        posted_dates.append(date.text.strip() if date else None)
    
    #extracting job links
    for link in soup.find_all("div", class_="internship_meta"):
        link_tag = link.select_one('a.job-title-href')
        if link_tag:
            job_links.append("https://internshala.com" + link_tag['href'])

time.sleep(1)

# Storing Data in DataFrame
data = pd.DataFrame({
    "Job Title": job_titles,
    "Company Name": company_names,
    "Location": locations,
    "Experience Required": experience_list,
    "Salary" : salary,
    "Skills Required": skills_required,
    "Job Description": job_description,
    "Posted Date": posted_dates,
    "Scrape Date": pd.Timestamp.now().date(),
    "Job Link" : job_links ,
    "Source Platform": "Internshala" , 
    })

# Job Filtering based on required job roles
relevant_keywords = [
    "data analyst",
    "data scientist",
    "business analyst",
    "machine learning",
    "data engineer",
    "product analyst",
    "analytics",
    "bi",
    "etl"
]

# Create regex pattern
pattern = "|".join(re.escape(keyword) for keyword in relevant_keywords)

# Filter rows based on job title
df = data[data["Job Title"].str.contains(pattern, case=False, na=False)]

df.reset_index(drop=True, inplace=True)
print(df.head())
print(df.shape)
print("Scrapping Completed Successfully!")

data.to_csv(DATA_DIR / "raw" / "jobs_raw.csv", index=False)
df.to_csv(DATA_DIR / "processed" / "jobs_filtered.csv", index=False)
print("Data saved to CSV files successfully!")