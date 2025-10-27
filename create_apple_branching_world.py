#!/usr/bin/env python3
"""
Create a branching apple eating world with multiple paths.

This world includes:
- Different ways to prepare the apple (cut vs bite)
- Different eating patterns
- Alternative endings (fully eaten, partially eaten, abandoned)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World, State, Action, Transition

# Define states
s0 = State(
    description="Empty white table with only a red apple sitting in the center",
    state_id="s0"
)

# Branch 1: Cut the apple
s1a = State(
    description="The red apple has been sliced in half, showing the white flesh and seeds inside. A knife is visible next to the apple halves",
    state_id="s1a"
)

# Branch 2: Bite the apple
s1b = State(
    description="The apple has a large bite taken out of it, showing teeth marks on one side. The apple is still whole otherwise",
    state_id="s1b"
)

# From s1a: Eat the cut apple slices
s2a = State(
    description="The apple slices have been eaten, leaving only the apple cores and knife on the table",
    state_id="s2a"
)

# From s1a: Put one half in a container
s2b = State(
    description="One apple half has been placed in a transparent container. The other half and knife remain on the table",
    state_id="s2b"
)

# From s1b: Continue biting (multiple bites)
s2c = State(
    description="The apple has multiple bite marks and only the core remains visible. Apple pieces are scattered on the table",
    state_id="s2c"
)

# From s1b: Slice the bitten apple
s2d = State(
    description="The bitten apple has been cut into slices around the bite mark. Knife and irregular apple pieces on table",
    state_id="s2d"
)

# From s2b: Eat the remaining half
s3a = State(
    description="The container with one apple half is on the table. The other half has been eaten, leaving only the core and knife",
    state_id="s3a"
)

# Define actions
a0a = Action(
    description="Cut the apple in half with a knife, exposing the inside",
    action_id="a0a"
)

a0b = Action(
    description="Take a large bite directly from the apple",
    action_id="a0b"
)

a1a = Action(
    description="Eat the apple slices, leaving only the cores",
    action_id="a1a"
)

a1b = Action(
    description="Place one apple half in a transparent container",
    action_id="a1b"
)

a1c = Action(
    description="Continue biting the apple multiple times until only the core remains",
    action_id="a1c"
)

a1d = Action(
    description="Use the knife to slice the bitten apple into pieces",
    action_id="a1d"
)

a2a = Action(
    description="Eat the remaining apple half",
    action_id="a2a"
)

# Create world with all transitions
world = World(
    name="apple_eating_branching",
    description="Eating an apple with multiple preparation and consumption methods",
    states=[s0, s1a, s1b, s2a, s2b, s2c, s2d, s3a],
    actions=[a0a, a0b, a1a, a1b, a1c, a1d, a2a],
    transitions=[
        # Branch 1: Cut path
        Transition(s0, a0a, s1a),
        Transition(s1a, a1a, s2a),  # Canonical: cut and eat all
        Transition(s1a, a1b, s2b),  # Alternative: save one half

        # Branch 2: Bite path
        Transition(s0, a0b, s1b),
        Transition(s1b, a1c, s2c),  # Continue biting
        Transition(s1b, a1d, s2d),  # Switch to cutting after bite

        # Continue from s2b
        Transition(s2b, a2a, s3a),
    ],
    initial_state=s0,
    goal_states=[s2a, s2c, s3a]  # Multiple successful endings
)

# Print world summary
print("Apple Eating Branching World")
print("=" * 70)
print(f"Name: {world.name}")
print(f"Description: {world.description}")
print(f"\nStates: {len(world.states)}")
for state in world.states:
    print(f"  [{state.state_id}] {state.description[:60]}...")

print(f"\nActions: {len(world.actions)}")
for action in world.actions:
    print(f"  [{action.action_id}] {action.description}")

print(f"\nTransitions: {len(world.transitions)}")
for i, t in enumerate(world.transitions):
    print(f"  {t.start_state.state_id} --[{t.action.action_id}]--> {t.end_state.state_id}")

print(f"\nInitial State: {world.initial_state.state_id}")
print(f"Goal States: {[s.state_id for s in world.goal_states]}")

# Get paths
print(f"\n" + "=" * 70)
print("PATHS ANALYSIS")
print("=" * 70)

paths = world.get_all_paths()
print(f"\nTotal paths from initial to goal: {len(paths)}")
for i, path in enumerate(paths, 1):
    print(f"\nPath {i}: ({len(path)} transitions)")
    path_str = world.initial_state.state_id
    for transition in path:
        path_str += f" --[{transition.action.action_id}]--> {transition.end_state.state_id}"
    print(f"  {path_str}")

# Save to JSON
output_file = "apple_eating_branching_world.json"
world.save(output_file)
print(f"\n" + "=" * 70)
print(f"Saved to: {output_file}")
print("=" * 70)
