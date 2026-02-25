#!/usr/bin/env python3
"""
Quick test script for Cube World Navigation Maze
"""

import json
from pathlib import Path

def test_cube_world():
    """Test that cube world JSON is valid and well-formed."""

    world_path = Path("worlds/video_worlds/cube_world_navigation_maze.json")

    print("=" * 70)
    print("CUBE WORLD NAVIGATION MAZE - TEST SCRIPT")
    print("=" * 70)

    # Load JSON
    with open(world_path) as f:
        data = json.load(f)

    print(f"\n✓ JSON loaded successfully from: {world_path}")
    print(f"\n📋 World: {data['name']}")
    print(f"📝 Description: {data['description'][:100]}...")

    # Check basic structure
    print(f"\n🏗️  STRUCTURE:")
    print(f"   States: {len(data['states'])}")
    print(f"   Transitions: {len(data['transitions'])}")
    print(f"   Initial state: {data['initial_state_id']}")
    print(f"   Goal states: {len(data['goal_state_ids'])}")
    print(f"   Failure states: {len(data['failure_state_ids'])}")

    # Verify video files exist
    print(f"\n🎥 VIDEO FILES:")
    video_dir = Path("experiments/recorded_videos/cube_world")
    missing_videos = []

    for transition in data['transitions']:
        video_path = Path(transition['video_path'])
        if video_path.exists():
            print(f"   ✓ {video_path.name}")
        else:
            print(f"   ✗ MISSING: {video_path}")
            missing_videos.append(video_path)

    if missing_videos:
        print(f"\n⚠️  Warning: {len(missing_videos)} video files not found")
    else:
        print(f"\n✓ All {len(data['transitions'])} video files found!")

    # Analyze paths
    print(f"\n🗺️  PATH ANALYSIS:")

    # Success paths
    print(f"\n   Success Paths ({len(data['goal_state_ids'])}):")
    for i, goal_id in enumerate(data['goal_state_ids'], 1):
        goal_state = next(s for s in data['states'] if s['state_id'] == goal_id)
        success_type = goal_state['metadata'].get('success_type', 'unknown')
        path_length = goal_state['metadata'].get('path_length', 'unknown')
        print(f"      {i}. {goal_id}: {success_type} ({path_length} path)")

    # Dead ends
    print(f"\n   Dead-Ends ({len(data['failure_state_ids'])}):")
    for i, fail_id in enumerate(data['failure_state_ids'], 1):
        fail_state = next(s for s in data['states'] if s['state_id'] == fail_id)
        track = fail_state['metadata'].get('track', 'unknown')
        print(f"      {i}. {fail_id}: {track}")

    # Branching analysis
    print(f"\n🌲 BRANCHING POINTS:")
    branching_points = data['metadata']['branching_points']
    for bp in branching_points:
        print(f"   {bp['state_id']}: {bp['branches']} branches - {bp['description']}")

    # Test connectivity
    print(f"\n🔗 CONNECTIVITY TEST:")
    state_ids = {s['state_id'] for s in data['states']}
    orphaned = []

    for state in data['states']:
        if state['state_id'] == data['initial_state_id']:
            continue  # Initial state is always connected

        # Check if any transition leads to this state
        has_incoming = any(t['end_state_id'] == state['state_id']
                          for t in data['transitions'])

        if not has_incoming:
            orphaned.append(state['state_id'])

    if orphaned:
        print(f"   ⚠️  Warning: {len(orphaned)} orphaned states: {orphaned}")
    else:
        print(f"   ✓ All non-initial states are reachable!")

    # Verify all transitions reference valid states
    print(f"\n🔍 TRANSITION VALIDATION:")
    invalid_refs = []

    for i, transition in enumerate(data['transitions']):
        if transition['start_state_id'] not in state_ids:
            invalid_refs.append(f"T{i}: Invalid start_state {transition['start_state_id']}")
        if transition['end_state_id'] not in state_ids:
            invalid_refs.append(f"T{i}: Invalid end_state {transition['end_state_id']}")

    if invalid_refs:
        print(f"   ✗ Errors found:")
        for ref in invalid_refs:
            print(f"      {ref}")
    else:
        print(f"   ✓ All {len(data['transitions'])} transitions reference valid states!")

    # Statistics
    print(f"\n📊 STATISTICS:")

    # Calculate path lengths to each goal
    from collections import deque

    def find_shortest_path(start_id, goal_id):
        """BFS to find shortest path."""
        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            current_id, path = queue.popleft()

            if current_id == goal_id:
                return path

            # Find all transitions from current state
            for t in data['transitions']:
                if t['start_state_id'] == current_id:
                    next_id = t['end_state_id']
                    if next_id not in visited:
                        visited.add(next_id)
                        queue.append((next_id, path + [next_id]))

        return None

    print(f"\n   Shortest paths from {data['initial_state_id']}:")
    for goal_id in data['goal_state_ids']:
        path = find_shortest_path(data['initial_state_id'], goal_id)
        if path:
            print(f"      → {goal_id}: {len(path)-1} transitions")
            print(f"         Path: {' → '.join(path)}")
        else:
            print(f"      → {goal_id}: UNREACHABLE!")

    # Summary
    print(f"\n" + "=" * 70)
    print("✅ CUBE WORLD VALIDATION COMPLETE")
    print("=" * 70)

    if not missing_videos and not orphaned and not invalid_refs:
        print("\n🎉 All tests passed! World is ready for agent testing.")
        print(f"\n🎮 To play interactively:")
        print(f"   python game.py --video {world_path}")
        print(f"\n🎬 To run video demo:")
        print(f"   python interactive_video_demo.py")
        print(f"   (Select option 4: cube_world_navigation_maze.json)")
        return True
    else:
        print("\n⚠️  Some issues detected. Please review above.")
        return False


if __name__ == "__main__":
    success = test_cube_world()
    exit(0 if success else 1)
