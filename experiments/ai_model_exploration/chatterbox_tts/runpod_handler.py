"""Runpod handler for Chatterbox TTS inference.

This script runs on the Runpod instance and handles TTS inference requests.
"""

from __future__ import annotations

import base64
import io
from typing import Any

import runpod
import torchaudio as ta
from chatterbox.tts_turbo import ChatterboxTurboTTS


# Global model (loaded once on cold start)
model: ChatterboxTurboTTS | None = None


def load_model() -> ChatterboxTurboTTS:
    """Load the Chatterbox TTS model.

    Returns:
        Loaded model instance
    """
    global model

    if model is None:
        print("Loading Chatterbox Turbo TTS model...")

        model = ChatterboxTurboTTS.from_pretrained(device="cuda")

        print("Model loaded successfully!")

    return model


def handler(job: dict[str, Any]) -> dict[str, Any]:
    """Handle TTS inference requests.

    Args:
        job: Job input containing text and parameters

    Returns:
        Dictionary with generated audio
    """
    try:
        job_input = job["input"]

        # Get parameters
        text = job_input["text"]
        exaggeration = job_input.get("exaggeration", 0.5)
        cfg_weight = job_input.get("cfg_weight", 0.5)
        temperature = job_input.get("temperature", 1.0)

        # Load model
        tts_model = load_model()

        # Run inference
        print(f"Synthesizing speech for text: {text[:50]}...")

        wav = tts_model.generate(
            text,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
        )

        # Encode audio as base64
        buffer = io.BytesIO()
        ta.save(buffer, wav, tts_model.sr, format="wav")
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()

        print("Speech synthesized successfully")

        return {"audio": audio_b64}

    except Exception as e:
        print(f"Error during inference: {e}")
        return {"error": str(e)}


# Start the serverless worker
runpod.serverless.start({"handler": handler})
