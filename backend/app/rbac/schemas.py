from pydantic import BaseModel
from typing import Optional


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    user_id: int
    role_name: str


class PermissionCreate(BaseModel):
    role_id: int
    resource: str
    action: str


class PermissionResponse(BaseModel):
    id: int
    role_id: int
    resource: str
    action: str

    class Config:
        from_attributes = True
