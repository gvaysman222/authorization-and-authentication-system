from pydantic import BaseModel, EmailStr

class ResourceIn(BaseModel):
    code: str

class PermissionIn(BaseModel):
    resource_code: str
    action: str

class RoleIn(BaseModel):
    name: str

class AttachPermissionIn(BaseModel):
    role_name: str
    resource_code: str
    action: str

class AttachRoleToUserIn(BaseModel):
    user_email: EmailStr
    role_name: str
