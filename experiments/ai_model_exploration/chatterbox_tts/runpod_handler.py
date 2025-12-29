"""Runpod handler for Chatterbox TTS inference.

This script runs on the Runpod instance and handles TTS inference requests.
"""

from __future__ import annotations

import base64
import io
import os
import re
from typing import Any

import runpod
import torch
import torchaudio as ta
from chatterbox.tts_turbo import ChatterboxTurboTTS
from huggingface_hub import login


# Global model (loaded once on cold start)
model: ChatterboxTurboTTS | None = None


def load_model() -> ChatterboxTurboTTS:
    """Load the Chatterbox TTS model.

    Returns:
        Loaded model instance
    """
    global model

    if model is None:
        # Authenticate with Hugging Face
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError(
                "HF_TOKEN environment variable is required for Chatterbox Turbo. "
                "Please set it in your Runpod endpoint configuration."
            )

        print("Authenticating with Hugging Face...")
        login(token=hf_token)

        print("Loading Chatterbox Turbo TTS model...")
        model = ChatterboxTurboTTS.from_pretrained(device="cuda")
        print("Model loaded successfully!")

    return model


def count_tokens(text: str, tokenizer) -> int:
    """Count tokens in text using model's tokenizer.

    Args:
        text: Input text
        tokenizer: Model's tokenizer

    Returns:
        Number of tokens
    """
    tokens = tokenizer.encode(text)
    return len(tokens)


def split_text_into_chunks(text: str, tokenizer, max_tokens: int = 950) -> list[str]:
    """Split text into chunks at sentence boundaries, keeping under max_tokens.

    Args:
        text: Input text to split
        tokenizer: Model's tokenizer
        max_tokens: Maximum tokens per chunk (default 950 for buffer)

    Returns:
        List of text chunks
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence, tokenizer)

        if sentence_tokens > max_tokens:
            parts = re.split(r"(?<=,)\s+", sentence)
            for part in parts:
                part_tokens = count_tokens(part, tokenizer)
                if current_tokens + part_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [part]
                        current_tokens = part_tokens
                    else:
                        chunks.append(part)
                else:
                    current_chunk.append(part)
                    current_tokens += part_tokens
        else:
            if current_tokens + sentence_tokens > max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def generate_long_audio(
    text: str, model: ChatterboxTurboTTS, tokenizer, **kwargs
) -> torch.Tensor:
    """Generate audio for text longer than 1000 tokens by chunking.

    Args:
        text: Input text (any length)
        model: Chatterbox model
        tokenizer: Model's tokenizer
        **kwargs: Parameters to pass to model.generate()

    Returns:
        Concatenated audio waveform
    """
    total_tokens = count_tokens(text, tokenizer)

    if total_tokens <= 950:
        print(f"Text has {total_tokens} tokens, generating directly...")
        return model.generate(text, **kwargs)

    print(f"Text has {total_tokens} tokens (exceeds 1000 limit)")
    chunks = split_text_into_chunks(text, tokenizer, max_tokens=950)
    print(f"Split into {len(chunks)} chunks")

    audio_chunks = []
    for i, chunk in enumerate(chunks, 1):
        chunk_tokens = count_tokens(chunk, tokenizer)
        print(f"  Chunk {i}/{len(chunks)}: {chunk_tokens} tokens")
        wav = model.generate(chunk, **kwargs)
        audio_chunks.append(wav)

    print("Concatenating audio chunks...")
    concatenated = torch.cat(audio_chunks, dim=-1)
    return concatenated


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

        # Get tokenizer for chunking
        tokenizer = tts_model.text_encoder.tokenizer

        # Run inference with automatic chunking for long text
        print(f"Synthesizing speech for text: {text[:50]}...")

        wav = generate_long_audio(
            text,
            tts_model,
            tokenizer,
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
