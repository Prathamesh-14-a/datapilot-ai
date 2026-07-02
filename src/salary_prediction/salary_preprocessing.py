import pandas as pd

from src.config.paths import DATA_DIR

# Data for Salary Prediction Model was collected from different sources including scrapping full detailed
# data collection code is available on salary_data_collection.ipynb

#------------------------------------------------------
# PATH
#-----------------------------------------------------

DATA_PATH = DATA_DIR / 'Salary Prediction Data'

SALARY_DATA_FILE = DATA_PATH / 'salary_cleaned_data.csv'

OUTPUT_DATA = DATA_PATH / 'salary_preprocessed_data.csv'

#------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
def load_data():
    try:
        df = pd.read_csv(SALARY_DATA_FILE)

    except FileNotFoundError:
        print('File Not Found')

    except Exception as e:
        print(f'File Loading Eroor : {e}')

    return df

# ------------------------------------------------------
# DATA INSPECTION
# ------------------------------------------------------
def inspect_data(df):
    print(f'Shape: {df.shape}')
    print(f'5 Samples:\n {df.sample(5)}')
    print(f'Null Values : \n {df.isnull().sum()}')
    print(f'Duplicated Values : \n {df.duplicated().sum()}')
    

def distribution_check(df):
    print('Salary Distribution : ')
    print(df.groupby(
            "Standardized_Job_Title"
                    )["salary_avg"].describe())
    print('Experience Distribution : ')
    print(df.groupby(
            "Standardized_Job_Title"
                    )["Experience_Years"].describe())
    print('Role Distribution : ')
    print(df.Standardized_Job_Title.value_counts())
    print('Location Distribution : ')
    print(df.Location.value_counts().head(20))


#------------------------------------------------------
# PREPROCESSING
#------------------------------------------------------
def standardize_locations(df):
    location_mapping = {

        # NCR Region
        "Delhi": "Delhi NCR",
        "Noida": "Delhi NCR",
        "Gurgaon": "Gurugram",

        # Optional additional mappings
        "Bangalore": "Bengaluru",

    }

    df["Location"] = df["Location"].replace(location_mapping)

    return df


def remove_skills_nulls(df):
    df = df[df['Skills Required'].notnull()].copy()
    return df


def remove_salary_outliers(df, lower_q=0.01, upper_q=0.99):
    lower = df["salary_avg"].quantile(lower_q)
    upper = df["salary_avg"].quantile(upper_q)

    print(f"\nLower Salary Threshold: {lower}")
    print(f"Upper Salary Threshold: {upper}")

    filtered_df = df[
        (df["salary_avg"] >= lower) &
        (df["salary_avg"] <= upper)
    ].copy()

    print(f"\nRows Before: {len(df)}")
    print(f"Rows After: {len(filtered_df)}")
    print(f"Rows Removed: {len(df) - len(filtered_df)}")

    return filtered_df


def remove_duplicates(df):
    before = len(df)

    df = df.drop_duplicates().copy()

    after = len(df)

    print(f"\nDuplicates Removed: {before - after}")

    return df


def change_column_names(df):
    df = df.rename(columns={
        "Standardized_Job_Title": "Job_Title",
        "Experience_Years": "Experience",
        "salary_avg": "Salary",
        "Skills Required": "Skills" , 
    })

    return df


# ------------------------------------------------------
# SAVE OUTPUTS
# ------------------------------------------------------
def save_preprocessed_data(df):
    try:
        df.to_csv(OUTPUT_DATA, index=False)
        print(f"Preprocessed data saved to {OUTPUT_DATA}")
    except Exception as e:
        print(f"Error saving preprocessed data: {e}")

    
#------------------------------------------------------------
# MAIN PREPROCESSING PIPELINE
#-------------------------------------------------------------
def main():
    df = load_data()

    inspect_data(df)

    distribution_check(df)

    df = standardize_locations(df)

    df = remove_skills_nulls(df)

    df = remove_salary_outliers(df)

    df = remove_duplicates(df)

     # inspect after preprocessing
    print("\nAfter Preprocessing:")
    inspect_data(df)
    distribution_check(df)

    df = change_column_names(df)

    save_preprocessed_data(df)

   

# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    main()

