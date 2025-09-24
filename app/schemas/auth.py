from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    first_name: str = ""
    last_name: str = ""
    patronymic: str = ""
    email: EmailStr
    password: str = Field(min_length=6)
    password_repeat: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    token: str
    expires_at: datetime
