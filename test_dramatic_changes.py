#!/usr/bin/env python3
"""Test image generation with more dramatic changes."""

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
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World, State, Action, Transition

# Create a world with DRAMATIC changes
print("Creating world with dramatic changes...")

s0 = State(
    description="Empty white table with only a red apple sitting in the center",
    state_id="s0"
)

s1 = State(
    description="The red apple has been sliced in half, showing the white flesh and seeds inside. A knife is visible next to the apple halves",
    state_id="s1"
)

s2 = State(
    description="The apple slices have been eaten, leaving only the apple cores and knife on the table",
    state_id="s2"
)

a0 = Action(
    description="Cut the apple in half with a knife, exposing the inside",
    action_id="a0"
)

a1 = Action(
    description="Eat the apple slices, leaving only the cores",
    action_id="a1"
)

world = World(
    name="apple_eating",
    description="Eating an apple with dramatic visual changes",
    states=[s0, s1, s2],
    actions=[a0, a1],
    transitions=[
        Transition(s0, a0, s1),
        Transition(s1, a1, s2)
    ],
    initial_state=s0,
    goal_states=[s2]
)

print("States:")
print(f"  s0: {s0.description}")
print(f"  s1: {s1.description}")
print(f"  s2: {s2.description}")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Generate images
print("\n" + "=" * 70)
print("GENERATING IMAGES WITH IMPROVED PROMPTS")
print("=" * 70)
print("\nThis will generate 3 images with DRAMATIC changes")
print("Estimated cost: ~$0.007")

generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images"
)

try:
    image_world = generator.generate_image_world(
        text_world=world,
        strategy="canonical_path"
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nGenerated {len(image_world.states)} images:")
    for img_state in image_world.states:
        print(f"\n  [{img_state.state_id}] {img_state.image_path}")
        print(f"      Description: {img_state.text_description}")
        print(f"      Prompt: {img_state.generation_prompt[:120]}...")

    image_world.save("apple_eating_image_world.json")
    print(f"\nSaved to: apple_eating_image_world.json")

    print("\nImages saved to:")
    print(f"  generated_images/apple_eating_images/")
    print("\nPlease check if the changes are now MORE VISIBLE:")
    print("  s0: Whole red apple")
    print("  s1: Apple cut in half (should see knife and inside)")
    print("  s2: Only cores left (apple eaten)")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
