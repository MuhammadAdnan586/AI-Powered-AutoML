"""
Auth Service - Business Logic
Register, Login, Refresh Token, Logout
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.auth.models import User, RefreshToken
from app.auth.schemas import RegisterRequest, LoginRequest
from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_token_expiry,
)
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        """
        Register a new user.
        - Check email uniqueness
        - Hash password
        - Save to DB
        """
        # Check if email already exists
        existing = db.query(User).filter(User.email == data.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered. Please login.",
            )

        user = User(
            full_name=data.full_name,
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"New user registered: {user.email} (id={user.id})")
        return user

    @staticmethod
    def login(db: Session, data: LoginRequest) -> dict:
        """
        Authenticate user and return access + refresh tokens.
        """
        user = db.query(User).filter(User.email == data.email.lower()).first()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        # Create tokens
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        })
        refresh_token_str = create_refresh_token()

        # Store refresh token in DB
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=get_token_expiry(),
        )
        db.add(refresh_token)

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"User logged in: {user.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> dict:
        """
        Issue new access token using a valid refresh token.
        """
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
        ).first()

        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked refresh token",
            )

        # Check expiry
        if token_obj.expires_at < datetime.now(timezone.utc):
            token_obj.is_revoked = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired. Please login again.",
            )

        user = db.query(User).filter(User.id == token_obj.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found or inactive",
            )

        # Issue new access token
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        })

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def logout(db: Session, refresh_token: str) -> None:
        """Revoke refresh token on logout"""
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        if token_obj:
            token_obj.is_revoked = True
            db.commit()
