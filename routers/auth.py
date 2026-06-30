"""
HireGenius AI — Authentication Router
=======================================
FastAPI endpoints for login, registration, and user management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse,
    UserResponse, UserUpdate
)
from services.auth_service import AuthService
from utils.security import get_current_user, require_admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with username and password.
    Returns JWT access token on success.
    """
    return AuthService.login(db, request)


@router.post("/register", response_model=UserResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Register a new user account. Admin access required.
    """
    return AuthService.register(db, request)


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    return AuthService.get_profile(current_user)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users. Admin access required.
    """
    return AuthService.get_all_users(db)


@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activate or deactivate a user account. Admin access required.
    """
    return AuthService.update_user_status(db, user_id, is_active)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint. JWT is stateless, so this is a client-side action.
    Returns success message for the client to clear the stored token.
    """
    return {"message": "Successfully logged out", "detail": "Clear the token on client side"}
