# app/services/tts_service.py

import os
import uuid
from typing import Optional

import httpx


class TTSService:
    """
    Text-to-Speech service.

    Responsibilities:
    - Convert text → audio
    - Save audio files locally
    - Return file path for playback
    - Allow future provider swapping

    NOT responsible for:
    - AI generation
    - Lesson logic
    - Session management
    """

    def __init__(
        self,
        output_dir: str = "app/storage/tts",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.output_dir = output_dir
        self.api_key = api_key or os.getenv("TTS_API_KEY")
        self.base_url = base_url or os.getenv("TTS_BASE_URL")

        os.makedirs(self.output_dir, exist_ok=True)

    # ----------------------------
    # MAIN TTS GENERATION
    # ----------------------------
    async def synthesize(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0
    ) -> dict:
        """
        Converts text to speech and stores audio file.
        """

        if not text:
            raise ValueError("Text is required for TTS")

        audio_id = f"{uuid.uuid4()}.mp3"
        file_path = os.path.join(self.output_dir, audio_id)

        audio_content = await self._call_tts_api(
            text=text,
            voice=voice,
            speed=speed
        )

        with open(file_path, "wb") as f:
            f.write(audio_content)

        return {
            "audio_id": audio_id,
            "file_path": file_path,
            "text": text,
            "voice": voice,
            "speed": speed
        }

    # ----------------------------
    # BATCH TTS (LESSON PRE-GENERATION)
    # ----------------------------
    async def synthesize_batch(
        self,
        texts: list[str],
        voice: str = "default"
    ) -> list[dict]:
        """
        Pre-generates multiple audio clips for lessons.
        """

        results = []

        for text in texts:
            result = await self.synthesize(
                text=text,
                voice=voice
            )
            results.append(result)

        return results

    # ----------------------------
    # INTERNAL API CALL
    # ----------------------------
    async def _call_tts_api(
        self,
        text: str,
        voice: str,
        speed: float
    ) -> bytes:
        """
        Calls external TTS provider.

        Replace this with:
        - ElevenLabs
        - Google TTS
        - Azure Speech
        - Amazon Polly
        """

        if not self.base_url:
            # fallback mock audio (for dev)
            return b"FAKE_AUDIO_DATA"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "voice": voice,
            "speed": speed
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(
                    f"TTS API failed: {response.text}"
                )

            return response.content