from sqlalchemy.orm import Session
from app.models.rbac import Resource, Permission, Role, RolePermission, UserRole
from app.models.user import User

def ensure_resource(db: Session, code: str) -> Resource:
    code = code.strip().lower()
    res = db.query(Resource).filter_by(code=code).first()
    if res: return res
    res = Resource(code=code); db.add(res); db.commit(); db.refresh(res); return res

def create_permission(db: Session, resource_code: str, action: str) -> Permission:
    res = ensure_resource(db, resource_code)
    action = action.strip().lower()
    perm = db.query(Permission).filter_by(resource_id=res.id, action=action).first()
    if perm: return perm
    perm = Permission(resource_id=res.id, action=action)
    db.add(perm); db.commit(); db.refresh(perm); return perm

def create_role(db: Session, name: str) -> Role:
    name = name.strip().lower()
    role = db.query(Role).filter_by(name=name).first()
    if role: return role
    role = Role(name=name); db.add(role); db.commit(); db.refresh(role); return role

def attach_permission_to_role(db: Session, role_name: str, resource_code: str, action: str):
    role = create_role(db, role_name)
    perm = create_permission(db, resource_code, action)
    if not db.query(RolePermission).filter_by(role_id=role.id, permission_id=perm.id).first():
        db.add(RolePermission(role_id=role.id, permission_id=perm.id)); db.commit()

def attach_role_to_user(db: Session, user: User, role_name: str):
    role = create_role(db, role_name)
    if not db.query(UserRole).filter_by(user_id=user.id, role_id=role.id).first():
        db.add(UserRole(user_id=user.id, role_id=role.id)); db.commit()

def user_has_permission(db: Session, user: User, resource_code: str, action: str) -> bool:
    q = (
        db.query(RolePermission)
        .join(Role, RolePermission.role_id == Role.id)
        .join(UserRole, UserRole.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .join(Resource, Resource.id == Permission.resource_id)
        .filter(UserRole.user_id == user.id)
        .filter(Resource.code == resource_code)
        .filter(Permission.action == action)
    )
    return db.query(q.exists()).scalar()
