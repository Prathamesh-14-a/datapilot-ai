import streamlit as st
import json

from components.sidebar import show_sidebar
from src.auth.session_manager import is_authenticated
from src.database.crud import (
	get_ai_chat_sessions,
	save_ai_chat_session,
)
from src.llm.career_chat import ask_career_ai


st.set_page_config(
	page_title="AI Mentor",
	page_icon="🤖",
	layout="wide",
)


if not is_authenticated():
	st.warning("Please login first")
	st.stop()


show_sidebar()


PROMPT_BATCHES = [
	[
		"How can I become a Data Scientist?",
		"Is Data Analytics a good career in 2026?",
		"What skills do I need for a Data Engineer role?",
		"Should I learn Data Science or Data Analytics first?",
		"What is the career roadmap for Machine Learning Engineer?",
	],
	[
		"Create a 6-month Data Analyst roadmap",
		"What should I learn after Python and SQL?",
		"Build a roadmap for becoming a Data Scientist",
		"How can I learn Machine Learning from scratch?",
		"What projects should I build to get hired?",
	],
	[
		"Common Data Analyst interview questions",
		"SQL interview questions for freshers",
		"Python interview questions for Data Science",
		"How should I answer \"Tell me about yourself\"?",
		"Mock interview for Data Analyst role",
	],
	[
		"How can I improve my ATS score?",
		"What skills should I add to my resume?",
		"How should I describe my projects?",
		"What mistakes should I avoid in my resume?",
		"Review my resume for Data Analyst jobs",
	],
	[
		"What salary can I expect as a Data Analyst?",
		"Which data roles pay the most?",
		"How do I negotiate salary?",
		"What are the highest-paying skills in Data Science?",
		"Which companies hire freshers in Data Analytics?",
	],
	[
		"Suggest beginner Data Analytics projects",
		"Suggest intermediate Machine Learning projects",
		"How can I make my GitHub portfolio stand out?",
		"What projects should I add to my resume?",
		"Give me a real-world data science project idea",
	],
	[
		"Which data skills are most in demand?",
		"Is Power BI still worth learning?",
		"Should I learn Tableau or Power BI?",
		"What are the latest trends in AI and ML?",
		"Which tools are recruiters looking for?",
	],
]


def _load_chat_messages(chat_session):
	try:
		return json.loads(chat_session.messages_json)
	except Exception:
		return []


def _get_chat_title(messages, fallback_question=""):
	for message in messages:
		if message.get("role") == "user" and message.get("content"):
			return message["content"][:70]

	return fallback_question[:70]


def _ensure_state():
	if "mentor_messages" not in st.session_state:
		st.session_state["mentor_messages"] = []

	if "mentor_chat_session_id" not in st.session_state:
		st.session_state["mentor_chat_session_id"] = None

	if "mentor_prompt_batch" not in st.session_state:
		st.session_state["mentor_prompt_batch"] = 0

	if "mentor_pending_question" not in st.session_state:
		st.session_state["mentor_pending_question"] = None


def _load_recent_history():
	user_id = st.session_state.get("user_id")
	if not user_id:
		return []
	return get_ai_chat_sessions(user_id)[:12]


def _reset_chat():
	st.session_state["mentor_messages"] = []
	st.session_state["mentor_chat_session_id"] = None
	st.session_state["mentor_pending_question"] = None


def _rotate_prompt_batch():
	st.session_state["mentor_prompt_batch"] = (
		st.session_state["mentor_prompt_batch"] + 1
	) % len(PROMPT_BATCHES)


def _queue_question(question):
	st.session_state["mentor_pending_question"] = question


def _load_chat_session(chat_session):
	st.session_state["mentor_messages"] = _load_chat_messages(chat_session)
	st.session_state["mentor_chat_session_id"] = chat_session.id
	st.session_state["mentor_pending_question"] = None


def _save_current_chat(user_id, fallback_question):
	if not st.session_state["mentor_messages"]:
		return

	title = _get_chat_title(st.session_state["mentor_messages"], fallback_question)
	chat_session = save_ai_chat_session(
		user_id=user_id,
		title=title,
		messages=st.session_state["mentor_messages"],
		chat_session_id=st.session_state.get("mentor_chat_session_id"),
	)
	st.session_state["mentor_chat_session_id"] = chat_session.id


def _render_prompt_cards(prompts):
	rows = [prompts[i : i + 2] for i in range(0, len(prompts), 2)]
	for row_index, row in enumerate(rows):
		cols = st.columns(len(row))
		for col, prompt in zip(cols, row):
			with col:
				st.button(
					prompt,
					key=f"prompt_{st.session_state['mentor_prompt_batch']}_{row_index}_{prompt}",
					use_container_width=True,
					on_click=_queue_question,
					args=(prompt,),
				)


def _render_history_sidebar(conversations):
	with st.sidebar:
		st.markdown("## 💬 Chat History")
		st.caption("Open any previous chat in one click.")

		if st.button("➕ New Chat", use_container_width=True):
			_reset_chat()

		if not conversations:
			st.info("No previous chats yet.")
			return

		for chat_session in conversations:
			label = chat_session.title
			if len(label) > 70:
				label = f"{label[:70]}..."
			if st.button(
				label,
				key=f"history_{chat_session.id}",
				use_container_width=True,
			):
				_load_chat_session(chat_session)


def _render_messages():
	for message in st.session_state["mentor_messages"]:
		with st.chat_message(message["role"]):
			st.markdown(message["content"])


_ensure_state()

recent_history = _load_recent_history()
_render_history_sidebar(recent_history)


st.markdown(
	"""
	<style>
	.mentor-hero {
		background: linear-gradient(135deg, rgba(15,118,110,0.10), rgba(14,165,233,0.10));
		border: 1px solid rgba(148,163,184,0.25);
		border-radius: 22px;
		padding: 1.25rem 1.35rem;
		box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
		margin-bottom: 1rem;
	}
	.mentor-subtitle {
		color: #475569;
		line-height: 1.65;
		margin-bottom: 0;
	}
	</style>
	""",
	unsafe_allow_html=True,
)


st.title("🤖 AI Mentor")
st.markdown(
	'<div class="mentor-hero"><p class="mentor-subtitle" style = "color:#CEDCCA">Ask anything about careers, jobs, interviews, resumes, ' \
	'projects, salary, or learning paths. The chat keeps your conversation history and lets you reopen ' \
	'older chats in one click.</p></div>',
	unsafe_allow_html=True,
)


current_batch = PROMPT_BATCHES[st.session_state["mentor_prompt_batch"]]

st.markdown("### Suggested Questions")
st.caption("Click any prompt to start the chat. Use More prompts to see the next set of ideas.")

_render_prompt_cards(current_batch)

if st.button("More prompts", use_container_width=True):
	_rotate_prompt_batch()
	st.rerun()


st.divider()

if not st.session_state["mentor_messages"]:
	with st.chat_message("assistant"):
		st.markdown(
			"Hi, I am your AI Mentor. Ask a question about your career or job search, and I will reply one step at a time."
		)


_render_messages()


pending_question = st.session_state.get("mentor_pending_question")
user_input = st.chat_input("Ask a career or job question...")

question_to_answer = pending_question or user_input

if question_to_answer:
	st.session_state["mentor_pending_question"] = None

	st.session_state["mentor_messages"].append(
		{"role": "user", "content": question_to_answer}
	)

	with st.chat_message("user"):
		st.markdown(question_to_answer)

	with st.chat_message("assistant"):
		with st.spinner("Thinking..."):
			answer = ask_career_ai(
				question_to_answer,
				conversation_history=st.session_state["mentor_messages"],
			)

		st.markdown(answer)

	st.session_state["mentor_messages"].append(
		{"role": "assistant", "content": answer}
	)

	user_id = st.session_state.get("user_id")
	if user_id:
		_save_current_chat(user_id, question_to_answer)

