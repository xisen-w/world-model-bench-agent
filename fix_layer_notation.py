#!/usr/bin/env python3
"""
Fix cube descriptions to use proper Rubik's cube layer twist notation.
Each action is a 90-degree rotation of a specific layer.
"""

import json

# Proper layer twist descriptions
# Based on video names, mapping to likely layer moves
action_descriptions = {
    "a0_initial": "Pick up the cube to begin. Starting configuration ready for first move.",

    # Recovering right path - likely R moves
    "a1_recover_right_1": "Twist the right face 90° clockwise (R move). The right layer rotates, changing the edge and corner pieces on that face.",

    "a2_recover_right_2": "Twist the right face 90° clockwise again (R move). Second consecutive right face rotation.",

    # Turn right clean - another R move
    "a3_turn_right_clean": "Twist the right face 90° clockwise (R move). Rotate the right layer to change its configuration.",

    # Turn down - likely D move (bottom face)
    "a4_turn_down_t2": "Twist the bottom face 90° clockwise (D move). The bottom layer rotates, affecting the lower edges and corners.",

    # Turn left - likely L move
    "a5_turn_left_recover": "Twist the left face 90° clockwise (L move). The left layer rotates, changing pieces on that side.",

    # Loop back continuation
    "a14_loop_back": "Continue to next configuration. The cube state cycles back to an earlier branching point.",

    # Turn down from track 3 - D move
    "a6_turn_down_t3": "Twist the bottom face 90° clockwise (D move). Rotate the bottom layer to change the lower face configuration.",

    # Turn up - likely U move (top face)
    "a7_turn_up": "Twist the top face 90° clockwise (U move). The upper layer rotates, changing the top edges and corners.",

    # Turn right from track 4 - R move
    "a8_turn_right_t4": "Twist the right face 90° clockwise (R move). Another right face layer rotation.",

    # Turn right again - second consecutive R
    "a9_turn_right_again": "Twist the right face 90° clockwise again (R move). Second consecutive right layer twist in this sequence.",

    # Turn down after rights - D move
    "a10_turn_down_t4_1_1": "Twist the bottom face 90° clockwise (D move). Rotate the bottom layer downward.",

    # Turn right third time - third R
    "a11_turn_right_third": "Twist the right face 90° clockwise for the third time (R move). Third consecutive right layer rotation completes this sequence.",

    # Direct left - L move
    "a12_direct_left": "Twist the left face 90° clockwise (L move). Direct left layer rotation from this configuration.",

    # Turn left-down - could be L followed by D, or a different interpretation
    "a13_turn_left_down": "Twist the left face 90° clockwise followed by bottom face 90° clockwise (L then D moves). Combined layer rotation sequence."
}

# State descriptions focusing on layer configurations
state_descriptions = {
    "s0": "Starting configuration. The cube is in its initial state, ready for the first layer twist. All faces show their starting color patterns.",

    "s1": "After the first move, the cube shows a new configuration. Multiple layer twists are possible: right face (R), left face (L), top face (U), or bottom face (D). Each will create a different arrangement of colors and patterns.",

    "s2_track1": "The right face has been twisted once (R move applied). The layer rotation created new edge and corner positions. Another right face twist is available to continue this sequence.",

    "s_success_1": "Success! After two consecutive right face twists (R R sequence), the cube has reached a solved configuration. The color patterns align correctly.",

    "s3_track2": "One right face twist completed (R move). From here, you can twist either the bottom face (D move) or the left face (L move). Different layer choices lead to different outcomes.",

    "s_dead_1": "Dead end. After twisting right then down (R D sequence), the cube is in an unsolvable configuration for this challenge. The layer combination doesn't lead to any solution.",

    "s4_track2_recovery": "After right and left layer twists (R then L sequence), the cube has returned to a familiar configuration. The state resembles an earlier branching point with multiple options.",

    "s_dead_2": "Dead end. The bottom face twist from the initial state (D move) led to a configuration that doesn't connect to any solution path. This layer choice was not productive.",

    "s5_track4": "The top face has been twisted (U move applied). The upper layer rotation changed the top edges and corners. From this configuration, three layer options are available: right face (R), left face (L), or a combination move.",

    "s6_track4_1": "After top and right twists (U R sequence). The cube shows the result of these two layer rotations. Another choice: continue with right (R) or twist bottom (D).",

    "s7_track4_1_again": "Two consecutive right face twists after the top twist (U R R sequence). The layer rotations have significantly changed the configuration. Final decision: one more right twist (R) or bottom twist (D).",

    "s_dead_3": "Dead end. The sequence U R R D (top, right, right, down) led to an unsolvable configuration. The bottom face twist at this point was the wrong choice.",

    "s_success_3": "Success! Three consecutive right face twists after the top twist (U R R R sequence) solved the cube. This longer layer sequence reached a valid solution.",

    "s_success_2": "Success! The top face followed by left face twist (U L sequence) quickly solved the cube. This efficient two-move layer sequence is the shortest solution.",

    "s_dead_4": "Dead end. After the top twist, the left-bottom combination (U then L D) created an unsolvable state. This layer sequence doesn't lead to solutions."
}

def main():
    # Update video world
    video_path = "worlds/video_worlds/cube_world_navigation_maze.json"
    with open(video_path) as f:
        video_world = json.load(f)

    # Update name and description
    video_world["name"] = "rubiks_cube_layer_twist_challenge"
    video_world["description"] = "A 3x3 Rubik's cube layer twist challenge. Each action is a 90-degree rotation of a specific layer (R, L, U, D, F, B notation). Find the correct sequence of layer twists to reach solved configurations."

    # Update state descriptions
    for state in video_world['states']:
        sid = state['state_id']
        if sid in state_descriptions:
            state['text_description'] = state_descriptions[sid]

    # Update action descriptions
    for transition in video_world['transitions']:
        aid = transition['action_id']
        if aid in action_descriptions:
            transition['action_description'] = action_descriptions[aid]

    with open(video_path, 'w') as f:
        json.dump(video_world, f, indent=2)

    print(f"✅ Updated video world: {video_path}")

    # Update text world
    text_path = "worlds/llm_worlds/cube_world_recorded_gameplay.json"
    with open(text_path) as f:
        text_world = json.load(f)

    # Update name and description
    text_world["name"] = "rubiks_cube_layer_twist_challenge"
    text_world["description"] = "3x3 Rubik's cube layer manipulation challenge with standard notation (R, L, U, D moves)."

    # Update states
    for state in text_world['states']:
        sid = state['state_id']
        if sid in state_descriptions:
            state['description'] = state_descriptions[sid]

    # Update initial state
    if text_world['initial_state']['state_id'] in state_descriptions:
        text_world['initial_state']['description'] = state_descriptions[text_world['initial_state']['state_id']]

    # Update goal states
    for goal in text_world['goal_states']:
        sid = goal['state_id']
        if sid in state_descriptions:
            goal['description'] = state_descriptions[sid]

    # Update actions
    for action in text_world['actions']:
        aid = action['action_id']
        if aid in action_descriptions:
            action['description'] = action_descriptions[aid]

    # Update transitions
    for trans in text_world['transitions']:
        if trans['start_state']['state_id'] in state_descriptions:
            trans['start_state']['description'] = state_descriptions[trans['start_state']['state_id']]
        if trans['end_state']['state_id'] in state_descriptions:
            trans['end_state']['description'] = state_descriptions[trans['end_state']['state_id']]
        if trans['action']['action_id'] in action_descriptions:
            trans['action']['description'] = action_descriptions[trans['action']['action_id']]

    with open(text_path, 'w') as f:
        json.dump(text_world, f, indent=2)

    print(f"✅ Updated text world: {text_path}")
    print("\n✅ NOW USING PROPER LAYER NOTATION!")
    print("   - Each action = 90° layer twist")
    print("   - R = Right face clockwise")
    print("   - L = Left face clockwise")
    print("   - U = Top face clockwise")
    print("   - D = Bottom face clockwise")
    print("   - Example sequences: R R (double right) or U R R R (top + triple right)")

if __name__ == "__main__":
    main()
