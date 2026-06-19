# app/routes/lesson.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.prompts.lesson_generator_prompt import build_lesson_prompt
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService
from app.models.lesson import Lesson, LessonModule, LessonStep
from app.core.lesson_engine import LessonEngine

router = APIRouter()

llm = LLMService()
storage = StorageService()
lesson_engine = LessonEngine()


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
        # 1. Generate sub-topics list
        subtopics_data = await lesson_engine.generate_sub_topics(
            topic=request.topic,
            extra_materials=request.extra_materials,
            context_prompt=request.context_prompt
        )

        if not subtopics_data or "sub_topics" not in subtopics_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate sub-topics"
            )

        lesson_title = subtopics_data.get("lesson_title", request.topic)
        sub_topics = subtopics_data["sub_topics"]

        # 2. Create the Lesson object
        lesson = Lesson.create(topic=lesson_title, user_id=request.user_id)
        lesson.sub_topics = sub_topics
        lesson.context_prompt = request.context_prompt

        # 3. Generate first 2 modules
        for i in range(min(2, len(sub_topics))):
            try:
                module_data = await lesson_engine.generate_single_module(
                    lesson_title=lesson_title,
                    sub_topic=sub_topics[i],
                    context_prompt=request.context_prompt
                )

                if module_data and "steps" in module_data:
                    steps = [
                        LessonStep(
                            step_id=s.get("step_id", str(uuid.uuid4())),
                            speech=s.get("speech", ""),
                            board=s.get("board", {"type": "bullet", "content": []}),
                            question=s.get("question", {"type": "recall", "text": ""}),
                            expected_concepts=s.get("expected_concepts", [])
                        ) for s in module_data["steps"]
                    ]

                    lesson.modules.append(
                        LessonModule(
                            module_title=module_data.get("module_title", sub_topics[i]),
                            steps=steps
                        )
                    )
            except Exception as e:
                print(f"Error generating initial module {i}: {e}")

        if not lesson.modules:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any initial modules"
            )

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
