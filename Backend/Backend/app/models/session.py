# app/models/session.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


@dataclass
class Session:
    """
    Represents an active learning session.

    This is the runtime brain of your tutor system.
    """

    _id: str = field(default_factory=lambda: str(uuid.uuid4()))

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    user_id: str = ""
    lesson_id: str = ""

    current_module_index: int = 0
    current_step_index: int = 0

    status: str = "active"  # active | paused | completed

    # Stores quick runtime context for AI
    context_memory: Dict[str, Any] = field(default_factory=dict)

    # Step history (lightweight tracking)
    step_history: List[Dict[str, Any]] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: str(datetime.utcnow()))
    updated_at: str = field(default_factory=lambda: str(datetime.utcnow()))

    # ----------------------------
    # CREATE SESSION
    # ----------------------------
    @staticmethod
    def create(user_id: str, lesson_id: str) -> "Session":

        return Session(
            user_id=user_id,
            lesson_id=lesson_id
        )

    # ----------------------------
    # ADVANCE STEP
    # ----------------------------
    def advance_step(self) -> None:
        self.current_step_index += 1
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # ADVANCE MODULE
    # ----------------------------
    def advance_module(self) -> None:
        self.current_module_index += 1
        self.current_step_index = 0
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # ADD HISTORY ENTRY
    # ----------------------------
    def add_history(self, entry: Dict[str, Any]) -> None:

        self.step_history.append(entry)
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # UPDATE CONTEXT MEMORY
    # ----------------------------
    def update_context(self, key: str, value: Any) -> None:

        self.context_memory[key] = value
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # TO DICT
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:

        return {
            "_id": self._id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,

            "current_module_index": self.current_module_index,
            "current_step_index": self.current_step_index,

            "status": self.status,

            "context_memory": self.context_memory,
            "step_history": self.step_history,

            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    # ----------------------------
    # FROM DICT
    # ----------------------------
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Session":

        return Session(
            _id=data.get("_id", str(uuid.uuid4())),
            session_id=data.get("session_id", str(uuid.uuid4())),
            user_id=data.get("user_id", ""),
            lesson_id=data.get("lesson_id", ""),

            current_module_index=data.get("current_module_index", 0),
            current_step_index=data.get("current_step_index", 0),

            status=data.get("status", "active"),

            context_memory=data.get("context_memory", {}),
            step_history=data.get("step_history", []),

            created_at=data.get("created_at", str(datetime.utcnow())),
            updated_at=data.get("updated_at", str(datetime.utcnow()))
        )