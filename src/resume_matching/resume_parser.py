import pdfplumber
import re
from pathlib import Path
import logging
import pytesseract
from pdf2image import convert_from_path


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# -------------------------------
# TECHNICAL SKILL LISTS
# -------------------------------
TECHNICAL_SKILLS = [
    
    'python', 'r', 'sql', 
    'excel' 'microsoft excel',
    'power bi', 'tableau',

    'etl', 'spark', 'hadoop',
    'airflow', 'dbt',

    'machine learning',
    'tensorflow', 'pytorch', 'scikit-learn',
    'deep learning'

    'aws', 'azure', 'gcp', 'statistics'

    'pandas', 'numpy', 'matplotlib',
    'seaborn', 'plotly', 'ggplot2',

    ]


# ---------------------------------------------------
# SKILL ALIASES
# ---------------------------------------------------

ALIASES = {
    "powerbi": "power bi",
    "power-bi": "power bi",
    "machinelearning": "machine learning",
    "eda": "exploratory data analysis",
    "sklearn": "scikit-learn",
    "nlp": "natural language processing",
    "cnn": "convolutional neural networks",
    "rnn": "recurrent neural networks",
    "postgres": "postgresql" , 

}

# ---------------------------------------------------
# TESSERACT PATH (WINDOWS)
# ---------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ---------------------------------------
# RESUME TEXT CLEAN
# ---------------------------------------
def clean_resume_text(text:str) -> str:

    # lower case
    text =  text.lower()
     # normalize aliases before cleanup
    for alias, original in ALIASES.items():
        text = text.replace(alias, original)
    # extra spaces
    text = re.sub(r'\s+', ' ', text)
    # character symbols
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ' , text)
    # extra characters
    text = re.sub(r'[\r\n\xa0]+' , ' ' , text)
    # irrelavent numbers
    text = re.sub(r'\b\d+\b', '', text)
    # design symbols
    text = re.sub(r"[•★►▪]", " ", text)
    #extra spaces
    text = re.sub(r'\s+' ,' ' , text)

    return text.strip()


# ------------------------------------------
# EXTRACT TEXT THROUGH RESUME PDF 
# ------------------------------------------
def extract_resume_text(path:str) ->str:

    pages_text = []

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text :
                    pages_text.append(page_text)
                

        return  " ".join(pages_text)

    except Exception as e:
        logging.error(f'Error Reading Resume : {e}')
        return ""
    

# -----------------------------------------------
# OCR TEXT EXTRACTION
# -----------------------------------------------
def extract_with_ocr(path: str) -> str:

    extracted_text = []

    try:

        images = convert_from_path(
            path )

        for image in images:

            text = pytesseract.image_to_string(image)

            extracted_text.append(text)

        return " ".join(extracted_text)

    except Exception as e:

        print(f"OCR Error: {e}")

        return ""
    

# ------------------------------------------------
# TEXT VALIDATION
# ------------------------------------------------
def text_validation(text:str) -> bool:

    # if not a text
    if not text:
        return False

    # if length is minimun
    if len(text) < 100:
        return False
    
    # if words are limited 
    if len(text.split()) < 30:
        return False
    
    return True


# ----------------------------------------------
# EXTRACT SKILL FROM RESUME
# ----------------------------------------------
def extract_skills(resume_text: str, skills_list: list) -> list:

    resume_text = resume_text.lower()
    skill_set = set()

    for skill in skills_list:
        escape_skill = re.escape(skill.lower())
        pattern = rf'\b{escape_skill}\b'

        if re.search(pattern, resume_text):
            normalized_skill = ALIASES.get(skill.lower(), skill.lower())
            skill_set.add(normalized_skill)

    return sorted(skill_set)

# -------------------------------------------------
# RESUME PROCESS
# -------------------------------------------------
def process_resume(path:str) -> dict:


    
    # trying normal extraction
    resume_text = extract_resume_text(path)

    if not text_validation(resume_text):

        
        resume_text = extract_with_ocr(path)
    
    # clean text
    cleaned_text = clean_resume_text(resume_text)

    # Extract skills
    skills = extract_skills(cleaned_text, TECHNICAL_SKILLS)

    # validation
    if not cleaned_text:
        return {
            'status' : 'failed' ,
            'skills' : [] , 
            'resume_text' : ''
        }
    
     # determine extraction method
    extraction_method = (
        "ocr"
        if not text_validation(
            extract_resume_text(path)
        )
        else "pdfplumber"
    )

    return {
        'status' : 'successful' , 
        'skills' : skills , 
        'method' : extraction_method ,
        'resume_text' : resume_text[0:100] + '.......'
    }


# ------------------------------------------------
# TESTING
# ------------------------------------------------

if __name__ == "__main__":

    path = Path(r"d:\Startup\Project\ai-career-coach\data\resume\Pratham_resume.pdf")
    result = process_resume(path)
    print(result)

    # testing on 10 resumes
    for i in range(1 , 18):
        resume_paths = Path((rf"d:\Startup\Project\ai-career-coach\data\resume\resume_{i}.pdf"))
        result = process_resume(resume_paths)
        print(f'Resume Skill Extraction For Resume No. {i}')
        print(result)
