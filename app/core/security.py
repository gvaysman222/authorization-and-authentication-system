import secrets, uuid
from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt
from app.core.config import settings

def hash_password(p: str) -> str:
    return bcrypt.hash(p)

def verify_password(p: str, h: str) -> bool:
    return bcrypt.verify(p, h)

def issue_token_pair() -> tuple[str, datetime]:
    token = f"{uuid.uuid4()}.{secrets.token_hex(16)}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.TOKEN_TTL_HOURS)
    return token, expires_at
