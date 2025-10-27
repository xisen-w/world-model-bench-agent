#!/usr/bin/env python3
"""Test video generation for apple eating world with fixed veo.py."""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

sys.path.insert(0, str(script_dir))

# Load environment
env_path = script_dir / ".env"
load_dotenv(env_path)

from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from utils.veo import VeoVideoGenerator
from google import genai
import os

print("=" * 70)
print("TESTING FIXED VIDEO GENERATION FOR APPLE EATING WORLD")
print("=" * 70)

# Load the apple_eating world
world_file = script_dir / "apple_eating_image_world.json"
if not world_file.exists():
    print(f"\nERROR: {world_file} not found")
    print("Please run test_dramatic_changes.py first to generate the world")
    sys.exit(1)

with open(world_file) as f:
    world_data = json.load(f)

print(f"\nLoaded world: {world_data['name']}")
print(f"States: {len(world_data['states'])}")
print(f"Transitions: {len(world_data.get('transitions', []))}")

# Initialize Veo client
print("\nInitializing Veo client...")
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

client = genai.Client(api_key=api_key)
veo_client = VeoVideoGenerator(
    api_key=api_key,
    client=client,
    acknowledged_paid_feature=True
)

print("Veo client initialized")

# Initialize video generator
print("Initializing VideoWorldGenerator...")
video_gen = VideoWorldGenerator(
    veo_client=veo_client,
    aspect_ratio="16:9",
    resolution="720p"
)

print("Video generator initialized")

# Load image world
from world_model_bench_agent.image_world_generator import ImageWorld

print("\nLoading ImageWorld from JSON...")
image_world = ImageWorld.load(str(world_file))

# Generate videos for all transitions
print("\n" + "=" * 70)
print("GENERATING TRANSITION VIDEOS")
print("=" * 70)

output_path = Path("apple_eating_world_videos.json")

try:
    video_world = video_gen.generate_video_world(
        image_world=image_world,
        strategy="all_transitions"
    )

    # Save to file
    video_world.save(str(output_path))

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nVideo world saved to: {output_path}")
    print(f"Total transitions with videos: {len(video_world.transitions)}")

    # Show generated video files
    print("\nGenerated videos:")
    for trans in video_world.transitions:
        if trans.video_path:
            print(f"  - {trans.video_path}")

except Exception as e:
    print("\n" + "=" * 70)
    print("ERROR")
    print("=" * 70)
    print(f"\n{type(e).__name__}: {e}")

    import traceback
    traceback.print_exc()
    sys.exit(1)
