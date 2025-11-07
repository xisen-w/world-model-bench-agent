#!/usr/bin/env python3
"""Fix the plant world JSON to have correct transition format."""

import json
from pathlib import Path

# Load the file
world_file = Path("worlds/llm_worlds/indoor_plant_watering_repotting_branching_egocentric_world.json")
with open(world_file) as f:
    world = json.load(f)

# Create lookup dictionaries
states_by_id = {s["state_id"]: s for s in world["states"]}
actions_by_id = {a["action_id"]: a for a in world["actions"]}

# Fix transitions - convert string IDs to full objects
fixed_transitions = []
for t in world["transitions"]:
    start_id = t["start_state"]
    action_id = t["action"]
    end_id = t["end_state"]

    # Get full objects
    start_state = states_by_id.get(start_id)
    action = actions_by_id.get(action_id)
    end_state = states_by_id.get(end_id)

    if not start_state:
        print(f"Warning: start_state '{start_id}' not found")
        continue
    if not action:
        print(f"Warning: action '{action_id}' not found")
        continue
    if not end_state:
        print(f"Warning: end_state '{end_id}' not found")
        continue

    fixed_transitions.append({
        "transition_id": t["transition_id"],
        "start_state": start_state,
        "action": action,
        "end_state": end_state
    })

# Update world with fixed transitions
world["transitions"] = fixed_transitions

# Also fix initial_state if it's a string
if isinstance(world.get("initial_state"), str):
    initial_id = world["initial_state"]
    world["initial_state"] = states_by_id.get(initial_id)

# Fix goal_state if it's a string
if isinstance(world.get("goal_state"), str):
    goal_id = world["goal_state"]
    world["goal_state"] = states_by_id.get(goal_id)

# Fix goal_states if they're strings
if "goal_states" in world:
    goal_states = []
    for gs in world["goal_states"]:
        if isinstance(gs, str):
            goal_states.append(states_by_id.get(gs))
        else:
            goal_states.append(gs)
    world["goal_states"] = goal_states

# Fix final_states if they're strings
if "final_states" in world:
    final_states = []
    for fs in world["final_states"]:
        if isinstance(fs, str):
            final_states.append(states_by_id.get(fs))
        else:
            final_states.append(fs)
    world["final_states"] = final_states

# Save fixed file
with open(world_file, 'w') as f:
    json.dump(world, f, indent=2)

print(f"✅ Fixed {len(fixed_transitions)} transitions")
print(f"✅ Saved to {world_file}")
