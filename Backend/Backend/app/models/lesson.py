# app/models/lesson.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class LessonStep:
    step_id: str
    speech: str
    board: Dict[str, Any]
    question: Dict[str, Any]
    expected_concepts: List[str]


@dataclass
class LessonModule:
    module_title: str
    steps: List[LessonStep]


@dataclass
class Lesson:
    """
    MongoDB-ready Lesson model
    (still works with JSON storage)
    """

    _id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Mongo-style ID

    lesson_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    topic: str = ""

    modules: List[LessonModule] = field(default_factory=list)

    created_at: str = field(default_factory=lambda: str(datetime.utcnow()))
    updated_at: str = field(default_factory=lambda: str(datetime.utcnow()))

    # ----------------------------
    # CREATE EMPTY LESSON
    # ----------------------------
    @staticmethod
    def create(topic: str, user_id: str = "") -> "Lesson":
        return Lesson(
            topic=topic,
            user_id=user_id
        )

    # ----------------------------
    # TO DICT (FOR JSON / MONGO)
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:

        return {
            "_id": self._id,
            "lesson_id": self.lesson_id,
            "user_id": self.user_id,
            "topic": self.topic,

            "modules": [
                {
                    "module_title": m.module_title,
                    "steps": [
                        {
                            "step_id": s.step_id,
                            "speech": s.speech,
                            "board": s.board,
                            "question": s.question,
                            "expected_concepts": s.expected_concepts
                        }
                        for s in m.steps
                    ]
                }
                for m in self.modules
            ],

            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    # ----------------------------
    # FROM DICT (MONGO OR JSON)
    # ----------------------------
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Lesson":

        modules = []

        for m in data.get("modules", []):

            steps = [
                LessonStep(
                    step_id=s.get("step_id", str(uuid.uuid4())),
                    speech=s.get("speech", ""),
                    board=s.get("board", {}),
                    question=s.get("question", {}),
                    expected_concepts=s.get("expected_concepts", [])
                )
                for s in m.get("steps", [])
            ]

            modules.append(
                LessonModule(
                    module_title=m.get("module_title", ""),
                    steps=steps
                )
            )

        return Lesson(
            _id=data.get("_id", str(uuid.uuid4())),
            lesson_id=data.get("lesson_id", str(uuid.uuid4())),
            user_id=data.get("user_id", ""),
            topic=data.get("topic", ""),
            modules=modules,
            created_at=data.get("created_at", str(datetime.utcnow())),
            updated_at=data.get("updated_at", str(datetime.utcnow()))
        )