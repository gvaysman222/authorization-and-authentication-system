from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str
    email: EmailStr
    is_active: bool
    class Config:
        from_attributes = True

class UpdateUserIn(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)
