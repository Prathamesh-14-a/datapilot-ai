import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# LOAD DATA
# -------------------------------
def load_data(path):
    return pd.read_csv(path)


# BASIC INFO
# -------------------------------
def basic_info(df):
    print(f"Dataset Shape: {df.shape}")
    print("\nMissing Values:\n", df.isnull().sum())


# ROLE ANALYSIS
# -------------------------------
def role_analysis(df):
    role_count = df['Standardized_Job_Title'].value_counts()

    plt.figure(figsize=(12, 6))
    role_count.plot(
        kind='bar',
        color=sns.color_palette('viridis', len(role_count)),
        edgecolor='black',
        linewidth=1.2
    )
    plt.title('Job Role Distribution')
    plt.xticks(rotation=45)
    plt.show()

    return role_count


# LOCATION ANALYSIS
# -------------------------------
def location_analysis(df):
    location_count = df['Location'].value_counts()

    location_count.head(10).plot(
        kind='bar',
        color='green',
        alpha=0.7,
        edgecolor='black'
    )
    plt.title('Top Hiring Locations')
    plt.xticks(rotation=45)
    plt.show()

    return location_count


# EXPERIENCE ANALYSIS
# -------------------------------
def experience_analysis(df):
    exp_counts = df['Experience_Years'].value_counts().sort_values()

    exp_counts.plot(
        kind='barh',
        color='orange',
        alpha=0.7,
        edgecolor='black'
    )
    plt.title('Experience Required')
    plt.show()

    return exp_counts


# SALARY ANALYSIS
# -------------------------------
def salary_analysis(df):
    print("Salary Summary:\n", df["salary_avg"].describe())

    sns.histplot(df['salary_avg'].dropna(), bins=30, kde=True)
    plt.title('Salary Distribution')
    plt.show()

    df["salary_avg"].plot(kind="box")
    plt.title("Salary Boxplot")
    plt.show()

    salary_by_role = df.groupby("Standardized_Job_Title")["salary_avg"].median()
    print("\nSalary by Role:\n", salary_by_role)

    return salary_by_role


# REMOTE VS ONSITE
# -------------------------------
def remote_analysis(df):
    remote_count = df[df['Location'] == 'Remote'].shape[0]
    onsite_count = df[df['Location'] != 'Remote'].shape[0]

    plt.figure(figsize=(6, 6))
    plt.pie(
        [remote_count, onsite_count],
        labels=['Remote', 'On-site'],
        autopct='%1.1f%%'
    )
    plt.title('Remote vs On-site Jobs')
    plt.show()

    return remote_count, onsite_count


# COMPANY ANALYSIS
# -------------------------------
def company_analysis(df):
    return df["Company Name"].value_counts().head(10)


#EXPORT RESULTS
#-------------------------------
def save_outputs(role_count, location_count):
    role_count.to_csv("data/processed/role_distribution.csv")
    location_count.to_csv("data/processed/location_distribution.csv")


# MAIN PIPELINE
# -------------------------------
def main():
    df = load_data("data/processed/jobs_with_skills.csv")

    basic_info(df)

    role_count = role_analysis(df)
    location_count = location_analysis(df)
    experience_analysis(df)
    salary_analysis(df)
    remote_analysis(df)
    company_analysis(df)

    save_outputs(role_count, location_count)

    print("EDA pipeline executed successfully!")


# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    main()