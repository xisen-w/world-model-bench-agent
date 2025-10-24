#!/usr/bin/env python3
"""
Example usage of VeoVideoGenerator for video generation.

This script demonstrates how to use the VeoVideoGenerator class to:
1. Generate images from text prompts
2. Generate videos from text prompts
3. Generate videos from images
4. Check generation status
5. Download generated content

NOTE: This requires a valid GEMINI_KEY in your .env file and will make
actual API calls to Google's Gemini/Veo services.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Import required modules
from utils.veo import VeoVideoGenerator
from utils.unified_interface import VideoGenerationError


def setup_veo_generator():
    """Initialize the VeoVideoGenerator with proper configuration."""
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        raise ValueError("GEMINI_KEY not found in .env file")

    print("Setting up VeoVideoGenerator...")
    print(f"API Key: {api_key[:10]}...")

    try:
        import google.generativeai as genai

        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # Create VeoVideoGenerator instance
        veo_gen = VeoVideoGenerator(
            api_key=api_key,
            client=genai,  # Pass the configured genai module
            acknowledged_paid_feature=True,  # Acknowledge that this is a paid feature
            poll_interval_seconds=20,  # Check every 20 seconds
            operation_timeout_seconds=600,  # 10 minute timeout
        )

        print(f"SUCCESS: VeoVideoGenerator initialized")
        print(f"  Provider: {veo_gen.provider_name}")
        print(f"  Model: {veo_gen.model_name}")
        print(f"  Image Model: {veo_gen.image_model_id}")

        return veo_gen

    except ImportError as e:
        raise ImportError(
            f"Failed to import google.generativeai: {e}\n"
            "Install it with: pip install google-generativeai"
        )


def example_1_generate_image(veo_gen):
    """Example 1: Generate an image from a text prompt."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Generate Image from Text Prompt")
    print("=" * 70)

    prompt = "A futuristic cityscape at sunset with flying cars"
    print(f"\nPrompt: {prompt}")
    print("Generating image...")

    try:
        image = veo_gen.generate_image_from_prompt(
            prompt=prompt,
            aspect_ratio="16:9",
            negative_prompt="blurry, low quality, distorted",
            save_path="output/example1_cityscape.png"
        )

        print(f"SUCCESS: Image generated successfully!")
        print(f"  Size: {image.size}")
        print(f"  Format: {image.format}")
        print(f"  Saved to: output/example1_cityscape.png")

        return image

    except Exception as e:
        print(f"FAILED: Failed: {type(e).__name__}: {e}")
        return None


def example_2_generate_video_from_prompt(veo_gen):
    """Example 2: Generate a video from a text prompt only."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Generate Video from Text Prompt")
    print("=" * 70)

    prompt = "A dolphin jumping out of crystal clear ocean water in slow motion"
    print(f"\nPrompt: {prompt}")
    print("Generating video (this may take several minutes)...")

    try:
        result = veo_gen.generate_video_from_prompt_only(
            prompt=prompt,
            aspect_ratio="16:9",
            resolution="720p",
            negative_prompt="static, still image, blurry",
            number_of_videos=1
        )

        print(f"\nSUCCESS: Video generation complete!")
        print(f"  Video ID: {result.id}")
        print(f"  Status: {result.status}")
        print(f"  Progress: {result.progress * 100:.1f}%")
        print(f"  Model: {result.model}")
        print(f"  Quality: {result.quality}")
        print(f"  Size: {result.size}")

        if result.download_url:
            print(f"  Download URL: {result.download_url[:50]}...")

        # Download the video
        if result.status.lower() == "completed":
            output_path = "output/example2_dolphin.mp4"
            print(f"\nDownloading video to {output_path}...")
            veo_gen.download_video(result.id, output_path)
            print(f"SUCCESS: Video downloaded successfully!")

        return result

    except Exception as e:
        print(f"FAILED: Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def example_3_generate_video_from_image(veo_gen, image=None):
    """Example 3: Generate a video from an image."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Generate Video from Image")
    print("=" * 70)

    if image is None:
        print("\nNo input image provided, generating one first...")
        image = veo_gen.generate_image_from_prompt(
            prompt="A serene forest path in autumn",
            aspect_ratio="16:9"
        )
        print("SUCCESS: Generated starting image")

    prompt = "Camera slowly moves forward along the forest path"
    print(f"\nPrompt: {prompt}")
    print("Generating video from image (this may take several minutes)...")

    try:
        result = veo_gen.generate_video_with_image(
            prompt=prompt,
            start_image=image,
            aspect_ratio="16:9",
            resolution="720p",
            number_of_videos=1
        )

        print(f"\nSUCCESS: Video generation complete!")
        print(f"  Video ID: {result.id}")
        print(f"  Status: {result.status}")
        print(f"  Progress: {result.progress * 100:.1f}%")

        if result.status.lower() == "completed":
            output_path = "output/example3_forest_walk.mp4"
            print(f"\nDownloading video to {output_path}...")
            veo_gen.download_video(result.id, output_path)
            print(f"SUCCESS: Video downloaded successfully!")

        return result

    except Exception as e:
        print(f"FAILED: Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def example_4_unified_interface(veo_gen):
    """Example 4: Using the unified generate_video interface."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Using Unified generate_video Interface")
    print("=" * 70)

    print("\nThe VeoVideoGenerator provides a smart dispatcher that")
    print("automatically selects the right generation method based on inputs.")

    # Example 4a: Prompt-only (auto-routes to generate_video_from_prompt_only)
    print("\n4a. Prompt-only generation:")
    result = veo_gen.generate_video(
        prompt="A bird flying through clouds",
        size="16:9",
        quality="720p"
    )
    print(f"   Routed to: prompt-only generation")
    print(f"   Status: {result.status}")

    return result


def example_5_check_status(veo_gen, video_id):
    """Example 5: Check the status of a video generation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Check Video Generation Status")
    print("=" * 70)

    print(f"\nChecking status for video ID: {video_id}")

    try:
        result = veo_gen.get_status(video_id)

        print(f"\nStatus Information:")
        print(f"  Video ID: {result.id}")
        print(f"  Status: {result.status}")
        print(f"  Progress: {result.progress * 100:.1f}%")
        print(f"  Prompt: {result.prompt}")

        if result.download_url:
            print(f"  Download URL available: Yes")
        else:
            print(f"  Download URL available: No (still processing)")

        return result

    except Exception as e:
        print(f"FAILED: Failed: {type(e).__name__}: {e}")
        return None


def main():
    """Run all examples."""
    print("=" * 70)
    print("  VEO VIDEO GENERATOR - USAGE EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates various use cases for VeoVideoGenerator.")
    print("\nWARNING: These examples will make actual API calls to Google's")
    print("Gemini/Veo services and may incur charges on your account.")

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir.absolute()}")

    # Confirm with user
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != "yes":
        print("Exiting without running examples.")
        return 0

    try:
        # Setup
        veo_gen = setup_veo_generator()

        # Run examples
        # Note: Comment out examples you don't want to run to save API costs

        # Example 1: Generate image (relatively quick and cheap)
        image = example_1_generate_image(veo_gen)

        # Example 2: Generate video from prompt (slow and expensive)
        # Uncomment to run:
        # video_result = example_2_generate_video_from_prompt(veo_gen)

        # Example 3: Generate video from image (slow and expensive)
        # Uncomment to run:
        # if image:
        #     video_result = example_3_generate_video_from_image(veo_gen, image)

        # Example 4: Unified interface
        # Uncomment to run:
        # result = example_4_unified_interface(veo_gen)

        # Example 5: Check status (only works if you have a video_id)
        # Uncomment to run:
        # if 'video_result' in locals():
        #     example_5_check_status(veo_gen, video_result.id)

        print("\n" + "=" * 70)
        print("  EXAMPLES COMPLETE")
        print("=" * 70)
        print("\nCheck the 'output/' directory for generated files.")
        print("\nTo run video generation examples, uncomment them in the code.")
        print("Note: Video generation can take 5-10 minutes and incurs API costs.")

        return 0

    except Exception as e:
        print(f"\nFAILED: Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
