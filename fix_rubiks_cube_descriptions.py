#!/usr/bin/env python3
"""
Fix cube world descriptions to properly reflect Rubik's cube manipulation
instead of maze navigation.
"""

import json

# Proper Rubik's cube state descriptions based on what the player sees
state_descriptions = {
    "s0": "You're holding a Rubik's cube at the starting configuration. The cube sits on the desk in front of you, ready to be manipulated. Your hands are positioned to make the first move.",

    "s1": "The cube is in a new configuration after the initial rotation. From this position, you can see multiple colored faces. You have several rotation options: rotate the cube to show different faces, or twist specific layers. Multiple moves are possible from here.",

    "s2_track1": "You've rotated the cube to reveal a specific face configuration. The cube's orientation has changed, showing a different arrangement of colors. Another rotation in a similar direction is available.",

    "s_success_1": "The cube has reached a target configuration! The colors align in a specific pattern. This is one of the solved states for this challenge.",

    "s3_track2": "The cube is oriented showing a particular face arrangement. From this configuration, you have choices: you can rotate downward to see the bottom, or rotate left to change the viewing angle.",

    "s_dead_1": "This cube configuration is a dead end. The color pattern here doesn't lead to any valid solution paths. You'll need to backtrack and try a different rotation sequence.",

    "s4_track2_recovery": "After the previous rotation, the cube is back in a familiar-looking configuration. The color patterns and face orientations resemble an earlier position. You've effectively returned to a state with multiple options again.",

    "s_dead_2": "The cube is oriented with the bottom face visible, but this configuration leads nowhere. The color arrangement here is not part of any solution sequence.",

    "s5_track4": "You've rotated the cube upward, now viewing it from a higher angle. The top face and upper edge colors are prominently visible. From this elevated perspective, you have three rotation options: continue rotating right, rotate directly left, or tilt left-downward.",

    "s6_track4_1": "The cube has been rotated to the right from the upper perspective. You're viewing a specific corner and edge arrangement. Another rotation choice: continue right again, or rotate downward.",

    "s7_track4_1_again": "After two consecutive right rotations, the cube shows a different face configuration. You've rotated significantly from the starting position. One more right rotation would complete a pattern, or you could rotate down to explore a different orientation.",

    "s_dead_3": "This cube orientation after the downward rotation is a dead end. The face configuration here doesn't connect to any solution paths.",

    "s_success_3": "Success! After three consecutive right rotations, the cube has reached a solved configuration. The color patterns align correctly for this solution path.",

    "s_success_2": "Success! The direct left rotation from the upper view brought the cube to a solved state quickly. This is the most efficient solution path.",

    "s_dead_4": "The left-downward rotation led to a configuration that doesn't advance toward any solution. The visible faces show a pattern that isn't part of the solution space."
}

# Proper Rubik's cube action descriptions
action_descriptions = {
    "a0_initial": "Pick up the cube and make the first rotation. Position your hands to begin manipulating the cube.",

    "a1_recover_right_1": "Rotate the cube to the right. Twist your wrist to show the right-side faces.",

    "a2_recover_right_2": "Rotate the cube to the right again. Continue the rightward rotation to reveal the next face configuration.",

    "a3_turn_right_clean": "Rotate the cube to the right. Turn the cube to display the right-facing surfaces.",

    "a4_turn_down_t2": "Rotate the cube downward. Tilt the cube forward to bring the bottom face into view.",

    "a5_turn_left_recover": "Rotate the cube to the left. Turn the cube counterclockwise to show the left-side faces.",

    "a14_loop_back": "Continue rotating. The cube completes its rotation sequence and returns to a familiar orientation with multiple available moves.",

    "a6_turn_down_t3": "Rotate the cube downward. Tilt the cube to expose the bottom face and lower edges.",

    "a7_turn_up": "Rotate the cube upward. Lift and tilt the cube backward to bring the top face into prominent view.",

    "a8_turn_right_t4": "Rotate the cube to the right. From the upper viewing angle, rotate clockwise to change the visible faces.",

    "a9_turn_right_again": "Rotate the cube to the right again. Make a second consecutive rightward rotation, showing progressively different face configurations.",

    "a10_turn_down_t4_1_1": "Rotate the cube downward. After the previous rotations, tilt the cube forward to view the lower faces.",

    "a11_turn_right_third": "Rotate the cube to the right for the third time. Complete the third consecutive rightward rotation, bringing the cube to a final configuration.",

    "a12_direct_left": "Rotate the cube to the left. From the upper view, make a direct leftward rotation.",

    "a13_turn_left_down": "Rotate the cube left and downward. Combine a leftward turn with a downward tilt, viewing the cube from a lower angle."
}

def main():
    # Update video world
    video_path = "worlds/video_worlds/cube_world_navigation_maze.json"
    with open(video_path) as f:
        video_world = json.load(f)

    # Update metadata
    video_world["name"] = "rubiks_cube_rotation_challenge"
    video_world["description"] = "A Rubik's cube manipulation challenge with multiple solution paths. Physical cube rotations lead to different configurations, with some sequences reaching solved states and others leading to dead ends."
    video_world["domain"] = "physical_manipulation"

    # Update state descriptions
    for state in video_world['states']:
        sid = state['state_id']
        if sid in state_descriptions:
            state['text_description'] = state_descriptions[sid]

    # Update action descriptions in transitions
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

    # Update metadata
    text_world["name"] = "rubiks_cube_rotation_challenge"
    text_world["description"] = "A Rubik's cube manipulation challenge with branching rotation sequences."
    text_world["domain"] = "physical_manipulation"

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
        # Update state descriptions
        if trans['start_state']['state_id'] in state_descriptions:
            trans['start_state']['description'] = state_descriptions[trans['start_state']['state_id']]
        if trans['end_state']['state_id'] in state_descriptions:
            trans['end_state']['description'] = state_descriptions[trans['end_state']['state_id']]
        # Update action description
        if trans['action']['action_id'] in action_descriptions:
            trans['action']['description'] = action_descriptions[trans['action']['action_id']]

    with open(text_path, 'w') as f:
        json.dump(text_world, f, indent=2)

    print(f"✅ Updated text world: {text_path}")
    print("\n✅ FIXED: Now properly describes Rubik's cube manipulation!")
    print("   - States describe cube configurations and visible faces")
    print("   - Actions describe physical rotations (right, left, up, down)")
    print("   - Success = reaching solved cube configurations")
    print("   - Dead ends = configurations that don't lead to solutions")
    print("   - No more 'corridor' or 'maze' language!")

if __name__ == "__main__":
    main()
