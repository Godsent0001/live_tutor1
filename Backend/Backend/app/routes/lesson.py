# app/routes/lesson.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.prompts.lesson_generator_prompt import build_lesson_prompt
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService
from app.models.lesson import Lesson

router = APIRouter()

llm = LLMService()
storage = StorageService()


# ----------------------------
# REQUEST MODEL
# ----------------------------
class LessonRequest(BaseModel):
    user_id: str
    topic: str
    extra_materials: Optional[List[str]] = None  # renamed from `materials` to match frontend
    context_prompt: Optional[str] = None          # new: user-supplied context


# ----------------------------
# CREATE LESSON
# ----------------------------
@router.post("/create")
async def create_lesson(request: LessonRequest):

    try:
        prompt = build_lesson_prompt(
            topic=request.topic,
            extra_materials=request.extra_materials,
            context_prompt=request.context_prompt
        )

        lesson_json = await llm.generate_json(prompt)

        if not lesson_json:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate lesson"
            )

        lesson = Lesson.from_dict(lesson_json)
        lesson.user_id = request.user_id
        lesson.topic = request.topic

        storage.save_lesson(
            lesson.lesson_id,
            lesson.to_dict()
        )

        return {
            "message": "Lesson created successfully",
            "lesson": lesson.to_dict()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------
# GET LESSON
# ----------------------------
@router.get("/{lesson_id}")
def get_lesson(lesson_id: str):

    lesson = storage.get_lesson(lesson_id)

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    return lesson
