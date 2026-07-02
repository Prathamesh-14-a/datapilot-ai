from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = [
    ROOT / "src" / "ATS" / "ats_match.py",
    ROOT / "src" / "ATS" / "resume_parser.py",
    ROOT / "src" / "ATS" / "roadmap_generator.py",
    ROOT / "src" / "ATS" / "skill_recommender.py",
    ROOT / "src" / "llm" / "analyze_resume.py",
    ROOT / "src" / "llm" / "resume_feedback.py",
    ROOT / "src" / "processing" / "clean_jobs.py",
    ROOT / "src" / "processing" / "extract_skills.py",
    ROOT / "src" / "scraper" / "Salary_data_scrape.py",
    ROOT / "src" / "scraper" / "scrape_jobs.py",
]

PATTERN = re.compile(r"d:\\Startup|D:\\Startup|C:\\Users|/Users/|/home/|Tesseract-OCR")


def test_runtime_python_files_do_not_contain_hardcoded_repo_paths():
    offenders = []
    for path in RUNTIME_FILES:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if PATTERN.search(content):
            offenders.append(path.relative_to(ROOT).as_posix())

    assert not offenders, f"Hardcoded repo paths found in: {offenders}"
