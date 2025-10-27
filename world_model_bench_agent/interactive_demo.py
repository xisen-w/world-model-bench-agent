#!/usr/bin/env python3
"""
Interactive Demo for AC-World Benchmark.

This script allows users to interactively explore world scenarios by:
1. Loading a world from JSON
2. Displaying current state
3. Showing available actions
4. Transitioning to next states based on user choices
5. Tracking success/failure outcomes
"""

import sys
import os
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from world_model_bench_agent.benchmark_curation import (
    World,
    State,
    Action,
    Transition,
    load_world_from_json
)


class InteractiveWorldExplorer:
    """Interactive explorer for world scenarios."""

    def __init__(self, world: World):
        """
        Initialize the explorer with a world.

        Args:
            world: The World object to explore
        """
        self.world = world
        self.current_state = world.initial_state
        self.history: List[Transition] = []
        self.steps_taken = 0

    def display_state(self):
        """Display the current state with formatting."""
        print("\n" + "=" * 70)
        print("CURRENT STATE")
        print("=" * 70)
        print(f"\nState ID: {self.current_state.state_id}")
        print(f"Description: {self.current_state.description}")

        # Show metadata if available
        if self.current_state.metadata:
            print(f"\nMetadata:")
            for key, value in self.current_state.metadata.items():
                print(f"  - {key}: {value}")

        # Show step count
        print(f"\nSteps taken: {self.steps_taken}")

    def display_actions(self) -> List[Action]:
        """
        Display available actions from current state.

        Returns:
            List of available actions
        """
        available_actions = self.world.get_possible_actions(self.current_state)

        if not available_actions:
            return []

        print("\n" + "-" * 70)
        print("AVAILABLE ACTIONS")
        print("-" * 70)

        for i, action in enumerate(available_actions, 1):
            print(f"\n{i}. {action.description}")
            if action.action_type:
                print(f"   Type: {action.action_type}")
            if action.metadata:
                for key, value in action.metadata.items():
                    print(f"   {key}: {value}")

        return available_actions

    def display_outcome(self):
        """Display the final outcome when reaching an endpoint."""
        print("\n" + "=" * 70)
        print("FINAL OUTCOME")
        print("=" * 70)

        is_goal = self.world.is_goal_state(self.current_state)
        is_final = self.world.is_final_state(self.current_state)

        if is_goal:
            print("\nSUCCESS! You reached a goal state!")
            quality = self.current_state.metadata.get("quality", "N/A")
            print(f"Quality: {quality}")
        elif is_final:
            print("\nFAILURE. You reached a non-goal final state.")
            quality = self.current_state.metadata.get("quality", "N/A")
            print(f"Quality: {quality}")

        print(f"\nFinal State: {self.current_state.description}")
        print(f"Total steps: {self.steps_taken}")

        # Show the path taken
        if self.history:
            print("\n" + "-" * 70)
            print("YOUR PATH")
            print("-" * 70)
            for i, transition in enumerate(self.history, 1):
                print(f"\nStep {i}:")
                print(f"  From: {transition.start_state.state_id}")
                print(f"  Action: {transition.action.description}")
                print(f"  To: {transition.end_state.state_id}")

    def get_user_choice(self, available_actions: List[Action]) -> Optional[Action]:
        """
        Get user's action choice.

        Args:
            available_actions: List of actions to choose from

        Returns:
            Selected action or None if user wants to quit
        """
        while True:
            print("\n" + "-" * 70)
            choice = input(f"Choose an action (1-{len(available_actions)}) or 'q' to quit: ").strip().lower()

            if choice == 'q':
                return None

            try:
                index = int(choice) - 1
                if 0 <= index < len(available_actions):
                    return available_actions[index]
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(available_actions)}.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")

    def perform_action(self, action: Action) -> bool:
        """
        Perform an action and transition to the next state.

        Args:
            action: The action to perform

        Returns:
            True if transition was successful, False otherwise
        """
        # Find the transition
        next_states = self.world.get_next_states(self.current_state, action)

        if not next_states:
            print("\nError: No valid transition found for this action.")
            return False

        # If multiple next states (non-deterministic), pick the first one
        # In the future, could add probabilistic selection
        next_state = next_states[0]

        # Find the actual transition object for history
        transition = None
        for t in self.world.transitions:
            if t.start_state == self.current_state and t.action == action and t.end_state == next_state:
                transition = t
                break

        # Update state
        self.current_state = next_state
        self.steps_taken += 1

        if transition:
            self.history.append(transition)

        # Show transition
        print("\n" + ">" * 70)
        print(f"Performing action: {action.description}")
        print(">" * 70)

        return True

    def run(self):
        """Run the interactive exploration."""
        print("\n" + "=" * 70)
        print(f"INTERACTIVE WORLD EXPLORER: {self.world.name}")
        print("=" * 70)
        print(f"\n{self.world.description}")

        # Show world info
        print(f"\nWorld Statistics:")
        print(f"  Total states: {len(self.world.states)}")
        print(f"  Total actions: {len(self.world.actions)}")
        print(f"  Total transitions: {len(self.world.transitions)}")
        print(f"  Goal states: {len(self.world.goal_states)}")
        print(f"  Final states: {len(self.world.get_final_states())}")

        print("\nGoals (Successful Outcomes):")
        for goal in self.world.goal_states:
            quality = goal.metadata.get("quality", "N/A")
            print(f"  - [{goal.state_id}] Quality: {quality}")

        input("\nPress Enter to start exploring...")

        # Main game loop
        while True:
            # Display current state
            self.display_state()

            # Check if we're at a final state
            if self.world.is_final_state(self.current_state):
                self.display_outcome()
                break

            # Display available actions
            available_actions = self.display_actions()

            if not available_actions:
                print("\nNo actions available from this state. Exploration ends here.")
                break

            # Get user choice
            chosen_action = self.get_user_choice(available_actions)

            if chosen_action is None:
                print("\nExploration ended by user.")
                break

            # Perform action
            if not self.perform_action(chosen_action):
                print("Failed to perform action. Try again.")
                continue

        # Final summary
        print("\n" + "=" * 70)
        print("EXPLORATION COMPLETE")
        print("=" * 70)
        print(f"\nThank you for exploring '{self.world.name}'!")


def list_available_worlds() -> List[str]:
    """
    List all available world JSON files in the current directory.

    Returns:
        List of JSON file paths
    """
    json_files = list(Path(".").glob("*_world.json"))
    return [str(f) for f in json_files]


def select_world() -> Optional[str]:
    """
    Let user select a world to explore.

    Returns:
        Selected world file path or None
    """
    worlds = list_available_worlds()

    if not worlds:
        print("No world files found in current directory.")
        print("Please run 'benchmark_curation.py' first to generate world files.")
        return None

    print("\n" + "=" * 70)
    print("AVAILABLE WORLDS")
    print("=" * 70)

    for i, world_file in enumerate(worlds, 1):
        print(f"{i}. {world_file}")

    while True:
        choice = input(f"\nSelect a world (1-{len(worlds)}) or 'q' to quit: ").strip().lower()

        if choice == 'q':
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(worlds):
                return worlds[index]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(worlds)}.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("AC-WORLD INTERACTIVE DEMO")
    print("=" * 70)
    print("\nExplore action-conditioned world scenarios interactively!")
    print("Make choices, see outcomes, and understand state transitions.")

    # Select world
    world_file = select_world()
    if not world_file:
        print("\nExiting.")
        return 0

    # Load world
    try:
        print(f"\nLoading world from: {world_file}")
        world = World.load(world_file)
        print(f"World loaded successfully!")
    except Exception as e:
        print(f"\nError loading world: {e}")
        return 1

    # Validate world has initial state
    if not world.initial_state:
        print("\nError: World has no initial state defined.")
        return 1

    # Run interactive explorer
    explorer = InteractiveWorldExplorer(world)
    explorer.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
