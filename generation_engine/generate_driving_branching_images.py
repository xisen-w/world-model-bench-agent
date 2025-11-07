#!/usr/bin/env python3
"""
Generate images for the BRANCHING driving world (all paths and endings).
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
print("GENERATING IMAGES FOR BRANCHING DRIVING WORLD")
print("=" * 70)

# Load the BRANCHING driving world
world_file = "driving_branching_world.json"
print(f"\nLoading world: {world_file}")
text_world = World.load(world_file)

print(f"\n✅ World loaded:")
print(f"   States: {len(text_world.states)}")
print(f"   Actions: {len(text_world.actions)}")
print(f"   Transitions: {len(text_world.transitions)}")
print(f"   Final states: {len(text_world.final_states)}")

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

# Generate images for ALL states using full_world strategy
print("\n" + "=" * 70)
print("GENERATING IMAGES (FULL BRANCHING WORLD)")
print("=" * 70)
print(f"\nThis will generate {len(text_world.states)} images for ALL states and paths.")
print(f"Including all success and failure endings!")
print(f"Estimated cost: ~${len(text_world.states) * 0.0024:.3f}")
print(f"Estimated time: ~{len(text_world.states) * 15} seconds")
print("\nStrategy: full_world (generates images for all reachable states)")

image_world = generator.generate_image_world(
    text_world=text_world,
    strategy="full_world",  # Use full_world for branching paths
    world_name="starting_to_drive_branching"
)

print("\n✅ Image world generated!")
print(f"   States with images: {len(image_world.states)}")
print(f"   Transitions: {len(image_world.transitions)}")

# Save
output_file = "driving_branching_image_world.json"
image_world.save(output_file)
print(f"\n💾 Saved to: {output_file}")

# Show generated images
print("\n📸 Generated Images:")
for state in image_world.states:
    print(f"   [{state.state_id}] {state.image_path}")

print("\n🏁 Endings with images:")
for final_state in text_world.final_states:
    state_id = final_state.state_id
    quality = final_state.metadata.get('quality', 'N/A')
    outcome = final_state.metadata.get('outcome', 'unknown')
    emoji = "✅" if outcome == "success" else "❌"
    print(f"   {emoji} [{state_id}] Quality: {quality}, Outcome: {outcome}")
    print(f"      {final_state.description[:70]}...")

print("\n" + "=" * 70)
print("SUCCESS! Branching driving images generated!")
print("=" * 70)
print(f"\nFiles created:")
print(f"  • {output_file} - Image world metadata")
print(f"  • generated_images/starting_to_drive_branching_images/ - {len(text_world.states)} images")
print(f"\nNext steps:")
print(f"  • Play the game: python interactive_image_demo.py")
print(f"  • Select '{output_file}'")
print(f"  • Explore different paths and endings!")
