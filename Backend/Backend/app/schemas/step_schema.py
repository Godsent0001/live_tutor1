# app/schemas/step_schema.py

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


# ----------------------------
# BOARD ELEMENTS
# ----------------------------
class BoardSchema(BaseModel):
    """
    What gets rendered on the "teaching board"
    (text, diagrams, ASCII visuals, structured notes)
    """

    title: Optional[str] = None

    content: Dict[str, Any] = Field(
        default_factory=dict
    )

    ascii_visual: Optional[str] = None

    diagrams: Optional[List[Dict[str, Any]]] = None


# ----------------------------
# QUESTION
# ----------------------------
class QuestionSchema(BaseModel):
    """
    Question shown at the end of a step.
    """

    question_text: str

    expected_answer: Optional[str] = None

    hints: Optional[List[str]] = None

    difficulty: Optional[str] = "medium"


# ----------------------------
# STEP CORE
# ----------------------------
class StepSchema(BaseModel):
    """
    One learning unit inside a lesson.
    """

    step_id: str

    module_title: Optional[str] = None

    # What teacher says (TTS + text display)
    speech: str

    # Visual board content
    board: BoardSchema

    # Question at end of step
    question: QuestionSchema

    # Used by AI evaluator / feedback system
    expected_concepts: List[str] = Field(
        default_factory=list
    )

    # Flow control
    is_last_step: bool = False


# ----------------------------
# STEP RESPONSE WRAPPER
# ----------------------------
class StepResponse(BaseModel):
    """
    What frontend receives when requesting a step.
    """

    success: bool

    message: str

    step: StepSchema


# ----------------------------
# STEP ADVANCE RESPONSE
# ----------------------------
class StepAdvanceResponse(BaseModel):
    """
    Returned after student answers and system moves forward.
    """

    success: bool

    message: str

    current_step: Optional[StepSchema] = None

    session_state: Dict[str, Any] = Field(
        default_factory=dict
    )