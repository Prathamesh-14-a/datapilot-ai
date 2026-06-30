# services/password_reset.py
import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.models import PasswordResetToken, User
# Reuse whatever password hashing your auth already uses:
from src.auth.password import hash_password  # <-- adjust import to your project

TOKEN_TTL_MINUTES = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "30"))

def _hash_token(raw_token: str) -> str:
    # HMAC with a server secret so DB leak alone can't be used to forge
    secret = os.getenv("RESET_TOKEN_SECRET", "change-me").encode()
    return hmac.new(secret, raw_token.encode(), hashlib.sha256).hexdigest()

def create_reset_token(db: Session, user: User, requested_ip: str | None = None) -> str:
    # Invalidate any existing unused tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": datetime.utcnow()})

    raw_token = secrets.token_urlsafe(48)
    record = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
        requested_ip=requested_ip,
    )
    db.add(record)
    db.commit()
    return raw_token  # return raw token only once; never store it

def verify_reset_token(db: Session, raw_token: str) -> PasswordResetToken | None:
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
    user: User = rec.user
    user.password_hash = hash_password(new_password)  # adjust field name to your User model
    rec.used_at = datetime.utcnow()
    db.add(user)
    db.add(rec)
    db.commit()
