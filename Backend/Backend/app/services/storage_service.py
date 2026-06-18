# app/services/storage_service.py

import os
import json
from typing import Dict, Any, List, Optional
from app.db.local_db import LocalDB
from app.config import settings


class StorageService:
    """
    Central storage abstraction layer.

    Responsibilities:
    - Save JSON data (lessons, sessions, users)
    - Read JSON data
    - Update records
    - Delete records
    - Abstract storage implementation (local now, DB later)

    NOT responsible for:
    - AI logic
    - File parsing
    - Business logic
    """

    def __init__(self, base_path: str = None):
        self.db = LocalDB(base_path or settings.STORAGE_PATH + "/db")

    # ----------------------------
    # GENERIC SAVE
    # ----------------------------
    def save_json(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Saves JSON data into a specific collection.
        """
        self.db.save(collection, document_id, data)
        return document_id

    # ----------------------------
    # GENERIC READ
    # ----------------------------
    def read_json(
        self,
        collection: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Reads JSON data from storage.
        """
        return self.db.get(collection, document_id)

    # ----------------------------
    # UPDATE JSON
    # ----------------------------
    def update_json(
        self,
        collection: str,
        document_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing JSON file.
        """
        data = self.read_json(collection, document_id)
        if not data:
            return None

        data.update(updates)
        self.save_json(collection, document_id, data)
        return data

    # ----------------------------
    # DELETE JSON
    # ----------------------------
    def delete_json(
        self,
        collection: str,
        document_id: str
    ) -> bool:
        """
        Deletes a JSON document.
        """
        return self.db.delete(collection, document_id)

    # ----------------------------
    # LIST FILES
    # ----------------------------
    def list_files(
        self,
        collection: str
    ) -> List[str]:
        """
        Lists all document IDs in a collection.
        """
        all_docs = self.db.list_all(collection)

        ids = []
        id_keys = {
            "users": "user_id",
            "lessons": "lesson_id",
            "sessions": "session_id",
            "responses": "response_id"
        }

        id_key = id_keys.get(collection, "id")

        for doc in all_docs:
            if id_key in doc:
                ids.append(doc[id_key])
            elif "id" in doc:
                ids.append(doc["id"])
            elif "_id" in doc:
                ids.append(doc["_id"])

        return ids

    # ----------------------------
    # LESSON HELPERS
    # ----------------------------
    def save_lesson(
        self,
        lesson_id: str,
        lesson_data: Dict[str, Any]
    ) -> str:
        return self.save_json(
            "lessons",
            lesson_id,
            lesson_data
        )

    def get_lesson(
        self,
        lesson_id: str
    ) -> Optional[Dict[str, Any]]:
        return self.read_json(
            "lessons",
            lesson_id
        )

    # ----------------------------
    # SESSION HELPERS
    # ----------------------------
    def save_session(
        self,
        session_id: str,
        session_data: Dict[str, Any]
    ) -> str:
        return self.save_json(
            "sessions",
            session_id,
            session_data
        )

    def get_session(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        return self.read_json(
            "sessions",
            session_id
        )

    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return self.update_json(
            "sessions",
            session_id,
            updates
        )

    # ----------------------------
    # USER HELPERS
    # ----------------------------
    def save_user(
        self,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> str:
        return self.save_json(
            "users",
            user_id,
            user_data
        )

    def get_user(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        return self.read_json(
            "users",
            user_id
        )