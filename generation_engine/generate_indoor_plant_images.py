#!/usr/bin/env python3
"""
Generate images for the indoor plant watering and repotting world.

This script generates egocentric images for each state in the plant care world.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.genai as genai

sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found in .env file")
    print("Please see API_KEY_SETUP.md for instructions")
    sys.exit(1)

from world_model_bench_agent.benchmark_curation import World
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from utils.veo import VeoVideoGenerator

print("=" * 80)
print("GENERATING IMAGES FOR INDOOR PLANT WATERING & REPOTTING WORLD")
print("=" * 80)

# Choose which world to use
print("\nWhich world would you like to generate images for?")
print("  1. Linear world (9 states, canonical path only)")
print("  2. Branching world (16 states, multiple paths and endings)")

choice = input("\nEnter choice (1 or 2) [default: 1]: ").strip() or "1"

if choice == "2":
    world_file = "worlds/llm_worlds/indoor_plant_watering_repotting_branching_world.json"
    strategy = "full_world"
    world_type = "branching"
else:
    world_file = "worlds/llm_worlds/indoor_plant_watering_repotting_linear_world.json"
    strategy = "canonical_path"
    world_type = "linear"

# Load the world
print(f"\nLoading {world_type} world: {world_file}")
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

# Initialize Image Generator
print("Initializing Image World Generator...")
generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images",
    camera_perspective="first_person_ego",  # Egocentric view
    aspect_ratio="16:9",
    use_advanced_generation=True,  # Use 5-step VLM/LLM pipeline
    llm_client=veo
)

# Generate images
print("\n" + "=" * 80)
print(f"GENERATING IMAGES ({strategy.upper().replace('_', ' ')})")
print("=" * 80)
print(f"\nThis will generate {len(text_world.states)} images for the {world_type} plant care procedure.")
print(f"Strategy: {strategy}")
print(f"\nEstimated time: ~{len(text_world.states) * 2} minutes")
print(f"Estimated cost: ~${len(text_world.states) * 0.0024:.3f}")

# Confirm
confirm = input("\nProceed with image generation? (yes/no) [yes]: ").strip().lower()
if confirm and confirm not in ['yes', 'y']:
    print("❌ Cancelled by user")
    sys.exit(0)

print("\n🚀 Starting image generation...\n")

try:
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy=strategy,
        world_name=f"indoor_plant_{world_type}"
    )

    print("\n" + "=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)

    print(f"\nGenerated {len(image_world.states)} images:")
    for i, state in enumerate(image_world.states, 1):
        status = "✓" if state.image_path else "✗"
        print(f"  {status} {i:2d}. {state.state_id:20s} - {state.image_path}")

    # Save the image world
    output_file = f"indoor_plant_watering_repotting_{world_type}_image_world.json"
    image_world.save(output_file)
    print(f"\n✅ Saved image world to: {output_file}")

    # Also save to worlds/image_worlds/ directory
    worlds_dir = Path("worlds/image_worlds")
    worlds_dir.mkdir(parents=True, exist_ok=True)
    worlds_output = worlds_dir / output_file
    image_world.save(str(worlds_output))
    print(f"✅ Also saved to: {worlds_output}")

    print("\n📁 Images saved to:")
    if image_world.states and image_world.states[0].image_path:
        image_dir = Path(image_world.states[0].image_path).parent
        print(f"   {image_dir}/")

    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total states: {len(text_world.states)}")
    print(f"Images generated: {sum(1 for s in image_world.states if s.image_path)}")
    print(f"Strategy: {strategy}")
    print(f"Camera perspective: first_person_ego")
    print(f"Aspect ratio: 16:9")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. View the generated images:")
    if image_world.states and image_world.states[0].image_path:
        image_dir = Path(image_world.states[0].image_path).parent
        print(f"   open {image_dir}/")
    
    print("\n2. Generate videos from these images:")
    print(f"   python generate_indoor_plant_videos.py")
    
    print("\n3. View in interactive demo:")
    print(f"   python interactive_image_demo.py")

except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERROR")
    print("=" * 80)
    print(f"\n{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("🎉 IMAGE GENERATION COMPLETE!")
print("=" * 80)

