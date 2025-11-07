#!/usr/bin/env python3
"""
Generate images for Coffee Making - Egocentric Linear World.

This demonstrates image generation from an egocentric key-frame world.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found in .env file")
    sys.exit(1)

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World

print("=" * 80)
print("☕ COFFEE MAKING - EGOCENTRIC LINEAR WORLD IMAGE GENERATION")
print("=" * 80)

world_file = "worlds/llm_worlds/coffee_making_linear_egocentric_world.json"
print(f"\n📂 Loading world from: {world_file}")

try:
    text_world = World.load(world_file)
except Exception as e:
    print(f"❌ Error loading world: {e}")
    print(f"\nMake sure the file exists at: {world_file}")
    sys.exit(1)

print(f"\n✅ World loaded successfully!")
print(f"\n📊 World Summary:")
print(f"  Name: {text_world.name}")
print(f"  Description: {text_world.description}")
print(f"  States: {len(text_world.states)}")
print(f"  Actions: {len(text_world.actions)}")
print(f"  Transitions: {len(text_world.transitions)}")

# Show first state as example
print(f"\n🎬 Example Key Frame (s0):")
first_state = text_world.states[0]
print(f"  Description: {first_state.description[:200]}...")
print(f"  Metadata: {first_state.metadata}")

# Initialize Veo
print("\n🔧 Initializing Veo image generation client...")
try:
    client = genai.Client(api_key=api_key)
    veo = VeoVideoGenerator(
        api_key=api_key,
        client=client,
        acknowledged_paid_feature=True
    )
    print("✅ Veo client initialized")
except Exception as e:
    print(f"❌ Error initializing Veo: {e}")
    sys.exit(1)

# Generate images
print("\n" + "=" * 80)
print("IMAGE GENERATION SETUP")
print("=" * 80)
print(f"\n📸 Generation Strategy: CANONICAL_PATH (all {len(text_world.states)} states)")
print(f"📹 Camera Perspective: first_person_ego (egocentric)")
print(f"📐 Aspect Ratio: 16:9")
print(f"🧠 Advanced Generation: Enabled (5-step VLM/LLM pipeline)")

print(f"\n💰 Estimated Cost: ~${len(text_world.states) * 0.0024:.3f}")
print(f"⏱️  Estimated Time: ~{len(text_world.states) * 2} minutes")

# Confirm
if "--yes" in sys.argv or "-y" in sys.argv:
    print("\n🚀 Auto-proceeding with image generation (--yes flag)")
else:
    confirm = input("\n🚀 Proceed with image generation? (yes/no) [yes]: ").strip().lower()
    if confirm and confirm not in ['yes', 'y']:
        print("❌ Cancelled by user")
        sys.exit(0)

print("\n" + "=" * 80)
print("STARTING IMAGE GENERATION")
print("=" * 80)

generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images",
    camera_perspective="first_person_ego",
    aspect_ratio="16:9",
    use_advanced_generation=True,
    llm_client=veo
)

try:
    print("\n☕ Generating egocentric coffee-making images...")
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy="canonical_path",  # Linear path - all states in sequence
        world_name="coffee_making_egocentric"
    )

    print("\n" + "=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)

    print(f"\n🖼️  Generated {len(image_world.states)} images:")

    for i, s in enumerate(image_world.states, 1):
        progress = s.metadata.get('progress', 0)
        progress_bar = '█' * int(progress * 20)
        progress_empty = '░' * (20 - int(progress * 20))

        print(f"\n  {i}. [{s.state_id}] Progress: [{progress_bar}{progress_empty}] {progress*100:.0f}%")
        print(f"     👁️  Focus: {s.metadata.get('main_focus', 'N/A')}")
        print(f"     📷 {s.image_path}")

    # Save the image world
    output_file = "coffee_making_linear_egocentric_image_world.json"
    image_world.save(output_file)
    print(f"\n💾 Saved image world to: {output_file}")

    # Also save to worlds/image_worlds/
    worlds_dir = Path("worlds/image_worlds")
    worlds_dir.mkdir(parents=True, exist_ok=True)
    worlds_output = worlds_dir / output_file
    image_world.save(str(worlds_output))
    print(f"💾 Also saved to: {worlds_output}")

    print("\n📁 Images saved to:")
    if image_world.states and image_world.states[0].image_path:
        image_dir = Path(image_world.states[0].image_path).parent
        print(f"   {image_dir}/")

    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print(f"✓ Expected states: {len(text_world.states)}")
    print(f"✓ Generated states: {len(image_world.states)}")

    if len(image_world.states) == len(text_world.states):
        print("\n✅ All states generated successfully!")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. 🖼️  View the generated images:")
    if image_world.states and image_world.states[0].image_path:
        image_dir = Path(image_world.states[0].image_path).parent
        print(f"   open {image_dir}/")

    print("\n2. 🎮 Test in interactive demo:")
    print(f"   python3 interactive_image_demo.py")

    print("\n3. 📊 Compare egocentric vs third-person:")
    print(f"   - Egocentric: generated_images/coffee_making_egocentric/")
    print(f"   - Third-person: (if you generate one with standard generator)")

except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERROR")
    print("=" * 80)
    print(f"\n{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("🎉 IMAGE GENERATION COMPLETE!")
print("=" * 80)
print("\n☕ Your egocentric coffee-making world is now fully visualized!")
