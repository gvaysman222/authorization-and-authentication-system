from datetime import datetime, timezone
from typing import List
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, default="")
    last_name: Mapped[str] = mapped_column(String, default="")
    patronymic: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    roles: Mapped[List["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[List["SessionToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
