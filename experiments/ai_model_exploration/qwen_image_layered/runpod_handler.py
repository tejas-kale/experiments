"""Runpod handler for Qwen-Image-Layered inference.

This script runs on the Runpod instance and handles inference requests.
"""

from __future__ import annotations

import base64
import io
from typing import Any

import runpod
import torch
from diffusers import QwenImageLayeredPipeline
from PIL import Image


# Global pipeline (loaded once on cold start)
pipeline: QwenImageLayeredPipeline | None = None


def load_model() -> QwenImageLayeredPipeline:
    """Load the Qwen-Image-Layered model.

    Returns:
        Loaded pipeline instance
    """
    global pipeline

    if pipeline is None:
        print("Loading Qwen-Image-Layered model...")

        pipeline = QwenImageLayeredPipeline.from_pretrained(
            "Qwen/Qwen-Image-Layered",
            torch_dtype=torch.bfloat16,  # Use bf16 for better quality
        )
        pipeline = pipeline.to("cuda")

        print("Model loaded successfully!")

    return pipeline


def handler(job: dict[str, Any]) -> dict[str, Any]:
    """Handle inference requests.

    Args:
        job: Job input containing image and parameters

    Returns:
        Dictionary with generated layers
    """
    try:
        job_input = job["input"]

        # Decode input image
        image_b64 = job_input["image"]
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Get parameters
        num_layers = job_input.get("num_layers", 4)
        resolution = job_input.get("resolution", 640)
        num_inference_steps = job_input.get("num_inference_steps", 50)
        true_cfg_scale = job_input.get("true_cfg_scale", 4.0)
        cfg_normalize = job_input.get("cfg_normalize", True)
        use_en_prompt = job_input.get("use_en_prompt", True)

        # Load model
        pipe = load_model()

        # Run inference
        print(f"Generating {num_layers} layers...")

        with torch.inference_mode():
            output = pipe(
                image=image,
                generator=torch.Generator(device="cuda").manual_seed(777),
                true_cfg_scale=true_cfg_scale,
                negative_prompt=" ",
                num_inference_steps=num_inference_steps,
                layers=num_layers,
                resolution=resolution,
                cfg_normalize=cfg_normalize,
                use_en_prompt=use_en_prompt,
            )

        # Encode output layers as base64
        layers_b64 = []
        for layer_image in output.images[0]:
            buffer = io.BytesIO()
            layer_image.save(buffer, format="PNG")
            layer_b64 = base64.b64encode(buffer.getvalue()).decode()
            layers_b64.append(layer_b64)

        print(f"Successfully generated {len(layers_b64)} layers")

        return {"layers": layers_b64}

    except Exception as e:
        print(f"Error during inference: {e}")
        return {"error": str(e)}


# Start the serverless worker
runpod.serverless.start({"handler": handler})
