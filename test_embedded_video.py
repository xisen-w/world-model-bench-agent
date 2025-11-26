#!/usr/bin/env python3
"""Test embedded video playback."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
import time
from game import WorldExplorerGame

def test_embedded_video():
    """Test embedded video playback flow."""
    world_path = "worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json"

    print("Testing embedded video playback...")
    game = WorldExplorerGame("video", world_path)

    print(f"\n✅ Game initialized")
    print(f"   Current state: {game.current_state.state_id}")

    # Get first action
    action = game.action_buttons[0].action
    print(f"\n📹 Starting video playback...")
    print(f"   Action: {action.description[:60]}...")

    # Perform action (should load video)
    game.perform_action(action)

    if game.video_player.is_playing:
        print(f"   ✅ Video player started!")
        print(f"   Video: {game.video_player.video_path}")
        print(f"   FPS: {game.video_player.fps}")
        print(f"   Total frames: {game.video_player.total_frames}")
        print(f"   Pending action: {game.pending_action is not None}")

        # Simulate game loop updates
        print(f"\n▶️  Simulating playback...")
        frame_count = 0
        max_frames = 50  # Test first 50 frames

        start_time = pygame.time.get_ticks()
        last_frame = 0

        while frame_count < max_frames and game.video_player.is_playing:
            # Advance pygame ticks
            pygame.time.wait(10)  # Small delay

            # Update video
            game.video_player.update()

            # Check if finished
            if game.video_player.is_finished() and game.pending_action:
                start_state, _, end_state = game.pending_action
                game.complete_action(start_state, action, end_state)
                game.pending_action = None
                print(f"   ✅ Video finished and action completed!")
                print(f"   New state: {game.current_state.state_id}")
                break

            # Check if new frame
            if game.video_player.frame_count > last_frame:
                last_frame = game.video_player.frame_count
                if last_frame % 10 == 0:
                    progress = (game.video_player.frame_count / game.video_player.total_frames) * 100
                    print(f"   Frame {game.video_player.frame_count}/{game.video_player.total_frames} ({progress:.1f}%)")

            frame_count += 1

        if frame_count >= max_frames:
            print(f"   ⏸️  Stopped test after {frame_count} frames")
            print(f"   Video still playing: {game.video_player.is_playing}")

    else:
        print(f"   ❌ Video player did not start")
        return False

    pygame.quit()
    print(f"\n✅ Embedded video test complete!")
    return True

if __name__ == "__main__":
    success = test_embedded_video()
    sys.exit(0 if success else 1)
