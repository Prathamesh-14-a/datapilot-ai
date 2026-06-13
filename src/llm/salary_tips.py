from src.llm.gemini_client import generate_response

def generate_salary_tips(
       job_title,
       experience,
       location,
       skills,
       predicted_salary=None,
):
    prompt = f"""
       You are an expert Salary Growth and Career Negotiation Coach.

       Job Title:
       {job_title}

       Experience:
       {experience} years

       Location:
       {location}

       Skills:
       {skills}

       Current Salary (if known):
       {predicted_salary}

       Provide a concise but practical salary improvement guide with these sections:
       1. Why this profile can command more salary
       2. What skills or achievements to improve next
       3. How to position the profile in interviews and negotiations
       4. Company and market factors that may affect the offer
       5. 5 actionable tips to increase salary in the next 30 to 90 days

       Rules:
       - Be specific, practical, and realistic.
       - Mention that salary varies by company, market timing, interview performance, and negotiation.
       - Tailor advice to the provided experience level and skills.
       - Keep the response easy to read with short bullet points.

       Do not give generic motivational content.
    """
    response = generate_response(prompt)

    return response


def generate_skill_feedback(ats_result, role):
       return generate_salary_tips(
              job_title=role,
              experience="Unknown",
              location="Unknown",
              skills=", ".join(ats_result.get("Matched", [])),
              predicted_salary="Unknown",
       )
