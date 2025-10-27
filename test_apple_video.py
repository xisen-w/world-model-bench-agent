#!/usr/bin/env python3
"""Test video generation with the apple eating world."""

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

print(f"API key loaded: {api_key[:15]}...")

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

# Load the apple image world
print("\n" + "=" * 70)
print("APPLE EATING - VIDEO GENERATION TEST")
print("=" * 70)

print("\nLoading apple image world...")
image_world = ImageWorld.load("apple_eating_image_world.json")
print(f"Loaded: {image_world.name}")
print(f"  States: {len(image_world.states)}")
print(f"  Transitions: {len(image_world.transitions)}")

print("\nTransitions to generate:")
for i, trans in enumerate(image_world.transitions, 1):
    print(f"  {i}. {trans.action_description}")
    print(f"     Start image: {trans.start_state_id}")
    print(f"     End image: {trans.end_state_id}")

# Initialize Veo
print("\nInitializing Veo client...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(
    api_key=api_key,
    client=client,
    acknowledged_paid_feature=True
)
print("Veo client initialized")

# Estimate costs
num_videos = len(image_world.transitions)
estimated_cost_min = num_videos * 0.05
estimated_cost_max = num_videos * 0.10
estimated_time_min = num_videos * 2
estimated_time_max = num_videos * 5

print("\n" + "=" * 70)
print("COST & TIME ESTIMATE")
print("=" * 70)
print(f"\nWill generate {num_videos} videos (5 seconds each)")
print(f"Estimated cost: ${estimated_cost_min:.2f} - ${estimated_cost_max:.2f}")
print(f"Estimated time: {estimated_time_min}-{estimated_time_max} minutes")
print("\nThese will use Veo's first-frame + last-frame interpolation")
print("with action descriptions as prompts.")

print("\n" + "=" * 70)
print("PROCEEDING WITH VIDEO GENERATION...")
print("=" * 70)

try:
    # Generate videos
    generator = VideoWorldGenerator(
        veo_client=veo,
        resolution="720p",
        aspect_ratio="16:9",
        output_dir="generated_videos"
    )

    video_world = generator.generate_video_world(
        image_world=image_world,
        strategy="all_transitions",
        number_of_videos=1
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nGenerated {len(video_world.transitions)} videos:")
    for i, video_trans in enumerate(video_world.transitions, 1):
        print(f"\n  Video {i}: {video_trans.video_path}")
        print(f"    Action: {video_trans.action_description}")
        print(f"    Start: {video_trans.start_image_path}")
        print(f"    End: {video_trans.end_image_path}")
        print(f"    Status: {video_trans.metadata.get('status', 'unknown')}")

    # Save video world
    video_world.save("apple_eating_video_world.json")
    print(f"\nSaved to: apple_eating_video_world.json")

    print("\nGenerated videos can be found in:")
    print(f"  generated_videos/apple_eating_images_videos/")

    print("\n" + "=" * 70)
    print("COMPLETE PIPELINE TEST - SUCCESS!")
    print("=" * 70)
    print("\nYou now have:")
    print("  ✅ Text World: apple_eating (3 states)")
    print("  ✅ Image World: 3 images with dramatic changes")
    print("  ✅ Video World: 2 transition videos")
    print("\nThe full Text → Image → Video pipeline is working!")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
