#!/usr/bin/env python3
"""
Rephrase cube world actions to remove god-perspective hints.
Describe only what the agent sees in geometric/spatial terms.
"""

import json

# New action descriptions in pure geometric/observational terms
action_descriptions = {
    "a0_initial": "Move forward through the geometric entrance tunnel. The cube walls shift around you as you proceed deeper into the structure.",

    "a1_recover_right_1": "Turn right. The corridor curves smoothly to the right with clean geometric angles.",

    "a2_recover_right_2": "Continue forward and turn right again. The corridor bends in the same direction, maintaining consistent rightward curvature.",

    "a3_turn_right_clean": "Turn right. A straight, well-lit corridor extends ahead. You notice another branching point in the distance.",

    "a4_turn_down_t2": "Turn down. The corridor descends vertically. The passage slopes downward into the lower levels of the cube structure.",

    "a5_turn_left_recover": "Turn left. The corridor curves to the left, arcing through the cube geometry.",

    "a14_loop_back": "Continue forward. The corridor completes its curve and opens into a familiar-looking crossroads area.",

    "a6_turn_down_t3": "Turn down. The passage descends steeply. Vertical walls narrow as you move downward through the cube layers.",

    "a7_turn_up": "Turn up. The corridor ascends vertically, rising through the cube structure to an upper level. The geometry opens up as you reach higher elevation.",

    "a8_turn_right_t4": "Turn right. A corridor extends forward with parallel geometric walls and consistent angles.",

    "a9_turn_right_again": "Turn right again. Another rightward turn, following the same directional pattern. The corridor continues with similar geometric properties.",

    "a10_turn_down_t4_1_1": "Turn down. The corridor descends from this junction, angling downward through the cube geometry.",

    "a11_turn_right_third": "Turn right once more. A third consecutive rightward turn. The corridor bends in the same direction, completing a consistent rotational sequence.",

    "a12_direct_left": "Turn left. A direct leftward turn from this junction. The corridor extends in this new direction.",

    "a13_turn_left_down": "Turn left and down. The corridor slopes both leftward and downward simultaneously, descending at an angle."
}

# State descriptions - remove hints about success/failure
state_descriptions = {
    "s0": "You stand at the entrance of a geometric cube maze. Multiple pathways branch into the structure. Cubic walls form precise angles around you.",

    "s1": "You're at a major junction. Four distinct corridors branch from this central point: right with a curve, right straight ahead, down, and up. The cube's geometry makes it impossible to see beyond the immediate branches.",

    "s2_track1": "You're in a curved rightward corridor. The walls angle in a consistent arc. Another turn is visible ahead, continuing in a similar direction.",

    "s_success_1": "The corridor opens into an exit chamber. Geometric patterns align perfectly on the walls. You've found one of the maze exits.",

    "s3_track2": "You're in a straight corridor after a right turn. Another branching point ahead: one path leads down, another curves left.",

    "s_dead_1": "The corridor terminates in a solid wall. No further passage. The geometric patterns here are irregular and chaotic.",

    "s4_track2_recovery": "You're in a curving leftward corridor. The passage arcs smoothly. You notice the geometry starting to look familiar.",

    "s_dead_2": "The downward corridor ends abruptly. A solid wall blocks any further progress. The passage terminates here.",

    "s5_track4": "You're at an upper-level junction after ascending. Three corridors branch from here: right, directly left, and left-downward. The space feels more open at this elevation.",

    "s6_track4_1": "You're in a corridor after turning right from the upper level. The passage extends forward. Another branching point is visible ahead: right again, or down.",

    "s7_track4_1_again": "You're in a corridor after two consecutive right turns. A junction ahead offers: right for a third time, or turn down. The right path appears slightly wider and better lit.",

    "s_dead_3": "The corridor ends at a solid geometric corner. No exit. The passage terminates in a closed angle of the cube structure.",

    "s_success_3": "The corridor opens dramatically into an exit chamber. The walls form perfect aligned angles. You've navigated through to an exit.",

    "s_success_2": "The left corridor opens quickly into an exit chamber. Geometric walls align to form the maze exit. You've reached an exit point.",

    "s_dead_4": "The downward-sloping corridor ends in a narrow corner. No further passage. The walls converge to a closed point."
}

def main():
    # Update video world
    video_path = "worlds/video_worlds/cube_world_navigation_maze.json"
    with open(video_path) as f:
        video_world = json.load(f)

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
    print("\n✅ All descriptions updated to remove god-perspective!")
    print("   - Actions now describe only geometric movements")
    print("   - No hints about 'recovery', 'right answer', 'success', etc.")
    print("   - Pure observational descriptions of the cube maze")

if __name__ == "__main__":
    main()
