from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)

class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    action: Mapped[str] = mapped_column(String)
    __table_args__ = (UniqueConstraint("resource_id", "action", name="uq_perm_resource_action"),)
    resource: Mapped[Resource] = relationship()

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

class RolePermission(Base):
    __tablename__ = "role_permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"))
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_perm"),)
    role: Mapped[Role] = relationship()
    permission: Mapped[Permission] = relationship()

class UserRole(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)
    user: Mapped["User"] = relationship("User", back_populates="roles")
    role: Mapped[Role] = relationship()
