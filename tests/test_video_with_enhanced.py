#!/usr/bin/env python3
"""Generate video with full enhanced prompts."""

import sys
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

from world_model_bench_agent.image_world_generator import ImageWorld
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from utils.veo import VeoVideoGenerator
from google import genai

print("=" * 80)
print("GENERATING VIDEO WITH FULL ENHANCED PROMPTS")
print("=" * 80)

# Load the apple_eating world
world_file = script_dir / "apple_eating_image_world.json"
image_world = ImageWorld.load(str(world_file))

print(f"\nLoaded world: {image_world.name}")
print(f"States: {len(image_world.states)}")
print(f"Transitions: {len(image_world.transitions)}")

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

# Initialize video generator WITH FULL ENHANCED PROMPTS
print("\nInitializing VideoWorldGenerator with ENHANCED prompts...")
video_gen = VideoWorldGenerator(
    veo_client=veo_client,
    aspect_ratio="16:9",
    resolution="720p",
    output_dir="generated_videos_enhanced",
    use_enhanced_prompts=True  # Enable full enhanced prompts
)

print("Video generator initialized")

# Generate videos
print("\n" + "=" * 80)
print("GENERATING TRANSITION VIDEOS WITH ENHANCED PROMPTS")
print("=" * 80)
print("\nThis will use comprehensive prompts including:")
print("  - Initial State (camera, lighting, composition)")
print("  - Action (egocentric POV with visible hands)")
print("  - Final State (verification of changes)")
print("  - Continuity Constraints (physics, object identity)")
print("  - Success Criteria (frame-by-frame checks)")

try:
    video_world = video_gen.generate_video_world(
        image_world=image_world,
        strategy="all_transitions"
    )

    # Save to file
    output_file = "apple_eating_world_videos_enhanced.json"
    video_world.save(output_file)

    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)

    print(f"\nVideo world saved to: {output_file}")
    print(f"Total transitions with videos: {len(video_world.transitions)}")

    # Show generated video files
    print("\nGenerated videos with enhanced prompts:")
    for trans in video_world.transitions:
        if trans.video_path:
            video_path = Path(trans.video_path)
            if video_path.exists():
                size_mb = video_path.stat().st_size / (1024 * 1024)
                print(f"  - {trans.video_path} ({size_mb:.2f} MB)")
            else:
                print(f"  - {trans.video_path}")

    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print("\nCompare these enhanced videos with the simple prompt videos:")
    print("  - Simple: generated_videos/apple_eating_images_videos/")
    print("  - Enhanced: generated_videos_enhanced/apple_eating_images_videos/")

except Exception as e:
    print("\n" + "=" * 80)
    print("ERROR")
    print("=" * 80)
    print(f"\n{type(e).__name__}: {e}")

    import traceback
    traceback.print_exc()
    sys.exit(1)
