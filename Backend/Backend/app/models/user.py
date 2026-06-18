# app/models/user.py

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
import uuid


@dataclass
class User:
    """
    Represents a learner in the system.
    """

    _id: str = field(default_factory=lambda: str(uuid.uuid4()))

    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    name: str = ""
    email: str = ""

    level: str = "beginner"

    # Learning stats (optional but useful)
    total_sessions: int = 0
    completed_lessons: int = 0

    # Preferences for AI tutor style
    preferences: Dict[str, Any] = field(default_factory=dict)

    # Learning history references
    session_ids: List[str] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: str(datetime.utcnow()))
    updated_at: str = field(default_factory=lambda: str(datetime.utcnow()))

    # ----------------------------
    # CREATE USER
    # ----------------------------
    @staticmethod
    def create(
        name: str,
        email: str = ""
    ) -> "User":

        return User(
            name=name,
            email=email
        )

    # ----------------------------
    # ADD SESSION
    # ----------------------------
    def add_session(self, session_id: str) -> None:

        self.session_ids.append(session_id)
        self.total_sessions += 1
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # COMPLETE LESSON
    # ----------------------------
    def complete_lesson(self) -> None:

        self.completed_lessons += 1
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # UPDATE PREFERENCES
    # ----------------------------
    def update_preferences(self, key: str, value: Any) -> None:

        self.preferences[key] = value
        self.updated_at = str(datetime.utcnow())

    # ----------------------------
    # TO DICT
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:

        return {
            "_id": self._id,
            "user_id": self.user_id,

            "name": self.name,
            "email": self.email,

            "level": self.level,

            "total_sessions": self.total_sessions,
            "completed_lessons": self.completed_lessons,

            "preferences": self.preferences,
            "session_ids": self.session_ids,

            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    # ----------------------------
    # FROM DICT
    # ----------------------------
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":

        return User(
            _id=data.get("_id", str(uuid.uuid4())),
            user_id=data.get("user_id", str(uuid.uuid4())),

            name=data.get("name", ""),
            email=data.get("email", ""),

            level=data.get("level", "beginner"),

            total_sessions=data.get("total_sessions", 0),
            completed_lessons=data.get("completed_lessons", 0),

            preferences=data.get("preferences", {}),
            session_ids=data.get("session_ids", []),

            created_at=data.get("created_at", str(datetime.utcnow())),
            updated_at=data.get("updated_at", str(datetime.utcnow()))
        )