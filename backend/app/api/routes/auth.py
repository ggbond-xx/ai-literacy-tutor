from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db import mysql as mysql_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.auth import LoginRequest, TokenResponse, UserCreateRequest, UserProfileUpdateRequest, UserResponse
from app.services.json_store import create_user as create_json_user
from app.services.json_store import get_user_by_username
from app.services.json_store import update_user_profile as update_json_user_profile

router = APIRouter()


def _serialize_user(user: User | dict) -> dict:
    if isinstance(user, dict):
        profile = user.get("profile") or None
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "student"),
            "class_id": user.get("class_id"),
            "profile": profile,
        }

    return UserResponse.model_validate(user).model_dump()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreateRequest, db: Session = Depends(mysql_db.get_db)) -> User | dict:
    if mysql_db.database_mode != "json-fallback":
        existing_user = db.query(User).filter(User.username == payload.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")

        user = User(
            username=payload.username,
            password_hash=get_password_hash(payload.password),
            role=payload.role,
            class_id=payload.class_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        if payload.profile is not None:
            profile = UserProfile(user_id=user.id, **payload.profile.model_dump())
            db.add(profile)
            db.commit()
        return db.query(User).options(selectinload(User.profile)).filter(User.id == user.id).first()

    try:
        return create_json_user(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(mysql_db.get_db)) -> TokenResponse:
    if mysql_db.database_mode != "json-fallback":
        user = db.query(User).options(selectinload(User.profile)).filter(User.username == payload.username).first()
        password_hash = user.password_hash if user else ""
    else:
        user = get_user_by_username(payload.username)
        password_hash = user["password_hash"] if user else ""
    if not user or not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    access_token = create_access_token(
        subject=str(user["id"] if isinstance(user, dict) else user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={
            "role": user["role"] if isinstance(user, dict) else user.role,
            "username": user["username"] if isinstance(user, dict) else user.username,
        },
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=_serialize_user(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User | dict = Depends(get_current_user)) -> dict:
    return _serialize_user(user)


@router.put("/me/profile", response_model=UserResponse)
def update_profile(
    payload: UserProfileUpdateRequest,
    user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
) -> dict:
    profile_data = payload.model_dump()
    user_id = user["id"] if isinstance(user, dict) else user.id

    if mysql_db.database_mode == "json-fallback":
        try:
            updated_user = update_json_user_profile(user_id, profile_data)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return _serialize_user(updated_user)

    db_user = db.query(User).options(selectinload(User.profile)).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if db_user.profile is None:
        db_user.profile = UserProfile(**profile_data)
    else:
        for field_name, field_value in profile_data.items():
            setattr(db_user.profile, field_name, field_value)

    db.add(db_user)
    db.commit()
    refreshed_user = db.query(User).options(selectinload(User.profile)).filter(User.id == user_id).first()
    return _serialize_user(refreshed_user)
