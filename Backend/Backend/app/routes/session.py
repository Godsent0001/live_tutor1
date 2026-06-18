# app/routes/session.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.storage_service import StorageService
from app.models.session import Session
from app.core.step_engine import StepEngine

router = APIRouter()
storage = StorageService()
step_engine = StepEngine()


# ----------------------------
# REQUEST MODELS
# ----------------------------
class StartSessionRequest(BaseModel):
    user_id: str
    lesson_id: str


# ----------------------------
# START SESSION
# ----------------------------
@router.post("/start")
def start_session(request: StartSessionRequest):

    try:
        session = Session.create(
            user_id=request.user_id,
            lesson_id=request.lesson_id
        )

        storage.save_session(
            session.session_id,
            session.to_dict()
        )

        return {
            "message": "Session started",
            "session": session.to_dict()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------
# GET SESSION
# ----------------------------
@router.get("/{session_id}")
def get_session(session_id: str):

    session = storage.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session


# ----------------------------
# ADVANCE STEP (CORE TUTOR FLOW)
# ----------------------------
@router.post("/{session_id}/next-step")
def next_step(session_id: str):

    try:
        updated_session = step_engine.advance_step(session_id)

        if "error" in updated_session:
            raise HTTPException(
                status_code=404,
                detail=updated_session["error"]
            )

        return {
            "message": "Moved to next step",
            "session": updated_session
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------
# CURRENT STEP
# ----------------------------
@router.get("/{session_id}/current-step")
def get_current_step(session_id: str):

    try:
        current_step = step_engine.get_current_step(session_id)

        if not current_step:
            raise HTTPException(
                status_code=404,
                detail="Session not found or lesson completed"
            )

        return current_step

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------
# PAUSE SESSION
# ----------------------------
@router.post("/{session_id}/pause")
def pause_session(session_id: str):

    session_data = storage.get_session(session_id)

    if not session_data:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session = Session.from_dict(session_data)

    session.status = "paused"

    storage.save_session(
        session.session_id,
        session.to_dict()
    )

    return {
        "message": "Session paused",
        "session": session.to_dict()
    }


# ----------------------------
# RESUME SESSION
# ----------------------------
@router.post("/{session_id}/resume")
def resume_session(session_id: str):

    session_data = storage.get_session(session_id)

    if not session_data:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session = Session.from_dict(session_data)

    session.status = "active"

    storage.save_session(
        session.session_id,
        session.to_dict()
    )

    return {
        "message": "Session resumed",
        "session": session.to_dict()
    }