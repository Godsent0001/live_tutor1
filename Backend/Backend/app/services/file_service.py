# app/services/file_service.py

import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from typing import List, Dict, Any


class FileService:
    """
    Simple file handler for AI Tutor system.

    Responsibilities:
    - Save uploaded files
    - Return file metadata
    - Manage file paths
    - Delete files if needed

    NOT responsible for:
    - Reading file content
    - Parsing PDFs/DOCX
    - AI processing
    """

    def __init__(self, upload_dir: str = "app/storage/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    # ----------------------------
    # SAVE SINGLE FILE
    # ----------------------------
    async def save_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Saves uploaded file locally and returns metadata.
        """

        if not file.filename:
            raise ValueError("File must have a name")

        extension = Path(file.filename).suffix.lower()

        file_id = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(self.upload_dir, file_id)

        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "file_id": file_id,
            "original_name": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "size_bytes": len(content)
        }

    # ----------------------------
    # SAVE MULTIPLE FILES
    # ----------------------------
    async def save_multiple_files(
        self,
        files: List[UploadFile]
    ) -> List[Dict[str, Any]]:
        """
        Saves multiple uploaded files.
        """

        results = []

        for file in files:
            saved = await self.save_file(file)
            results.append(saved)

        return results

    # ----------------------------
    # GET FILE PATHS ONLY (FOR GEMINI)
    # ----------------------------
    def get_file_paths(
        self,
        files_metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extracts file paths for AI processing (Gemini input).
        """

        return [
            file["file_path"]
            for file in files_metadata
        ]

    # ----------------------------
    # DELETE FILE
    # ----------------------------
    def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file from storage.
        """

        if os.path.exists(file_path):
            os.remove(file_path)
            return True

        return False

    # ----------------------------
    # CHECK FILE EXISTS
    # ----------------------------
    def file_exists(self, file_path: str) -> bool:
        """
        Checks if file exists.
        """

        return os.path.exists(file_path)

    # ----------------------------
    # CLEAN UP ALL FILES (OPTIONAL)
    # ----------------------------
    def clear_uploads(self) -> None:
        """
        Deletes all uploaded files (use carefully).
        """

        for file_name in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, file_name)

            if os.path.isfile(file_path):
                os.remove(file_path)