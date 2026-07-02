import pandas as pd

from src.config.paths import DATA_DIR
from src.resume_matching.resume_parser import process_resume


# ----------------------------------------------
# CONFIG
# ----------------------------------------------
DATA_PATH = DATA_DIR / 'processed'

SKILL_BENCHMARK_FILE = DATA_PATH / 'top_skills_by_role.csv'

OUTPUT_PATH = DATA_PATH / "resume_match_results.csv"

RESUME_DATA_PATH = DATA_DIR / 'resume'

RESUME_1 = RESUME_DATA_PATH / 'Pratham_resume.pdf'




# ------------------------------------------------
# EXTRACT RESUME SKILLS
# ------------------------------------------------
def extract_resume_skill(path):
    result = process_resume(path)
    resume_skills = result['skills']
    resume_skills =list(set(resume_skills))
    return resume_skills


# -----------------------------------------------------
# EXTRACT BENCHMARK SKILLS
# -----------------------------------------------------
def load_benchmark():
    try:
        benchmark_df = pd.read_csv(SKILL_BENCHMARK_FILE)

    except FileNotFoundError:
        print('File Not Found')

    except Exception as e:
        print(f'File Loading Eroor : {e}')

    return benchmark_df


# -------------------------------------------------
# CALCULATE MATCH SCORE
# -------------------------------------------------
def get_role_skills(benchmark_df,target_role):
    target_role = (
    target_role
    .lower()
    .strip()
    )
    role_df = (
    benchmark_df[
        benchmark_df[
            "Standardized_Job_Title"
        ]
        .str.lower()
        .str.strip()
        == target_role
    ]
    )
    role_skills = role_df['Skill'].tolist()
    # normalize skills
    role_skills = [
        skill.lower().strip()
        for skill in role_skills
    ]

    return set(role_skills)
    

def calculate_match_score(resume_skills,role_skills):
    # converting skills lists into set
    resume_set = set(resume_skills)
    role_set = set(role_skills)

    # matched skills
    matched_skills = sorted(
    resume_set & role_set
    )

    #missing skills
    missing_skills = sorted(
    role_set - resume_set
    )

    # match score calculation
    if len(role_set) > 0:
        match_score = (
            len(matched_skills)
            / len(role_set)
            ) * 100
    else:
        match_score = 0

    match_score = round(match_score , 2)

    # result
    result = {

    "Match Score %": match_score,

    "Matched Skills": matched_skills,

    "Missing Skills": missing_skills,

    "Matched Skill Count": len(
        matched_skills
    ),

    "Missing Skill Count": len(
        missing_skills
    )
    }

    return result


# -----------------------------------------------
# SAVE RESULTS
# -----------------------------------------------
def save_results(result, target_role):
    final_result = {
        "Role": target_role,
        "Match Score %": result[
            "Match Score %"
        ],
        "Matched Skills": ", ".join(
            result[
                "Matched Skills"
            ]
        ),
        "Missing Skills": ", ".join(
            result[
                "Missing Skills"
            ]
        ),
        "Matched Skill Count": result[
            "Matched Skill Count"
        ],
        "Missing Skill Count": result[
            "Missing Skill Count"
        ]
        }

    # convert to dataframe
    result_df = pd.DataFrame(
        [final_result]
    )

    # save csv
    result_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nResults Saved Successfully!")


# -----------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------

def main():
    target_role = 'Data Analyst'
    resume_skills = extract_resume_skill(RESUME_1)

    benchmark_df = load_benchmark()

    role_skills = get_role_skills(benchmark_df, target_role)

    result = calculate_match_score(resume_skills,role_skills)

    save_results(result, target_role)

# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
def test_multiple_resumes(num_resumes=10, target_role="Data Analyst"):
    """
    Test match engine on multiple resumes and save results to CSV
    """
    benchmark_df = load_benchmark()
    role_skills = get_role_skills(benchmark_df, target_role)
    
    results_list = []
    
    for i in range(1, num_resumes + 1):
        resume_path = RESUME_DATA_PATH / f'resume_{i}.pdf'
        
        # Check if resume exists
        if not resume_path.exists():
            print(f"⚠️  Resume not found: {resume_path}")
            continue
        
        try:
            print(f"Processing resume_{i}.pdf...")
            
            # Extract skills from resume
            resume_skills = extract_resume_skill(resume_path)
            
            # Calculate match score
            result = calculate_match_score(resume_skills, role_skills)
            
            # Format result for CSV
            final_result = {
                "Resume": f"resume_{i}",
                "Role": target_role,
                "Match Score %": result["Match Score %"],
                "Matched Skills": ", ".join(result["Matched Skills"]),
                "Missing Skills": ", ".join(result["Missing Skills"]),
                "Matched Skill Count": result["Matched Skill Count"],
                "Missing Skill Count": result["Missing Skill Count"]
            }
            
            results_list.append(final_result)
            print(f"✓ Resume {i} processed - Match Score: {result['Match Score %']}%\n")
            
        except Exception as e:
            print(f"✗ Error processing resume_{i}.pdf: {e}\n")
            continue
    
    # Convert results to DataFrame
    if results_list:
        results_df = pd.DataFrame(results_list)
        
        # Save to CSV
        output_file = DATA_PATH / f'{target_role.lower().replace(" ", "_")}_batch_results.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*60}")
        print(f"✓ All results saved to: {output_file}")
        print(f"Total resumes processed: {len(results_list)}")
        print(f"{'='*60}\n")
        print(results_df)
        
        return results_df
    else:
        print("No resumes were processed successfully.")
        return None


if __name__ == "__main__":
    # Run batch testing on 10 resumes
    print("Starting batch resume testing...\n")
    test_multiple_resumes(num_resumes=10, target_role="Data Analyst")
    test_multiple_resumes(num_resumes=17, target_role="Data Scientist")






