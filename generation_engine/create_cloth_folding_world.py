#!/usr/bin/env python3
"""
Create the cloth folding multi-ending world using the World API.
This ensures proper format with full state/action objects in transitions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World, State, Action, Transition

# Create the cloth folding world
world = World(name="Cloth Folding and Sorting", description="A multi-ending world about folding and sorting laundry with different approaches and outcomes")

# Define all states
states = {
    "s0": State(
        state_id="s0",
        description="Large pile of clean laundry dumped on bed - mixed clothes, towels, and linens all jumbled together",
        metadata={"sorting_progress": 0.0, "organization_level": "chaotic"}
    ),
    "s1a": State(
        state_id="s1a",
        description="Clothes carefully sorted into neat piles by category - shirts, pants, towels, linens each in separate stacks",
        metadata={"sorting_progress": 0.3, "organization_level": "organized", "sorted_by_category": True}
    ),
    "s1b": State(
        state_id="s1b",
        description="Grabbed random items from pile and started folding without sorting - mixed categories scattered around",
        metadata={"sorting_progress": 0.1, "organization_level": "messy", "sorted_by_category": False}
    ),
    "s2a": State(
        state_id="s2a",
        description="Methodically folding each category using proper techniques - crisp folds, uniform stack heights",
        metadata={"sorting_progress": 0.6, "organization_level": "excellent", "folding_quality": "professional"}
    ),
    "s2b": State(
        state_id="s2b",
        description="Haphazardly folding items in random order - some folded neatly, others crumpled, losing track of what's done",
        metadata={"sorting_progress": 0.3, "organization_level": "chaotic", "folding_quality": "inconsistent"}
    ),
    "s3a": State(
        state_id="s3a",
        description="All items folded beautifully - stacks organized by type, ready to be put away in drawers",
        metadata={"sorting_progress": 0.9, "organization_level": "perfect", "folding_quality": "excellent"}
    ),
    "s2c": State(
        state_id="s2c",
        description="Frustrated with tedious folding - some items tossed in wrinkled balls, debating whether to continue",
        metadata={"sorting_progress": 0.25, "organization_level": "deteriorating", "frustration_level": "high"}
    ),
    "s3b": State(
        state_id="s3b",
        description="Mixed results - some items folded acceptably, others barely folded, piles starting to tip over",
        metadata={"sorting_progress": 0.6, "organization_level": "unstable", "folding_quality": "mediocre"}
    ),
    "s3c": State(
        state_id="s3c",
        description="Gave up on folding properly - just making rough rectangles and stacking loosely",
        metadata={"sorting_progress": 0.5, "organization_level": "barely acceptable", "folding_quality": "minimal"}
    ),
    "s_perfect": State(
        state_id="s_perfect",
        description="Perfect completion: All laundry folded using Marie Kondo method, organized by category, stacked vertically in drawers for easy visibility",
        metadata={"sorting_complete": True, "quality": 1.0, "outcome": "success", "organization_level": "marie_kondo_level", "time_taken": "careful"}
    ),
    "s_organized": State(
        state_id="s_organized",
        description="Well organized: All laundry folded neatly, sorted by type, stacks are stable and tidy in closet",
        metadata={"sorting_complete": True, "quality": 0.8, "outcome": "success", "organization_level": "very_good", "time_taken": "moderate"}
    ),
    "s_acceptable": State(
        state_id="s_acceptable",
        description="Acceptable finish: Laundry mostly folded, some wrinkles remain, stacks are uneven but functional",
        metadata={"sorting_complete": True, "quality": 0.6, "outcome": "success", "organization_level": "adequate", "wrinkles": "some"}
    ),
    "s_gave_up": State(
        state_id="s_gave_up",
        description="Gave up frustrated: Half-folded pile abandoned on bed, many items still wrinkled and unfolded",
        metadata={"sorting_complete": False, "quality": 0.2, "outcome": "failure", "organization_level": "failed", "items_unfinished": "many"}
    ),
    "s_stuffed": State(
        state_id="s_stuffed",
        description="Stuffed drawers: Gave up folding, just crammed everything into drawers - clothes compressed and wrinkled",
        metadata={"sorting_complete": False, "quality": 0.3, "outcome": "failure", "organization_level": "compressed_chaos", "wrinkles": "severe"}
    ),
    "s_avalanche": State(
        state_id="s_avalanche",
        description="Stack collapse: Poorly stacked piles toppled over when moving them, clothes scattered across floor requiring re-folding",
        metadata={"sorting_complete": False, "quality": 0.1, "outcome": "failure", "organization_level": "disaster", "needs_refold": True}
    )
}

# Define all actions
actions = {
    "a_sort_carefully": Action(
        action_id="a_sort_carefully",
        description="Sort all clothes carefully by category before folding - shirts, pants, towels, linens",
        action_type="preparation"
    ),
    "a_skip_sorting": Action(
        action_id="a_skip_sorting",
        description="Skip sorting step and start folding items randomly from the pile",
        action_type="preparation"
    ),
    "a_fold_methodical": Action(
        action_id="a_fold_methodical",
        description="Fold each category methodically using proper folding techniques, taking time to make crisp folds",
        action_type="execution"
    ),
    "a_fold_random": Action(
        action_id="a_fold_random",
        description="Fold items randomly without system, using inconsistent techniques",
        action_type="execution"
    ),
    "a_persist_quality": Action(
        action_id="a_persist_quality",
        description="Continue folding carefully maintaining high quality standards throughout",
        action_type="persistence"
    ),
    "a_get_frustrated": Action(
        action_id="a_get_frustrated",
        description="Get frustrated with tedious folding task, quality starts to decline",
        action_type="emotional"
    ),
    "a_perfect_finish": Action(
        action_id="a_perfect_finish",
        description="Finish with Marie Kondo vertical folding method, organize perfectly in drawers",
        action_type="finishing"
    ),
    "a_good_finish": Action(
        action_id="a_good_finish",
        description="Complete folding competently, stack neatly in closet",
        action_type="finishing"
    ),
    "a_quit_frustrated": Action(
        action_id="a_quit_frustrated",
        description="Give up in frustration, leave half-folded pile on bed",
        action_type="termination"
    ),
    "a_rush_finish": Action(
        action_id="a_rush_finish",
        description="Rush through remaining items just to finish, quality suffers",
        action_type="finishing"
    ),
    "a_stuff_drawers": Action(
        action_id="a_stuff_drawers",
        description="Give up folding, just stuff remaining clothes into drawers unfolded",
        action_type="termination"
    ),
    "a_sloppy_stack": Action(
        action_id="a_sloppy_stack",
        description="Stack items sloppily without care for stability",
        action_type="finishing"
    ),
    "a_quick_acceptable": Action(
        action_id="a_quick_acceptable",
        description="Fold quickly but acceptably, prioritize speed over perfection",
        action_type="finishing"
    ),
    "a_move_stacks": Action(
        action_id="a_move_stacks",
        description="Try to move unstable stacks to closet",
        action_type="finishing"
    )
}

# Assign states and actions to world
world.states = list(states.values())
world.actions = list(actions.values())

# Set initial state
world.initial_state = states["s0"]

# Define and create all transitions
transitions_data = [
    ("s0", "a_sort_carefully", "s1a"),
    ("s0", "a_skip_sorting", "s1b"),
    ("s1a", "a_fold_methodical", "s2a"),
    ("s1b", "a_fold_random", "s2b"),
    ("s2a", "a_persist_quality", "s3a"),
    ("s2b", "a_get_frustrated", "s2c"),
    ("s2b", "a_sloppy_stack", "s3b"),
    ("s3a", "a_perfect_finish", "s_perfect"),
    ("s3a", "a_good_finish", "s_organized"),
    ("s2c", "a_quit_frustrated", "s_gave_up"),
    ("s2c", "a_rush_finish", "s3c"),
    ("s3c", "a_quick_acceptable", "s_acceptable"),
    ("s3c", "a_stuff_drawers", "s_stuffed"),
    ("s3b", "a_quick_acceptable", "s_acceptable"),
    ("s3b", "a_move_stacks", "s_avalanche")
]

world.transitions = []
for i, (start_id, action_id, end_id) in enumerate(transitions_data):
    transition = Transition(
        transition_id=f"t_{i}",
        start_state=states[start_id],
        action=actions[action_id],
        end_state=states[end_id]
    )
    world.transitions.append(transition)

# Save the world
output_file = "worlds/llm_worlds/cloth_folding_multi_ending_world.json"
Path("worlds/llm_worlds").mkdir(parents=True, exist_ok=True)
world.save(output_file)

print("=" * 70)
print("CLOTH FOLDING WORLD CREATED")
print("=" * 70)
print(f"\n✅ World saved to: {output_file}")
print(f"\nStates: {len(world.states)}")
print(f"Actions: {len(world.actions)}")
print(f"Transitions: {len(world.transitions)}")
print(f"\nInitial state: {world.initial_state.state_id}")

print("\nState breakdown:")
print(f"  Initial: 1 (s0)")
print(f"  Intermediate: 8 (s1a, s1b, s2a, s2b, s2c, s3a, s3b, s3c)")
print(f"  Final endings: 6")
print(f"    - Success: 3 (s_perfect, s_organized, s_acceptable)")
print(f"    - Failure: 3 (s_gave_up, s_stuffed, s_avalanche)")

print("\n✅ Ready to generate images with:")
print("   python3 generate_cloth_folding_images.py")
