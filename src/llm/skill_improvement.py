from src.llm.gemini_client import generate_response

def generate_skill_feedback(
       ats_result ,
       role
):
    prompt = f"""
    You are an experienced Data Science Career Coach.

    Target Role:
    {role}

    Strengths:
    {', '.join(ats_result['Matched'])}

    Missing Skills:
    {', '.join(ats_result['Missing'])}

    Provide:

    Skills Improvment Roadmap with all coverage of syllabus

    Keep the advice practical and actionable and precise.
    """
    response = generate_response(prompt)

    return response
