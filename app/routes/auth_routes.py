from datetime import UTC, datetime

import bcrypt
from fastapi import APIRouter, HTTPException, status

from app.auth.security import create_access_token
from app.database.connection import database
from app.schemas.auth_schema import UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["Authentication"])
users_collection = database["users"]


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    user_data = {
        "username": user.username,
        "password": hashed_password,
        "created_at": datetime.now(UTC),
    }
    users_collection.insert_one(user_data)
    return {
        "message": "User registered successfully",
        "username": user.username,
    }


@router.post("/login")
def login_user(user: UserLogin):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user is None or not bcrypt.checkpw(
        user.password.encode("utf-8"),
        existing_user["password"].encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
