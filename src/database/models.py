from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime , ForeignKey , Index
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Float , Text
import uuid


class Base(DeclarativeBase):
    pass


# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship(
        "Resume",
        back_populates="user",
        lazy="joined")
    
    analyses = relationship(
        "Analysis",
        back_populates="user"
    )

    salary_predictions = relationship(
    "SalaryPrediction",
    back_populates="user"
    )

    job_fit_histories = relationship(
        "JobFitHistory",
        back_populates="user"
    )

# Resume Table
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    resume_name = Column(String(255))
    resume_path = Column(String(500))

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )

    analyses = relationship(
    "Analysis",
    back_populates="resume"
    )

    job_fit_histories = relationship(
        "JobFitHistory",
        back_populates="resume"
    )

# Analysis Table
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    ats_score = Column(Float)

    match_score = Column(Float)

    target_role = Column(String(255))

    analysis_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="analyses"
    )

    resume = relationship(
        'Resume',
        back_populates="analyses"
    )


# JOB FIT HISTORY TABLE
class JobFitHistory(Base):
    __tablename__ = "job_fit_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=True
    )

    best_role = Column(String(255))
    best_score = Column(Float)
    predictions_json = Column(Text)
    missing_skills = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="job_fit_histories"
    )

    resume = relationship(
        'Resume',
        back_populates="job_fit_histories"
    )


    # SALARY PREDICTION DATA TABLE
class SalaryPrediction(Base):
    __tablename__ = "salary_predictions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    role = Column(String(255))

    experience = Column(Float)

    location = Column(String(255))

    skills = Column(Text)

    predicted_salary = Column(Float)

    prediction_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="salary_predictions"
    )


class AIConversation(Base):

    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    question = Column(Text)

    response = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class AIChatSession(Base):

    __tablename__ = "ai_chat_sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    messages_json = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token_hash = Column(String(128), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    requested_ip = Column(String(64), nullable=True)

    user = relationship("User", backref="password_reset_tokens")

    __table_args__ = (
        Index("ix_prt_user_active", "user_id", "used_at"),
    )


