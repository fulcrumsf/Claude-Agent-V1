"""
Provider registry and routing for image generation.

This is the basic version with Google AI Studio as the default (and only) provider.

Usage:
    from tools.providers import get_image_provider, is_sync

    provider, name = get_image_provider("nano-banana-pro")  # Google (default)
"""

from . import google

# --- Image model registry ---
IMAGE_PROVIDERS = {
    "nano-banana": {
        "default": "google",
        "providers": {"google": google},
    },
    "nano-banana-pro": {
        "default": "google",
        "providers": {"google": google},
    },
}

# --- Video model registry (not available in basic version) ---
VIDEO_PROVIDERS = {}


def get_image_provider(model="nano-banana-pro", provider_override=None):
    """
    Get the provider module for an image model.

    Args:
        model: Image model name (e.g., "nano-banana-pro")
        provider_override: Force a specific provider (e.g., "google")

    Returns:
        tuple: (provider_module, provider_name)
    """
    model_config = IMAGE_PROVIDERS.get(model)
    if not model_config:
        raise ValueError(f"Unknown image model: '{model}'. Available: {list(IMAGE_PROVIDERS.keys())}")

    provider_name = provider_override or model_config["default"]
    provider = model_config["providers"].get(provider_name)
    if not provider:
        available = list(model_config["providers"].keys())
        raise ValueError(f"Provider '{provider_name}' not available for '{model}'. Available: {available}")

    return provider, provider_name


def get_video_provider(model="veo-3.1", provider_override=None):
    """
    Get the provider module for a video model.

    Note: Video generation is not available in the basic version.
    For video support, join RoboNuggets.com for the full Creative Content Engine.
    """
    raise ValueError(
        "Video generation is not available in the basic version. "
        "Join RoboNuggets.com for the full Creative Content Engine with video support."
    )


def is_sync(provider_module, generation_type):
    """
    Check if a provider's generation is synchronous (no polling needed).

    Args:
        provider_module: The provider module (e.g., google)
        generation_type: "image" or "video"

    Returns:
        bool: True if synchronous (result returned immediately)
    """
    return getattr(provider_module, f"{generation_type}_IS_SYNC", False)
