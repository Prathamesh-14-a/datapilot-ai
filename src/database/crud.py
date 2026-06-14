import json

from src.database.db_connection import SessionLocal, engine
from src.database.models import Base, SalaryPrediction, User, AIConversation, AIChatSession
from src.database.models import Resume
from sqlalchemy.orm import joinedload
from src.database.models import Analysis


#-------------------------------------------------------
# CREATE USER FUNCTION
#-------------------------------------------------------
def create_user(username, email, password_hash):
    session = SessionLocal()

    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


#----------------------------------------------------------
# GET USER BY EMAIL
#----------------------------------------------------------
def get_user_by_email(email):
    session = SessionLocal()

    try:
        user = session.query(User).filter(
            User.email == email
        ).first()

        return user
    
    finally:
        session.close()

    
#-------------------------------------------------------------------
# CREATE RESUME
#-----------------------------------------------------------
def save_resume(
        user_id, 
        resume_name , 
        resume_path
):
    session = SessionLocal()

    try:
        resume = Resume(
            user_id = user_id,
            resume_name = resume_name,
            resume_path = resume_path
        )

        session.add(resume)
        session.commit()

        return resume
    
    except Exception:
        session.rollback()
        raise

    
    finally:
        session.close()




#----------------------------------------------------------
# GET RESUMES BY USER ID
#----------------------------------------------------------
def get_user_resumes(user_id):

    session = SessionLocal()

    try:
        resumes = session.query(Resume).filter(
            Resume.user_id == user_id
        ).all()

        return resumes

    finally:
        session.close()



def get_user(user_id):
    session = SessionLocal()

    try:
        return (
            session.query(User)
            .options(joinedload(User.resumes))
            .filter(User.id == user_id)
            .first()
            )
    finally:
        session.close()


#------------------------------------------------
# SAVE ANALYSIS
#------------------------------------------------
def save_analysis(
    user_id,
    resume_id,
    ats_score,
    match_score,
    target_role
):
    session = SessionLocal()

    try:
        analysis = Analysis(
            user_id=user_id,
            resume_id=resume_id,
            ats_score=ats_score,
            match_score=match_score,
            target_role=target_role
        )

        session.add(analysis)
        session.commit()

        return analysis
    
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_analysis_history(user_id):
    session = SessionLocal()

    try:
        analyses = session.query(Analysis).filter(
            Analysis.user_id == user_id
        ).all()

        return analyses
    
    finally:
        session.close()


#------------------------------------------
# SAVE SALARY PREDICTION
#------------------------------------------
def save_salary_prediction(
    user_id,
    role,
    experience,
    location,
    skills,
    predicted_salary
):
    session = SessionLocal()

    try:
        salary_prediction = SalaryPrediction(
            user_id=user_id,
            role=role,
            experience=experience,
            location=location,
            skills=skills,
            predicted_salary=predicted_salary
        )

        session.add(salary_prediction)
        session.commit()

        return salary_prediction
    
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_prediction_history(user_id):
    session = SessionLocal()

    try:
        predictions = session.query(SalaryPrediction).filter(
            SalaryPrediction.user_id == user_id
        ).all()

        return predictions
    
    finally:
        session.close()

    
#------------------------------------------------
# SAVE AI CONVERSATION
#------------------------------------------------

_ai_chat_sessions_table_ready = False


def _ensure_ai_chat_sessions_table():
    global _ai_chat_sessions_table_ready

    if not _ai_chat_sessions_table_ready:
        Base.metadata.create_all(bind=engine)
        _ai_chat_sessions_table_ready = True

def save_ai_conversation(
    user_id,
    question,
    response
):
    session = SessionLocal()

    try:

        conversation = AIConversation(
            user_id=user_id,
            question=question,
            response=response
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def get_ai_conversation_history(
    user_id
):

    session = SessionLocal()

    try:

        conversations = (
            session.query(
                AIConversation
            )
            .filter(
                AIConversation.user_id == user_id
            )
            .order_by(
                AIConversation.created_at.desc()
            )
            .all()
        )

        return conversations

    finally:

        session.close()


def get_ai_conversation(conversation_id):

    session = SessionLocal()

    try:

        conversation = (
            session.query(AIConversation)
            .filter(
                AIConversation.id == conversation_id
            )
            .first()
        )

        return conversation

    finally:
        session.close()


def delete_ai_conversation(conversation_id):

    session = SessionLocal()

    try:

        conversation = (
            session.query(AIConversation)
            .filter(
                AIConversation.id == conversation_id
            )
            .first()
        )

        if conversation:
            session.delete(conversation)
            session.commit()

            return True

        return False

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def save_ai_chat_session(user_id, title, messages, chat_session_id=None):
    session = SessionLocal()

    try:
        _ensure_ai_chat_sessions_table()
        messages_json = json.dumps(messages)

        if chat_session_id:
            chat_session = (
                session.query(AIChatSession)
                .filter(AIChatSession.id == chat_session_id)
                .first()
            )

            if chat_session:
                chat_session.title = title
                chat_session.messages_json = messages_json
                session.commit()
                session.refresh(chat_session)
                return chat_session

        chat_session = AIChatSession(
            user_id=user_id,
            title=title,
            messages_json=messages_json,
        )

        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)

        return chat_session

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_ai_chat_sessions(user_id):
    session = SessionLocal()

    try:
        _ensure_ai_chat_sessions_table()
        return (
            session.query(AIChatSession)
            .filter(AIChatSession.user_id == user_id)
            .order_by(AIChatSession.updated_at.desc())
            .all()
        )

    finally:
        session.close()


def get_ai_chat_session(chat_session_id):
    session = SessionLocal()

    try:
        _ensure_ai_chat_sessions_table()
        return (
            session.query(AIChatSession)
            .filter(AIChatSession.id == chat_session_id)
            .first()
        )

    finally:
        session.close()

