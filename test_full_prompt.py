#!/usr/bin/env python3
"""Test full enhanced prompt with initial state + action + final state structure."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

sys.path.insert(0, str(script_dir))

# Load environment
env_path = script_dir / ".env"
load_dotenv(env_path)

from world_model_bench_agent.image_world_generator import ImageWorld
from world_model_bench_agent.prompt_enhancer import PromptEnhancer

print("=" * 80)
print("TESTING FULL ENHANCED PROMPT STRUCTURE")
print("=" * 80)

# Load the apple_eating world
world_file = script_dir / "apple_eating_image_world.json"
image_world = ImageWorld.load(str(world_file))

print(f"\nLoaded world: {image_world.name}")

# Get first transition
first_trans = image_world.transitions[0]
start_state = None
end_state = None

for state in image_world.states:
    if state.state_id == first_trans.start_state_id:
        start_state = state
    if state.state_id == first_trans.end_state_id:
        end_state = state

print(f"\nFirst transition:")
print(f"  {first_trans.start_state_id} --> {first_trans.end_state_id}")
print(f"  Action: {first_trans.action_description}")

# Extract objects
common_objects = ['apple', 'knife', 'plate', 'bowl', 'table', 'counter']
combined_text = (start_state.text_description + " " +
                 end_state.text_description).lower()
objects = [obj for obj in common_objects if obj in combined_text]

print(f"\nDetected objects: {objects}")

# Generate full enhanced prompt
print("\n" + "=" * 80)
print("FULL ENHANCED PROMPT")
print("=" * 80)

enhancer = PromptEnhancer()
full_prompt = enhancer.enhance_full_transition(
    initial_state=start_state.text_description,
    action=first_trans.action_description,
    final_state=end_state.text_description,
    objects=objects,
    location="domestic kitchen countertop"
)

print("\n" + full_prompt)

print("\n" + "=" * 80)
print("PROMPT STATISTICS")
print("=" * 80)
print(f"Total length: {len(full_prompt)} characters")
print(f"Total lines: {len(full_prompt.splitlines())} lines")

# Count sections
sections = ['Initial State', 'Action', 'Final State', 'Continuity', 'Success Criteria']
for section in sections:
    if section in full_prompt:
        print(f"✓ Contains '{section}' section")

print("\n" + "=" * 80)
print("READY TO GENERATE VIDEO")
print("=" * 80)
print("\nThis prompt structure includes:")
print("  1. Initial State (with camera, lighting, framing)")
print("  2. Action (with egocentric POV, physical motion)")
print("  3. Final State (with changes verification)")
print("  4. Continuity Constraints (object identity, physics)")
print("  5. Success Criteria (frame-by-frame verification)")
