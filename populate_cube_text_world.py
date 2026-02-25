#!/usr/bin/env python3
"""
Populate the text world companion file with states, actions, and transitions
from the video world, so the game can navigate properly.
"""

import json
from pathlib import Path

def main():
    # Load video world
    video_world_path = "worlds/video_worlds/cube_world_navigation_maze.json"
    with open(video_world_path) as f:
        video_world = json.load(f)

    # Create full text world structure
    text_world = {
        "name": video_world["name"],
        "description": video_world["description"],
        "domain": "spatial_navigation",
        "initial_state": {
            "state_id": video_world["initial_state_id"],
            "description": next(s["text_description"] for s in video_world["states"]
                               if s["state_id"] == video_world["initial_state_id"]),
            "metadata": {}
        },
        "goal_states": [],
        "states": [],
        "actions": [],
        "transitions": [],
        "metadata": video_world.get("metadata", {})
    }

    # Add all states
    for vstate in video_world["states"]:
        text_world["states"].append({
            "state_id": vstate["state_id"],
            "description": vstate["text_description"],
            "metadata": vstate.get("metadata", {})
        })

    # Add goal states
    for goal_id in video_world["goal_state_ids"]:
        goal_state = next(s for s in video_world["states"] if s["state_id"] == goal_id)
        text_world["goal_states"].append({
            "state_id": goal_id,
            "description": goal_state["text_description"],
            "metadata": goal_state.get("metadata", {})
        })

    # Create actions and transitions from video transitions
    action_set = {}  # Track unique actions by action_id

    for vtrans in video_world["transitions"]:
        action_id = vtrans["action_id"]

        # Add action if not already added
        if action_id not in action_set:
            action_set[action_id] = {
                "action_id": action_id,
                "description": vtrans["action_description"],
                "metadata": vtrans.get("metadata", {})
            }

        # Add transition
        text_world["transitions"].append({
            "start_state": {
                "state_id": vtrans["start_state_id"],
                "description": next(s["text_description"] for s in video_world["states"]
                                   if s["state_id"] == vtrans["start_state_id"])
            },
            "action": {
                "action_id": action_id,
                "description": vtrans["action_description"]
            },
            "end_state": {
                "state_id": vtrans["end_state_id"],
                "description": next(s["text_description"] for s in video_world["states"]
                                   if s["state_id"] == vtrans["end_state_id"])
            },
            "metadata": vtrans.get("metadata", {})
        })

    # Add all unique actions
    text_world["actions"] = list(action_set.values())

    # Save to text world file
    text_world_path = "worlds/llm_worlds/cube_world_recorded_gameplay.json"
    with open(text_world_path, 'w') as f:
        json.dump(text_world, f, indent=2)

    print(f"✅ Created complete text world")
    print(f"   States: {len(text_world['states'])}")
    print(f"   Actions: {len(text_world['actions'])}")
    print(f"   Transitions: {len(text_world['transitions'])}")
    print(f"   Goal states: {len(text_world['goal_states'])}")
    print(f"   📝 Saved to: {text_world_path}")

    # Verify first state has actions
    s0_actions = [t for t in text_world['transitions']
                  if t['start_state']['state_id'] == video_world["initial_state_id"]]
    print(f"\n🎮 From initial state '{video_world['initial_state_id']}': {len(s0_actions)} available actions")
    for t in s0_actions:
        print(f"   → {t['action']['action_id']}: {t['end_state']['state_id']}")

if __name__ == "__main__":
    main()
