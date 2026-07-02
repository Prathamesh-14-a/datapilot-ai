# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

import pandas as pd

from src.config.paths import DATA_DIR


# ============================================================
# PATHS
# ============================================================

DATA_PATH = DATA_DIR / 'processed'

MATCH_RESULTS_PATH = DATA_PATH / 'data_analyst_batch_results.csv'

BENCHMARK_PATH = DATA_PATH / 'top_skills_by_role.csv'

OUTPUT_PATH = DATA_PATH / "recommended_skills.csv"


# ============================================================
# SKILL CATEGORY MAPPING
# ============================================================

SKILL_CATEGORIES = {

    "sql": "Database",

    "python": "Programming",

    'r' : 'Programming' , 

    "power bi": "BI Tool",

    "tableau": "Visualization",

    "excel": "Spreadsheet",

    "statistics": "Mathematics",

    "machine learning": "AI/ML",

    "tensorflow": "Deep Learning",

    "pandas": "Python Library",

    "numpy": "Python Library"
}


# ============================================================
# LOAD MATCH RESULTS
# ============================================================

def load_match_results(path):

    match_df = pd.read_csv(path)

    return match_df


# ============================================================
# LOAD BENCHMARK DATA
# ============================================================

def load_benchmark_data(path):

    benchmark_df = pd.read_csv(path)

    # ------------------------------------------------
    # NORMALIZE COLUMNS
    # ------------------------------------------------

    benchmark_df[
        "Standardized_Job_Title"
    ] = (

        benchmark_df[
            "Standardized_Job_Title"
        ]

        .str.lower()
        .str.strip()
    )

    benchmark_df["Skill"] = (

        benchmark_df["Skill"]

        .str.lower()
        .str.strip()
    )

    return benchmark_df


# ============================================================
# EXTRACT TARGET ROLE
# ============================================================

def extract_target_role(match_df):

    target_role = (

        match_df.loc[
            0,
            "Role"
        ]

        .lower()
        .strip()
    )

    return target_role


# ============================================================
# EXTRACT MISSING SKILLS
# ============================================================

def extract_missing_skills(match_df):

    missing_skills_text = (

        match_df.loc[
            0,
            "Missing Skills"
        ]
    )

    missing_skills = [

        skill.lower().strip()

        for skill in

        missing_skills_text.split(",")
    ]

    return missing_skills


# ============================================================
# FILTER ROLE + MISSING SKILLS
# ============================================================

def filter_missing_skill_benchmark(

    benchmark_df,
    target_role,
    missing_skills
):

    filtered_df = benchmark_df[

        (
            benchmark_df[
                "Standardized_Job_Title"
            ] == target_role
        )

        &

        (
            benchmark_df["Skill"]

            .isin(missing_skills)
        )
    ]

    return filtered_df


# ============================================================
# PRIORITIZE MISSING SKILLS
# ============================================================

def prioritize_missing_skills(
    filtered_df
):

    prioritized_df = (

        filtered_df

        .sort_values(
            by="Count",
            ascending=False
        )

        .reset_index(drop=True)
    )

    return prioritized_df


# ============================================================
# ASSIGN PRIORITY LABELS
# ============================================================

def assign_priority_labels(
    prioritized_df
):

    def get_priority(count):

        if count >= 15:

            return "High"

        elif count >= 7:

            return "Medium"

        else:

            return "Low"

    prioritized_df["Priority"] = (

        prioritized_df["Count"]

        .apply(get_priority)
    )

    return prioritized_df


# ============================================================
# MAP SKILL CATEGORIES
# ============================================================

def map_skill_categories(
    recommendation_df
):

    recommendation_df["Category"] = (

        recommendation_df["Skill"]

        .map(SKILL_CATEGORIES)
    )

    return recommendation_df


# ============================================================
# GENERATE LEARNING ROADMAP
# ============================================================

def generate_learning_roadmap(
    recommendation_df
):

    roadmap = (

        recommendation_df["Skill"]

        .tolist()
    )

    return roadmap


# ============================================================
# SAVE RECOMMENDATIONS
# ============================================================

def save_recommendations(

    recommendation_df,
    output_path
):

    recommendation_df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nRecommendations Saved!"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    # ------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------

    match_df = load_match_results(
        MATCH_RESULTS_PATH
    )

    benchmark_df = load_benchmark_data(
        BENCHMARK_PATH
    )

    # ------------------------------------------------
    # EXTRACT ROLE
    # ------------------------------------------------

    target_role = extract_target_role(
        match_df
    )

    # ------------------------------------------------
    # EXTRACT MISSING SKILLS
    # ------------------------------------------------

    missing_skills = extract_missing_skills(
        match_df
    )

    print("\nMissing Skills:\n")

    print(missing_skills)

    # ------------------------------------------------
    # FILTER BENCHMARK
    # ------------------------------------------------

    filtered_df = (

        filter_missing_skill_benchmark(

            benchmark_df,
            target_role,
            missing_skills
        )
    )

    # ------------------------------------------------
    # PRIORITIZE SKILLS
    # ------------------------------------------------

    prioritized_df = (

        prioritize_missing_skills(
            filtered_df
        )
    )

    # ------------------------------------------------
    # ASSIGN PRIORITY LABELS
    # ------------------------------------------------

    recommendation_df = (

        assign_priority_labels(
            prioritized_df
        )
    )

    # ------------------------------------------------
    # MAP CATEGORIES
    # ------------------------------------------------

    recommendation_df = (

        map_skill_categories(
            recommendation_df
        )
    )

    # ------------------------------------------------
    # GENERATE ROADMAP
    # ------------------------------------------------

    roadmap = generate_learning_roadmap(
        recommendation_df
    )

    print(
        "\nRecommended Learning Path:\n"
    )

    for index, skill in enumerate(
        roadmap,
        start=1
    ):

        print(f"{index}. {skill}")

    # ------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------

    print(
        "\nFinal Recommendation Data:\n"
    )

    print(recommendation_df)

    # ------------------------------------------------
    # SAVE RESULTS
    # ------------------------------------------------

    save_recommendations(

        recommendation_df,
        OUTPUT_PATH
    )


# ============================================================
# RUN PIPELINE
# ============================================================

if __name__ == "__main__":

    main()

