"""Utility functions for secure-runpod-chat."""

import os
import re
import sys
from typing import Dict, Optional, Tuple
from huggingface_hub import HfApi, model_info
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def get_model_info(model_id: str) -> Dict:
    """Fetch model information from Hugging Face Hub.

    Args:
        model_id: Hugging Face model ID

    Returns:
        Dictionary containing model information
    """
    try:
        api = HfApi()
        info = model_info(model_id)
        return {
            "id": info.id,
            "pipeline_tag": getattr(info, "pipeline_tag", None),
            "safetensors": getattr(info, "safetensors", None),
            "tags": getattr(info, "tags", []),
            "library_name": getattr(info, "library_name", None),
        }
    except Exception as e:
        console.print(f"[red]Error fetching model info: {e}[/red]")
        return {}


def estimate_model_size_gb(model_id: str) -> float:
    """Estimate model size in GB from Hugging Face Hub.

    Args:
        model_id: Hugging Face model ID

    Returns:
        Estimated model size in GB
    """
    try:
        api = HfApi()
        files = api.list_repo_files(model_id)

        # Try to get file sizes from safetensors or bin files
        total_size = 0
        for file in files:
            if file.endswith(('.safetensors', '.bin', '.pt', '.pth')):
                try:
                    file_info = api.get_paths_info(model_id, file)
                    if hasattr(file_info, 'size'):
                        total_size += file_info.size
                except:
                    pass

        if total_size > 0:
            return total_size / (1024 ** 3)  # Convert to GB

        # Fallback: estimate from model name
        model_name_lower = model_id.lower()
        if any(x in model_name_lower for x in ['405b', '405-b']):
            return 810  # ~810GB for 405B parameter models
        elif any(x in model_name_lower for x in ['70b', '70-b']):
            return 140  # ~140GB for 70B parameter models
        elif any(x in model_name_lower for x in ['13b', '13-b']):
            return 26  # ~26GB for 13B parameter models
        elif any(x in model_name_lower for x in ['7b', '7-b']):
            return 14  # ~14GB for 7B parameter models
        elif any(x in model_name_lower for x in ['3b', '3-b', '3.2b']):
            return 6  # ~6GB for 3B parameter models
        elif any(x in model_name_lower for x in ['1b', '1-b', '1.5b']):
            return 3  # ~3GB for 1-2B parameter models

        # Default estimate
        return 10

    except Exception as e:
        console.print(f"[yellow]Warning: Could not estimate model size: {e}[/yellow]")
        return 10  # Default to 10GB


def determine_gpu_requirements(model_size_gb: float, is_vision: bool = False) -> Tuple[str, int]:
    """Determine appropriate GPU type and count based on model size.

    Args:
        model_size_gb: Model size in GB
        is_vision: Whether the model is a vision-language model

    Returns:
        Tuple of (gpu_type, gpu_count)
    """
    # Add overhead for VLLM, KV cache, etc. (2x for inference)
    total_vram_needed = model_size_gb * 2

    # Vision models need more memory
    if is_vision:
        total_vram_needed *= 1.5

    # GPU options (VRAM in GB)
    gpu_options = [
        ("NVIDIA RTX A4000", 16),
        ("NVIDIA RTX A5000", 24),
        ("NVIDIA A40", 48),
        ("NVIDIA RTX A6000", 48),
        ("NVIDIA A100", 80),
        ("NVIDIA A100 80GB", 80),
    ]

    # Find suitable GPU
    for gpu_name, vram in gpu_options:
        if vram >= total_vram_needed:
            return gpu_name, 1
        elif vram * 2 >= total_vram_needed:
            return gpu_name, 2
        elif vram * 4 >= total_vram_needed:
            return gpu_name, 4

    # Default to A100 80GB if model is very large
    num_gpus = max(1, int(total_vram_needed / 80) + 1)
    return "NVIDIA A100 80GB", num_gpus


def is_vision_model(model_info: Dict) -> bool:
    """Check if model is a vision-language model.

    Args:
        model_info: Model information dictionary

    Returns:
        True if model supports vision inputs
    """
    pipeline_tag = model_info.get("pipeline_tag", "")
    tags = model_info.get("tags", [])

    vision_indicators = [
        "image-text-to-text",
        "visual-question-answering",
        "vision",
        "multimodal",
        "llava",
        "clip",
    ]

    return any(indicator in str(pipeline_tag).lower() for indicator in vision_indicators) or \
           any(indicator in str(tag).lower() for tag in tags for indicator in vision_indicators)


def format_cost(cost_per_hour: float) -> str:
    """Format cost per hour for display.

    Args:
        cost_per_hour: Cost in dollars per hour

    Returns:
        Formatted cost string
    """
    return f"${cost_per_hour:.4f}/hour (${cost_per_hour * 24:.2f}/day)"


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation.

    Args:
        message: Confirmation message
        default: Default value if user just presses Enter

    Returns:
        True if user confirms
    """
    suffix = "[Y/n]" if default else "[y/N]"
    response = console.input(f"{message} {suffix}: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes']


def sanitize_path(path: str) -> str:
    """Sanitize file path to prevent directory traversal.

    Args:
        path: File path to sanitize

    Returns:
        Sanitized path
    """
    # Remove any path traversal attempts
    path = path.replace("..", "").replace("~", "")
    # Remove leading slashes for relative paths
    path = path.lstrip("/")
    return path


def validate_api_key(api_key: Optional[str]) -> str:
    """Validate RunPod API key.

    Args:
        api_key: API key to validate

    Returns:
        Valid API key

    Raises:
        ValueError: If API key is invalid
    """
    if not api_key:
        raise ValueError(
            "RunPod API key not found. Please set RUNPOD_API_KEY environment variable."
        )

    if not api_key.strip():
        raise ValueError("RunPod API key is empty.")

    return api_key.strip()
