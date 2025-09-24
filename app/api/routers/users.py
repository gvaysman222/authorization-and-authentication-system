from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserOut, UpdateUserIn
from app.services.user_service import update_user_profile, soft_delete_user
from app.models.user import User

router = APIRouter(tags=["users"])

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@router.patch("/me", response_model=UserOut)
def update_me(payload: UpdateUserIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = update_user_profile(db, user,
        first_name=payload.first_name,
        last_name=payload.last_name,
        patronymic=payload.patronymic,
        password=payload.password
    )
    return user

@router.delete("/me")
def soft_delete_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    soft_delete_user(db, user)
    return {"detail": "account deactivated"}
