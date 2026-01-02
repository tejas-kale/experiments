"""Configuration management for Qwen-Image-Layered CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class Config:
    """Manages configuration for the Qwen-Image-Layered CLI."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize configuration manager.

        Args:
            config_dir: Optional custom config directory (defaults to ~/.qwen-image-layered)
        """
        if config_dir is None:
            config_dir = Path.home() / ".qwen-image-layered"

        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self._config = json.load(f)
        else:
            self._config = {}

    def _save(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Check environment variables first
        env_key = f"RUNPOD_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Fall back to config file
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self._save()

    def get_api_key(self) -> str | None:
        """Get Runpod API key.

        Returns:
            API key or None if not configured
        """
        return self.get("api_key")

    def get_endpoint_id(self) -> str | None:
        """Get Runpod endpoint ID.

        Returns:
            Endpoint ID or None if not configured
        """
        return self.get("endpoint_id")

    def get_template_id(self) -> str | None:
        """Get Runpod template ID.

        Returns:
            Template ID or None if not configured
        """
        return self.get("template_id")

    def get_docker_image(self) -> str | None:
        """Get Docker image name.

        Returns:
            Docker image name or None if not configured
        """
        return self.get("docker_image")

    def get_gpu_type(self) -> str:
        """Get preferred GPU type.

        Returns:
            GPU type (defaults to 'NVIDIA RTX 3090')
        """
        return self.get("gpu_type", "NVIDIA RTX 3090")

    def is_configured(self) -> bool:
        """Check if the CLI is fully configured.

        Returns:
            True if API key and endpoint ID are set
        """
        return self.get_api_key() is not None and self.get_endpoint_id() is not None

    def clear(self) -> None:
        """Clear all configuration."""
        self._config = {}
        self._save()
