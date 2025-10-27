#!/usr/bin/env python3
"""
Test full world image generation with all connecting paths.
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
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World

# Load the branching world
print("=" * 70)
print("FULL WORLD IMAGE GENERATION TEST")
print("=" * 70)

world_file = "apple_eating_branching_world.json"
print(f"\nLoading world from: {world_file}")
text_world = World.load(world_file)

print(f"\nWorld Summary:")
print(f"  Name: {text_world.name}")
print(f"  States: {len(text_world.states)}")
print(f"  Actions: {len(text_world.actions)}")
print(f"  Transitions: {len(text_world.transitions)}")
print(f"  Initial State: {text_world.initial_state.state_id}")
print(f"  Goal States: {[s.state_id for s in text_world.goal_states]}")

# Show all paths
paths = text_world.get_all_paths()
print(f"\n  Total Paths: {len(paths)}")
for i, path in enumerate(paths, 1):
    path_str = text_world.initial_state.state_id
    for t in path:
        path_str += f" → {t.end_state.state_id}"
    print(f"    Path {i}: {path_str} ({len(path)} transitions)")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Generate images for FULL WORLD
print("\n" + "=" * 70)
print("GENERATING IMAGES FOR ALL STATES (FULL WORLD)")
print("=" * 70)
print(f"\nThis will generate {len(text_world.states)} images")
print(f"Estimated cost: ~${len(text_world.states) * 0.0024:.3f}")
print("\nStarting generation...")

generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images"
)

try:
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy="full_world"  # Use full_world strategy
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nGenerated {len(image_world.states)} images:")
    for img_state in image_world.states:
        print(f"\n  [{img_state.state_id}]")
        print(f"    Image: {img_state.image_path}")
        print(f"    Description: {img_state.text_description[:60]}...")
        if img_state.parent_state_id:
            print(f"    Parent: {img_state.parent_state_id} via {img_state.parent_action_id}")

    print(f"\n\nGenerated {len(image_world.transitions)} transitions:")
    for trans in image_world.transitions:
        print(f"  {trans.start_state_id} --[{trans.action_id}]--> {trans.end_state_id}")

    # Save the image world
    output_file = "apple_eating_branching_image_world.json"
    image_world.save(output_file)
    print(f"\n\nSaved to: {output_file}")

    print("\nImages saved to:")
    print(f"  generated_images/{image_world.name}/")

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(f"✓ Expected states: {len(text_world.states)}")
    print(f"✓ Generated states: {len(image_world.states)}")
    print(f"✓ Expected transitions: {len(text_world.transitions)}")
    print(f"✓ Generated transitions: {len(image_world.transitions)}")

    if len(image_world.states) == len(text_world.states):
        print("\n✅ All states generated successfully!")
    else:
        print(f"\n⚠️  State count mismatch!")

    if len(image_world.transitions) == len(text_world.transitions):
        print("✅ All transitions recorded successfully!")
    else:
        print(f"⚠️  Transition count mismatch!")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
