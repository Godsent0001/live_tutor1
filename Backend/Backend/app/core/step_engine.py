# app/core/step_engine.py

from typing import Dict, Any, Optional

from app.services.storage_service import StorageService
from app.models.lesson import Lesson


class StepEngine:
    """
    Core runtime engine that controls lesson progression.

    This is the "brain" that decides:
    - what step the student is on
    - what to show next
    - when lesson is finished
    """

    def __init__(self):
        self.storage = StorageService()

    # ----------------------------
    # GET CURRENT STEP
    # ----------------------------
    def get_current_step(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:

        session = self.storage.get_session(session_id)

        if not session:
            return None

        lesson_data = self.storage.get_lesson(
            session["lesson_id"]
        )

        if not lesson_data:
            return None

        lesson = Lesson.from_dict(lesson_data)

        m_idx = session.get("current_module_index", 0)
        s_idx = session.get("current_step_index", 0)

        # Safety checks
        if m_idx >= len(lesson.modules):
            return None

        module = lesson.modules[m_idx]

        if s_idx >= len(module.steps):
            return None

        step = module.steps[s_idx]

        return {
            "session_id": session_id,
            "lesson_id": lesson.lesson_id,

            "module_index": m_idx,
            "step_index": s_idx,

            "module_title": module.module_title,

            "step": {
                "step_id": step.step_id,
                "speech": step.speech,
                "board": step.board,
                "question": step.question,
                "expected_concepts": step.expected_concepts
            },

            "is_last_step": self._is_last_step(
                lesson, m_idx, s_idx
            )
        }

    # ----------------------------
    # ADVANCE STEP LOGIC
    # ----------------------------
    def advance_step(
        self,
        session_id: str
    ) -> Dict[str, Any]:

        session = self.storage.get_session(session_id)

        if not session:
            return {"error": "Session not found"}

        lesson_data = self.storage.get_lesson(
            session["lesson_id"]
        )

        if not lesson_data:
            return {"error": "Lesson not found"}

        lesson = Lesson.from_dict(lesson_data)

        m_idx = session.get("current_module_index", 0)
        s_idx = session.get("current_step_index", 0)

        module = lesson.modules[m_idx]

        # Move step forward
        if s_idx + 1 < len(module.steps):
            session["current_step_index"] += 1

        else:
            # Move to next module
            if m_idx + 1 < len(lesson.modules):
                session["current_module_index"] += 1
                session["current_step_index"] = 0
            else:
                # Lesson complete
                session["status"] = "completed"

        self.storage.save_session(
            session["session_id"],
            session
        )

        return session

    # ----------------------------
    # CHECK IF LAST STEP
    # ----------------------------
    def _is_last_step(
        self,
        lesson: Lesson,
        m_idx: int,
        s_idx: int
    ) -> bool:

        if m_idx >= len(lesson.modules):
            return True

        module = lesson.modules[m_idx]

        is_last_module = (m_idx == len(lesson.modules) - 1)
        is_last_step = (s_idx == len(module.steps) - 1)

        return is_last_module and is_last_step