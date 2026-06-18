# app/schemas/user_schema.py

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


# ----------------------------
# USER CORE
# ----------------------------
class UserSchema(BaseModel):

    user_id: str

    name: str

    email: Optional[str] = None

    level: str = "beginner"

    total_sessions: int = 0

    completed_lessons: int = 0

    preferences: Dict[str, Any] = Field(
        default_factory=dict
    )

    session_ids: List[str] = Field(
        default_factory=list
    )

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ----------------------------
# CREATE USER REQUEST
# ----------------------------
class CreateUserRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: Optional[str] = None


# ----------------------------
# CREATE USER RESPONSE
# ----------------------------
class CreateUserResponse(BaseModel):

    success: bool

    message: str

    user: UserSchema


# ----------------------------
# GET USER RESPONSE
# ----------------------------
class GetUserResponse(BaseModel):

    success: bool

    message: str

    user: UserSchema