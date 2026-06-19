# app/routes/response.py

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.prompts.teacher_prompt import build_teacher_prompt
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService

from app.core.step_engine import StepEngine
from app.models.response import StudentResponse
from app.models.session import Session
from app.models.lesson import Lesson, LessonModule, LessonStep
from app.core.lesson_engine import LessonEngine

router = APIRouter()

llm = LLMService()
storage = StorageService()
step_engine = StepEngine()
lesson_engine = LessonEngine()


# ----------------------------
# REQUEST MODEL
# ----------------------------
class ResponseRequest(BaseModel):
    session_id: str
    lesson_id: str
    step_id: str
    student_answer: str


# ----------------------------
# SUBMIT RESPONSE (CORE LOOP)
# ----------------------------
@router.post("/submit")
async def submit_response(request: ResponseRequest):

    try:
        # 1. Load session
        session_data = storage.get_session(request.session_id)

        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        session = Session.from_dict(session_data)

        # 2. Get CURRENT STEP from Step Engine (REAL DATA)
        current_step_data = step_engine.get_current_step(
            request.session_id
        )

        if not current_step_data:
            raise HTTPException(
                status_code=404,
                detail="Step not found or lesson completed"
            )

        step = current_step_data["step"]

        # 3. Load lesson (for context richness)
        lesson = storage.get_lesson(request.lesson_id)

        if not lesson:
            raise HTTPException(
                status_code=404,
                detail="Lesson not found"
            )

        # 4. Build REAL teacher prompt (NO PLACEHOLDERS)
        prompt = build_teacher_prompt(
            lesson_title=lesson["topic"],
            current_module=current_step_data["module_title"],
            current_step=step,
            current_explanation=step["speech"],
            question_asked=step["question"],
            student_response=request.student_answer
        )

        # 5. Get AI response
        ai_response = await llm.generate_json(prompt)

        if not ai_response:
            raise HTTPException(
                status_code=500,
                detail="AI response failed"
            )

        # 6. Create response object
        response = StudentResponse.create(
            session_id=request.session_id,
            lesson_id=request.lesson_id,
            step_id=step["step_id"],
            student_answer=request.student_answer
        )

        response.attach_ai_response(
            teacher_response=ai_response["teacher_response"],
            board_update=ai_response["board_update"]
        )

        # 7. Save response
        storage.save_json(
            "responses",
            response.response_id,
            response.to_dict()
        )

        # 8. Add to session history
        session.add_history(response.to_dict())

        # 9. ADVANCE STEP (REAL FLOW CONTROL)
        updated_session = step_engine.advance_step(
            request.session_id
        )

        # 10. TRIGGER NEXT MODULE GENERATION IF NEEDED
        # When user reaches step 3 (index 2) of a module, generate the next one
        # but only if there are more sub-topics to cover.
        lesson_obj = Lesson.from_dict(lesson)
        current_module_idx = updated_session.get("current_module_index", 0)
        current_step_idx = updated_session.get("current_step_index", 0)

        # Check if we should trigger generation
        # We trigger when the user just advanced TO index 2 (the 3rd step)
        # and we haven't already started generating the next module.
        if current_step_idx == 2:
            num_modules_generated = len(lesson_obj.modules)
            num_subtopics = len(lesson_obj.sub_topics)

            # If there's a sub-topic that hasn't been turned into a module yet
            # AND we are currently in the LAST generated module
            if num_modules_generated < num_subtopics and current_module_idx == num_modules_generated - 1:
                # Generate the NEXT sub-topic (at index num_modules_generated)
                next_subtopic = lesson_obj.sub_topics[num_modules_generated]

                try:
                    module_data = await lesson_engine.generate_single_module(
                        lesson_title=lesson_obj.topic,
                        sub_topic=next_subtopic,
                        context_prompt=lesson_obj.context_prompt
                    )

                    if module_data and "steps" in module_data:
                        new_steps = [
                            LessonStep(
                                step_id=s.get("step_id", str(uuid.uuid4())),
                                speech=s.get("speech", ""),
                                board=s.get("board", {"type": "bullet", "content": []}),
                                question=s.get("question", {"type": "recall", "text": ""}),
                                expected_concepts=s.get("expected_concepts", [])
                            ) for s in module_data["steps"]
                        ]

                        lesson_obj.modules.append(
                            LessonModule(
                                module_title=module_data.get("module_title", next_subtopic),
                                steps=new_steps
                            )
                        )

                        # Save the updated lesson
                        storage.save_lesson(
                            lesson_obj.lesson_id,
                            lesson_obj.to_dict()
                        )
                except Exception as e:
                    # Log error but don't crash the main flow
                    print(f"Error generating next module: {e}")

        # 11. Save updated session
        storage.save_session(
            session.session_id,
            updated_session
        )

        # 12. Get NEXT STEP (optional but powerful UX)
        next_step = step_engine.get_current_step(
            request.session_id
        )

        return {
            "message": "Response processed successfully",

            "current_response": response.to_dict(),

            "current_step": current_step_data,

            "next_step": next_step,

            "session": updated_session
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )