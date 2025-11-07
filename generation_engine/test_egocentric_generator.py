#!/usr/bin/env python3
"""
Test the new Egocentric World Generator.

This demonstrates the enhanced key-frame focused, first-person world generation.
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

from world_model_bench_agent.egocentric_world_generator import EgocentricWorldGenerator

print("=" * 80)
print("🎥 EGOCENTRIC WORLD GENERATOR TEST")
print("=" * 80)

# Initialize generator
generator = EgocentricWorldGenerator(api_key=api_key)

# Test scenario: Making coffee
print("\n📝 Test Scenario: Coffee Making")
print("-" * 80)

world = generator.generate_egocentric_linear_world(
    scenario="coffee_making",
    initial_state="You're standing in your kitchen. An empty coffee cup sits on the counter in front of you. To your left is a French press with ground coffee and hot water ready.",
    goal_state="You hold a full cup of freshly brewed coffee, steam rising from the surface. The rich aroma fills the air.",
    num_steps=4,  # Will create 6 total states (s0-s5)
    camera_perspective="first_person_ego",
    camera_height="1.6m (eye level)",
    context="Simple French press coffee brewing - focus on the tactile and visual experience"
)

print("\n" + "=" * 80)
print("✅ GENERATED WORLD PREVIEW")
print("=" * 80)

print(f"\n🌍 World: {world.name}")
print(f"📊 States: {len(world.states)}")
print(f"⚡ Actions: {len(world.actions)}")
print(f"🔗 Transitions: {len(world.transitions)}")

print("\n" + "-" * 80)
print("🎬 KEY FRAMES (States)")
print("-" * 80)

for state in world.states:
    progress_bar = '█' * int(state.metadata.get('progress', 0) * 30)
    progress_empty = '░' * (30 - len(progress_bar))
    print(f"\n[{state.state_id}] Progress: [{progress_bar}{progress_empty}] {state.metadata.get('progress', 0)*100:.0f}%")

    # Wrap description for readability
    desc = state.description
    if len(desc) > 300:
        desc = desc[:300] + "..."
    print(f"Description: {desc}")

    metadata = state.metadata
    if 'main_focus' in metadata:
        print(f"👁️  Focus: {metadata['main_focus']}")
    if 'hands_visible' in metadata:
        print(f"🖐️  Hands: {'Visible' if metadata['hands_visible'] else 'Not visible'}")

print("\n" + "-" * 80)
print("⚡ ACTIONS")
print("-" * 80)

for i, transition in enumerate(world.transitions):
    print(f"\n[{transition.action.action_id}] {transition.start_state.state_id} → {transition.end_state.state_id}")

    # Wrap action description
    desc = transition.action.description
    if len(desc) > 200:
        desc = desc[:200] + "..."
    print(f"   {desc}")

    metadata = transition.action.metadata
    if metadata.get('hand_action'):
        print(f"   🖐️  Hand action: {metadata.get('both_hands', 'one hand')}")
    if metadata.get('tool_use'):
        print(f"   🔧 Tool: {metadata['tool_use']}")

# Save the world
print("\n" + "=" * 80)
print("💾 SAVING WORLD")
print("=" * 80)

output_file = generator.save_world(world)
print(f"✅ World saved successfully!")

print("\n" + "=" * 80)
print("🎬 KEY DIFFERENCES FROM STANDARD GENERATION")
print("=" * 80)

print("""
✅ EGOCENTRIC ENHANCEMENTS:

1️⃣  First-Person Perspective
   - Old: "The coffee is poured into the cup"
   - New: "You tilt the French press and watch hot coffee stream into your cup"

2️⃣  Visual Key Frames
   - Each state describes what you SEE from your eye-level view
   - Camera position, visual field, what's in frame

3️⃣  Hand & Body Positions
   - "Your left hand steadies the cup while your right hand presses down"
   - Body posture: standing, leaning, reaching

4️⃣  Sensory Details
   - Touch: "The press handle feels warm in your palm"
   - Sight: "You watch the dark liquid rise in the glass cup"
   - Sound: "You hear the gentle gurgle as coffee pours"

5️⃣  Present Continuous
   - Everything happening NOW in real-time
   - "You're pouring..." not "You poured..."

6️⃣  Spatial Awareness
   - "To your left...", "In front of you...", "Within arm's reach..."
   - Clear positioning of objects relative to you

7️⃣  Optimized for Video/Image Generation
   - Each state can be directly converted to image prompts
   - Clear visual composition and camera angles
""")

print("\n" + "=" * 80)
print("📋 NEXT STEPS")
print("=" * 80)

print(f"""
1. 🖼️  Generate images from this world:
   python generation_engine/generate_images_from_world.py {output_file}

2. 🎮 Test in interactive demo:
   python interactive_demo.py

3. 🔄 Generate branching version:
   # Use the egocentric linear world as base
   # Expand with risky actions, shortcuts, recovery paths
""")

print("\n" + "=" * 80)
print("🎉 TEST COMPLETE!")
print("=" * 80)
