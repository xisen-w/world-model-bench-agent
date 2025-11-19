#!/usr/bin/env python3
"""
Generate video world for indoor_plant_egocentric_branching.

This script loads the indoor plant image world and generates videos for all transitions
using Google's Veo video generation API.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get API key
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found in .env file")
    sys.exit(1)

# Import required modules
from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

def main():
    """Generate video world for indoor plant egocentric branching scenario."""

    print("=" * 70)
    print("INDOOR PLANT VIDEO WORLD GENERATION")
    print("=" * 70)

    # Define paths
    image_world_file = "worlds/image_worlds/indoor_plant_watering_repotting_branching_egocentric_image_world.json"
    print(f"\nLoading image world from: {image_world_file}")

    if not Path(image_world_file).exists():
        print(f"ERROR: {image_world_file} not found!")
        sys.exit(1)

    # Load image world
    image_world = ImageWorld.load(image_world_file)

    print(f"\nImage World Summary:")
    print(f"  Name: {image_world.name}")
    print(f"  States: {len(image_world.states)}")
    print(f"  Transitions: {len(image_world.transitions)}")

    print(f"\n  All Transitions to Generate:")
    for i, trans in enumerate(image_world.transitions, 1):
        print(f"    {i}. {trans.start_state_id} → {trans.end_state_id}")
        print(f"       Action: {trans.action_description[:80]}...")

    # Initialize Veo
    print("\nInitializing Veo Video Generator...")
    client = genai.Client(api_key=api_key)
    veo = VeoVideoGenerator(
        api_key=api_key,
        client=client,
        acknowledged_paid_feature=True
    )

    print(f"  Provider: {veo.provider_name}")
    print(f"  Model: {veo.model_name}")

    # Estimate costs
    num_transitions = len(image_world.transitions)
    estimated_time = num_transitions * 8  # ~8 minutes per video
    estimated_cost = num_transitions * 0.10  # ~$0.10 per video

    print("\n" + "=" * 70)
    print("GENERATION PLAN")
    print("=" * 70)
    print(f"Number of videos to generate: {num_transitions}")
    print(f"Estimated time: ~{estimated_time} minutes ({estimated_time/60:.1f} hours)")
    print(f"Estimated cost: ~${estimated_cost:.2f}")
    print("\nEach video will use:")
    print("  - Start image and end image from the image world")
    print("  - Action description as the video prompt")
    print("  - Enhanced cinematic prompts for better quality")

    # Auto-confirm (skip prompt)
    print("\n" + "=" * 70)
    print("\nProceeding with video generation...")

    # Generate videos
    print("\n" + "=" * 70)
    print("GENERATING VIDEOS FOR ALL TRANSITIONS")
    print("=" * 70)
    print("\nStarting generation...")

    generator = VideoWorldGenerator(
        veo_client=veo,
        output_dir="generated_videos",
        use_enhanced_prompts=True  # Use enhanced cinematic prompts
    )

    try:
        video_world = generator.generate_video_world(
            image_world=image_world,
            strategy="all_transitions",  # Generate ALL transitions
            number_of_videos=1
        )

        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)

        # Display results
        print(f"\nGenerated {len(video_world.transitions)} videos:")
        successful = 0
        failed = 0

        for i, video_trans in enumerate(video_world.transitions, 1):
            status = "✓" if video_trans.video_path else "✗"
            if video_trans.video_path:
                successful += 1
            else:
                failed += 1

            print(f"  {status} {i}. {video_trans.start_state_id} → {video_trans.end_state_id}")
            if video_trans.video_path:
                print(f"     Video: {video_trans.video_path}")

        # Save the video world
        output_file = "indoor_plant_watering_repotting_branching_egocentric_video_world.json"
        video_world.save(output_file)
        print(f"\n\nVideo World saved to: worlds/video_worlds/{output_file}")

        print("\nVideos saved to:")
        print(f"  generated_videos/{video_world.name}/")

        print("\n" + "=" * 70)
        print("FINAL STATISTICS")
        print("=" * 70)
        print(f"Total transitions: {len(image_world.transitions)}")
        print(f"Videos generated successfully: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {successful/len(image_world.transitions)*100:.1f}%")

        if successful == len(image_world.transitions):
            print("\n✅ All videos generated successfully!")
            return 0
        else:
            print(f"\n⚠️  {failed} video(s) failed to generate")
            return 1

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
