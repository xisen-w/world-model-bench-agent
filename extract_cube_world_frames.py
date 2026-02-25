#!/usr/bin/env python3
"""
Extract frames from cube_world videos to create state images.
Uses the first frame of transition videos as the start state image.
"""

import json
import cv2
from pathlib import Path

def extract_first_frame(video_path: str, output_path: str) -> bool:
    """Extract first frame from video."""
    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(output_path, frame)
            print(f"✓ Extracted: {output_path}")
            return True
        else:
            print(f"✗ Failed to read: {video_path}")
            return False
    finally:
        cap.release()

def main():
    # Load the world
    world_path = "worlds/video_worlds/cube_world_navigation_maze.json"
    with open(world_path) as f:
        world = json.load(f)

    # Create output directory
    output_dir = Path("generated_images/cube_world_states")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Output directory: {output_dir}")
    print(f"🎬 Processing {len(world['transitions'])} transitions...")
    print()

    # Map of state_id -> video path (use first transition TO that state)
    state_to_video = {}

    # For initial state, use the first transition FROM it
    for transition in world['transitions']:
        end_state = transition['end_state_id']
        if end_state not in state_to_video:
            state_to_video[end_state] = transition['video_path']

    # For the initial state (s0), use the video of the first transition
    first_transition = world['transitions'][0]
    state_to_video['s0'] = first_transition['video_path']

    # Extract frames for each state
    extracted = 0
    for state in world['states']:
        state_id = state['state_id']

        if state_id in state_to_video:
            video_path = state_to_video[state_id]
            output_path = output_dir / f"{state_id}.png"

            if extract_first_frame(video_path, str(output_path)):
                # Update the state's image_path
                state['image_path'] = str(output_path)
                extracted += 1
        else:
            print(f"⚠ No video found for state: {state_id}")

    # Save updated world
    with open(world_path, 'w') as f:
        json.dump(world, f, indent=2)

    print()
    print(f"✅ Extracted {extracted}/{len(world['states'])} state images")
    print(f"✅ Updated {world_path}")

if __name__ == "__main__":
    main()
