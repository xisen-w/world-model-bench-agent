#!/usr/bin/env python3
"""
Generate a 'Starting to Drive' world using LLM.

This creates a realistic driving startup procedure with:
- Multiple steps (check mirrors, seatbelt, start engine, etc.)
- Branching paths (skip steps, wrong order, etc.)
- Multiple endings (safe drive, unsafe, stalled engine, etc.)
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

from world_model_bench_agent.llm_world_generator import LLMWorldGenerator

print("=" * 70)
print("GENERATING DRIVING WORLD WITH LLM")
print("=" * 70)

# Initialize generator
print("\nInitializing LLM World Generator...")
generator = LLMWorldGenerator(api_key=api_key)

# Step 1: Generate linear world (perfect procedure)
print("\n" + "=" * 70)
print("STEP 1: GENERATING LINEAR WORLD (PERFECT PROCEDURE)")
print("=" * 70)

linear_world = generator.generate_linear_world(
    scenario="starting_to_drive",
    initial_description="Driver sitting in parked car, engine off, car in parking lot",
    goal_description="Car safely driving on the road, all safety checks complete",
    num_steps=6,  # Will create 8 total states (start + 6 intermediate + goal)
    context="""
    This is a driving startup procedure. Include realistic steps like:
    - Adjusting seat and mirrors
    - Fastening seatbelt
    - Checking surroundings
    - Starting engine
    - Releasing parking brake
    - Checking blind spots
    - Pulling out safely

    Make each step clear and visual.
    """
)

print("\n✅ Linear world generated!")
print(f"   States: {len(linear_world.states)}")
print(f"   Actions: {len(linear_world.actions)}")
print(f"   Transitions: {len(linear_world.transitions)}")

# Save linear world
linear_output = "driving_linear_world.json"
linear_world.save(linear_output)
print(f"\n💾 Saved to: {linear_output}")

# Show the linear path
print("\n📋 Linear Path:")
current_state = linear_world.initial_state
print(f"   Start: {current_state.description}")

for transition in linear_world.transitions:
    print(f"   → Action: {transition.action.description}")
    print(f"   → State: {transition.end_state.description}")

# Step 2: Expand to branching world
print("\n" + "=" * 70)
print("STEP 2: EXPANDING TO BRANCHING WORLD (MULTIPLE PATHS)")
print("=" * 70)
print("\nThis will add:")
print("  - Alternative paths (skip steps, wrong order)")
print("  - Failure states (forgot seatbelt, didn't check mirrors, stalled)")
print("  - Success variations (rushed but ok, perfect procedure)")

branching_world = generator.expand_to_branching_world(
    linear_world=linear_world,
    total_states=15,  # Target 15 total states
    num_endings=5,  # 5 different endings
    success_endings=3,  # 3 successful ways to drive
    failure_endings=2,  # 2 failure scenarios,
    branching_points=3  # 3 decision points
)

print("\n✅ Branching world generated!")
print(f"   States: {len(branching_world.states)}")
print(f"   Actions: {len(branching_world.actions)}")
print(f"   Transitions: {len(branching_world.transitions)}")
print(f"   Goal states: {len(branching_world.goal_states)}")
print(f"   Final states: {len(branching_world.get_final_states())}")

# Save branching world
branching_output = "driving_branching_world.json"
branching_world.save(branching_output)
print(f"\n💾 Saved to: {branching_output}")

# Analyze paths
paths = branching_world.get_all_paths()
print("\n📊 Path Analysis:")
print(f"   Total success paths: {len(paths)}")
for i, path in enumerate(paths, 1):
    states = [branching_world.initial_state.state_id]
    for t in path:
        states.append(t.end_state.state_id)
    print(f"   Path {i}: {' → '.join(states)} ({len(path)} steps)")

# Show all possible endings
print("\n🏁 Possible Endings:")
final_states = branching_world.get_final_states()
for state in final_states:
    outcome = state.metadata.get('outcome', 'unknown')
    quality = state.metadata.get('quality', 'N/A')
    emoji = '✅' if outcome == 'success' else '❌'
    print(f"   {emoji} [{state.state_id}] {state.description[:60]}...")
    print(f"      Quality: {quality}, Outcome: {outcome}")

print("\n" + "=" * 70)
print("SUCCESS! Driving world generated!")
print("=" * 70)
print(f"\nFiles created:")
print(f"  1. {linear_output} - Simple linear path")
print(f"  2. {branching_output} - Full branching world")
print(f"\nNext steps:")
print(f"  • Generate images: Use image_world_generator.py")
print(f"  • Generate videos: Use video_world_generator.py")
print(f"  • Play interactively: Use interactive_image_demo.py")
