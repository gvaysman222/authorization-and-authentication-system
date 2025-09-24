from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.auth import RegisterIn, LoginIn, TokenOut
from app.schemas.user import UserOut
from app.services.user_service import create_user, get_user_by_email
from app.services.session_service import login as login_service, logout_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if data.password != data.password_repeat:
        raise HTTPException(400, "Пароли не совпадают")
    if get_user_by_email(db, data.email):
        raise HTTPException(400, "Email уже используется")
    user = create_user(db,
        first_name=data.first_name, last_name=data.last_name,
        patronymic=data.patronymic, email=str(data.email),
        password=data.password
    )
    return user

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    st = login_service(db, str(data.email), data.password)
    if not st:
        raise HTTPException(401, "Неверные учетные данные или пользователь деактивирован")
    return TokenOut(token=st.token, expires_at=st.expires_at)

@router.post("/logout")
def logout(db: Session = Depends(get_db), authorization: str | None = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Authorization header missing")
    token = authorization.split(" ", 1)[1].strip()
    logout_token(db, token)
    return {"detail": "ok"}
