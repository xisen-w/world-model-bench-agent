#!/usr/bin/env python3
"""
Interactive Video Demo - Cinematic World Explorer Game

Play through world scenarios with transition videos!
Watch videos of your actions playing out in real-time.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
import subprocess
import time

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World, Action, Transition
from world_model_bench_agent.video_world_generator import VideoWorld, VideoTransition
from world_model_bench_agent.image_world_generator import ImageState


class CinematicWorldExplorer:
    """Interactive explorer with video playback."""

    def __init__(self, video_world: VideoWorld, text_world: World):
        """
        Initialize the cinematic explorer.

        Args:
            video_world: VideoWorld with transition videos
            text_world: Original text world for game logic
        """
        self.video_world = video_world
        self.text_world = text_world

        # Find initial state
        initial_state_id = text_world.initial_state.state_id
        self.current_state = self._find_image_state(initial_state_id)
        self.current_text_state = text_world.initial_state

        self.history: List[Transition] = []
        self.steps_taken = 0

    def _find_image_state(self, state_id: str) -> Optional[ImageState]:
        """Find state by ID."""
        for state in self.video_world.states:
            if state.state_id == state_id:
                return state
        return None

    def _find_text_state(self, state_id: str):
        """Find text state by ID."""
        for state in self.text_world.states:
            if state.state_id == state_id:
                return state
        return None

    def _find_video_transition(self, start_id: str, action_id: str, end_id: str) -> Optional[VideoTransition]:
        """Find video transition."""
        for trans in self.video_world.transitions:
            if (trans.start_state_id == start_id and
                trans.action_id == action_id and
                trans.end_state_id == end_id):
                return trans
        return None

    def play_video(self, video_path: str):
        """Play a video file."""
        if not Path(video_path).exists():
            print(f"\n📹 [Video not available: {video_path}]")
            return

        print(f"\n🎬 Playing video: {Path(video_path).name}")
        print("   [Opening video player...]")

        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", video_path], check=False)
            elif sys.platform == "win32":  # Windows
                os.startfile(video_path)
            else:  # Linux
                subprocess.run(["xdg-open", video_path], check=False)

            print("   ▶️  Video playing in viewer")
            time.sleep(2)  # Give time for video to start

        except Exception as e:
            print(f"   ❌ Could not play video: {e}")

    def display_current_frame(self):
        """Display current state image."""
        if not self.current_state or not self.current_state.image_path:
            print("\n[No image available]")
            return

        image_path = Path(self.current_state.image_path)

        if not image_path.exists():
            print(f"\n[Image not found: {image_path}]")
            return

        print(f"\n📷 Current Frame: {image_path.name}")

        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(image_path)], check=False)
            elif sys.platform == "win32":
                os.startfile(str(image_path))
            else:
                subprocess.run(["xdg-open", str(image_path)], check=False)
            print("   [Frame displayed]")
        except Exception as e:
            print(f"   [Could not display: {e}]")

    def display_state(self):
        """Display current state."""
        print("\n" + "=" * 70)
        print("🎬 CURRENT SCENE")
        print("=" * 70)
        print(f"\n🏷️  State: {self.current_text_state.state_id}")
        print(f"📝 {self.current_text_state.description}")

        # Show metadata with cinematiceffects
        if self.current_text_state.metadata:
            print(f"\n📊 Status:")
            for key, value in self.current_text_state.metadata.items():
                if key == 'assembly_progress':
                    progress_bar = '█' * int(value * 20) + '░' * (20 - int(value * 20))
                    print(f"   Progress: [{progress_bar}] {value*100:.0f}%")
                elif key == 'quality':
                    stars = '⭐' * int(value * 5)
                    print(f"   Quality: {stars} ({value})")
                elif key == 'outcome':
                    emoji = '✅' if value == 'success' else '❌'
                    print(f"   Outcome: {emoji} {value.upper()}")
                elif key == 'frustration_level':
                    print(f"   😤 Frustration: {value}")
                else:
                    print(f"   {key}: {value}")

        print(f"\n🎞️  Scene: {self.steps_taken + 1}")

        # Display current frame
        self.display_current_frame()

    def display_actions(self) -> List[Action]:
        """Display available actions as scene choices."""
        available_actions = self.text_world.get_possible_actions(self.current_text_state)

        if not available_actions:
            return []

        print("\n" + "-" * 70)
        print("🎬 WHAT HAPPENS NEXT? (Choose Your Action)")
        print("-" * 70)

        for i, action in enumerate(available_actions, 1):
            # Add cinematic emoji
            emoji = "🎬"
            if "read" in action.description.lower() or "instruction" in action.description.lower():
                emoji = "📖"
            elif "careful" in action.description.lower() or "methodical" in action.description.lower():
                emoji = "🧘"
            elif "skip" in action.description.lower() or "toss" in action.description.lower():
                emoji = "🗑️"
            elif "frustrat" in action.description.lower():
                emoji = "😤"
            elif "quit" in action.description.lower() or "give up" in action.description.lower():
                emoji = "🚪"
            elif "rush" in action.description.lower():
                emoji = "💨"
            elif "perfect" in action.description.lower():
                emoji = "✨"
            elif "test" in action.description.lower():
                emoji = "🧪"

            print(f"\n{i}. {emoji} {action.description}")

            # Show if video is available
            next_states = self.text_world.get_next_states(self.current_text_state, action)
            if next_states:
                next_state = next_states[0]
                video_trans = self._find_video_transition(
                    self.current_text_state.state_id,
                    action.action_id,
                    next_state.state_id
                )
                if video_trans and video_trans.video_path:
                    print(f"   🎥 Video available!")
                else:
                    print(f"   📸 Images only")

        return available_actions

    def display_outcome(self):
        """Display final outcome."""
        print("\n" + "=" * 70)
        print("🎬 THE END")
        print("=" * 70)

        is_goal = self.text_world.is_goal_state(self.current_text_state)

        if is_goal:
            quality = self.current_text_state.metadata.get("quality", 0)
            stars = '⭐' * int(quality * 5)
            print(f"\n🎉 SUCCESS! {stars}")
            print(f"Quality Score: {quality}")

            if quality == 1.0:
                print("\n🏆 PERFECT ENDING!")
                print("You achieved the best possible outcome!")
            elif quality >= 0.8:
                print("\n🥈 GOOD ENDING!")
                print("Great work! Minor imperfections.")
            else:
                print("\n🥉 ACCEPTABLE ENDING")
                print("You made it, but it could be better.")

        else:
            quality = self.current_text_state.metadata.get("quality", 0)
            print(f"\n💔 BAD ENDING")
            print(f"Quality Score: {quality}")

            if quality <= 0.2:
                print("\n😞 You gave up too soon...")
            elif quality <= 0.3:
                print("\n🔧 Wrong assembly path...")
            else:
                print("\n💥 Structural failure...")

        print(f"\nFinal Scene: {self.current_text_state.description}")
        print(f"Total Scenes: {self.steps_taken + 1}")

        # Show the movie you created
        if self.history:
            print("\n" + "-" * 70)
            print("🎞️  YOUR MOVIE")
            print("-" * 70)
            for i, transition in enumerate(self.history, 1):
                print(f"\nScene {i}:")
                print(f"  🎬 {transition.action.description}")
                print(f"  📍 {transition.start_state.state_id} → {transition.end_state.state_id}")

    def get_user_choice(self, available_actions: List[Action]) -> Optional[Action]:
        """Get user's action choice."""
        while True:
            print("\n" + "-" * 70)
            choice = input(f"🎬 Choose scene (1-{len(available_actions)}) or 'q' to quit: ").strip().lower()

            if choice == 'q':
                return None

            try:
                index = int(choice) - 1
                if 0 <= index < len(available_actions):
                    return available_actions[index]
                else:
                    print(f"❌ Invalid. Choose 1-{len(available_actions)}.")
            except ValueError:
                print("❌ Invalid input.")

    def perform_action(self, action: Action) -> bool:
        """Perform action with video playback."""
        # Find next state
        next_states = self.text_world.get_next_states(self.current_text_state, action)

        if not next_states:
            print("\n❌ No valid transition!")
            return False

        next_state = next_states[0]

        # Find transition
        transition = None
        for t in self.text_world.transitions:
            if (t.start_state == self.current_text_state and
                t.action == action and
                t.end_state == next_state):
                transition = t
                break

        # Find and play video
        video_trans = self._find_video_transition(
            self.current_text_state.state_id,
            action.action_id,
            next_state.state_id
        )

        print("\n" + ">" * 70)
        print(f"🎬 ACTION: {action.description}")
        print(">" * 70)

        if video_trans and video_trans.video_path and Path(video_trans.video_path).exists():
            print("\n🎥 Playing transition video...")
            self.play_video(video_trans.video_path)
            input("\n⏸️  Press Enter when video finishes...")
        else:
            print("\n📸 (Video not available, showing still images)")
            time.sleep(1)

        # Update state
        self.current_text_state = next_state
        self.current_state = self._find_image_state(next_state.state_id)
        self.steps_taken += 1

        if transition:
            self.history.append(transition)

        return True

    def run(self):
        """Run the cinematic game."""
        print("\n" + "=" * 70)
        print(f"🎬 CINEMATIC WORLD EXPLORER: {self.text_world.name}")
        print("=" * 70)
        print(f"\n{self.text_world.description}")

        # Show info
        print(f"\n📊 Production Stats:")
        print(f"  Scenes: {len(self.text_world.states)}")
        print(f"  Actions: {len(self.text_world.actions)}")
        print(f"  Videos: {len([t for t in self.video_world.transitions if t.video_path])}")

        print("\n🎯 Possible Endings:")
        for goal in self.text_world.goal_states:
            quality = goal.metadata.get("quality", "N/A")
            stars = '⭐' * int(float(quality) * 5) if isinstance(quality, (int, float)) else ''
            print(f"  [{goal.state_id}] {stars} Quality: {quality}")

        input("\n🎬 Press Enter to start the movie...")

        # Main loop
        while True:
            self.display_state()

            if self.text_world.is_final_state(self.current_text_state):
                self.display_outcome()
                break

            available_actions = self.display_actions()

            if not available_actions:
                print("\n🎬 THE END (No more choices)")
                break

            chosen_action = self.get_user_choice(available_actions)

            if chosen_action is None:
                print("\n🎬 Movie cancelled.")
                break

            if not self.perform_action(chosen_action):
                continue

        print("\n" + "=" * 70)
        print("🎬 CREDITS ROLL")
        print("=" * 70)
        print(f"\nThank you for watching '{self.text_world.name}'!")
        print("\n🎥 Your choices created a unique story!")


def list_video_worlds() -> List[Path]:
    """List video world JSON files."""
    video_worlds_dir = Path("worlds/video_worlds")
    if video_worlds_dir.exists():
        return list(video_worlds_dir.glob("*.json"))
    return []


def select_world() -> Optional[Path]:
    """Let user select a video world."""
    worlds = list_video_worlds()

    if not worlds:
        print("❌ No video worlds found.")
        print("Run video generation first.")
        return None

    print("\n" + "=" * 70)
    print("🎬 AVAILABLE CINEMATIC WORLDS")
    print("=" * 70)

    for i, world_file in enumerate(worlds, 1):
        print(f"{i}. {world_file.name}")

    while True:
        choice = input(f"\nSelect (1-{len(worlds)}) or 'q': ").strip().lower()

        if choice == 'q':
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(worlds):
                return worlds[index]
        except ValueError:
            pass
        print("❌ Invalid input.")


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🎬 CINEMATIC WORLD EXPLORER")
    print("=" * 70)
    print("\n🎥 Watch your choices come to life!")
    print("🎞️  Interactive storytelling with videos!")

    world_file = select_world()
    if not world_file:
        return 0

    try:
        print(f"\n📂 Loading: {world_file}")
        video_world = VideoWorld.load(str(world_file))

        # Load text world from worlds/llm_worlds/
        # Handle different naming patterns
        image_source = video_world.image_world_source
        if "ikea_desk_multi_ending" in image_source:
            text_world_file = "ikea_desk_multi_ending_world.json"
        elif "apple_eating" in image_source:
            text_world_file = "apple_eating_branching_world.json"
        elif "indoor_plant" in image_source:
            text_world_file = "indoor_plant_watering_repotting_branching_egocentric_world.json"
        else:
            text_world_name = image_source.replace("_images", "").replace("_image_world", "")
            text_world_file = f"{text_world_name}.json"

        # Look in worlds/llm_worlds/
        text_world_path = Path("worlds/llm_worlds") / text_world_file
        if not text_world_path.exists():
            # Fallback to current directory
            text_world_path = Path(text_world_file)
            if not text_world_path.exists():
                print(f"❌ Text world not found: {text_world_file}")
                print(f"   Looked in: worlds/llm_worlds/ and current directory")
                return 1

        text_world = World.load(str(text_world_path))
        print(f"✅ Loaded successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if not text_world.initial_state:
        print("\n❌ No initial state.")
        return 1

    explorer = CinematicWorldExplorer(video_world, text_world)
    explorer.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
