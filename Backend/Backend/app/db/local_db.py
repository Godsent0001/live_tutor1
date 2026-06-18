# app/db/local_db.py

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class LocalDB:
    """
    Simple JSON-based storage.

    Collections:
    - users
    - lessons
    - sessions
    - responses
    """

    def __init__(self, base_path: str = "app/storage/db"):
        self.base_path = Path(base_path)

        self.collections = [
            "users",
            "lessons",
            "sessions",
            "responses"
        ]

        self._initialize()

    # ----------------------------
    # SETUP
    # ----------------------------
    def _initialize(self):

        self.base_path.mkdir(
            parents=True,
            exist_ok=True
        )

        for collection in self.collections:

            collection_file = (
                self.base_path / f"{collection}.json"
            )

            if not collection_file.exists():

                with open(
                    collection_file,
                    "w",
                    encoding="utf-8"
                ) as f:
                    json.dump({}, f)

    # ----------------------------
    # INTERNAL HELPERS
    # ----------------------------
    def _get_file(self, collection: str) -> Path:

        return self.base_path / f"{collection}.json"

    def _read_collection(
        self,
        collection: str
    ) -> Dict[str, Any]:

        file_path = self._get_file(collection)

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    def _write_collection(
        self,
        collection: str,
        data: Dict[str, Any]
    ) -> None:

        file_path = self._get_file(collection)

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ----------------------------
    # CREATE / UPDATE
    # ----------------------------
    def save(
        self,
        collection: str,
        document_id: str,
        document: Dict[str, Any]
    ) -> None:

        data = self._read_collection(collection)

        data[document_id] = document

        self._write_collection(
            collection,
            data
        )

    # ----------------------------
    # READ
    # ----------------------------
    def get(
        self,
        collection: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:

        data = self._read_collection(collection)

        return data.get(document_id)

    # ----------------------------
    # DELETE
    # ----------------------------
    def delete(
        self,
        collection: str,
        document_id: str
    ) -> bool:

        data = self._read_collection(collection)

        if document_id not in data:
            return False

        del data[document_id]

        self._write_collection(
            collection,
            data
        )

        return True

    # ----------------------------
    # LIST
    # ----------------------------
    def list_all(
        self,
        collection: str
    ) -> list:

        data = self._read_collection(collection)

        return list(data.values())