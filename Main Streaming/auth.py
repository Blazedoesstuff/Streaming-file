from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_database
from models.users import User
from schemas.auth import RegisterRequest, LoginRequest
from security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
@router.post("/register")
def register(
    request: RegisterRequest,
    database: Session = Depends(get_database)
):

    existing_user = (
        database.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(
            request.password
        )
    )

    database.add(user)
    database.commit()

    return {
        "message": "Account created"
    }
@router.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    class LoginRequest(BaseModel):
        email: str
        password: str