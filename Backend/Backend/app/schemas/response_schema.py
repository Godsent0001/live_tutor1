# app/schemas/response_schema.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


# ----------------------------
# SUBMIT RESPONSE REQUEST
# ----------------------------
class SubmitResponseRequest(BaseModel):

    session_id: str

    lesson_id: str

    step_id: str

    student_answer: str = Field(
        min_length=1,
        max_length=10000
    )


# ----------------------------
# STUDENT RESPONSE
# ----------------------------
class StudentResponseSchema(BaseModel):

    response_id: str

    session_id: str

    lesson_id: str

    step_id: str

    student_answer: str

    teacher_response: Optional[str] = None

    board_update: Optional[
        Dict[str, Any]
    ] = None

    created_at: Optional[str] = None


# ----------------------------
# SUBMIT RESPONSE RESPONSE
# ----------------------------
class SubmitResponseResult(BaseModel):

    success: bool

    message: str

    response: StudentResponseSchema