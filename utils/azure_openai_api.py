"""
Azure OpenAI API Utilities for World Model Bench Agent.

This module provides a unified interface for Azure OpenAI services:
- Chat completions (GPT-4o, GPT-4o-mini, o1, etc.)
- Vision models (GPT-4o with image input)
- Embeddings (text-embedding-3-small)
- API key testing and validation

Configuration is loaded from .env file.
"""

import os
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import base64

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    print("Warning: python-dotenv not installed. Using system environment variables only.")

# Try to import OpenAI SDK
try:
    from openai import AzureOpenAI
    HAS_AZURE_OPENAI = True
except ImportError:
    HAS_AZURE_OPENAI = False
    print("Warning: openai package not installed. Run: pip install openai")


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class AzureOpenAIConfig:
    """Configuration for Azure OpenAI services."""

    # GPT-4o (standard chat + vision)
    gpt4o_endpoint: str
    gpt4o_api_key: str
    gpt4o_deployment: str
    gpt4o_api_version: str

    # GPT-4.1-nano (fast, cheap)
    nano_deployment: str

    # o1 (reasoning model)
    o1_deployment: str

    # o4-mini (compact reasoning)
    o4_mini_deployment: str

    # Embeddings (using gpt4o endpoint)
    embedding_deployment: str = "text-embedding-3-small"

    @classmethod
    def from_env(cls) -> 'AzureOpenAIConfig':
        """Load configuration from environment variables."""
        return cls(
            gpt4o_endpoint=os.getenv("AZURE_OPENAI_4O_ENDPOINT", ""),
            gpt4o_api_key=os.getenv("AZURE_OPENAI_4O_API_KEY", ""),
            gpt4o_deployment=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT", "gpt-4o"),
            gpt4o_api_version=os.getenv("AZURE_OPENAI_4O_API_VERSION", "2025-01-01-preview"),
            nano_deployment=os.getenv("AZURE_OPENAI_NANO_DEPLOYMENT", "gpt-4.1-nano"),
            o1_deployment=os.getenv("AZURE_OPENAI_O1_DEPLOYMENT", "o1"),
            o4_mini_deployment=os.getenv("AZURE_OPENAI_O4_MINI_DEPLOYMENT", "o4-mini"),
            embedding_deployment="text-embedding-3-small"
        )

    def validate(self) -> bool:
        """Check if all required fields are set."""
        required = [
            self.gpt4o_endpoint,
            self.gpt4o_api_key,
            self.gpt4o_deployment
        ]
        return all(required)


# =============================================================================
# Azure OpenAI Client Manager
# =============================================================================

class AzureOpenAIManager:
    """
    Unified manager for Azure OpenAI services.

    Handles multiple models:
    - gpt-4o: Standard chat + vision
    - gpt-4.1-nano: Fast and cheap
    - o1: Reasoning model
    - o4-mini: Compact reasoning

    Usage:
        manager = AzureOpenAIManager()

        # Chat completion
        response = manager.chat(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-4o"
        )

        # Vision (image + text)
        response = manager.vision(
            image_path="state.png",
            prompt="Describe this Rubik's cube",
            model="gpt-4o"
        )

        # Embeddings
        embedding = manager.embed("some text")
    """

    def __init__(self, config: Optional[AzureOpenAIConfig] = None):
        """
        Initialize Azure OpenAI manager.

        Args:
            config: Optional config. If None, loads from .env
        """
        self.config = config or AzureOpenAIConfig.from_env()

        if not self.config.validate():
            raise ValueError(
                "Azure OpenAI configuration incomplete. Check .env file.\n"
                "Required: AZURE_OPENAI_4O_ENDPOINT, AZURE_OPENAI_4O_API_KEY, AZURE_OPENAI_GPT4O_DEPLOYMENT"
            )

        if not HAS_AZURE_OPENAI:
            raise ImportError("openai package not installed. Run: pip install openai")

        # Initialize client
        self.client = AzureOpenAI(
            api_key=self.config.gpt4o_api_key,
            api_version=self.config.gpt4o_api_version,
            azure_endpoint=self.config.gpt4o_endpoint
        )

        # Model mappings
        self.model_map = {
            "gpt-4o": self.config.gpt4o_deployment,
            "gpt-4.1-nano": self.config.nano_deployment,
            "o1": self.config.o1_deployment,
            "o4-mini": self.config.o4_mini_deployment,
        }

    def _resolve_model(self, model: str) -> str:
        """Map friendly name to deployment name."""
        return self.model_map.get(model, model)

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Send chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use ("gpt-4o", "gpt-4.1-nano", "o1", "o4-mini")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for API

        Returns:
            Response text

        Example:
            response = manager.chat([
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "What is 2+2?"}
            ])
        """
        deployment = self._resolve_model(model)

        response = self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.choices[0].message.content

    def vision(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        model: str = "gpt-4o",
        max_tokens: int = 500,
        detail: str = "auto",
        **kwargs
    ) -> str:
        """
        Send vision request (image + text).

        Args:
            prompt: Text prompt/question
            image_path: Path to local image file
            image_url: URL to image
            image_base64: Base64-encoded image
            model: Model to use (must support vision)
            max_tokens: Maximum tokens
            detail: Image detail level ("auto", "low", "high")
            **kwargs: Additional parameters

        Returns:
            Response text

        Example:
            response = manager.vision(
                prompt="Describe the Rubik's cube state",
                image_path="state.png"
            )
        """
        # Prepare image content
        if image_path:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Detect media type
            ext = Path(image_path).suffix.lower()
            media_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/jpeg')

            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{image_data}",
                    "detail": detail
                }
            }
        elif image_url:
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": detail
                }
            }
        elif image_base64:
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": detail
                }
            }
        else:
            raise ValueError("Must provide one of: image_path, image_url, or image_base64")

        # Build message
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                image_content
            ]
        }]

        deployment = self._resolve_model(model)

        response = self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.choices[0].message.content

    def embed(
        self,
        text: Union[str, List[str]],
        model: str = "text-embedding-3-small"
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate text embeddings.

        Args:
            text: Single text or list of texts
            model: Embedding model

        Returns:
            Embedding vector(s)

        Example:
            embedding = manager.embed("Hello world")
            embeddings = manager.embed(["text1", "text2"])
        """
        is_single = isinstance(text, str)
        texts = [text] if is_single else text

        response = self.client.embeddings.create(
            model=model,
            input=texts
        )

        embeddings = [item.embedding for item in response.data]
        return embeddings[0] if is_single else embeddings


# =============================================================================
# API Testing Functions
# =============================================================================

def test_api_keys(verbose: bool = True) -> Dict[str, bool]:
    """
    Test all Azure OpenAI API keys and endpoints.

    Args:
        verbose: Print detailed results

    Returns:
        Dict mapping test name to success status

    Example:
        results = test_api_keys()
        if all(results.values()):
            print("All tests passed!")
    """
    results = {}

    if verbose:
        print("=" * 70)
        print("Azure OpenAI API Key Testing")
        print("=" * 70)
        print()

    # Test 1: Configuration loading
    if verbose:
        print("Test 1: Loading configuration from .env...")

    try:
        config = AzureOpenAIConfig.from_env()
        if config.validate():
            results["config_load"] = True
            if verbose:
                print("  ✅ Configuration loaded successfully")
                print(f"     Endpoint: {config.gpt4o_endpoint}")
                print(f"     GPT-4o deployment: {config.gpt4o_deployment}")
        else:
            results["config_load"] = False
            if verbose:
                print("  ❌ Configuration incomplete")
            return results
    except Exception as e:
        results["config_load"] = False
        if verbose:
            print(f"  ❌ Failed to load config: {e}")
        return results

    if verbose:
        print()

    # Test 2: Client initialization
    if verbose:
        print("Test 2: Initializing Azure OpenAI client...")

    try:
        manager = AzureOpenAIManager(config)
        results["client_init"] = True
        if verbose:
            print("  ✅ Client initialized successfully")
    except Exception as e:
        results["client_init"] = False
        if verbose:
            print(f"  ❌ Failed to initialize client: {e}")
        return results

    if verbose:
        print()

    # Test 3: Simple chat completion
    if verbose:
        print("Test 3: Testing chat completion (gpt-4o)...")

    try:
        response = manager.chat(
            messages=[{"role": "user", "content": "Say 'test successful' and nothing else."}],
            model="gpt-4o",
            max_tokens=50,
            temperature=0
        )
        results["chat_completion"] = True
        if verbose:
            print(f"  ✅ Chat completion working")
            print(f"     Response: {response[:100]}")
    except Exception as e:
        results["chat_completion"] = False
        if verbose:
            print(f"  ❌ Chat completion failed: {e}")

    if verbose:
        print()

    # Test 4: Embeddings (optional - not critical)
    if verbose:
        print("Test 4: Testing embeddings (optional)...")

    try:
        embedding = manager.embed("test embedding")
        if len(embedding) > 0:
            results["embeddings"] = True
            if verbose:
                print(f"  ✅ Embeddings working")
                print(f"     Dimension: {len(embedding)}")
        else:
            results["embeddings"] = False
            if verbose:
                print("  ⚠️  Empty embedding returned")
    except Exception as e:
        results["embeddings"] = False
        if verbose:
            print(f"  ⚠️  Embeddings not available: {e}")
            print(f"     (This is optional - agents can work without embeddings)")

    if verbose:
        print()

    # Test 5: Alternative models (nano)
    if verbose:
        print("Test 5: Testing alternative model (gpt-4.1-nano)...")

    try:
        response = manager.chat(
            messages=[{"role": "user", "content": "Hi"}],
            model="gpt-4.1-nano",
            max_tokens=20
        )
        results["nano_model"] = True
        if verbose:
            print(f"  ✅ Nano model working")
    except Exception as e:
        results["nano_model"] = False
        if verbose:
            print(f"  ⚠️  Nano model not available: {e}")

    if verbose:
        print()
        print("=" * 70)
        print("Summary:")
        print("=" * 70)
        passed = sum(results.values())
        total = len(results)
        print(f"Tests passed: {passed}/{total}")

        # Check critical tests (chat is required, embeddings optional)
        if results.get("chat_completion"):
            if passed == total:
                print("✅ All tests passed! API is fully ready.")
            else:
                print("✅ Core functionality working (chat completion)!")
                if not results.get("embeddings"):
                    print("   Note: Embeddings not available (optional)")
        else:
            print("❌ Critical tests failed. Check configuration.")

    return results


def test_vision_api(image_path: Optional[str] = None, verbose: bool = True) -> bool:
    """
    Test vision API with an image.

    Args:
        image_path: Path to test image (optional)
        verbose: Print results

    Returns:
        True if vision API works

    Example:
        success = test_vision_api("test_image.png")
    """
    if verbose:
        print("=" * 70)
        print("Testing Vision API")
        print("=" * 70)
        print()

    try:
        manager = AzureOpenAIManager()

        if image_path and Path(image_path).exists():
            if verbose:
                print(f"Testing with image: {image_path}")

            response = manager.vision(
                prompt="Describe this image briefly in one sentence.",
                image_path=image_path,
                max_tokens=100
            )

            if verbose:
                print(f"✅ Vision API working!")
                print(f"Response: {response}")

            return True
        else:
            if verbose:
                print("⚠️  No test image provided. Skipping vision test.")
                print("   Run: test_vision_api('path/to/image.png')")
            return False

    except Exception as e:
        if verbose:
            print(f"❌ Vision API failed: {e}")
        return False


# =============================================================================
# Convenience Functions
# =============================================================================

def get_azure_openai_manager() -> AzureOpenAIManager:
    """Get configured Azure OpenAI manager (singleton-style)."""
    return AzureOpenAIManager()


# =============================================================================
# CLI Test Runner
# =============================================================================

if __name__ == "__main__":
    import sys

    print("Azure OpenAI API Utilities")
    print()

    # Run tests
    results = test_api_keys(verbose=True)

    # Test vision if image provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print()
        test_vision_api(image_path, verbose=True)

    # Exit with status (chat completion is critical, embeddings optional)
    if results.get("chat_completion"):
        print()
        if all(results.values()):
            print("🎉 All tests passed! Azure OpenAI is fully ready.")
        else:
            print("✅ Azure OpenAI is ready (chat working)!")
            print("   Note: Some optional features not available")
        sys.exit(0)
    else:
        print()
        print("⚠️  Critical tests failed. Please check your configuration.")
        sys.exit(1)
