from src.ATS.master_pipeline import analyze_resume
from src.config.paths import DATA_DIR

resume_file = DATA_DIR / "resume" / "Pratham_Resume_Updated.pdf"
resume_file2 = DATA_DIR / "resume" / "resume_5.pdf"
resume_file3 = DATA_DIR / "resume" / "resume_11.pdf"
resume_file4 = DATA_DIR / "resume" / "resume_8.pdf"

print('resume 1')
result = analyze_resume(resume_file , 'Data Analyst')
print(result)

print('resume 2')
result2 = analyze_resume(resume_file2 , 'Data Scientist')
print(result2)

print('resume 3')
result3 = analyze_resume(resume_file3 , 'Data Engineer')
print(result3)

print('resume 4')
result4 = analyze_resume(resume_file4 , 'Machine Learning Engineer')
print(result4)



