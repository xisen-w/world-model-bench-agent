#!/usr/bin/env python3
"""Test script to validate game initialization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Set SDL to use dummy video driver for headless testing
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from game import WorldExplorerGame

def test_game_init():
    """Test game initialization."""
    world_path = "worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json"

    print("Initializing game...")
    try:
        game = WorldExplorerGame("video", world_path)
        print(f"✅ Game initialized successfully!")
        print(f"   World: {game.world_name}")
        print(f"   Current state: {game.current_state.state_id}")
        print(f"   Action buttons: {len(game.action_buttons)}")

        # Test action execution
        if game.action_buttons:
            print(f"\n   Testing action execution...")
            first_action = game.action_buttons[0].action
            print(f"   Performing: {first_action.description[:50]}...")
            game.perform_action(first_action)
            print(f"   ✅ Action executed! New state: {game.current_state.state_id}")
            print(f"   ✅ New action count: {len(game.action_buttons)}")

        pygame.quit()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_game_init()
    sys.exit(0 if success else 1)
