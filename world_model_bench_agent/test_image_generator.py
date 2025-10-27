#!/usr/bin/env python3
"""
Test script for Image World Generator.

Tests converting text worlds to vision worlds with consistent images.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Verify API key
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print(f"ERROR: GEMINI_KEY not found in environment")
    print(f"Tried loading from: {env_path}")
    print(f"File exists: {env_path.exists()}")
    print("\nPlease see API_KEY_SETUP.md for instructions on getting a valid API key.")
    sys.exit(1)

print(f"API key loaded successfully")

from world_model_bench_agent.image_world_generator import (
    ImageWorldGenerator,
    load_text_world_and_generate_images
)
from world_model_bench_agent.benchmark_curation import World
from utils.veo import VeoVideoGenerator


def test_simple_linear_world():
    """Test with a simple handcrafted linear world."""
    print("\n" + "=" * 70)
    print("TEST 1: Simple Linear World (3 states)")
    print("=" * 70)

    # Create simple world
    from world_model_bench_agent.benchmark_curation import State, Action, Transition

    s0 = State(description="Empty cup on kitchen table", state_id="s0")
    s1 = State(description="Cup filled with hot water from kettle", state_id="s1")
    s2 = State(description="Tea bag steeping in cup of hot water", state_id="s2")

    a0 = Action(description="Pour hot water from kettle into cup", action_id="a0")
    a1 = Action(description="Place tea bag into cup", action_id="a1")

    t0 = Transition(start_state=s0, action=a0, end_state=s1)
    t1 = Transition(start_state=s1, action=a1, end_state=s2)

    world = World(
        name="simple_tea",
        description="Simple tea making process",
        states=[s0, s1, s2],
        actions=[a0, a1],
        transitions=[t0, t1],
        initial_state=s0,
        goal_states=[s2]
    )

    # Save text world
    world.save("simple_tea_world.json")
    print(f"Created text world with {len(world.states)} states")

    # Initialize Veo client
    print("\nInitializing Veo client...")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        veo = VeoVideoGenerator(
            api_key=api_key,
            client=client,
            acknowledged_paid_feature=True
        )
        print("Veo client initialized")
    except Exception as e:
        print(f"ERROR initializing Veo client: {e}")
        print("\nPlease check API_KEY_SETUP.md for instructions.")
        return None

    # Generate images
    print("\nGenerating images for canonical path...")
    print("WARNING: This will make 3 API calls (1 initial + 2 variations)")
    print("Estimated cost: ~$0.01")

    # Check if running interactively
    if sys.stdin.isatty():
        response = input("\nProceed? (yes/no): ").strip().lower()
        if response != "yes":
            print("Test cancelled")
            return None
    else:
        if "--yes" not in sys.argv:
            print("\nNon-interactive mode. Add --yes flag to proceed.")
            return None

    try:
        generator = ImageWorldGenerator(
            veo_client=veo,
            output_dir="generated_images"
        )

        image_world = generator.generate_image_world(
            text_world=world,
            strategy="canonical_path"
        )

        print(f"\nSUCCESS! Generated {len(image_world.states)} images")
        print("\nGenerated images:")
        for img_state in image_world.states:
            print(f"  [{img_state.state_id}] {img_state.image_path}")
            print(f"      {img_state.text_description[:60]}...")

        # Save image world
        image_world.save("simple_tea_image_world.json")
        print(f"\nSaved to: simple_tea_image_world.json")

        return image_world

    except Exception as e:
        print(f"\nERROR during image generation: {type(e).__name__}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_load_existing_world():
    """Test loading an existing text world and generating images."""
    print("\n\n" + "=" * 70)
    print("TEST 2: Load Existing Text World")
    print("=" * 70)

    # Check for existing worlds
    world_files = list(Path(".").glob("*_world.json"))
    # Filter out image worlds
    world_files = [f for f in world_files if "image" not in f.name]

    if not world_files:
        print("No text world files found. Skipping this test.")
        print("Run test_generator.py first to create text worlds.")
        return None

    print(f"\nFound {len(world_files)} text worlds:")
    for i, f in enumerate(world_files, 1):
        print(f"  {i}. {f.name}")

    # Use the first one
    world_file = world_files[0]
    print(f"\nUsing: {world_file}")

    try:
        world = World.load(str(world_file))
        print(f"Loaded world: {world.name}")
        print(f"  States: {len(world.states)}")
        print(f"  Goal states: {len(world.goal_states)}")

        # Check if it has successful paths
        paths = world.get_successful_paths()
        if not paths:
            print("WARNING: World has no successful paths. Cannot generate images.")
            return None

        print(f"  Successful paths: {len(paths)}")
        print(f"  Canonical path length: {len(paths[0])} transitions")

        # Initialize Veo
        print("\nInitializing Veo client...")
        from google import genai
        client = genai.Client(api_key=api_key)
        veo = VeoVideoGenerator(
            api_key=api_key,
            client=client,
            acknowledged_paid_feature=True
        )

        # Estimate cost
        num_images = len(paths[0]) + 1  # +1 for initial state
        estimated_cost = 0.003 + (num_images - 1) * 0.002
        print(f"\nWill generate {num_images} images")
        print(f"Estimated cost: ${estimated_cost:.3f}")

        # Check if running interactively
        if sys.stdin.isatty():
            response = input("\nProceed? (yes/no): ").strip().lower()
            if response != "yes":
                print("Test cancelled")
                return None
        else:
            if "--yes" not in sys.argv:
                print("\nNon-interactive mode. Add --yes flag to proceed.")
                return None

        # Generate images
        generator = ImageWorldGenerator(veo_client=veo)
        image_world = generator.generate_image_world(
            text_world=world,
            strategy="canonical_path"
        )

        print(f"\nSUCCESS! Generated {len(image_world.states)} images")

        # Save
        output_name = world_file.stem + "_image_world.json"
        image_world.save(output_name)
        print(f"Saved to: {output_name}")

        return image_world

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run image generation tests."""
    print("\n" + "=" * 70)
    print("IMAGE WORLD GENERATOR TEST SUITE")
    print("=" * 70)
    print("\nThis will test converting text worlds to vision worlds.")
    print("Each test makes several image generation API calls.")
    print("\nNOTE: Requires valid GEMINI_KEY in .env file.")
    print("See API_KEY_SETUP.md if you have API key issues.")

    # Test 1: Simple world
    result1 = test_simple_linear_world()

    # Test 2: Existing world (if available)
    if "--all" in sys.argv or (sys.stdin.isatty() and result1):
        input("\nPress Enter to run Test 2 (or Ctrl+C to stop)...")
        result2 = test_load_existing_world()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)

    if result1:
        print("\nGenerated Files:")
        print("  - simple_tea_world.json (text world)")
        print("  - simple_tea_image_world.json (image world)")
        print("  - generated_images/simple_tea_images/*.png (images)")
        print("\nYou can now:")
        print("  1. View the generated images")
        print("  2. Inspect the image world JSON")
        print("  3. Use for video generation (next step)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
