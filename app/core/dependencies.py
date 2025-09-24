from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.session import SessionToken
from app.models.user import User
from app.services.rbac_service import user_has_permission
from datetime import datetime, timezone


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None)
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

    raw = authorization.split(" ", 1)[1].strip()
    session = db.query(SessionToken).filter_by(token=raw, is_active=True).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")

    # --- фикс naive/aware ---
    now_utc_naive = datetime.utcnow()  # naive UTC
    exp = session.expires_at
    if exp.tzinfo is not None:
        # приводим к naive UTC
        exp = exp.astimezone(timezone.utc).replace(tzinfo=None)
    if exp <= now_utc_naive:
        raise HTTPException(status_code=401, detail="Token expired")
    # -------------------------

    user = db.query(User).get(session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
    return user

def require_permission(resource_code: str, action: str):
    def wrapper(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if not user_has_permission(db, user, resource_code, action):
            raise HTTPException(status_code=403, detail="Forbidden")
        return {"user": user, "db": db}
    return wrapper
