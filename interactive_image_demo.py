#!/usr/bin/env python3
"""
Interactive Image Demo - Visual World Explorer Game

Play through world scenarios with images displayed for each state!
Shows images in the terminal using ASCII art or opens in default viewer.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from PIL import Image
import subprocess

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World, Action, Transition
from world_model_bench_agent.image_world_generator import ImageWorld, ImageState


class VisualWorldExplorer:
    """Interactive explorer with image display."""

    def __init__(self, image_world: ImageWorld, text_world: World):
        """
        Initialize the visual explorer.

        Args:
            image_world: ImageWorld with state images
            text_world: Original text world for transitions
        """
        self.image_world = image_world
        self.text_world = text_world

        # Find initial state in image world
        initial_state_id = text_world.initial_state.state_id
        self.current_image_state = self._find_image_state(initial_state_id)
        self.current_text_state = text_world.initial_state

        self.history: List[Transition] = []
        self.steps_taken = 0

    def _find_image_state(self, state_id: str) -> Optional[ImageState]:
        """Find image state by ID."""
        for state in self.image_world.states:
            if state.state_id == state_id:
                return state
        return None

    def _find_text_state(self, state_id: str):
        """Find text state by ID."""
        for state in self.text_world.states:
            if state.state_id == state_id:
                return state
        return None

    def display_image(self):
        """Display the current state image."""
        if not self.current_image_state or not self.current_image_state.image_path:
            print("\n[No image available for this state]")
            return

        image_path = Path(self.current_image_state.image_path)

        if not image_path.exists():
            print(f"\n[Image file not found: {image_path}]")
            return

        print(f"\n📷 Image: {image_path}")

        # Try to open image in default viewer
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(image_path)], check=False)
            elif sys.platform == "win32":  # Windows
                os.startfile(str(image_path))
            else:  # Linux
                subprocess.run(["xdg-open", str(image_path)], check=False)
            print("   [Image opened in viewer]")
        except Exception as e:
            print(f"   [Could not open image: {e}]")

    def display_state(self):
        """Display the current state with image."""
        print("\n" + "=" * 70)
        print("CURRENT STATE")
        print("=" * 70)
        print(f"\n🏷️  State ID: {self.current_text_state.state_id}")
        print(f"📝 Description: {self.current_text_state.description}")

        # Show metadata
        if self.current_text_state.metadata:
            print(f"\n📊 Metadata:")
            for key, value in self.current_text_state.metadata.items():
                if key == 'assembly_progress':
                    progress_bar = '█' * int(value * 20) + '░' * (20 - int(value * 20))
                    print(f"   {key}: [{progress_bar}] {value*100:.0f}%")
                elif key == 'quality':
                    stars = '⭐' * int(value * 5)
                    print(f"   {key}: {stars} ({value})")
                elif key == 'outcome':
                    emoji = '✅' if value == 'success' else '❌'
                    print(f"   {key}: {emoji} {value}")
                else:
                    print(f"   {key}: {value}")

        print(f"\n👣 Steps taken: {self.steps_taken}")

        # Display image
        self.display_image()

    def display_actions(self) -> List[Action]:
        """Display available actions."""
        available_actions = self.text_world.get_possible_actions(self.current_text_state)

        if not available_actions:
            return []

        print("\n" + "-" * 70)
        print("⚡ AVAILABLE ACTIONS")
        print("-" * 70)

        for i, action in enumerate(available_actions, 1):
            # Add emoji based on action type
            emoji = "🔧"
            if action.action_type == "preparation":
                emoji = "📚"
            elif action.action_type == "assembly":
                emoji = "🔨"
            elif action.action_type == "finishing":
                emoji = "✨"
            elif action.action_type == "emotional":
                emoji = "😤"
            elif action.action_type == "testing":
                emoji = "🧪"
            elif action.action_type == "termination":
                emoji = "🚪"

            print(f"\n{i}. {emoji} {action.description}")
            if action.action_type:
                print(f"   Type: {action.action_type}")

        return available_actions

    def display_outcome(self):
        """Display the final outcome."""
        print("\n" + "=" * 70)
        print("🏁 FINAL OUTCOME")
        print("=" * 70)

        is_goal = self.text_world.is_goal_state(self.current_text_state)
        is_final = self.text_world.is_final_state(self.current_text_state)

        if is_goal:
            quality = self.current_text_state.metadata.get("quality", 0)
            stars = '⭐' * int(quality * 5)
            print(f"\n✅ SUCCESS! You reached a goal state!")
            print(f"Quality: {stars} ({quality})")

            if quality == 1.0:
                print("\n🏆 PERFECT! You achieved the best possible outcome!")
            elif quality >= 0.8:
                print("\n🥈 Great job! Very good outcome!")
            else:
                print("\n🥉 Acceptable outcome, but could be better.")

        elif is_final:
            quality = self.current_text_state.metadata.get("quality", 0)
            print(f"\n❌ FAILURE. You reached a non-goal final state.")
            print(f"Quality: {quality}")

            if quality <= 0.2:
                print("\n😞 Better luck next time!")

        print(f"\nFinal State: {self.current_text_state.description}")
        print(f"Total steps: {self.steps_taken}")

        # Show the path taken
        if self.history:
            print("\n" + "-" * 70)
            print("🗺️  YOUR PATH")
            print("-" * 70)
            for i, transition in enumerate(self.history, 1):
                print(f"\nStep {i}:")
                print(f"  📍 From: {transition.start_state.state_id}")
                print(f"  ⚡ Action: {transition.action.description}")
                print(f"  📍 To: {transition.end_state.state_id}")

    def get_user_choice(self, available_actions: List[Action]) -> Optional[Action]:
        """Get user's action choice."""
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
                    print(f"❌ Invalid choice. Please enter 1-{len(available_actions)}.")
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'q'.")

    def perform_action(self, action: Action) -> bool:
        """Perform action and transition to next state."""
        # Find next states
        next_states = self.text_world.get_next_states(self.current_text_state, action)

        if not next_states:
            print("\n❌ Error: No valid transition found.")
            return False

        next_state = next_states[0]

        # Find transition for history
        transition = None
        for t in self.text_world.transitions:
            if (t.start_state == self.current_text_state and
                t.action == action and
                t.end_state == next_state):
                transition = t
                break

        # Update states
        self.current_text_state = next_state
        self.current_image_state = self._find_image_state(next_state.state_id)
        self.steps_taken += 1

        if transition:
            self.history.append(transition)

        # Show transition
        print("\n" + ">" * 70)
        print(f"⚡ Performing: {action.description}")
        print(">" * 70)

        return True

    def run(self):
        """Run the interactive visual exploration game."""
        print("\n" + "=" * 70)
        print(f"🎮 VISUAL WORLD EXPLORER: {self.text_world.name}")
        print("=" * 70)
        print(f"\n{self.text_world.description}")

        # Show world info
        print(f"\n📊 World Statistics:")
        print(f"  States: {len(self.text_world.states)}")
        print(f"  Actions: {len(self.text_world.actions)}")
        print(f"  Transitions: {len(self.text_world.transitions)}")
        print(f"  Images: {len(self.image_world.states)}")

        print("\n🎯 Goals (Successful Outcomes):")
        for goal in self.text_world.goal_states:
            quality = goal.metadata.get("quality", "N/A")
            stars = '⭐' * int(float(quality) * 5) if isinstance(quality, (int, float)) else ''
            print(f"  [{goal.state_id}] {stars} Quality: {quality}")

        input("\n🚀 Press Enter to start your journey...")

        # Main game loop
        while True:
            self.display_state()

            # Check if final state
            if self.text_world.is_final_state(self.current_text_state):
                self.display_outcome()
                break

            # Display actions
            available_actions = self.display_actions()

            if not available_actions:
                print("\n🛑 No actions available. Game ends here.")
                break

            # Get choice
            chosen_action = self.get_user_choice(available_actions)

            if chosen_action is None:
                print("\n👋 Goodbye!")
                break

            # Perform action
            if not self.perform_action(chosen_action):
                print("Failed to perform action. Try again.")
                continue

        # Final summary
        print("\n" + "=" * 70)
        print("🎮 GAME COMPLETE")
        print("=" * 70)
        print(f"\nThank you for playing '{self.text_world.name}'!")


def list_image_worlds() -> List[Path]:
    """List all image world JSON files."""
    image_worlds_dir = Path("worlds/image_worlds")
    if image_worlds_dir.exists():
        return list(image_worlds_dir.glob("*.json"))
    return []


def select_world() -> Optional[Path]:
    """Let user select an image world."""
    worlds = list_image_worlds()

    if not worlds:
        print("❌ No image world files found.")
        print("Please run the image world generator first.")
        return None

    print("\n" + "=" * 70)
    print("🌍 AVAILABLE IMAGE WORLDS")
    print("=" * 70)

    for i, world_file in enumerate(worlds, 1):
        print(f"{i}. {world_file.name}")

    while True:
        choice = input(f"\nSelect a world (1-{len(worlds)}) or 'q' to quit: ").strip().lower()

        if choice == 'q':
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(worlds):
                return worlds[index]
            else:
                print(f"❌ Invalid. Please enter 1-{len(worlds)}.")
        except ValueError:
            print("❌ Invalid input.")


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🎮 VISUAL WORLD EXPLORER GAME")
    print("=" * 70)
    print("\n🖼️  Explore worlds with images!")
    print("📸 Make choices and see the results visually!")

    # Select world
    world_file = select_world()
    if not world_file:
        print("\n👋 Exiting.")
        return 0

    try:
        print(f"\n📂 Loading: {world_file}")
        image_world = ImageWorld.load(str(world_file))

        # Load corresponding text world from worlds/llm_worlds/
        # Handle different naming patterns
        source = image_world.text_world_source
        if "IKEA_desk_assembly_multi_ending" in source or "ikea_desk_multi_ending" in source:
            text_world_file = "ikea_desk_multi_ending_world.json"
        elif "apple_eating_branching" in source or "apple_eating" in source:
            text_world_file = "apple_eating_branching_world.json"
        elif "coffee" in source:
            text_world_file = "coffee_linear_world.json"
        else:
            # Try with _world.json suffix first (standard naming)
            text_world_file = f"{source}_world.json"

        # Look in worlds/llm_worlds/
        text_world_path = Path("worlds/llm_worlds") / text_world_file
        if not text_world_path.exists():
            # Try without _world suffix
            text_world_file = f"{source}.json"
            text_world_path = Path("worlds/llm_worlds") / text_world_file

        if not text_world_path.exists():
            # Fallback to current directory for backward compatibility
            text_world_path = Path(text_world_file)
            if not text_world_path.exists():
                # Try one more time with _world suffix in current dir
                text_world_file = f"{source}_world.json"
                text_world_path = Path(text_world_file)
                if not text_world_path.exists():
                    print(f"❌ Text world not found: {text_world_file}")
                    print(f"   Tried: {source}_world.json and {source}.json")
                    print(f"   Looked in: worlds/llm_worlds/ and current directory")
                    return 1

        text_world = World.load(str(text_world_path))
        print(f"✅ Worlds loaded successfully!")

    except Exception as e:
        print(f"\n❌ Error loading world: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Validate
    if not text_world.initial_state:
        print("\n❌ World has no initial state.")
        return 1

    # Run game
    explorer = VisualWorldExplorer(image_world, text_world)
    explorer.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
