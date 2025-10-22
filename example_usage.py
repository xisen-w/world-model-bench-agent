#!/usr/bin/env python3
"""
Example usage of the AC-World Video Generation Framework

This script demonstrates how to use the unified video generation interface
to generate videos for the Action-Conditioned World Model benchmark.
"""

import os
import asyncio
from dotenv import load_dotenv

# Import our video generation utilities
from utils import VideoGenerationManager, SoraVideoGenerator


async def main():
    """Main example function demonstrating video generation."""

    # Load environment variables
    load_dotenv()

    # Initialize the video generation manager
    manager = VideoGenerationManager()

    # Register the Sora/OpenAI provider
    sora_api_key = os.getenv("OPENAI_API_KEY")
    if not sora_api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment")
        return

    sora_generator = SoraVideoGenerator(api_key=sora_api_key)
    manager.register_provider("sora", sora_generator)

    print("🎬 AC-World Video Generation Example")
    print("=" * 50)

    # Example prompts for different benchmark scenarios
    test_prompts = [
        {
            "name": "Simple Action Inference",
            "prompt": "A calico cat playing a piano on stage",
            "description": "Test basic video generation capability"
        },
        {
            "name": "Action-Conditioned Example",
            "prompt": "A person sitting at a desk, then standing up and walking to the door",
            "description": "Test temporal action sequence"
        },
        {
            "name": "Scene Transition Test",
            "prompt": "Initial: cup on table. Goal: cup on shelf. Show the action sequence.",
            "description": "Test action-conditioned world model scenario"
        }
    ]

    for i, test_case in enumerate(test_prompts, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        print(f"Prompt: {test_case['prompt']}")
        print(f"Description: {test_case['description']}")

        try:
            # Generate video using Sora
            result = manager.generate_video(
                provider_name="sora",
                prompt=test_case["prompt"],
                size="1024x1808",
                seconds="8",
                quality="standard"
            )

            print("
✅ Video generation started!"            print(f"   ID: {result.id}")
            print(f"   Status: {result.status}")
            print(f"   Progress: {result.progress:.1%}")
            print(f"   Model: {result.model}")
            print(f"   Provider: {result.provider}")

            # Check status after a short delay (simulating async behavior)
            await asyncio.sleep(2)
            status_result = manager.providers["sora"].get_status(result.id)
            print(f"   Updated Status: {status_result.status}")

            # Save result metadata
            with open(f"test_result_{i}.json", "w") as f:
                f.write(result.to_json())

            print(f"   📄 Results saved to: test_result_{i}.json")

        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")

    # Show provider information
    print("
📋 Provider Information:"    print("-" * 30)
    for provider_name in manager.get_available_providers():
        info = manager.get_provider_info(provider_name)
        print(f"• {provider_name}: {info['name']} ({info['model']})")
        print(f"  Features: {', '.join(info['features'])}")


def sync_example():
    """Synchronous example for simple usage."""
    print("\n🔄 Running synchronous example...")

    load_dotenv()
    manager = VideoGenerationManager()

    # Register Sora provider
    sora_api_key = os.getenv("OPENAI_API_KEY")
    if sora_api_key:
        sora_generator = SoraVideoGenerator(api_key=sora_api_key)
        manager.register_provider("sora", sora_generator)

        # Simple generation example
        try:
            result = manager.generate_video(
                "sora",
                "A simple test video of a cat",
                size="512x512",
                seconds="5"
            )
            print(f"✓ Generated video: {result.id}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("No OpenAI API key found")


if __name__ == "__main__":
    print("🚀 AC-World Video Generation Framework")
    print("=====================================")

    # Run async example
    asyncio.run(main())

    # Run sync example for comparison
    sync_example()

    print("
✨ Example completed!"    print("Check the generated JSON files for video generation results.")
    print("Next steps:")
    print("• Modify prompts in test_prompts array")
    print("• Add more video generation providers (Runway, Stability AI)")
    print("• Integrate with AC-World benchmark evaluation")


