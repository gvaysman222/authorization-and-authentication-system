from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.services.rbac_service import create_role, attach_permission_to_role, attach_role_to_user, create_permission, ensure_resource

ADMIN_RESOURCE = "access_control"
ADMIN_ACTION = "manage"

def run_seed(db: Session):
    # ресурс и право для админки
    ensure_resource(db, ADMIN_RESOURCE)
    create_permission(db, ADMIN_RESOURCE, ADMIN_ACTION)

    # роль admin + право manage
    create_role(db, "admin")
    attach_permission_to_role(db, "admin", ADMIN_RESOURCE, ADMIN_ACTION)

    # пользователь-админ
    admin = db.query(User).filter_by(email=settings.ADMIN_EMAIL.lower()).first()
    if not admin:
        admin = User(
            first_name="Admin", last_name="User", patronymic="",
            email=settings.ADMIN_EMAIL.lower(),
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            is_active=True,
        )
        db.add(admin); db.commit(); db.refresh(admin)

    # выдать роль admin
    attach_role_to_user(db, admin, "admin")
