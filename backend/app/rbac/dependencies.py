"""
RBAC Dependencies
Use these as FastAPI Depends() to enforce role/permission checks.

Usage:
    @router.delete("/model/{id}")
    def delete_model(
        id: int,
        current_user: User = Depends(require_role("admin")),
    ):
        ...

    @router.post("/train")
    def train(
        current_user: User = Depends(require_permission("models", "write")),
    ):
        ...
"""

from functools import lru_cache
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.rbac.models import UserRole, Role, Permission


def get_user_roles(user_id: int, db: Session) -> List[str]:
    rows = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return [r.name for r in rows]


def require_role(*roles: str):
    """
    FastAPI dependency factory – ensures user has at least one of the given roles.
    Example: Depends(require_role("admin", "analyst"))
    """
    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_roles = get_user_roles(current_user.id, db)
        if not any(r in user_roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}",
            )
        return current_user

    return dependency


def require_permission(resource: str, action: str):
    """
    FastAPI dependency factory – checks resource-level permission.
    Example: Depends(require_permission("models", "delete"))
    """
    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role_ids = (
            db.query(UserRole.role_id)
            .filter_by(user_id=current_user.id)
            .subquery()
        )
        has_perm = (
            db.query(Permission)
            .filter(
                Permission.role_id.in_(user_role_ids),
                Permission.resource == resource,
                Permission.action == action,
            )
            .first()
        )
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No permission to {action} on {resource}",
            )
        return current_user

    return dependency


def is_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    return require_role("admin")(db=db, current_user=current_user)
