# app/models/response.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class StudentResponse:
    """
    MongoDB-ready student interaction model
    """

    _id: str = field(default_factory=lambda: str(uuid.uuid4()))

    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    session_id: str = ""
    lesson_id: str = ""
    step_id: str = ""

    student_answer: str = ""

    teacher_response: Optional[str] = None
    board_update: Optional[Dict[str, Any]] = None

    created_at: str = field(default_factory=lambda: str(datetime.utcnow()))

    # ----------------------------
    # CREATE NEW RESPONSE
    # ----------------------------
    @staticmethod
    def create(
        session_id: str,
        lesson_id: str,
        step_id: str,
        student_answer: str
    ) -> "StudentResponse":

        return StudentResponse(
            session_id=session_id,
            lesson_id=lesson_id,
            step_id=step_id,
            student_answer=student_answer
        )

    # ----------------------------
    # ATTACH AI OUTPUT
    # ----------------------------
    def attach_ai_response(
        self,
        teacher_response: str,
        board_update: Dict[str, Any]
    ) -> None:

        self.teacher_response = teacher_response
        self.board_update = board_update

    # ----------------------------
    # TO DICT (MONGO / JSON)
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:

        return {
            "_id": self._id,
            "response_id": self.response_id,

            "session_id": self.session_id,
            "lesson_id": self.lesson_id,
            "step_id": self.step_id,

            "student_answer": self.student_answer,

            "teacher_response": self.teacher_response,
            "board_update": self.board_update,

            "created_at": self.created_at
        }

    # ----------------------------
    # FROM DICT
    # ----------------------------
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StudentResponse":

        return StudentResponse(
            _id=data.get("_id", str(uuid.uuid4())),
            response_id=data.get("response_id", str(uuid.uuid4())),

            session_id=data.get("session_id", ""),
            lesson_id=data.get("lesson_id", ""),
            step_id=data.get("step_id", ""),

            student_answer=data.get("student_answer", ""),

            teacher_response=data.get("teacher_response"),
            board_update=data.get("board_update"),

            created_at=data.get("created_at", str(datetime.utcnow()))
        )