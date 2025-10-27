#!/usr/bin/env python3
"""Simple test for image generation - just first 3 states of coffee world."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

print(f"API key loaded: {api_key[:15]}...")

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World

# Load the coffee linear world
print("\nLoading coffee linear world...")
world = World.load("coffee_linear_world.json")
print(f"Loaded: {world.name}")
print(f"  States: {len(world.states)}")
print(f"  Transitions: {len(world.transitions)}")

# Create a truncated version with only first 3 states
from world_model_bench_agent.benchmark_curation import State, Action, Transition

truncated_world = World(
    name="coffee_making_short",
    description="Short coffee making (3 states)",
    states=world.states[:3],
    actions=world.actions[:2],
    transitions=world.transitions[:2],
    initial_state=world.states[0],
    goal_states=[world.states[2]]
)

print(f"\nTruncated to 3 states:")
print(f"  s0: {truncated_world.states[0].description[:60]}...")
print(f"  s1: {truncated_world.states[1].description[:60]}...")
print(f"  s2: {truncated_world.states[2].description[:60]}...")

# Initialize Veo
print("\nInitializing Veo client...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(
    api_key=api_key,
    client=client,
    acknowledged_paid_feature=True
)
print("Veo client initialized")

# Generate images
print("\n" + "=" * 70)
print("GENERATING IMAGES")
print("=" * 70)
print("\nWill generate 3 images (1 initial + 2 variations)")
print("Estimated cost: ~$0.007")
print("Estimated time: ~2-3 minutes")

generator = ImageWorldGenerator(
    veo_client=veo,
    camera_perspective="first_person_ego",
    output_dir="generated_images"
)

try:
    image_world = generator.generate_image_world(
        text_world=truncated_world,
        strategy="canonical_path"
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"\nGenerated {len(image_world.states)} images:")
    for img_state in image_world.states:
        print(f"\n  [{img_state.state_id}] {img_state.image_path}")
        print(f"      Description: {img_state.text_description[:60]}...")
        print(f"      Prompt: {img_state.generation_prompt[:80]}...")

    # Save
    image_world.save("coffee_short_image_world.json")
    print(f"\nSaved to: coffee_short_image_world.json")

    print("\nGenerated images can be found in:")
    print(f"  generated_images/coffee_making_short_images/")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
