from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.security import verify_password, issue_token_pair
from app.models.session import SessionToken
from app.models.user import User

def create_session(db: Session, user: User) -> SessionToken:
    token, expires_at = issue_token_pair()
    st = SessionToken(
        user_id=user.id,
        token=token,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        is_active=True,
    )
    db.add(st); db.commit(); db.refresh(st)
    return st

def login(db: Session, email: str, password: str) -> SessionToken | None:
    user = db.query(User).filter_by(email=email.lower()).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return create_session(db, user)

def logout_token(db: Session, raw_token: str):
    st = db.query(SessionToken).filter_by(token=raw_token, is_active=True).first()
    if st:
        st.is_active = False
        db.commit()
