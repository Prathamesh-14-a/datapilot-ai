import pandas as pd

from src.config.paths import DATA_DIR

# -------------------------------------------
# DATA CONFIG 
# ------------------------------------------
DATA_PATH = DATA_DIR / 'processed'

BATCH_RESULT_DATA =  DATA_PATH / 'data_analyst_batch_results.csv'

OUTPUT_CAREER_INSIGHT = DATA_PATH / 'career_insight_output_df.csv'

CATEGORY_MAPPING = {
        "python": "Programming",
        "r": "Programming",
        "sql": "Database",
        "excel": "Spreadsheet",
        "power bi": "Visualization",
        "tableau": "Visualization",
        "dashboarding": "Visualization",
        "pandas": "Python Library",
        "numpy": "Python Library",
        "tensorflow": "Machine Learning",
        "pytorch": "Machine Learning",
        "nlm": "Machine Learning",
        "artificial intelligence": "Machine Learning",
        "statistics": "Statistics",
        "aws": "Cloud",
        "azure": "Cloud",
        "gcp": "Cloud",
        "snowflake": "Cloud",
        "big data": "Big Data",
        "spark": "Big Data",
        "dbt": "Data Engineering",
        "etl": "Data Engineering",
        "airflow": "Orchestration",
        "data preprocessing": "Data Engineering",
        "business analysis": "Business Analysis",
        "market research": "Business Analysis",
    }

# --------------------------------------------
# IMPORT DATA 
# --------------------------------------------
def data_import():
    try:
        match_df = pd.read_csv(BATCH_RESULT_DATA)
        return match_df

    except FileNotFoundError:
        print('File Not Found ... ')

    except Exception as e:
        print(f'File Loading Error {e}')

    return None

# --------------------------------------------------
# CANDIDATE PROFILE 
# --------------------------------------------------
def candidate_profile_extract(match_df):

    target_role = match_df.loc[0 , 'Role']
    match_score = match_df.loc[0 , 'Match Score %']
    matched_skills = match_df.loc[0 , 'Matched Skills']
    missing_skills = match_df.loc[0 , 'Missing Skills']
    matched_skills = [skill.strip() for skill in matched_skills.split(',')]
    missing_skills = [skill.strip() for skill in missing_skills.split(',')]

    candidate_profile = {

        "Role": target_role,

        "Match Score": match_score,

        "Matched Skills": matched_skills,

        "Missing Skills": missing_skills
    }

    return candidate_profile


# ----------------------------------------------------------
# MATCH SCORE INTERPRETATION
# ----------------------------------------------------------
# INTERPRET MATCH SCORE
def interpret_match_score(match_score):
   
    if match_score >= 80:

        return (

            "Your profile is strongly aligned "
            "with current market expectations "
            "for this role."
        )
    
    # MODERATELY ALIGNED
    elif match_score >= 60:

        return (

            "Your profile demonstrates "
            "moderate alignment with "
            "current market requirements."
        )

    # NEEDS UPSKILLING
    elif match_score >= 40:

        return (

            "Your profile shows partial "
            "alignment but requires "
            "additional upskilling."
        )
    
    # WEAK ALIGNMENT
    else:

        return (

            "Your current skill profile "
            "shows limited alignment "
            "with market expectations."
        )
    

# ====================================================
# IDENTIFY STRENGTH AREAS
# ====================================================

def identify_strength_areas( matched_skills):

    # EXTRACT CATEGORIES
    strength_categories = []

    for skill in matched_skills:
        normalized_skill = skill.lower().strip()
        category = CATEGORY_MAPPING.get(normalized_skill)
        if category:
            strength_categories.append(category)


    # REMOVE DUPLICATES
    strength_categories = sorted(set(strength_categories))

    # GENERATE DETAILED INSIGHTS

    # All three core competencies
    if (
        "Programming" in strength_categories
        and "Database" in strength_categories
        and "Visualization" in strength_categories
    ):
        return (
            "Exceptional well-rounded analytics profile with strong programming, "
            "database querying, and dashboard visualization capabilities. "
            "Positioned as a full-stack data professional ready for senior-level roles."
        )

    # Programming + Database + Cloud
    elif (
        "Programming" in strength_categories
        and "Database" in strength_categories
        and "Cloud" in strength_categories
    ):
        return (
            "Strong data engineering foundation with cloud expertise. "
            "Skilled in building scalable analytics solutions and modern data pipelines. "
            "Well-positioned for cloud data engineering roles."
        )

    # Programming + Database + Machine Learning
    elif (
        "Programming" in strength_categories
        and "Database" in strength_categories
        and "Machine Learning" in strength_categories
    ):
        return (
            "Advanced analytical skillset combining programming, database work, and ML. "
            "Capable of building predictive models and sophisticated analytics solutions. "
            "Ready for data science and advanced analytics roles."
        )

    # Programming + Database (core pair)
    elif (
        "Programming" in strength_categories
        and "Database" in strength_categories
    ):
        return (
            "Strong analytical and querying foundation. "
            "Excellent programmer with solid data management skills. "
            "Well-positioned for data analyst and junior data engineer roles."
        )

    # Programming + Visualization
    elif (
        "Programming" in strength_categories
        and "Visualization" in strength_categories
    ):
        return (
            "Strong technical foundation combining programming with visualization expertise. "
            "Capable of building automated analytics and interactive reporting solutions. "
            "Well-suited for analytics engineer and BI developer roles."
        )

    # Database + Visualization
    elif (
        "Database" in strength_categories
        and "Visualization" in strength_categories
    ):
        return (
            "Strong data querying and visualization capabilities. "
            "Excellent at transforming raw data into compelling dashboards and reports. "
            "Well-positioned for business intelligence and reporting roles."
        )

    # Programming + Cloud
    elif (
        "Programming" in strength_categories
        and "Cloud" in strength_categories
    ):
        return (
            "Strong programming skills combined with cloud platform expertise. "
            "Capable of deploying scalable analytics solutions on modern cloud infrastructure. "
            "Ready for cloud-based analytics development roles."
        )

    # Programming + Machine Learning
    elif (
        "Programming" in strength_categories
        and "Machine Learning" in strength_categories
    ):
        return (
            "Strong predictive modeling foundation anchored in solid programming. "
            "Capable of developing and deploying machine learning solutions. "
            "Well-positioned for data science and ML engineering roles."
        )

    # Just Programming
    elif "Programming" in strength_categories:
        return (
            "Strong programming skills provide excellent foundation for data roles. "
            "Ready to build specialized expertise in databases, analytics, or data science. "
            "Well-suited for entry to intermediate data engineering positions."
        )

    # Just Database
    elif "Database" in strength_categories:
        return (
            "Strong SQL and database querying skills. "
            "Excellent foundation for data analyst and BI roles. "
            "Consider adding Python or visualization skills for broader career options."
        )

    # Visualization + Cloud
    elif (
        "Visualization" in strength_categories
        and "Cloud" in strength_categories
    ):
        return (
            "Strong visualization and cloud platform expertise. "
            "Capable of building cloud-based BI solutions and dashboards. "
            "Well-positioned for cloud BI and analytics roles."
        )

    # Visualization + Machine Learning
    elif (
        "Visualization" in strength_categories
        and "Machine Learning" in strength_categories
    ):
        return (
            "Unique combination of visualization and ML skills. "
            "Excellent for communicating complex model results and building interpretable solutions. "
            "Well-positioned for ML explainability and analytics roles."
        )

    # Just Visualization
    elif "Visualization" in strength_categories:
        return (
            "Good visualization and dashboard design capabilities. "
            "Excellent at turning data into compelling stories and insights. "
            "Well-suited for BI developer and reporting analyst roles."
        )

    # Spreadsheet + Programming
    elif (
        "Spreadsheet" in strength_categories
        and "Programming" in strength_categories
    ):
        return (
            "Strong analytical skills spanning spreadsheet work and programming. "
            "Capable of automating analytics and scaling analysis workflows. "
            "Well-positioned for analytics and data engineering roles."
        )

    # Just Spreadsheet
    elif "Spreadsheet" in strength_categories:
        return (
            "Strong spreadsheet and data handling skills. "
            "Excellent foundation for tactical analysis and reporting. "
            "Consider adding SQL or Python to expand into broader data roles."
        )

    # Python Libraries with Programming
    elif (
        "Python Library" in strength_categories
        and "Programming" in strength_categories
    ):
        return (
            "Strong Python data tooling expertise for analysis and modeling. "
            "Capable of advanced data manipulation and statistical analysis. "
            "Well-positioned for data analyst and data science roles."
        )

    # Just Python Libraries
    elif "Python Library" in strength_categories:
        return (
            "Solid Python data tools foundation using pandas, numpy, and related libraries. "
            "Great for data processing and exploratory analysis. "
            "Consider adding SQL and visualization to build comprehensive analytics skills."
        )

    # Cloud expertise
    elif "Cloud" in strength_categories:
        return (
            "Familiar with cloud platforms for scalable analytics. "
            "Capable of working with modern cloud data infrastructure. "
            "Well-positioned for cloud analytics and data engineering roles."
        )

    # Big Data expertise
    elif "Big Data" in strength_categories:
        return (
            "Experience with large-scale data ecosystems and distributed computing. "
            "Capable of processing and analyzing massive datasets. "
            "Well-positioned for big data engineering and analytics roles."
        )

    # Machine Learning expertise
    elif "Machine Learning" in strength_categories:
        return (
            "Strong machine learning and AI capabilities. "
            "Experienced in building predictive models and intelligent systems. "
            "Well-positioned for data science and ML specialist roles."
        )

    # Statistics expertise
    elif "Statistics" in strength_categories:
        return (
            "Solid statistical foundations for rigorous data analysis and modeling. "
            "Excellent for hypothesis testing, forecasting, and statistical rigor. "
            "Well-positioned for analytics and data science roles."
        )

    # Data Engineering expertise
    elif "Data Engineering" in strength_categories:
        return (
            "Strong data engineering capabilities for building robust data systems. "
            "Capable of designing and implementing ETL pipelines. "
            "Well-positioned for data engineering and pipeline development roles."
        )

    # Orchestration expertise
    elif "Orchestration" in strength_categories:
        return (
            "Capable of managing complex data workflows and automation. "
            "Skilled in scheduling and orchestrating production data processes. "
            "Well-positioned for data engineering and workflow management roles."
        )

    # Business Analysis expertise
    elif "Business Analysis" in strength_categories:
        return (
            "Strong business acumen combined with data skills. "
            "Excellent at translating business needs into analytical solutions. "
            "Well-positioned for business analyst and analytics consultant roles."
        )

    # Default fallback
    else:
        return (
            "Demonstrates relevant technical foundations and "
            "is positioned to build further expertise in data analytics."
        )
    

# ====================================================
# IDENTIFY WEAKNESS AREAS
# ====================================================

def identify_weakness_areas( missing_skills):
    # CATEGORY INSIGHTS
    weakness_mapping  = {

    "Programming":
    "Limited programming skills reduce your ability to build automated analytics workflows and solve technical problems independently. "
    "This is a core gap for modern data roles.",

    "Statistics":
    "Insufficient statistical depth weakens your ability to validate models and interpret data with confidence. "
    "It can turn analysis into descriptive output rather than decision-ready insight.",

    "Machine Learning":
    "Weak machine learning exposure limits your ability to move into predictive analytics and intelligent systems development. "
    "It suggests gaps in model-building, evaluation, and deployment experience.",

    "Data Engineering":
    "Weak data engineering skills reduce readiness for real-world ETL pipelines and production data systems. "
    "This gap can hinder work with large-scale datasets and enterprise analytics environments.",

    "Database":
    "Insufficient database skills slow data extraction and querying work, undermining performance in analytics tasks. "
    "SQL and structured data capability are core requirements for most data roles.",

    "Visualization":
    "Limited visualization skills reduce the clarity and business impact of your analytical findings. "
    "This weakens your ability to communicate insights effectively to stakeholders.",

    "Business Analysis":
    "Limited business analysis exposure makes it harder to align technical work with business goals. "
    "This gap can leave insights lacking strategic context.",

    "Cloud":
    "Minimal cloud exposure lowers readiness for scalable, production-grade data environments. "
    "This gap makes it harder to adapt to modern cloud-native analytics workflows.",

    "Big Data":
    "Limited big data experience restricts your ability to work with high-volume distributed systems. "
    "It reduces preparedness for enterprise-scale analytics roles.",

    "Orchestration":
    "Weak orchestration skills make it harder to manage reliable data pipelines and workflow automation. "
    "This gap impacts production readiness and operational efficiency.",

    "Spreadsheet":
    "Limited spreadsheet skills reduce efficiency in quick business analysis and ad hoc reporting. "
    "Strong spreadsheet ability remains valuable for operational analytics across organizations.",

    "Python Library":
    "Insufficient experience with Python analytics libraries limits your ability to build efficient data workflows. "
    "It reduces productivity with standard tools like pandas, NumPy, and scikit-learn."

}

    # EXTRACT CATEGORIES
    weakness_categories = []

    # Handle both string and list inputs
    if isinstance(missing_skills, str):
        missing_skills = [skill.strip() for skill in missing_skills.split(',')]

    for skill in missing_skills:

        category = CATEGORY_MAPPING.get(skill.lower().strip())

        if category:

            weakness_categories.append(category)

    # REMOVE DUPLICATES

    weakness_categories = list(
        set(weakness_categories)
    )

    # GENERATE INSIGHTS

    weakness_insights = []

    for category in weakness_categories:

        insight = weakness_mapping.get(
            category
        )

        if insight:

            weakness_insights.append(
                insight
            )

    # FINAL OUTPUT

    if weakness_insights:

        return " ".join(weakness_insights)

    return (

        "The profile shows some missing "
        "technical capabilities that may "
        "affect market alignment."
    )


# --------------------------------------------------
# LEARNING INSIGHTS
# --------------------------------------------------
def learning_direction(missing_skills):

    learning_insight_mapping = {

        "Programming": (
            'Build a stronger programming foundation with regular coding practice and project work. '
            'This will improve your ability to automate analytics and solve technical problems independently.'
        ),

        "Statistics": (
            'Deepen your statistical understanding to interpret models and make data-driven decisions. '
            'Stronger statistics skills turn analysis into reliable insight instead of just reports.'
        ),

        "Machine Learning": (
            'Focus on practical ML skills like model training, evaluation, and deployment. '
            'Hands-on projects will help you move from reporting to predictive analytics and intelligent systems.'
        ),

        "Data Engineering": (
            'Learn ETL workflows, data pipelines, and scalable processing to work with production data systems. '
            'Improving these skills boosts readiness for enterprise analytics environments.'
        ),

        "Database": (
            'Strengthen SQL and database querying skills for efficient data extraction and transformation. '
            'Good database ability is essential for most analytics and BI roles.'
        ),

        "Visualization": (
            'Improve data storytelling and dashboard design to make insights clearer and more persuasive. '
            'Better visualization helps communicate results effectively to stakeholders.'
        ),

        "Business Analysis": (
            'Develop skills in business context, KPIs, and decision-making frameworks. '
            'This helps turn technical analysis into strategic, actionable recommendations.'
        ),

        "Cloud": (
            'Learn cloud platforms and their analytics workflows to support scalable, modern data systems. '
            'Cloud familiarity is increasingly necessary for production-grade analytics roles.'
        ),

        "Big Data": (
            'Explore big data tools and distributed processing to handle large-scale datasets. '
            'This prepares you for enterprise analytics where performance and scalability matter.'
        ),

        "Orchestration": (
            'Learn orchestration tools and workflow automation for reliable data pipelines. '
            'These skills are key to managing scalable production data operations.'
        ),

        "Spreadsheet": (
            'Build advanced spreadsheet proficiency for fast business analysis and reporting. '
            'Spreadsheets remain widely used for operational analytics and stakeholder collaboration.'
        ),

        "Python Library": (
            'Master core Python libraries like pandas, NumPy, and scikit-learn through practical use. '
            'This improves your productivity and effectiveness in real-world data workflows.'
        ),

    }

    # EXTRACT CATEGORIES
    learning_categories = []

    # Handle both string and list inputs
    if isinstance(missing_skills, str):
        missing_skills = [skill.strip() for skill in missing_skills.split(',')]

    for skill in missing_skills:

        category = CATEGORY_MAPPING.get(skill.lower().strip())

        if category:

            learning_categories.append(category)


     # REMOVE DUPLICATES

    learning_categories = list(
        set(learning_categories)
    )

    # GENERATE INSIGHTS

    learning_insights = []

    for category in learning_categories:

        insight = learning_insight_mapping.get(
            category
        )

        if insight:

            learning_insights.append(
                insight
            )

    # FINAL OUTPUT

    if learning_insights:

        return " ".join(learning_insights)

    return (

        """Your profile shows skill gaps in areas that are important 
        for building a well-rounded analytical and technical foundation. 
        Expanding your exposure to industry-relevant tools, technologies, 
        and problem-solving practices will improve your adaptability across 
        different data roles. Continuous learning and hands-on project experience are 
        essential for strengthening overall career readiness in evolving technology environments."""
    )

# --------------------------------------------------
# GENERATE CAREER INSIGHTS
# ---------------------------------------------------
def generate_career_insights(score_interpretation , strenght_insight , 
                             weakness_insight , learning_direction):
    final_insight = (

        f"{score_interpretation}\n\n"

        f"{strenght_insight}\n\n"

        f"{weakness_insight}\n\n"

        f"{learning_direction}"
    )

    return final_insight


# -------------------------------------------------------
# SAVE CAREER INSIGHT 
# -------------------------------------------------------

def save_career_insights(candidate_profile,
                         career_insight,):
    
    career_insight_output_df = pd.DataFrame([
        {
            "Role": candidate_profile["Role"],
            "Match Score": candidate_profile["Match Score"],
            "Matched Skills": ", ".join(
                candidate_profile["Matched Skills"]
            ),
            "Missing Skills": ", ".join(
                candidate_profile["Missing Skills"]
            ),
            "Career Insight": career_insight,
        }
    ])

    career_insight_output_df.to_csv(OUTPUT_CAREER_INSIGHT,
                                    index=False)
    
    print("\n Career Insight CSV Saved Sucessfully ....")


# ----------------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------------
def main():
    #Load DataSet
    match_df  = data_import()

    # Extract Profile
    candidate_profile = candidate_profile_extract(match_df)

    # Score Interpretation
    score_interpretation = interpret_match_score(
        candidate_profile['Match Score']
    )

    # Strenght Insight 
    strenght_insight = identify_strength_areas(
        candidate_profile['Matched Skills']
    )

    # Weakness Insight
    Weakness_insight = identify_weakness_areas(
        candidate_profile['Missing Skills']
    )

    # Learning Direction
    learning_direction_ = learning_direction(
        candidate_profile['Missing Skills']
    )

    # Career Insight
    career_insight = (
        generate_career_insights(
            score_interpretation , 
            strenght_insight , 
            Weakness_insight , 
            learning_direction_
        )
    ) 
    print('Career Insight')
    print(career_insight)

    # Save Output
    save_career_insights(candidate_profile,
                         career_insight)


# -------------------------------------------------
# RUN PIPELINE
# ------------------------------------------------
if __name__ == "__main__":
    main()
    
