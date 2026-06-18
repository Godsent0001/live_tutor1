# app/routes/module_qa.py
#
# Allows students to ask freeform questions after completing a module.
# The AI answers in context of that module's content.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.llm_service import LLMService
from app.services.storage_service import StorageService

router = APIRouter()
llm = LLMService()
storage = StorageService()


class ModuleQuestionRequest(BaseModel):
    session_id: str
    lesson_id: str
    module_index: int
    student_question: str


def _build_module_qa_prompt(
    lesson_title: str,
    module_title: str,
    module_steps_summary: str,
    student_question: str
) -> str:
    return f"""
You are a friendly tutor. A student just finished a module and has a follow-up question.
Answer it clearly and simply — as if explaining to a curious 14-year-old.

---

LESSON: {lesson_title}
MODULE: {module_title}

MODULE CONTENT SUMMARY:
{module_steps_summary}

STUDENT'S QUESTION:
{student_question}

---

RULES:
- Answer in 2–5 sentences MAX. Be concise.
- Use plain everyday language. No jargon.
- If helpful, use a short analogy or real-world example.
- Board should reinforce the answer visually (3–5 short items).

OUTPUT (strict JSON only, no markdown):

{{
  "answer": "Your clear, simple answer here.",
  "board_update": {{
    "type": "bullet",
    "content": [
      "key point 1",
      "key point 2",
      "key point 3"
    ]
  }}
}}
"""


@router.post("/ask")
async def ask_module_question(request: ModuleQuestionRequest):
    try:
        lesson_data = storage.get_lesson(request.lesson_id)
        if not lesson_data:
            raise HTTPException(status_code=404, detail="Lesson not found")

        modules = lesson_data.get("modules", [])
        if request.module_index >= len(modules):
            raise HTTPException(status_code=400, detail="Invalid module index")

        module = modules[request.module_index]
        module_title = module.get("module_title", "")

        # Build a short summary of the module's steps for context
        steps = module.get("steps", [])
        summary_lines = [
            f"- {s.get('speech', '')}" for s in steps if s.get("speech")
        ]
        module_summary = "\n".join(summary_lines) or "No content available."

        prompt = _build_module_qa_prompt(
            lesson_title=lesson_data.get("topic", ""),
            module_title=module_title,
            module_steps_summary=module_summary,
            student_question=request.student_question
        )

        ai_response = await llm.generate_json(prompt)

        if not ai_response:
            raise HTTPException(status_code=500, detail="AI response failed")

        return {
            "module_title": module_title,
            "student_question": request.student_question,
            "answer": ai_response.get("answer", ""),
            "board_update": ai_response.get("board_update", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
