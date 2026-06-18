# app/schemas/session_schema.py

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


# ----------------------------
# SESSION CORE
# ----------------------------
class SessionSchema(BaseModel):

    session_id: str

    user_id: str
    lesson_id: str

    current_module_index: int = 0
    current_step_index: int = 0

    status: str = "active"  # active | paused | completed

    context_memory: Dict[str, Any] = Field(
        default_factory=dict
    )

    step_history: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ----------------------------
# START SESSION REQUEST
# ----------------------------
class StartSessionRequest(BaseModel):

    user_id: str

    lesson_id: str


# ----------------------------
# START SESSION RESPONSE
# ----------------------------
class StartSessionResponse(BaseModel):

    success: bool

    message: str

    session: SessionSchema


# ----------------------------
# NEXT STEP RESPONSE
# ----------------------------
class NextStepResponse(BaseModel):

    success: bool

    message: str

    session: SessionSchema


# ----------------------------
# SESSION ACTION RESPONSE
# (pause/resume/etc.)
# ----------------------------
class SessionActionResponse(BaseModel):

    success: bool

    message: str

    session: SessionSchema