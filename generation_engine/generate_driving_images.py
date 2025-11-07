#!/usr/bin/env python3
"""
Generate images for the driving startup world.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.genai as genai

sys.path.insert(0, str(Path(__file__).parent))

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

from world_model_bench_agent.benchmark_curation import World
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from utils.veo import VeoVideoGenerator

print("=" * 70)
print("GENERATING IMAGES FOR DRIVING WORLD")
print("=" * 70)

# Load the linear driving world
world_file = "worlds/llm_worlds/driving_linear_world.json"
print(f"\nLoading world: {world_file}")
text_world = World.load(world_file)

print(f"\n✅ World loaded:")
print(f"   States: {len(text_world.states)}")
print(f"   Actions: {len(text_world.actions)}")
print(f"   Transitions: {len(text_world.transitions)}")

# Initialize Veo client
print("\nInitializing Veo client...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(
    api_key=api_key,
    client=client,
    acknowledged_paid_feature=True
)

# Initialize generator
print("Initializing Image World Generator...")
generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images",
    camera_perspective="first_person_ego",
    aspect_ratio="16:9"
)

# Generate images (linear path only)
print("\n" + "=" * 70)
print("GENERATING IMAGES (LINEAR PATH)")
print("=" * 70)
print("\nThis will generate 8 images for the linear driving procedure.")
print("Strategy: canonical_path (follows the main path)")

image_world = generator.generate_image_world(
    text_world=text_world,
    strategy="canonical_path",  # Use canonical path for linear world
    world_name="starting_to_drive_linear"
)

print("\n✅ Image world generated!")
print(f"   States with images: {len(image_world.states)}")
print(f"   Transitions: {len(image_world.transitions)}")

# Save
output_file = "driving_linear_image_world.json"
image_world.save(output_file)
print(f"\n💾 Saved to: {output_file}")

# Show generated images
print("\n📸 Generated Images:")
for state in image_world.states:
    print(f"   [{state.state_id}] {state.image_path}")

print("\n" + "=" * 70)
print("SUCCESS! Driving images generated!")
print("=" * 70)
print(f"\nFiles created:")
print(f"  • {output_file} - Image world metadata")
print(f"  • generated_images/starting_to_drive_linear_images/ - 8 images")
print(f"\nNext steps:")
print(f"  • Play the game: python interactive_image_demo.py")
print(f"  • Select 'driving_linear_image_world.json'")
