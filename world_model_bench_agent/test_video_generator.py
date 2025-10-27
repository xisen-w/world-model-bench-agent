#!/usr/bin/env python3
"""
Test script for Video World Generator.

Tests converting image worlds to video worlds with transition videos.
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

from world_model_bench_agent.video_world_generator import (
    VideoWorldGenerator,
    load_image_world_and_generate_videos
)
from world_model_bench_agent.image_world_generator import ImageWorld
from utils.veo import VeoVideoGenerator


def test_single_transition():
    """Test generating video for a single transition."""
    print("\n" + "=" * 70)
    print("TEST 1: Single Transition Video Generation")
    print("=" * 70)

    # Check for existing image worlds
    image_world_files = list(Path(".").glob("*_image_world.json"))

    if not image_world_files:
        print("No image world files found.")
        print("Please run test_image_generator.py first to create image worlds.")
        return None

    print(f"\nFound {len(image_world_files)} image worlds:")
    for i, f in enumerate(image_world_files, 1):
        print(f"  {i}. {f.name}")

    # Use the first one
    image_world_file = image_world_files[0]
    print(f"\nUsing: {image_world_file}")

    try:
        # Load image world
        image_world = ImageWorld.load(str(image_world_file))
        print(f"Loaded image world: {image_world.name}")
        print(f"  States: {len(image_world.states)}")
        print(f"  Transitions: {len(image_world.transitions)}")

        if not image_world.transitions:
            print("ERROR: No transitions found in image world")
            return None

        # Show first transition
        first_transition = image_world.transitions[0]
        print(f"\nFirst transition:")
        print(f"  Action: {first_transition.action_description}")
        print(f"  {first_transition.start_state_id} -> {first_transition.end_state_id}")

        # Initialize Veo client
        print("\nInitializing Veo client...")
        from google import genai
        client = genai.Client(api_key=api_key)
        veo = VeoVideoGenerator(
            api_key=api_key,
            client=client,
            acknowledged_paid_feature=True
        )
        print("Veo client initialized")

        # Estimate cost
        print(f"\nWill generate 1 video (5 seconds)")
        print(f"Estimated cost: $0.05 - $0.10")
        print(f"Estimated time: 2-5 minutes")

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

        # Generate video
        print("\nGenerating video for first transition...")
        generator = VideoWorldGenerator(veo_client=veo, resolution="720p")

        video_transition = generator.generate_transition_on_demand(
            image_world=image_world,
            transition_index=0,
            number_of_videos=1
        )

        if video_transition.video_path:
            print(f"\nSUCCESS! Video generated:")
            print(f"  Path: {video_transition.video_path}")
            print(f"  Prompt: {video_transition.generation_prompt[:80]}...")
            return video_transition
        else:
            print(f"\nERROR: Video generation failed")
            return None

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_canonical_path_videos():
    """Test generating videos for all transitions in canonical path."""
    print("\n\n" + "=" * 70)
    print("TEST 2: Canonical Path Video Generation")
    print("=" * 70)

    # Check for existing image worlds
    image_world_files = list(Path(".").glob("*_image_world.json"))

    if not image_world_files:
        print("No image world files found.")
        return None

    # Use the first one
    image_world_file = image_world_files[0]
    print(f"\nUsing: {image_world_file}")

    try:
        # Load image world
        image_world = ImageWorld.load(str(image_world_file))
        print(f"Loaded image world: {image_world.name}")

        # Count canonical transitions
        canonical_count = 0
        for transition in image_world.transitions:
            # Check if end state has this transition as parent
            for state in image_world.states:
                if (state.state_id == transition.end_state_id and
                    state.parent_state_id == transition.start_state_id):
                    canonical_count += 1
                    break

        if canonical_count == 0:
            canonical_count = len(image_world.transitions)

        print(f"  Canonical transitions: {canonical_count}")

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
        estimated_cost_min = canonical_count * 0.05
        estimated_cost_max = canonical_count * 0.10
        estimated_time_min = canonical_count * 2
        estimated_time_max = canonical_count * 5

        print(f"\nWill generate {canonical_count} videos")
        print(f"Estimated cost: ${estimated_cost_min:.2f} - ${estimated_cost_max:.2f}")
        print(f"Estimated time: {estimated_time_min}-{estimated_time_max} minutes")
        print("\nWARNING: This is expensive and time-consuming!")

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

        # Generate videos
        print("\nGenerating videos for canonical path...")
        generator = VideoWorldGenerator(veo_client=veo, resolution="720p")

        video_world = generator.generate_video_world(
            image_world=image_world,
            strategy="canonical_only",
            number_of_videos=1
        )

        print(f"\nSUCCESS! Generated {len(video_world.transitions)} videos")
        print("\nGenerated videos:")
        for video_trans in video_world.transitions:
            print(f"  [{video_trans.action_id}] {video_trans.video_path}")
            print(f"      {video_trans.action_description[:60]}...")

        # Save video world
        output_name = image_world_file.stem.replace("_image_world", "_video_world") + ".json"
        video_world.save(output_name)
        print(f"\nSaved to: {output_name}")

        return video_world

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_batch_generation():
    """Test generating videos for a specific batch of transitions."""
    print("\n\n" + "=" * 70)
    print("TEST 3: Batch Video Generation (First 2 Transitions)")
    print("=" * 70)

    # Check for existing image worlds
    image_world_files = list(Path(".").glob("*_image_world.json"))

    if not image_world_files:
        print("No image world files found.")
        return None

    image_world_file = image_world_files[0]
    print(f"\nUsing: {image_world_file}")

    try:
        # Load image world
        image_world = ImageWorld.load(str(image_world_file))
        print(f"Loaded image world: {image_world.name}")

        if len(image_world.transitions) < 2:
            print("Not enough transitions for batch test")
            return None

        print(f"\nWill generate videos for first 2 transitions:")
        for i in range(2):
            trans = image_world.transitions[i]
            print(f"  {i+1}. {trans.action_description}")

        # Initialize Veo
        from google import genai
        client = genai.Client(api_key=api_key)
        veo = VeoVideoGenerator(
            api_key=api_key,
            client=client,
            acknowledged_paid_feature=True
        )

        print(f"\nEstimated cost: $0.10 - $0.20")
        print(f"Estimated time: 4-10 minutes")

        if sys.stdin.isatty():
            response = input("\nProceed? (yes/no): ").strip().lower()
            if response != "yes":
                print("Test cancelled")
                return None
        else:
            if "--yes" not in sys.argv:
                print("\nNon-interactive mode. Add --yes flag to proceed.")
                return None

        # Generate videos
        generator = VideoWorldGenerator(veo_client=veo, resolution="720p")

        video_transitions = generator.generate_batch_transitions(
            image_world=image_world,
            transition_indices=[0, 1],
            number_of_videos=1
        )

        print(f"\nSUCCESS! Generated {len(video_transitions)} videos")
        for vt in video_transitions:
            print(f"  {vt.video_path}")

        return video_transitions

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run video generation tests."""
    print("\n" + "=" * 70)
    print("VIDEO WORLD GENERATOR TEST SUITE")
    print("=" * 70)
    print("\nThis will test converting image worlds to video worlds.")
    print("Each video generation takes 2-5 minutes and costs $0.05-$0.10.")
    print("\nNOTE: Requires valid GEMINI_KEY and existing image worlds.")
    print("See API_KEY_SETUP.md if you have API key issues.")

    # Test 1: Single transition (cheapest)
    result1 = test_single_transition()

    if not result1:
        print("\nTest 1 failed or was skipped. Cannot proceed with other tests.")
        return 1

    # Ask about Test 2 (more expensive)
    if "--all" in sys.argv:
        run_test2 = True
    elif sys.stdin.isatty():
        response = input("\nRun Test 2 (canonical path, multiple videos)? (yes/no): ").strip().lower()
        run_test2 = (response == "yes")
    else:
        run_test2 = False

    if run_test2:
        result2 = test_canonical_path_videos()

    # Ask about Test 3
    if "--batch" in sys.argv or ("--all" in sys.argv):
        run_test3 = True
    elif sys.stdin.isatty() and result1:
        response = input("\nRun Test 3 (batch generation, 2 videos)? (yes/no): ").strip().lower()
        run_test3 = (response == "yes")
    else:
        run_test3 = False

    if run_test3:
        result3 = test_batch_generation()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)

    if result1:
        print("\nGenerated Files:")
        print("  - generated_videos/[world_name]_videos/*.mp4")
        print("\nYou can now:")
        print("  1. View the generated videos")
        print("  2. Inspect the video world JSON")
        print("  3. Use for AI model evaluation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
