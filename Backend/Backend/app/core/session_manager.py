from typing import Dict, Any, Optional, List
import uuid
import json
import os
from datetime import datetime


class SessionManager:
    """
    Handles lesson sessions for users.

    Responsibilities:
    - Create session when lesson starts
    - Track current step
    - Store interaction history
    - Resume sessions
    - Update progress

    NOT responsible for:
    - Generating lessons
    - AI responses
    - Evaluating answers
    """

    def __init__(self, storage_path: str = "app/storage/sessions"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    # ----------------------------
    # CREATE SESSION
    # ----------------------------
    def create_session(
        self,
        user_id: str,
        lesson_id: str,
        total_steps: int
    ) -> Dict[str, Any]:

        session_id = str(uuid.uuid4())

        session = {
            "session_id": session_id,
            "user_id": user_id,
            "lesson_id": lesson_id,

            "current_step": 0,
            "total_steps": total_steps,

            "status": "active",

            "history": [],

            "created_at": str(datetime.utcnow()),
            "updated_at": str(datetime.utcnow())
        }

        self._save_session(session)

        return session

    # ----------------------------
    # GET SESSION
    # ----------------------------
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:

        path = self._get_path(session_id)

        if not os.path.exists(path):
            return None

        with open(path, "r") as f:
            return json.load(f)

    # ----------------------------
    # UPDATE STEP
    # ----------------------------
    def update_step(
        self,
        session_id: str,
        step_index: int
    ) -> Dict[str, Any]:

        session = self.get_session(session_id)

        if not session:
            raise Exception("Session not found")

        session["current_step"] = step_index
        session["updated_at"] = str(datetime.utcnow())

        self._save_session(session)

        return session

    # ----------------------------
    # ADD INTERACTION
    # ----------------------------
    def add_interaction(
        self,
        session_id: str,
        interaction: Dict[str, Any]
    ) -> Dict[str, Any]:

        session = self.get_session(session_id)

        if not session:
            raise Exception("Session not found")

        entry = {
            "timestamp": str(datetime.utcnow()),
            "step": session["current_step"],
            "interaction": interaction
        }

        session["history"].append(entry)
        session["updated_at"] = str(datetime.utcnow())

        self._save_session(session)

        return session

    # ----------------------------
    # NEXT STEP
    # ----------------------------
    def increment_step(
        self,
        session_id: str
    ) -> Dict[str, Any]:

        session = self.get_session(session_id)

        if not session:
            raise Exception("Session not found")

        if session["current_step"] < session["total_steps"] - 1:
            session["current_step"] += 1

        session["updated_at"] = str(datetime.utcnow())

        self._save_session(session)

        return session

    # ----------------------------
    # GET CURRENT STEP
    # ----------------------------
    def get_current_step(self, session: Dict[str, Any]) -> int:
        return session.get("current_step", 0)

    # ----------------------------
    # RESUME SESSION
    # ----------------------------
    def resume_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns session state for continuing lesson
        """

        return self.get_session(session_id)

    # ----------------------------
    # END SESSION
    # ----------------------------
    def end_session(self, session_id: str) -> Dict[str, Any]:

        session = self.get_session(session_id)

        if not session:
            raise Exception("Session not found")

        session["status"] = "completed"
        session["updated_at"] = str(datetime.utcnow())

        self._save_session(session)

        return session

    # ----------------------------
    # INTERNAL HELPERS
    # ----------------------------
    def _save_session(self, session: Dict[str, Any]):

        path = self._get_path(session["session_id"])

        with open(path, "w") as f:
            json.dump(session, f, indent=4)

    def _get_path(self, session_id: str) -> str:
        return os.path.join(self.storage_path, f"{session_id}.json")