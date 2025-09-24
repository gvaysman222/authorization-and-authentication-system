from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

def create_user(db: Session, *, first_name: str, last_name: str, patronymic: str, email: str, password: str) -> User:
    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        patronymic=patronymic.strip(),
        email=email.lower(),
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter_by(email=email.lower()).first()

def update_user_profile(db: Session, user: User, **fields) -> User:
    for k, v in fields.items():
        if v is None:
            continue
        if k == "password":
            user.password_hash = hash_password(v)
        elif hasattr(user, k):
            setattr(user, k, v.strip() if isinstance(v, str) else v)
    db.commit(); db.refresh(user)
    return user

def soft_delete_user(db: Session, user: User):
    from app.models.session import SessionToken
    user.is_active = False
    db.query(SessionToken).filter_by(user_id=user.id, is_active=True).update({"is_active": False})
    db.commit()
