#!/usr/bin/env python3
"""
Generate images for Indoor Plant Watering & Repotting - Original Branching World.

This creates third-person descriptive images for the complete branching world with:
- 9 canonical path states (s0-s8)
- 3 branching alternative states (s1_alt_0, s1_alt_1, s4_alt_0)
- 4 ending states (s_perfect, s_good, s_acceptable, f_critical_error, f_gave_up)
- Multiple risky, recovery, and shortcut paths
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
    print("Please create a .env file with your GEMINI_KEY")
    sys.exit(1)

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World

# Load the original branching text world
print("=" * 80)
print("INDOOR PLANT REPOTTING - ORIGINAL BRANCHING WORLD IMAGE GENERATION")
print("=" * 80)

world_file = "worlds/llm_worlds/indoor_plant_watering_repotting_branching_world.json"
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
print(f"  Initial State: {text_world.initial_state.state_id}")
print(f"  Goal States: {[s.state_id for s in text_world.goal_states]}")
print(f"  Final States: {[s.state_id for s in text_world.final_states]}")

# Analyze paths
print(f"\n🗺️  Path Analysis:")
try:
    paths = text_world.get_all_paths()
    print(f"  Total Paths to Goal: {len(paths)}")
    for i, path in enumerate(paths[:5], 1):  # Show first 5 paths
        path_states = [text_world.initial_state.state_id]
        for t in path:
            path_states.append(t.end_state.state_id)
        print(f"    Path {i}: {' → '.join(path_states)} ({len(path)} steps)")
    if len(paths) > 5:
        print(f"    ... and {len(paths) - 5} more paths")
except Exception as e:
    print(f"  (Path analysis skipped: {e})")

# Categorize states
canonical_states = [s for s in text_world.states if s.state_id.startswith('s') and not '_' in s.state_id and not s.state_id.startswith('f')]
branching_states = [s for s in text_world.states if '_alt_' in s.state_id]
success_endings = [s for s in text_world.states if s.state_id.startswith('s_')]
failure_endings = [s for s in text_world.states if s.state_id.startswith('f_')]

print(f"\n📋 State Categories:")
print(f"  Canonical path states: {len(canonical_states)} ({', '.join([s.state_id for s in canonical_states])})")
print(f"  Branching states: {len(branching_states)} ({', '.join([s.state_id for s in branching_states])})")
print(f"  Success endings: {len(success_endings)} ({', '.join([s.state_id for s in success_endings])})")
print(f"  Failure endings: {len(failure_endings)} ({', '.join([s.state_id for s in failure_endings])})")

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

# Generate images for FULL BRANCHING WORLD
print("\n" + "=" * 80)
print("IMAGE GENERATION SETUP")
print("=" * 80)
print(f"\n📸 Generation Strategy: FULL_WORLD (all {len(text_world.states)} states)")
print(f"📹 Camera Perspective: third_person (observational)")
print(f"📐 Aspect Ratio: 16:9")
print(f"🧠 Advanced Generation: Enabled (5-step VLM/LLM pipeline)")

print(f"\n💰 Estimated Cost: ~${len(text_world.states) * 0.0024:.3f}")
print(f"⏱️  Estimated Time: ~{len(text_world.states) * 2} minutes")

# Confirm before proceeding (allow --yes flag to skip)
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
    camera_perspective="third_person",  # Third-person observational view
    aspect_ratio="16:9",
    use_advanced_generation=True,  # Use advanced 5-step VLM/LLM pipeline
    llm_client=veo  # Use same veo client for LLM calls
)

try:
    print("\n🎨 Generating images for all states...")
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy="full_world",  # Generate ALL states in branching world
        world_name="indoor_plant_branching"
    )

    print("\n" + "=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)

    print(f"\n🖼️  Generated {len(image_world.states)} images:")

    # Group by category for better display
    print(f"\n  📍 Initial State:")
    for s in image_world.states:
        if s.state_id == "s0":
            print(f"    [{s.state_id}] {s.text_description[:70]}...")
            print(f"        📷 {s.image_path}")

    print(f"\n  🌱 Canonical Path States:")
    for s in image_world.states:
        if s.state_id in [cs.state_id for cs in canonical_states] and s.state_id != "s0":
            print(f"    [{s.state_id}] {s.text_description[:70]}...")
            print(f"        📷 {s.image_path}")

    print(f"\n  🔀 Branching Alternative States:")
    for s in image_world.states:
        if s.state_id in [bs.state_id for bs in branching_states]:
            print(f"    [{s.state_id}] {s.text_description[:70]}...")
            print(f"        from {s.parent_state_id} via {s.parent_action_id}")
            print(f"        📷 {s.image_path}")

    print(f"\n  ✅ Success Endings:")
    for s in image_world.states:
        if s.state_id in [se.state_id for se in success_endings]:
            quality = s.metadata.get('quality', 'N/A')
            print(f"    [{s.state_id}] Quality: {quality} - {s.text_description[:60]}...")
            print(f"        📷 {s.image_path}")

    print(f"\n  ❌ Failure Endings:")
    for s in image_world.states:
        if s.state_id in [fe.state_id for fe in failure_endings]:
            quality = s.metadata.get('quality', 'N/A')
            print(f"    [{s.state_id}] Quality: {quality} - {s.text_description[:60]}...")
            print(f"        📷 {s.image_path}")

    print(f"\n\n🔗 Generated {len(image_world.transitions)} transitions:")
    for trans in image_world.transitions[:10]:  # Show first 10
        print(f"  {trans.start_state_id} --[{trans.action_id}]--> {trans.end_state_id}")
    if len(image_world.transitions) > 10:
        print(f"  ... and {len(image_world.transitions) - 10} more transitions")

    # Save the image world
    output_file = "indoor_plant_watering_repotting_branching_image_world.json"
    image_world.save(output_file)
    print(f"\n💾 Saved image world to: {output_file}")

    # Also save to worlds/image_worlds/ directory
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

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. 🖼️  View the generated images:")
    if image_world.states and image_world.states[0].image_path:
        image_dir = Path(image_world.states[0].image_path).parent
        print(f"   open {image_dir}/")

    print("\n2. 🎮 Test in interactive demo:")
    print(f"   python3 interactive_image_demo.py")

    print("\n3. 🎬 Generate videos from these images:")
    print(f"   python3 generation_engine/generate_plant_branching_videos.py")

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
print("\n🌿 Your third-person plant repotting world is now fully visualized!")
