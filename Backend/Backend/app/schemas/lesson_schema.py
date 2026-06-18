# app/schemas/lesson_schema.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# ----------------------------
# STEP
# ----------------------------
class LessonStepSchema(BaseModel):
    step_id: str

    speech: str

    board: Dict[str, Any] = Field(
        default_factory=dict
    )

    question: Dict[str, Any] = Field(
        default_factory=dict
    )

    expected_concepts: List[str] = Field(
        default_factory=list
    )


# ----------------------------
# MODULE
# ----------------------------
class LessonModuleSchema(BaseModel):
    module_title: str

    steps: List[LessonStepSchema]


# ----------------------------
# LESSON
# ----------------------------
class LessonSchema(BaseModel):
    lesson_id: str
    user_id: str

    topic: str

    modules: List[LessonModuleSchema]

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ----------------------------
# CREATE LESSON REQUEST
# ----------------------------
class CreateLessonRequest(BaseModel):
    user_id: str
    topic: str = Field(
        min_length=2,
        max_length=500
    )

    materials: Optional[List[str]] = None


# ----------------------------
# CREATE LESSON RESPONSE
# ----------------------------
class CreateLessonResponse(BaseModel):
    success: bool
    message: str

    lesson: LessonSchema