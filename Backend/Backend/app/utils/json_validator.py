# app/utils/json_validator.py

import json
import re
from typing import Any, Dict


class JSONValidator:
    """
    Cleans and validates LLM JSON output.
    """

    # ----------------------------
    # EXTRACT JSON FROM TEXT
    # ----------------------------
    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """
        Extracts JSON even if wrapped in markdown or extra text.
        """

        if not text:
            raise ValueError("Empty LLM response")

        # Remove markdown code blocks
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)

        # Try direct parse
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try to extract first JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        raise ValueError("Invalid JSON from LLM")

    # ----------------------------
    # SAFE VALIDATION
    # ----------------------------
    @staticmethod
    def validate_keys(
        data: Dict[str, Any],
        required_keys: list
    ) -> bool:

        if not isinstance(data, dict):
            return False

        return all(
            key in data for key in required_keys
        )