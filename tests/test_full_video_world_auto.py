#!/usr/bin/env python3
"""
Test full world video generation - AUTOMATED (no prompts).

This test generates videos for ALL transitions in the branching apple world.
Use this for CI/CD or when you want to run without manual confirmation.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

# Load the branching image world
print("=" * 70)
print("FULL WORLD VIDEO GENERATION TEST (AUTOMATED)")
print("=" * 70)

image_world_file = "apple_eating_branching_image_world.json"
print(f"\nLoading image world from: {image_world_file}")

if not Path(image_world_file).exists():
    print(f"ERROR: {image_world_file} not found!")
    print("Please run test_full_apple_world.py first to generate the image world.")
    sys.exit(1)

image_world = ImageWorld.load(image_world_file)

print(f"\nImage World Summary:")
print(f"  Name: {image_world.name}")
print(f"  States: {len(image_world.states)}")
print(f"  Transitions: {len(image_world.transitions)}")

print(f"\n  All Transitions to Generate:")
for i, trans in enumerate(image_world.transitions, 1):
    print(f"    {i}. {trans.start_state_id} → {trans.end_state_id} ({trans.action_id})")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Generate videos for ALL TRANSITIONS
print("\n" + "=" * 70)
print("GENERATING VIDEOS FOR ALL TRANSITIONS (FULL WORLD)")
print("=" * 70)
print(f"\nGenerating {len(image_world.transitions)} videos...")
print(f"Estimated time: ~{len(image_world.transitions) * 8} minutes")
print(f"Estimated cost: ~${len(image_world.transitions) * 0.10:.2f}")
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
    output_file = "apple_eating_branching_video_world.json"
    video_world.save(output_file)
    print(f"\n\nSaved to: {output_file}")

    print("\nVideos saved to:")
    print(f"  generated_videos/{video_world.name}/")

    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    print(f"Total transitions: {len(image_world.transitions)}")
    print(f"Videos generated: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful/len(image_world.transitions)*100:.1f}%")

    if successful == len(image_world.transitions):
        print("\n✅ All videos generated successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} video(s) failed to generate")
        sys.exit(1)

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
