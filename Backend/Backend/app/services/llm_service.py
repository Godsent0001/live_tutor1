# app/services/llm_service.py

import os
import json
import asyncio
from typing import Optional, Dict, Any

import httpx


class LLMService:
    """
    Central LLM gateway.

    Responsibilities:
    - Send prompts to LLM
    - Handle retries
    - Parse JSON safely
    - Provide clean interface to core modules

    This is the ONLY place that talks to the AI provider.
    """

    def __init__(self):
        from app.config import settings
        self.api_key = settings.GEMINI_API_KEY
        # Gemini API URL structure:
        
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

        if not self.api_key:
            raise Exception("GEMINI_API_KEY not set in environment")

    # ----------------------------
    # RAW TEXT GENERATION
    # ----------------------------
    async def generate(self, prompt: str) -> str:
        """
        Returns raw text response from LLM (Gemini).
        """

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "text/plain",
                "maxOutputTokens": 8192
            }
        }

        response = await self._post(payload)

        # Gemini response structure extraction
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise Exception(f"Unexpected Gemini response structure: {response}")

    # ----------------------------
    # STRICT JSON GENERATION
    # ----------------------------
    async def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Forces LLM to return valid JSON.
        Includes retry logic for safety.
        """

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "application/json",
                "maxOutputTokens": 8192
            }
        }

        for attempt in range(3):
            try:
                response = await self._post(payload)
                raw = response["candidates"][0]["content"]["parts"][0]["text"]
                parsed = self._safe_json_parse(raw)

                if parsed:
                    return parsed

            except Exception as e:
                if attempt == 2:
                    raise Exception(f"LLM JSON generation failed: {str(e)}")

                await asyncio.sleep(0.5)

        return {}

    # ----------------------------
    # HTTP REQUEST HANDLER
    # ----------------------------
    async def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends request to LLM provider (Gemini).
        """

        headers = {
            "Content-Type": "application/json"
        }

        params = {
            "key": self.api_key
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                params=params,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(
                    f"LLM request failed (Status {response.status_code}): {response.text}"
                )

            return response.json()

    # ----------------------------
    # SAFE JSON PARSER
    # ----------------------------
    def _safe_json_parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extracts JSON even if model returns extra text.
        """

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON block
        try:
            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1:
                json_str = text[start:end + 1]
                return json.loads(json_str)

        except Exception:
            pass

        return None