# app/core/helpers.py

from typing import Any, Dict, List, Optional
import re
import uuid
from datetime import datetime


# ----------------------------
# ID GENERATION
# ----------------------------
def generate_id(prefix: str = "") -> str:
    return f"{prefix}_{uuid.uuid4().hex}" if prefix else str(uuid.uuid4())


# ----------------------------
# TIMESTAMP
# ----------------------------
def now() -> str:
    return str(datetime.utcnow())


# ----------------------------
# SAFE GET
# ----------------------------
def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


# ----------------------------
# CLEAN TEXT (for LLM outputs)
# ----------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


# ----------------------------
# CHECK EMPTY
# ----------------------------
def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}