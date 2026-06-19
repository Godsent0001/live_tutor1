from typing import Dict, Any, List
import uuid
import json

from app.services.llm_service import LLMService
from app.prompts.lesson_generator_prompt import (
    build_lesson_prompt,
    build_subtopics_prompt,
    build_single_module_prompt
)


class LessonEngine:
    """
    Responsible for generating structured lessons.

    Responsibilities:
    - Convert topic → structured lesson JSON
    - Break content into steps
    - Ensure consistent format for runtime engine

    NOT responsible for:
    - Teaching behavior
    - Student interaction
    - Session tracking
    """

    def __init__(self):
        self.llm = LLMService()

    async def generate_sub_topics(
        self,
        topic: str,
        extra_materials: List[str] = None,
        context_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Generates a list of sub-topics for a topic.
        """
        prompt = build_subtopics_prompt(
            topic=topic,
            extra_materials=extra_materials or [],
            context_prompt=context_prompt
        )
        return await self.llm.generate_json(prompt)

    async def generate_single_module(
        self,
        lesson_title: str,
        sub_topic: str,
        context_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Generates a single module for a sub-topic.
        """
        prompt = build_single_module_prompt(
            lesson_title=lesson_title,
            sub_topic=sub_topic,
            context_prompt=context_prompt
        )
        raw_module = await self.llm.generate_json(prompt)
        return self._normalize_module(raw_module)

    def _normalize_module(self, raw_module: Dict[str, Any]) -> Dict[str, Any]:
        steps = raw_module.get("steps", [])
        cleaned_steps = []
        for step in steps:
            cleaned_steps.append({
                "step_id": step.get("step_id", str(uuid.uuid4())),
                "speech": step.get("speech", ""),
                "board": step.get("board", {
                    "type": "bullet",
                    "content": []
                }),
                "question": step.get("question", {
                    "type": "recall",
                    "text": ""
                }),
                "expected_concepts": step.get("expected_concepts", [])
            })
        return {
            "module_title": raw_module.get("module_title", "Untitled Module"),
            "steps": cleaned_steps
        }

    async def create_lesson(
        self,
        topic: str,
        user_id: str = "",
        extra_materials: List[str] = None
    ) -> Dict[str, Any]:

        lesson_id = str(uuid.uuid4())

        prompt = build_lesson_prompt(
            topic=topic,
            extra_materials=extra_materials or []
        )

        raw_response = await self.llm.generate_json(prompt)

        lesson = self._normalize_lesson(
            lesson_id=lesson_id,
            user_id=user_id,
            topic=topic,
            raw_lesson=raw_response
        )

        return lesson

    def _normalize_lesson(
        self,
        lesson_id: str,
        user_id: str,
        topic: str,
        raw_lesson: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ensures lesson format is consistent
        even if LLM output is slightly messy.
        """

        modules = raw_lesson.get("modules", [])

        cleaned_modules = []

        for module in modules:
            steps = module.get("steps", [])

            cleaned_steps = []

            for step in steps:
                cleaned_steps.append({
                    "step_id": step.get("step_id", str(uuid.uuid4())),
                    "speech": step.get("speech", ""),
                    "board": step.get("board", {
                        "type": "bullet",
                        "content": []
                    }),
                    "question": step.get("question", {
                        "type": "recall",
                        "text": ""
                    }),
                    "expected_concepts": step.get("expected_concepts", [])
                })

            cleaned_modules.append({
                "module_title": module.get("module_title", "Untitled Module"),
                "steps": cleaned_steps
            })

        return {
            "lesson_id": lesson_id,
            "user_id": user_id,
            "topic": topic,
            "modules": cleaned_modules
        }

    async def validate_lesson(self, lesson: Dict[str, Any]) -> bool:
        """
        Basic validation to ensure lesson integrity.
        """

        if not lesson.get("modules"):
            return False

        for module in lesson["modules"]:
            if not module.get("steps"):
                return False

            for step in module["steps"]:
                if not step.get("speech"):
                    return False

                if not step.get("question"):
                    return False

        return True

    def get_total_steps(self, lesson: Dict[str, Any]) -> int:
        """
        Counts total steps in a lesson.
        """

        total = 0

        for module in lesson.get("modules", []):
            total += len(module.get("steps", []))

        return total

    def flatten_steps(self, lesson: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Converts nested modules into linear steps
        for easy runtime progression.
        """

        steps = []

        for module in lesson.get("modules", []):
            for step in module.get("steps", []):
                steps.append({
                    **step,
                    "module_title": module.get("module_title")
                })

        return steps