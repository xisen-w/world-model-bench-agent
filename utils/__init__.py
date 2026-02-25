"""
Utilities for AC-World Benchmark

This package provides:
- Video generation APIs (Sora, Runway, etc.)
- Azure OpenAI API utilities (chat, vision, embeddings)
- Unified interfaces for agent development
"""

__version__ = "0.1.0"

from .unified_interface import VideoGenerator, VideoGenerationResult
from .sora import SoraVideoGenerator

# Azure OpenAI utilities
try:
    from .azure_openai_api import (
        AzureOpenAIManager,
        AzureOpenAIConfig,
        test_api_keys,
        test_vision_api,
        get_azure_openai_manager
    )
    HAS_AZURE_API = True
except ImportError:
    HAS_AZURE_API = False

__all__ = [
    # Video generation
    "VideoGenerator",
    "VideoGenerationResult",
    "SoraVideoGenerator",
]

if HAS_AZURE_API:
    __all__.extend([
        # Azure OpenAI
        "AzureOpenAIManager",
        "AzureOpenAIConfig",
        "test_api_keys",
        "test_vision_api",
        "get_azure_openai_manager",
    ])


