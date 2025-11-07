#!/usr/bin/env python3
"""
Test full world video generation with all connecting paths.

This test generates videos for ALL transitions in the branching apple world.
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
print("FULL WORLD VIDEO GENERATION TEST")
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

print(f"\n  All Transitions:")
for i, trans in enumerate(image_world.transitions, 1):
    print(f"    {i}. {trans.start_state_id} --[{trans.action_id}]--> {trans.end_state_id}")
    print(f"       Action: {trans.action_description}")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Generate videos for ALL TRANSITIONS
print("\n" + "=" * 70)
print("GENERATING VIDEOS FOR ALL TRANSITIONS (FULL WORLD)")
print("=" * 70)
print(f"\nThis will generate {len(image_world.transitions)} videos")
print("Estimated time: ~7-10 minutes per video")
print(f"Total estimated time: ~{len(image_world.transitions) * 8} minutes")
print(f"Estimated cost: ~${len(image_world.transitions) * 0.10:.2f}")

# Ask for confirmation
print("\nWARNING: This will take significant time and cost!")
response = input("Do you want to continue? (yes/no): ")
if response.lower() not in ['yes', 'y']:
    print("Cancelled by user.")
    sys.exit(0)

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
    for i, video_trans in enumerate(video_world.transitions, 1):
        print(f"\n  {i}. {video_trans.start_state_id} → {video_trans.end_state_id}")
        print(f"     Action: {video_trans.action_description}")
        print(f"     Video: {video_trans.video_path}")
        print(f"     Status: {'✓ Success' if video_trans.video_path else '✗ Failed'}")

    # Save the video world
    output_file = "apple_eating_branching_video_world.json"
    video_world.save(output_file)
    print(f"\n\nSaved to: {output_file}")

    print("\nVideos saved to:")
    print(f"  generated_videos/{video_world.name}/")

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(f"✓ Expected transitions: {len(image_world.transitions)}")
    print(f"✓ Generated video transitions: {len(video_world.transitions)}")

    # Count successful videos
    successful_videos = sum(1 for vt in video_world.transitions if vt.video_path)
    print(f"✓ Successful video generations: {successful_videos}/{len(video_world.transitions)}")

    if len(video_world.transitions) == len(image_world.transitions):
        print("\n✅ All transitions processed!")
    else:
        print(f"\n⚠️  Transition count mismatch!")

    if successful_videos == len(video_world.transitions):
        print("✅ All videos generated successfully!")
    else:
        failed = len(video_world.transitions) - successful_videos
        print(f"⚠️  {failed} video(s) failed to generate")

    print("\n" + "=" * 70)
    print("WORLD STRUCTURE")
    print("=" * 70)
    print("\nBranching paths visualized:")
    print("                    s0")
    print("                  /    \\")
    print("           [a0a]          [a0b]")
    print("              /                \\")
    print("           s1a                 s1b")
    print("          /   \\               /   \\")
    print("    [a1a]     [a1b]     [a1c]     [a1d]")
    print("      /          \\         |         |")
    print("    s2a         s2b      s2c       s2d")
    print("   (GOAL)         |     (GOAL)")
    print("              [a2a]")
    print("                 |")
    print("               s3a")
    print("              (GOAL)")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
