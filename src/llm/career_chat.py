from src.llm.gemini_client import generate_response


def ask_career_ai(question):

    prompt = f"""
    You are an expert career coach.

    Help users with:
    - Career guidance
    - Interview preparation
    - Project ideas
    - Skill development
    - Learning roadmaps

    User Question:
    {question}
    """

    return generate_response(prompt)