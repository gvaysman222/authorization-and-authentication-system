from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import require_permission
from app.schemas.rbac import ResourceIn, PermissionIn, RoleIn, AttachPermissionIn, AttachRoleToUserIn
from app.services.rbac_service import (
    ensure_resource, create_permission, create_role,
    attach_permission_to_role, attach_role_to_user
)
from app.models.rbac import Resource, Permission, Role
from app.models.user import User

ADMIN_RESOURCE = "access_control"
ADMIN_ACTION = "manage"

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/resources")
def create_res(payload: ResourceIn, ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    if db.query(Resource).filter_by(code=payload.code.strip().lower()).first():
        raise HTTPException(400, "Resource уже существует")
    res = ensure_resource(db, payload.code)
    return {"id": res.id, "code": res.code}

@router.get("/resources")
def list_res(ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    return [{"id": r.id, "code": r.code} for r in db.query(Resource).all()]

@router.post("/permissions")
def create_perm(payload: PermissionIn, ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    perm = create_permission(db, payload.resource_code, payload.action)
    res = db.query(Resource).get(perm.resource_id)
    return {"id": perm.id, "resource": res.code if res else None, "action": perm.action}

@router.get("/permissions")
def list_perms(ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    rows = db.query(Permission).all()
    res_map = {r.id: r.code for r in db.query(Resource).all()}
    return [{"id": p.id, "resource": res_map.get(p.resource_id), "action": p.action} for p in rows]

@router.post("/roles")
def create_role_ep(payload: RoleIn, ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    role = create_role(db, payload.name)
    return {"id": role.id, "name": role.name}

@router.get("/roles")
def list_roles(ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    return [{"id": r.id, "name": r.name} for r in db.query(Role).all()]

@router.post("/role-permissions")
def attach_perm(payload: AttachPermissionIn, ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    attach_permission_to_role(db, payload.role_name, payload.resource_code, payload.action)
    return {"detail": "attached"}

@router.post("/user-roles")
def attach_role(payload: AttachRoleToUserIn, ctx=Depends(require_permission(ADMIN_RESOURCE, ADMIN_ACTION))):
    db: Session = ctx["db"]
    user: User | None = db.query(User).filter_by(email=str(payload.user_email).lower()).first()
    if not user:
        raise HTTPException(404, "User не найден")
    attach_role_to_user(db, user, payload.role_name)
    return {"detail": "attached"}
