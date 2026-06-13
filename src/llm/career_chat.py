from src.llm.gemini_client import client
import time


def _format_history(conversation_history):
    if not conversation_history:
        return ""

    formatted_lines = []

    for item in conversation_history[-8:]:
        if isinstance(item, dict):
            role = item.get("role", "user")
            content = item.get("content", "")
        else:
            role = "user"
            content = str(item)

        if content:
            formatted_lines.append(f"{role.capitalize()}: {content}")

    return "\n".join(formatted_lines)


def ask_career_ai(question, conversation_history=None):

    prompt = f"""
    You are an expert career coach for data, tech, and job-seeking users.

    Help users with:
    - Career guidance
    - Interview preparation
    - Project ideas
    - Skill development
    - Learning roadmaps

    Answer style rules:
    - Be practical, specific, and concise.
    - Use clear bullet points when giving steps or advice.
    - If the question is vague, ask one short follow-up question at the end.
    - Keep the tone supportive and professional.

    Conversation History:
    {_format_history(conversation_history)}

    User Question:
    {question}

    Response format:
    - Direct answer first
    - Actionable next steps
    - Short follow-up or recommendation if useful
    """

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text

        except Exception as e:

            print(f"Attempt {attempt+1}: {e}")

            time.sleep(2)

    return (
        "AI service is temporarily unavailable. "
        "Please try again later."
    )