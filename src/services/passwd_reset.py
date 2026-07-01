# services/password_reset.py
import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.auth.password import hash_password
from src.database.db_connection import engine
from src.database.models import Base, PasswordResetToken, User

TOKEN_TTL_MINUTES = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "30"))


def _ensure_reset_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _hash_token(raw_token: str) -> str:
    # HMAC with a server secret so DB leak alone can't be used to forge
    secret = os.getenv("RESET_TOKEN_SECRET", "change-me").encode()
    return hmac.new(secret, raw_token.encode(), hashlib.sha256).hexdigest()


def create_reset_token(db: Session, user: User, requested_ip: str | None = None) -> str:
    _ensure_reset_tables()

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": datetime.utcnow()}, synchronize_session=False)

    raw_token = secrets.token_urlsafe(48)
    record = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
        requested_ip=requested_ip,
    )
    db.add(record)
    db.commit()
    return raw_token


def verify_reset_token(db: Session, raw_token: str) -> PasswordResetToken | None:
    _ensure_reset_tables()

    if not raw_token:
        return None
    token_hash = _hash_token(raw_token)
    rec = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()
    if not rec:
        return None
    if rec.used_at is not None:
        return None
    if rec.expires_at < datetime.utcnow():
        return None
    return rec


def consume_reset_token(db: Session, rec: PasswordResetToken, new_password: str) -> None:
    _ensure_reset_tables()

    user: User = rec.user
    user.password_hash = hash_password(new_password)
    rec.used_at = datetime.utcnow()
    db.add(user)
    db.add(rec)
    db.commit()
