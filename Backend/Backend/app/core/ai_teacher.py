# app/core/ai_teacher.py

from app.services.llm_service import LLMService
from app.prompts.teacher_prompt import build_teacher_prompt
from app.prompts.humanizer_prompt import build_humanizer_prompt


class AITeacher:
    """
    AI Teacher

    Responsible for:
    - Responding to student answers
    - Answering student questions
    - Explaining concepts
    - Humanizing LLM output for both speech and board

    Not responsible for:
    - Lesson progression
    - Session tracking
    - Database operations
    """

    def __init__(self):
        self.llm = LLMService()

    async def respond(
        self,
        lesson_title: str,
        current_module: str,
        current_step: str,
        current_explanation: str,
        question_asked: str,
        student_response: str
    ):
        """
        Generates teacher feedback after the student responds,
        then humanizes both the response text and board content.
        """

        # Step 1: Generate raw teacher response + board
        prompt = build_teacher_prompt(
            lesson_title=lesson_title,
            current_module=current_module,
            current_step=current_step,
            current_explanation=current_explanation,
            question_asked=question_asked,
            student_response=student_response
        )

        raw = await self.llm.generate_json(prompt)

        teacher_response = raw.get("teacher_response", "").strip()
        board_update = raw.get("board_update", {})
        board_type = board_update.get("type", "bullet")
        board_content = board_update.get("content", [])

        # Step 2: Humanize both speech and board
        humanized = await self._humanize(
            teacher_response=teacher_response,
            board_content=board_content,
            board_type=board_type
        )

        return {
            "teacher_response": humanized.get("teacher_response", teacher_response),
            "board_update": {
                "type": board_type,
                "content": humanized.get("board_content", board_content)
            }
        }

    async def answer_question(
        self,
        lesson_title: str,
        current_module: str,
        current_step: str,
        current_explanation: str,
        student_question: str
    ):
        """
        Handles when the student asks a question mid-lesson.
        Also humanizes the response.
        """

        prompt = f"""
You are an expert university tutor.

LESSON:
{lesson_title}

MODULE:
{current_module}

CURRENT STEP:
{current_step}

CURRENT EXPLANATION:
{current_explanation}

STUDENT QUESTION:
{student_question}

Instructions:
- Answer the student's question clearly.
- Be concise but educational.
- Use simple language.
- Give an example if useful.
- Do not continue the lesson.
- Only answer the question.

TEACHER RESPONSE:
"""

        response = await self.llm.generate(prompt)
        raw_response = response.strip()

        # Humanize the answer (no board for question answers)
        humanized = await self._humanize(
            teacher_response=raw_response,
            board_content=[],
            board_type="bullet"
        )

        return {
            "teacher_response": humanized.get("teacher_response", raw_response)
        }

    async def _humanize(
        self,
        teacher_response: str,
        board_content: list,
        board_type: str
    ) -> dict:
        """
        Post-processes LLM output to sound warm and human.
        Falls back to original content if humanizer fails.
        """
        try:
            prompt = build_humanizer_prompt(
                teacher_response=teacher_response,
                board_content=board_content,
                board_type=board_type
            )

            result = await self.llm.generate_json(prompt)

            # Validate output has expected keys
            if "teacher_response" in result:
                return result

        except Exception:
            pass  # Silently fall back to original

        # Fallback — return originals unchanged
        return {
            "teacher_response": teacher_response,
            "board_content": board_content
        }
