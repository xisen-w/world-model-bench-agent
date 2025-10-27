"""
Google Veo Video Generation Provider.

This module exposes a provider implementation that wraps Veo-capable Gemini
endpoints via the unified video generation interface. It mirrors the usage
patterns from the official notebook snippets and offers higher-level helpers
for common Veo workflows (image generation, img2vid, reference-based runs,
prompt-only, and video extension).
"""

from __future__ import annotations

import base64
import io
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence

import requests

from .unified_interface import (
    VideoGenerationError,
    VideoGenerationResult,
    VideoGenerator,
)

DEFAULT_IMAGE_MODEL_ID = "gemini-2.5-flash-image"
DEFAULT_VEO_MODEL_ID = "veo-3.1-fast-generate-preview"


class VeoVideoGenerator(VideoGenerator):
    """
    Google Veo video generation provider.

    The class expects a Gemini client that exposes ``models``, ``files`` and
    ``operations`` sub-clients compatible with the public Veo notebook
    examples (e.g. the high-level ``google-generativeai`` client). Each Veo
    capability is implemented as a dedicated helper and the ``generate_video``
    dispatcher selects the appropriate workflow automatically.
    """

    def __init__(
        self,
        api_key: str,
        *,
        client: Any = None,
        types_module: Any = None,
        acknowledged_paid_feature: bool = False,
        veo_model_id: str = DEFAULT_VEO_MODEL_ID,
        image_model_id: str = DEFAULT_IMAGE_MODEL_ID,
        poll_interval_seconds: int = 20,
        operation_timeout_seconds: int = 20 * 60,
        **kwargs: Any,
    ):
        """
        Initialize the Veo video generator.

        Args:
            api_key: Google AI API key (used for informative errors only).
            client: Pre-configured Gemini/Veo client with ``models``, ``files``,
                and ``operations`` helpers. Required for actual requests.
            types_module: Optional types module (``google.generativeai.types``)
                used to build strongly typed request objects.
            acknowledged_paid_feature: Whether the caller acknowledged Veo fees.
            veo_model_id: Default Veo model identifier.
            image_model_id: Default Gemini image model identifier.
            poll_interval_seconds: Polling interval while waiting for LROs.
            operation_timeout_seconds: Timeout for long running operations.
            **kwargs: Additional configuration stored on the base class.
        """
        super().__init__(api_key, **kwargs)
        self.client = client
        self.types = types_module or self._try_import_types_module()
        self.veo_model_id = veo_model_id
        self.image_model_id = image_model_id
        self.poll_interval_seconds = poll_interval_seconds
        self.operation_timeout_seconds = operation_timeout_seconds
        self.user_acknowledged_paid_feature = acknowledged_paid_feature
        self._operation_cache: Dict[str, Dict[str, Any]] = {}

    # --------------------------------------------------------------------- #
    # Public helpers for paid feature acknowledgement and routing
    # --------------------------------------------------------------------- #

    def set_paid_feature_acknowledgement(self, acknowledged: bool) -> None:
        """Update acknowledgement flag for Veo/Gemini paid usage."""
        self.user_acknowledged_paid_feature = acknowledged

    # --------------------------------------------------------------------- #
    # Image generation flows
    # --------------------------------------------------------------------- #

    def generate_image_from_prompt(
        self,
        prompt: str,
        *,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        save_path: Optional[str] = None,
    ):
        """
        Generate an image from a textual prompt.

        Returns the produced PIL image so that downstream flows can reuse it.
        """
        self._assert_paid_feature()
        models_client = self._ensure_models_client()
        config = self._build_generate_content_config(
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
        )

        response = models_client.generate_content(
            model=self.image_model_id,
            contents=[prompt],
            config=config,
        )

        image = self._extract_image_from_response(response)

        if save_path:
            image.save(save_path)

        return image

    def generate_image_variation(
        self,
        prompt: str,
        base_image: Any,
        *,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
    ):
        """
        Generate a follow-up image conditioned on an input image.

        Args:
            prompt: The textual guidance for the variation.
            base_image: A PIL image, Gemini image response, or file handle.
        """
        self._assert_paid_feature()
        models_client = self._ensure_models_client()
        config = self._build_generate_content_config(
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
        )

        response = models_client.generate_content(
            model=self.image_model_id,
            contents=[prompt, base_image],
            config=config,
        )

        return self._extract_image_from_response(response)

    # --------------------------------------------------------------------- #
    # Video generation flows (each dedicated helper mirrors notebook usage)
    # --------------------------------------------------------------------- #

    def generate_video_with_image(
        self,
        prompt: str,
        *,
        start_image: Any,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        number_of_videos: int = 1,
    ) -> VideoGenerationResult:
        """Create a Veo video using a single starting image."""
        # Convert image to types.Image format
        converted_image = self._convert_to_types_image(start_image)

        config = self._build_generate_videos_config(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            negative_prompt=negative_prompt,
            number_of_videos=number_of_videos,
        )
        return self._generate_video_operation(
            prompt=prompt,
            config=config,
            image=converted_image,
        )

    def generate_video_with_initial_and_end_image(
        self,
        *,
        prompt: str = "",
        start_image: Any,
        end_image: Any,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        number_of_videos: int = 1,
    ) -> VideoGenerationResult:
        """Create a Veo video bridging a start and end frame."""
        # Convert both images to types.Image format
        converted_start_image = self._convert_to_types_image(start_image)
        converted_end_image = self._convert_to_types_image(end_image)

        config = self._build_generate_videos_config(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            negative_prompt=negative_prompt,
            number_of_videos=number_of_videos,
            last_frame=converted_end_image,
        )
        return self._generate_video_operation(
            prompt=prompt,
            config=config,
            image=converted_start_image,
        )

    def generate_video_from_prompt_only(
        self,
        prompt: str,
        *,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        number_of_videos: int = 1,
    ) -> VideoGenerationResult:
        """Create a video purely from a textual prompt."""
        config = self._build_generate_videos_config(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            negative_prompt=negative_prompt,
            number_of_videos=number_of_videos,
        )
        return self._generate_video_operation(
            prompt=prompt,
            config=config,
        )

    def generate_video_with_references(
        self,
        prompt: str,
        *,
        reference_images: Sequence[Any],
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        reference_type: str = "asset",
        number_of_videos: int = 1,
    ) -> VideoGenerationResult:
        """Create a Veo video constrained by reference images."""
        reference_objs = [
            self._build_reference_image(image=ref, reference_type=reference_type)
            for ref in reference_images
        ]
        config = self._build_generate_videos_config(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            negative_prompt=negative_prompt,
            number_of_videos=number_of_videos,
            reference_images=reference_objs,
        )
        return self._generate_video_operation(
            prompt=prompt,
            config=config,
        )

    def extend_video(
        self,
        *,
        video_asset: Any,
        prompt: str = "",
        negative_prompt: Optional[str] = None,
        resolution: str = "720p",
        number_of_videos: int = 1,
    ) -> VideoGenerationResult:
        """Extend an existing video clip using Veo."""
        config = self._build_generate_videos_config(
            resolution=resolution,
            negative_prompt=negative_prompt,
            number_of_videos=number_of_videos,
        )
        return self._generate_video_operation(
            prompt=prompt,
            config=config,
            video=video_asset,
        )

    # --------------------------------------------------------------------- #
    # Unified routing (exposed to the manager) and abstract method impls
    # --------------------------------------------------------------------- #

    def generate(
        self,
        prompt: str,
        size: str = "16:9",
        seconds: str = "unknown",
        quality: str = "1080p",
        **kwargs: Any,
    ) -> VideoGenerationResult:
        """
        Base interface implementation.

        Delegates to ``generate_video`` which inspects kwargs to determine the
        appropriate specialised helper. The ``size``/``seconds``/``quality`` are
        forwarded into the final ``VideoGenerationResult`` metadata.
        """
        return self.generate_video(
            prompt=prompt,
            size=size,
            seconds=seconds,
            quality=quality,
            **kwargs,
        )

    def generate_video(
        self,
        prompt: str,
        *,
        start_image: Any = None,
        end_image: Any = None,
        reference_images: Sequence[Any] | None = None,
        video_asset: Any = None,
        size: str = "16:9",
        seconds: str = "unknown",
        quality: str = "1080p",
        **kwargs: Any,
    ) -> VideoGenerationResult:
        """
        Smart dispatcher that chooses the best Veo helper based on inputs.

        Priority order:
            1. Video extension if ``video_asset`` provided.
            2. Reference-guided generation.
            3. Start & end image bridging.
            4. Start image only.
            5. Prompt-only generation.
        """
        self._assert_paid_feature()

        if video_asset is not None:
            result = self.extend_video(
                video_asset=video_asset,
                prompt=prompt,
                negative_prompt=kwargs.get("negative_prompt"),
                resolution=kwargs.get("resolution", quality),
                number_of_videos=kwargs.get("number_of_videos", 1),
            )
        elif reference_images:
            result = self.generate_video_with_references(
                prompt=prompt,
                reference_images=reference_images,
                negative_prompt=kwargs.get("negative_prompt"),
                aspect_ratio=kwargs.get("aspect_ratio", size),
                resolution=kwargs.get("resolution", quality),
                number_of_videos=kwargs.get("number_of_videos", 1),
            )
        elif start_image is not None and end_image is not None:
            result = self.generate_video_with_initial_and_end_image(
                prompt=prompt,
                start_image=start_image,
                end_image=end_image,
                negative_prompt=kwargs.get("negative_prompt"),
                aspect_ratio=kwargs.get("aspect_ratio", size),
                resolution=kwargs.get("resolution", quality),
                number_of_videos=kwargs.get("number_of_videos", 1),
            )
        elif start_image is not None:
            result = self.generate_video_with_image(
                prompt=prompt,
                start_image=start_image,
                negative_prompt=kwargs.get("negative_prompt"),
                aspect_ratio=kwargs.get("aspect_ratio", size),
                resolution=kwargs.get("resolution", quality),
                number_of_videos=kwargs.get("number_of_videos", 1),
            )
        else:
            result = self.generate_video_from_prompt_only(
                prompt=prompt,
                negative_prompt=kwargs.get("negative_prompt"),
                aspect_ratio=kwargs.get("aspect_ratio", size),
                resolution=kwargs.get("resolution", quality),
                number_of_videos=kwargs.get("number_of_videos", 1),
            )

        # Enrich base fields with manager-provided hints when available.
        result.size = size or result.size
        result.seconds = str(seconds or result.seconds)
        result.quality = quality or result.quality
        return result

    def get_status(self, video_id: str) -> VideoGenerationResult:
        """
        Fetch the latest status for a previously requested video.
        """
        operations_client = self._ensure_operations_client()
        cached = self._operation_cache.get(video_id, {})
        operation = operations_client.get(video_id)

        generated_videos = getattr(getattr(operation, "result", None), "generated_videos", None)
        config = cached.get("config")
        prompt = cached.get("prompt", "")

        return self._build_video_result(
            operation=operation,
            prompt=prompt,
            config=config,
            requested_model=cached.get("model_id", self.veo_model_id),
            generated_videos=generated_videos,
        )

    def download_video(self, video_id: str, output_path: str) -> str:
        """
        Download the first video asset associated with ``video_id``.
        """
        cached = self._operation_cache.get(video_id)
        if not cached:
            # fallback: attempt to refresh status first
            cached = {}
            status = self.get_status(video_id)
            cached = self._operation_cache.get(video_id, {})
            if status.download_url and status.download_url.startswith("http"):
                self._download_via_http(status.download_url, output_path)
                return output_path

        generated_videos = (cached or {}).get("generated_videos") or []
        if not generated_videos:
            raise VideoGenerationError(
                "No generated videos available for download",
                provider="google",
                video_id=video_id,
            )

        primary_video = generated_videos[0]
        video_resource = getattr(primary_video, "video", primary_video)

        # Try native file download first, fallback to HTTP.
        files_client = getattr(getattr(self.client, "files", None), "download", None)
        if callable(files_client):
            response = self.client.files.download(file=video_resource)
            data = self._extract_bytes_from_download(response)
            with open(output_path, "wb") as fh:
                fh.write(data)
            return output_path

        download_url = (
            getattr(video_resource, "uri", None)
            or getattr(video_resource, "download_uri", None)
            or getattr(video_resource, "downloadUrl", None)
            or (cached.get("download_url") if cached else None)
        )
        if not download_url:
            raise VideoGenerationError(
                "Download URL not available for generated video",
                provider="google",
                video_id=video_id,
            )

        self._download_via_http(download_url, output_path)
        return output_path

    def get_supported_features(self) -> List[str]:
        """List of supported Veo capabilities."""
        return [
            "image_generation",
            "prompt_to_video",
            "image_to_video",
            "image_pair_to_video",
            "reference_guided_video",
            "video_extension",
            "async_generation",
        ]

    # --------------------------------------------------------------------- #
    # Provider metadata
    # --------------------------------------------------------------------- #

    @property
    def provider_name(self) -> str:
        return "Google"

    @property
    def model_name(self) -> str:
        return self.veo_model_id

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _assert_paid_feature(self) -> None:
        if not self.user_acknowledged_paid_feature:
            message = (
                "Veo is a paid feature. Set 'acknowledged_paid_feature' to True or "
                "call 'set_paid_feature_acknowledgement(True)' to continue."
            )
            print(message)
            raise VideoGenerationError(
                message,
                provider="google",
            )

    def _ensure_models_client(self):
        self._ensure_client()
        models_client = getattr(self.client, "models", None)
        if models_client is None or not hasattr(models_client, "generate_content"):
            raise VideoGenerationError(
                "Configured client does not expose 'models.generate_content'. "
                "Please provide a Gemini client that supports the expected API.",
                provider="google",
            )
        return models_client

    def _ensure_operations_client(self):
        self._ensure_client()
        operations_client = getattr(self.client, "operations", None)
        if operations_client is None or not hasattr(operations_client, "get"):
            raise VideoGenerationError(
                "Configured client does not expose 'operations.get'.",
                provider="google",
            )
        return operations_client

    def _ensure_client(self) -> None:
        if self.client is None:
            raise VideoGenerationError(
                "Google Veo client not initialized. Pass a configured Gemini client "
                "via the 'client' parameter when constructing VeoVideoGenerator.",
                provider="google",
            )

    def _try_import_types_module(self):
        try:
            # Try new google-genai SDK first
            from google.genai import types as genai_types  # type: ignore
            return genai_types
        except ImportError:
            pass

        try:
            # Fall back to old google-generativeai SDK
            from google.generativeai import types as genai_types  # type: ignore
            return genai_types
        except ImportError:
            return None

    def _convert_to_types_image(self, image: Any) -> Any:
        """
        Convert various image formats to types.Image format required by Veo API.

        Accepts:
        - PIL Image objects
        - File paths (str or Path)
        - types.Image objects (returned as-is)

        Returns:
        - types.Image object with image_bytes and mime_type
        """
        # If already a types.Image, return as-is
        if self.types and hasattr(self.types, 'Image'):
            if isinstance(image, self.types.Image):
                return image

        # Import PIL for image handling
        try:
            from PIL import Image as PILImage
        except ImportError:
            raise VideoGenerationError(
                "PIL (Pillow) is required to convert images. Install with: pip install Pillow",
                provider="google"
            )

        # Handle different input types
        pil_image = None

        # Case 1: PIL Image object
        if isinstance(image, PILImage.Image):
            pil_image = image

        # Case 2: File path (string or Path)
        elif isinstance(image, str) or hasattr(image, '__fspath__'):  # str or Path-like
            try:
                pil_image = PILImage.open(image)
            except Exception as e:
                raise VideoGenerationError(
                    f"Failed to open image file: {e}",
                    provider="google"
                )

        # Case 3: Unknown type
        else:
            raise VideoGenerationError(
                f"Unsupported image type: {type(image)}. Expected PIL Image, file path, or types.Image",
                provider="google"
            )

        # Convert PIL image to bytes
        image_bytes_io = io.BytesIO()
        # Determine format (default to PNG if not available)
        image_format = pil_image.format if pil_image.format else 'PNG'
        pil_image.save(image_bytes_io, format=image_format)
        image_bytes = image_bytes_io.getvalue()

        # Determine MIME type
        mime_type_map = {
            'PNG': 'image/png',
            'JPEG': 'image/jpeg',
            'JPG': 'image/jpeg',
            'WEBP': 'image/webp',
        }
        mime_type = mime_type_map.get(image_format.upper(), 'image/png')

        # Create types.Image object
        if self.types and hasattr(self.types, 'Image'):
            return self.types.Image(image_bytes=image_bytes, mime_type=mime_type)
        else:
            raise VideoGenerationError(
                "types.Image not available. Ensure google-genai SDK is installed.",
                provider="google"
            )

    def _build_generate_content_config(
        self,
        *,
        aspect_ratio: str,
        negative_prompt: Optional[str] = None,
    ):
        if self.types and hasattr(self.types, "GenerateContentConfig"):
            kwargs: Dict[str, Any] = {
                "response_modalities": ["IMAGE"],
            }

            # Build ImageConfig with aspectRatio (camelCase for new SDK)
            if hasattr(self.types, "ImageConfig"):
                # Try camelCase first (new SDK), then snake_case (old SDK)
                try:
                    kwargs["image_config"] = self.types.ImageConfig(aspectRatio=aspect_ratio)
                except TypeError:
                    kwargs["image_config"] = self.types.ImageConfig(aspect_ratio=aspect_ratio)

            # Note: GenerateContentConfig doesn't support negative_prompt
            # It's only supported in GenerateVideosConfig
            config = self.types.GenerateContentConfig(**kwargs)
            return config

        # Fallback to dict-based config
        config: Dict[str, Any] = {
            "response_modalities": ["IMAGE"],
            "image_config": {"aspect_ratio": aspect_ratio},
        }
        # Note: negative_prompt is not supported for image generation
        return config

    def _build_generate_videos_config(
        self,
        *,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        number_of_videos: Optional[int] = None,
        last_frame: Any = None,
        reference_images: Optional[Sequence[Any]] = None,
    ):
        if self.types and hasattr(self.types, "GenerateVideosConfig"):
            kwargs: Dict[str, Any] = {}

            # Try camelCase first (new SDK), fallback to snake_case (old SDK)
            # New google-genai SDK uses camelCase, old google-generativeai uses snake_case
            try:
                if aspect_ratio is not None:
                    kwargs["aspectRatio"] = aspect_ratio
                if resolution is not None:
                    kwargs["resolution"] = resolution
                if negative_prompt is not None:
                    kwargs["negativePrompt"] = negative_prompt
                if number_of_videos is not None:
                    kwargs["numberOfVideos"] = number_of_videos
                if last_frame is not None:
                    kwargs["lastFrame"] = last_frame
                if reference_images:
                    kwargs["referenceImages"] = list(reference_images)
                return self.types.GenerateVideosConfig(**kwargs)
            except TypeError:
                # Fallback to snake_case for old SDK
                kwargs_snake: Dict[str, Any] = {}
                if aspect_ratio is not None:
                    kwargs_snake["aspect_ratio"] = aspect_ratio
                if resolution is not None:
                    kwargs_snake["resolution"] = resolution
                if negative_prompt is not None:
                    kwargs_snake["negative_prompt"] = negative_prompt
                if number_of_videos is not None:
                    kwargs_snake["number_of_videos"] = number_of_videos
                if last_frame is not None:
                    kwargs_snake["last_frame"] = last_frame
                if reference_images:
                    kwargs_snake["reference_images"] = list(reference_images)
                return self.types.GenerateVideosConfig(**kwargs_snake)

        # Fallback to dict-based config
        config: Dict[str, Any] = {}
        if aspect_ratio is not None:
            config["aspect_ratio"] = aspect_ratio
        if resolution is not None:
            config["resolution"] = resolution
        if negative_prompt is not None:
            config["negative_prompt"] = negative_prompt
        if number_of_videos is not None:
            config["number_of_videos"] = number_of_videos
        if last_frame is not None:
            config["last_frame"] = last_frame
        if reference_images:
            config["reference_images"] = list(reference_images)
        return config

    def _build_reference_image(self, *, image: Any, reference_type: str = "asset"):
        # Convert image to types.Image format first
        converted_image = self._convert_to_types_image(image)

        if (
            self.types
            and hasattr(self.types, "VideoGenerationReferenceImage")
            and callable(getattr(self.types, "VideoGenerationReferenceImage"))
        ):
            # Try camelCase first (new SDK), fallback to snake_case (old SDK)
            try:
                return self.types.VideoGenerationReferenceImage(
                    image=converted_image,
                    referenceType=reference_type,
                )
            except TypeError:
                return self.types.VideoGenerationReferenceImage(
                    image=converted_image,
                    reference_type=reference_type,
                )
        return {"image": converted_image, "reference_type": reference_type}

    def _extract_image_from_response(self, response: Any):
        try:
            from PIL import Image
        except ImportError as exc:
            raise VideoGenerationError(
                "Pillow is required to decode image responses. Install with `pip install Pillow`.",
                provider="google",
            ) from exc

        parts = getattr(response, "parts", None)
        if parts is None and hasattr(response, "candidates"):
            candidates = getattr(response, "candidates") or []
            if candidates:
                parts = getattr(candidates[0].content, "parts", None)

        if not parts:
            raise VideoGenerationError(
                "Image generation response did not include inline image data.",
                provider="google",
            )

        for part in parts:
            if hasattr(part, "as_image"):
                image = part.as_image()
                if image:
                    return image

            inline_data = getattr(part, "inline_data", None) or getattr(part, "inlineData", None)
            if inline_data:
                data = getattr(inline_data, "data", None) or inline_data.get("data")
                if not data:
                    continue
                binary = base64.b64decode(data)
                image = Image.open(io.BytesIO(binary))
                image.load()
                return image

        raise VideoGenerationError(
            "Unable to decode inline image data from the response.",
            provider="google",
        )

    def _generate_video_operation(
        self,
        *,
        prompt: str,
        config: Any,
        image: Any = None,
        video: Any = None,
    ) -> VideoGenerationResult:
        self._assert_paid_feature()
        models_client = self._ensure_models_client()

        payload = {
            "model": self.veo_model_id,
            "prompt": prompt,
            "config": config,
        }
        if image is not None:
            payload["image"] = image
        if video is not None:
            payload["video"] = video

        operation = models_client.generate_videos(**payload)
        final_operation = self._poll_operation(operation)
        generated_videos = getattr(getattr(final_operation, "result", None), "generated_videos", None)

        result = self._build_video_result(
            operation=final_operation,
            prompt=prompt,
            config=config,
            requested_model=self.veo_model_id,
            generated_videos=generated_videos,
        )

        self._operation_cache[result.id] = {
            "operation": final_operation,
            "generated_videos": generated_videos or [],
            "config": config,
            "prompt": prompt,
            "model_id": self.veo_model_id,
            "download_url": result.download_url,
        }

        return result

    def _poll_operation(self, operation: Any):
        operations_client = self._ensure_operations_client()
        start_time = time.time()
        current = operation

        while not getattr(current, "done", False):
            if (
                self.operation_timeout_seconds
                and (time.time() - start_time) > self.operation_timeout_seconds
            ):
                raise VideoGenerationError(
                    "Timed out while waiting for Veo operation to finish.",
                    provider="google",
                )

            time.sleep(self.poll_interval_seconds)
            current = operations_client.get(current)

        return current

    def _build_video_result(
        self,
        *,
        operation: Any,
        prompt: str,
        config: Any,
        requested_model: str,
        generated_videos: Optional[Iterable[Any]],
    ) -> VideoGenerationResult:
        operation_name = getattr(operation, "name", None) or getattr(operation, "id", None)
        metadata = getattr(operation, "metadata", None)
        done = getattr(operation, "done", False)

        status = "completed" if done else "running"
        if metadata is not None:
            state = getattr(metadata, "state", None) or getattr(metadata, "state_", None)
            if state:
                status = str(state).lower()
        progress = self._extract_progress(metadata, done)

        config_dict = self._object_to_plain_dict(config) if config is not None else {}
        aspect_ratio = config_dict.get("aspect_ratio", "unknown")
        resolution = config_dict.get("resolution", "unknown")

        download_url = None
        generated_list = list(generated_videos or [])
        if generated_list:
            video_resource = getattr(generated_list[0], "video", generated_list[0])
            download_url = (
                getattr(video_resource, "uri", None)
                or getattr(video_resource, "download_uri", None)
                or getattr(video_resource, "downloadUrl", None)
            )

        metadata_dump = {
            "raw_operation": self._object_to_plain_dict(operation),
            "config": config_dict,
        }

        return VideoGenerationResult(
            id=str(operation_name or "unknown_operation"),
            object="video",
            model=requested_model,
            status=status,
            progress=progress,
            created_at=datetime.utcnow(),
            size=str(aspect_ratio),
            seconds="unknown",
            quality=str(resolution),
            prompt=prompt,
            provider="google",
            download_url=download_url,
            metadata=metadata_dump,
        )

    def _extract_progress(self, metadata: Any, done: bool) -> float:
        if done:
            return 1.0
        if metadata is None:
            return 0.0

        candidates = [
            getattr(metadata, "progress_percent", None),
            getattr(metadata, "progressPercent", None),
            getattr(metadata, "progress", None),
        ]

        for value in candidates:
            if value is not None:
                try:
                    return max(0.0, min(1.0, float(value) / 100.0))
                except (TypeError, ValueError):
                    continue
        return 0.0

    def _extract_bytes_from_download(self, download_response: Any) -> bytes:
        if isinstance(download_response, bytes):
            return download_response

        if hasattr(download_response, "data") and download_response.data is not None:
            return download_response.data

        if hasattr(download_response, "content") and download_response.content is not None:
            return download_response.content

        if hasattr(download_response, "read"):
            return download_response.read()

        raise VideoGenerationError(
            "Unable to extract bytes from download response.",
            provider="google",
        )

    def _download_via_http(self, url: str, output_path: str) -> None:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)

    def _object_to_plain_dict(self, obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, dict):
            return {key: self._object_to_plain_dict(value) for key, value in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._object_to_plain_dict(item) for item in obj]
        if is_dataclass(obj):
            return asdict(obj)
        if hasattr(obj, "to_dict"):
            try:
                return obj.to_dict()
            except TypeError:
                pass
        if hasattr(obj, "__dict__"):
            return {
                key: self._object_to_plain_dict(value)
                for key, value in obj.__dict__.items()
                if not key.startswith("_")
            }
        return obj


# Backwards compatible alias for convenience.
VeoGenerator = VeoVideoGenerator

