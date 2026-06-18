# app/routes/user.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.storage_service import StorageService
from app.models.user import User

router = APIRouter()
storage = StorageService()


# ----------------------------
# REQUEST MODELS
# ----------------------------
class CreateUserRequest(BaseModel):
    name: str
    email: str = ""


# ----------------------------
# CREATE USER
# ----------------------------
@router.post("/create")
def create_user(request: CreateUserRequest):

    try:
        user = User.create(
            name=request.name,
            email=request.email
        )

        storage.save_user(
            user.user_id,
            user.to_dict()
        )

        return {
            "message": "User created successfully",
            "user": user.to_dict()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------
# GET USER
# ----------------------------
@router.get("/{user_id}")
def get_user(user_id: str):

    user = storage.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user