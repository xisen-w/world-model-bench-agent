"""
Unified Interface for Video Generation APIs

This module provides a common interface for different video generation services,
allowing easy integration and comparison across different providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class VideoGenerationResult:
    """Standardized result object for video generation operations."""

    id: str
    """Unique identifier for the video generation request"""

    object: str
    """Object type (usually 'video')"""

    model: str
    """Model used for generation"""

    status: str
    """Current status: 'queued', 'generating', 'completed', 'failed'"""

    progress: float
    """Generation progress (0.0 to 1.0)"""

    created_at: datetime
    """Creation timestamp"""

    size: str
    """Video dimensions (e.g., '1024x1808')"""

    seconds: str
    """Video duration in seconds"""

    quality: str
    """Quality setting (e.g., 'standard', 'hd')"""

    prompt: str
    """Original prompt used for generation"""

    provider: str
    """Provider name (e.g., 'openai', 'runway', 'stability')"""

    # Optional fields
    error: Optional[str] = None
    """Error message if generation failed"""

    download_url: Optional[str] = None
    """URL to download the generated video"""

    thumbnail_url: Optional[str] = None
    """URL to thumbnail/preview image"""

    metadata: Optional[Dict[str, Any]] = None
    """Additional provider-specific metadata"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "object": self.object,
            "model": self.model,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "size": self.size,
            "seconds": self.seconds,
            "quality": self.quality,
            "prompt": self.prompt,
            "provider": self.provider,
        }

        if self.error:
            data["error"] = self.error
        if self.download_url:
            data["download_url"] = self.download_url
        if self.thumbnail_url:
            data["thumbnail_url"] = self.thumbnail_url
        if self.metadata:
            data["metadata"] = self.metadata

        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class VideoGenerator(ABC):
    """
    Abstract base class for video generation providers.

    All video generation providers should implement this interface
    to ensure compatibility with the AC-World benchmark.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the video generator.

        Args:
            api_key: API key for the service
            **kwargs: Provider-specific configuration options
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        size: str = "1024x1808",
        seconds: str = "8",
        quality: str = "standard",
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate a video from a text prompt.

        Args:
            prompt: Text description of the video to generate
            size: Video dimensions (e.g., "1024x1808")
            seconds: Duration in seconds
            quality: Quality setting
            **kwargs: Provider-specific options

        Returns:
            VideoGenerationResult object with generation details
        """
        pass

    @abstractmethod
    def get_status(self, video_id: str) -> VideoGenerationResult:
        """
        Get the current status of a video generation request.

        Args:
            video_id: ID of the video generation request

        Returns:
            Updated VideoGenerationResult object
        """
        pass

    @abstractmethod
    def download_video(self, video_id: str, output_path: str) -> str:
        """
        Download the generated video to a local file.

        Args:
            video_id: ID of the video generation request
            output_path: Local file path to save the video

        Returns:
            Path to the downloaded video file
        """
        pass

    def supports_feature(self, feature: str) -> bool:
        """
        Check if the provider supports a specific feature.

        Args:
            feature: Feature to check (e.g., 'async_generation', 'custom_size')

        Returns:
            True if the feature is supported
        """
        supported_features = self.get_supported_features()
        return feature in supported_features

    @abstractmethod
    def get_supported_features(self) -> list[str]:
        """
        Get list of supported features for this provider.

        Returns:
            List of supported feature names
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the video generation provider."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the model used by this provider."""
        pass


class VideoGenerationError(Exception):
    """Exception raised when video generation fails."""

    def __init__(self, message: str, provider: str = None, video_id: str = None):
        super().__init__(message)
        self.provider = provider
        self.video_id = video_id


class VideoGenerationManager:
    """
    Manager class that can work with multiple video generation providers
    through a unified interface.
    """

    def __init__(self):
        self.providers: Dict[str, VideoGenerator] = {}

    def register_provider(self, name: str, provider: VideoGenerator):
        """
        Register a video generation provider.

        Args:
            name: Unique name for the provider
            provider: VideoGenerator instance
        """
        self.providers[name] = provider

    def generate_video(
        self,
        provider_name: str,
        prompt: str,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate a video using a specific provider.

        Args:
            provider_name: Name of the provider to use
            prompt: Text description for video generation
            **kwargs: Additional arguments for generation

        Returns:
            VideoGenerationResult object

        Raises:
            VideoGenerationError: If provider is not found or generation fails
        """
        if provider_name not in self.providers:
            raise VideoGenerationError(f"Provider '{provider_name}' not found")

        provider = self.providers[provider_name]
        return provider.generate(prompt, **kwargs)

    def get_available_providers(self) -> list[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())

    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """
        Get information about a specific provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary with provider information
        """
        if provider_name not in self.providers:
            raise VideoGenerationError(f"Provider '{provider_name}' not found")

        provider = self.providers[provider_name]
        return {
            "name": provider.provider_name,
            "model": provider.model_name,
            "features": provider.get_supported_features(),
        }


