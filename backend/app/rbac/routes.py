"""
Module 4 – Role-Based Access Control Routes
Admin-only routes to manage roles and assign them to users.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.rbac.dependencies import is_admin
from app.rbac.models import Role, UserRole, Permission
from app.rbac.schemas import (
    RoleCreate,
    RoleResponse,
    AssignRoleRequest,
    PermissionCreate,
    PermissionResponse,
)
from app.users.models import User

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.post("/roles", response_model=RoleResponse)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(is_admin),
):
    role = Role(name=payload.name, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/roles", response_model=List[RoleResponse])
def list_roles(db: Session = Depends(get_db), _admin: User = Depends(is_admin)):
    return db.query(Role).all()


@router.post("/assign")
def assign_role(
    payload: AssignRoleRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(is_admin),
):
    role = db.query(Role).filter_by(name=payload.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    existing = db.query(UserRole).filter_by(
        user_id=payload.user_id, role_id=role.id
    ).first()
    if existing:
        return {"detail": "Role already assigned"}

    user_role = UserRole(user_id=payload.user_id, role_id=role.id)
    db.add(user_role)
    db.commit()
    return {"detail": f"Role '{payload.role_name}' assigned to user {payload.user_id}"}


@router.delete("/revoke")
def revoke_role(
    payload: AssignRoleRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(is_admin),
):
    role = db.query(Role).filter_by(name=payload.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.query(UserRole).filter_by(user_id=payload.user_id, role_id=role.id).delete()
    db.commit()
    return {"detail": "Role revoked"}


@router.post("/permissions", response_model=PermissionResponse)
def add_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(is_admin),
):
    perm = Permission(
        role_id=payload.role_id,
        resource=payload.resource,
        action=payload.action,
    )
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm
