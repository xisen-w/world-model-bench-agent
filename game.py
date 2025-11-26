#!/usr/bin/env python3
"""
Interactive World Explorer Game

A pygame-based interactive game for exploring world scenarios.
Supports video, image, and text-only modes.

Usage:
    python game.py --video worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json
    python game.py --image worlds/image_worlds/indoor_plant_watering_repotting_branching_egocentric_image_world.json
    python game.py --text worlds/llm_worlds/indoor_plant_watering_repotting_branching_egocentric_world.json
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, List, Tuple
import subprocess
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World, State, Action
from world_model_bench_agent.video_world_generator import VideoWorld, VideoTransition
from world_model_bench_agent.image_world_generator import ImageWorld, ImageState

# Import pygame
try:
    import pygame
    from pygame import Surface, Rect
except ImportError:
    print("ERROR: pygame not installed. Install with: pip install pygame")
    sys.exit(1)

# Try to import PIL for image display
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: PIL not installed. Image display will be limited. Install with: pip install Pillow")

# Try to import opencv for video playback
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("WARNING: opencv-python not installed. Video playback will use external player. Install with: pip install opencv-python")


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)
BLUE = (70, 130, 220)
DARK_BLUE = (50, 90, 160)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
YELLOW = (255, 220, 60)


class VideoPlayer:
    """Embedded video player using OpenCV."""

    def __init__(self, rect: Rect):
        self.rect = rect
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.is_playing = False
        self.fps = 30
        self.frame_count = 0
        self.total_frames = 0
        self.last_frame_time = 0

    def load_video(self, video_path: str) -> bool:
        """Load a video file."""
        if not HAS_OPENCV:
            return False

        try:
            self.video_path = video_path
            self.cap = cv2.VideoCapture(video_path)

            if not self.cap.isOpened():
                print(f"Failed to open video: {video_path}")
                return False

            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_count = 0
            self.is_playing = True
            self.last_frame_time = pygame.time.get_ticks()

            print(f"Video loaded: {video_path}")
            print(f"  FPS: {self.fps}, Total frames: {self.total_frames}")

            return True

        except Exception as e:
            print(f"Error loading video: {e}")
            return False

    def update(self) -> bool:
        """Update video playback. Returns False when video ends."""
        if not self.is_playing or not self.cap:
            return False

        current_time = pygame.time.get_ticks()
        time_per_frame = 1000 / self.fps  # milliseconds per frame

        # Check if it's time for next frame
        if current_time - self.last_frame_time >= time_per_frame:
            ret, frame = self.cap.read()

            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Resize to fit rect
                frame_h, frame_w = frame.shape[:2]
                rect_w, rect_h = self.rect.width, self.rect.height

                # Calculate scaling to fit
                scale = min(rect_w / frame_w, rect_h / frame_h)
                new_w = int(frame_w * scale)
                new_h = int(frame_h * scale)

                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                # Convert to pygame surface
                self.current_frame = pygame.surfarray.make_surface(
                    np.transpose(frame, (1, 0, 2))
                )

                self.frame_count += 1
                self.last_frame_time = current_time
                return True
            else:
                # Video ended
                self.stop()
                return False

        return True

    def draw(self, surface: Surface):
        """Draw current video frame."""
        if self.current_frame:
            # Center frame in rect
            frame_rect = self.current_frame.get_rect()
            frame_rect.center = self.rect.center
            surface.blit(self.current_frame, frame_rect)

            # Draw progress bar
            if self.total_frames > 0:
                progress = self.frame_count / self.total_frames
                bar_width = self.rect.width - 40
                bar_height = 8
                bar_x = self.rect.x + 20
                bar_y = self.rect.bottom - 30

                # Background
                pygame.draw.rect(surface, DARK_GRAY,
                               (bar_x, bar_y, bar_width, bar_height),
                               border_radius=4)
                # Progress
                pygame.draw.rect(surface, GREEN,
                               (bar_x, bar_y, int(bar_width * progress), bar_height),
                               border_radius=4)

    def stop(self):
        """Stop video playback."""
        self.is_playing = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def is_finished(self) -> bool:
        """Check if video has finished."""
        return not self.is_playing


class Button:
    """Simple button widget."""

    def __init__(self, rect: Rect, text: str, color=BLUE, text_color=WHITE):
        self.rect = rect
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False

    def draw(self, surface: Surface, font):
        color = DARK_BLUE if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=8)

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def update_hover(self, pos: Tuple[int, int]):
        self.hovered = self.rect.collidepoint(pos)


class WorldExplorerGame:
    """Main game class for world exploration."""

    def __init__(self, world_type: str, world_path: str):
        """
        Initialize the game.

        Args:
            world_type: "video", "image", or "text"
            world_path: Path to the world JSON file
        """
        pygame.init()

        # Window setup
        self.width = 1400
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("World Explorer Game")

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # Load world
        self.world_type = world_type
        self.world_path = world_path
        self.load_world()

        # Game state
        self.running = True
        self.clock = pygame.time.Clock()
        self.current_state = None
        self.history = []
        self.action_buttons = []
        self.current_image = None

        # UI setup
        self.setup_ui()

        # Video player
        self.video_player = VideoPlayer(self.media_rect)
        self.pending_action = None  # Action to execute after video finishes

        # Start at initial state
        self.set_initial_state()

    def load_world(self):
        """Load the world based on type."""
        print(f"Loading {self.world_type} world from {self.world_path}")

        if self.world_type == "video":
            self.video_world = VideoWorld.load(self.world_path)
            # Load corresponding text world
            self.text_world = self.load_text_world_for_video()
            self.world_name = self.video_world.name

        elif self.world_type == "image":
            self.image_world = ImageWorld.load(self.world_path)
            # Load corresponding text world
            self.text_world = self.load_text_world_for_image()
            self.world_name = self.image_world.name

        elif self.world_type == "text":
            self.text_world = World.load(self.world_path)
            self.world_name = self.text_world.name

        else:
            raise ValueError(f"Unknown world type: {self.world_type}")

    def load_text_world_for_video(self) -> World:
        """Load text world for video world."""
        image_source = self.video_world.image_world_source

        # Determine text world filename
        if "ikea_desk" in image_source:
            text_file = "ikea_desk_multi_ending_world.json"
        elif "apple_eating" in image_source:
            text_file = "apple_eating_branching_world.json"
        elif "indoor_plant" in image_source:
            text_file = "indoor_plant_watering_repotting_branching_egocentric_world.json"
        else:
            text_file = image_source.replace("_images", "").replace("_image_world", "") + ".json"

        text_path = Path("worlds/llm_worlds") / text_file
        if not text_path.exists():
            text_path = Path(text_file)

        return World.load(str(text_path))

    def load_text_world_for_image(self) -> World:
        """Load text world for image world."""
        # Similar logic
        text_source = self.image_world.text_world_source
        text_file = f"{text_source}.json"

        text_path = Path("worlds/llm_worlds") / text_file
        if not text_path.exists():
            text_path = Path(text_file)

        return World.load(str(text_path))

    def setup_ui(self):
        """Setup UI layout."""
        # Media area (left side for video/image)
        self.media_rect = Rect(20, 20, 800, 600)

        # State description area (right side)
        self.desc_rect = Rect(840, 20, 540, 300)

        # Action buttons area (right side, below description)
        self.actions_rect = Rect(840, 340, 540, 400)

        # History/stats area (bottom left)
        self.stats_rect = Rect(20, 640, 800, 240)

    def set_initial_state(self):
        """Set the initial state."""
        self.current_state = self.text_world.initial_state
        self.history = []
        self.update_action_buttons()
        self.load_current_media()

    def load_current_media(self):
        """Load media (image/video) for current state."""
        if self.world_type == "video":
            # For video, we load the image of the current state
            state = self.find_image_state(self.current_state.state_id)
            if state and state.image_path:
                self.load_image(state.image_path)

        elif self.world_type == "image":
            state = self.find_image_state(self.current_state.state_id)
            if state and state.image_path:
                self.load_image(state.image_path)

    def load_image(self, image_path: str):
        """Load and scale image for display."""
        if not HAS_PIL:
            self.current_image = None
            return

        try:
            img = Image.open(image_path)
            # Convert to RGB
            img = img.convert('RGB')

            # Scale to fit media rect
            img_w, img_h = img.size
            rect_w, rect_h = self.media_rect.width, self.media_rect.height

            # Calculate scaling to fit
            scale = min(rect_w / img_w, rect_h / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)

            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Convert to pygame surface
            mode = img.mode
            size = img.size
            data = img.tobytes()

            py_image = pygame.image.fromstring(data, size, mode)
            self.current_image = py_image

        except Exception as e:
            print(f"Error loading image: {e}")
            self.current_image = None

    def find_image_state(self, state_id: str) -> Optional[ImageState]:
        """Find image state by ID."""
        if self.world_type == "video":
            for state in self.video_world.states:
                if state.state_id == state_id:
                    return state
        elif self.world_type == "image":
            for state in self.image_world.states:
                if state.state_id == state_id:
                    return state
        return None

    def update_action_buttons(self):
        """Update action buttons based on current state."""
        available_actions = self.text_world.get_possible_actions(self.current_state)

        self.action_buttons = []
        button_height = 60
        button_spacing = 10
        start_y = self.actions_rect.y + 10

        for i, action in enumerate(available_actions):
            button_rect = Rect(
                self.actions_rect.x + 10,
                start_y + i * (button_height + button_spacing),
                self.actions_rect.width - 20,
                button_height
            )

            # Truncate long action descriptions
            text = action.description[:60] + "..." if len(action.description) > 60 else action.description

            button = Button(button_rect, text, color=BLUE)
            button.action = action  # Attach action to button
            self.action_buttons.append(button)

    def perform_action(self, action: Action):
        """Perform an action and transition to next state."""
        # Find next state
        next_states = self.text_world.get_next_states(self.current_state, action)

        if not next_states:
            print("No valid transition!")
            return

        next_state = next_states[0]

        # Play video if available (embedded or external)
        video_played = False
        if self.world_type == "video":
            video_trans = self.find_video_transition(
                self.current_state.state_id,
                action.action_id,
                next_state.state_id
            )

            if video_trans and video_trans.video_path and Path(video_trans.video_path).exists():
                if HAS_OPENCV:
                    # Use embedded video player
                    if self.video_player.load_video(video_trans.video_path):
                        # Store pending action data to update after video finishes
                        self.pending_action = (self.current_state, action, next_state)
                        video_played = True
                else:
                    # Fall back to external player
                    self.play_video_external(video_trans.video_path)

        # If no video, update state immediately
        if not video_played:
            self.complete_action(self.current_state, action, next_state)

    def complete_action(self, start_state: State, action: Action, end_state: State):
        """Complete action transition after video finishes."""
        # Update state
        self.history.append((start_state, action, end_state))
        self.current_state = end_state

        # Update UI
        self.update_action_buttons()
        self.load_current_media()

    def find_video_transition(self, start_id: str, action_id: str, end_id: str) -> Optional[VideoTransition]:
        """Find video transition."""
        for trans in self.video_world.transitions:
            if (trans.start_state_id == start_id and
                trans.action_id == action_id and
                trans.end_state_id == end_id):
                return trans
        return None

    def play_video_external(self, video_path: str):
        """Play video using external system player."""
        try:
            # Use system default player
            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", video_path])
            elif sys.platform == "win32":  # Windows
                os.startfile(video_path)
            else:  # Linux
                subprocess.Popen(["xdg-open", video_path])
        except Exception as e:
            print(f"Error playing video: {e}")

    def draw_text_wrapped(self, surface: Surface, text: str, rect: Rect, font, color=BLACK):
        """Draw wrapped text within a rectangle."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = font.render(test_line, True, color)

            if test_surf.get_width() <= rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw lines
        y = rect.y + 10
        line_height = font.get_height() + 5

        for line in lines:
            if y + line_height > rect.bottom:
                break
            text_surf = font.render(line, True, color)
            surface.blit(text_surf, (rect.x + 10, y))
            y += line_height

    def draw(self):
        """Draw the game screen."""
        self.screen.fill(WHITE)

        # Draw media area
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.media_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, self.media_rect, width=3, border_radius=10)

        # Show video if playing, otherwise show image
        if self.video_player.is_playing:
            self.video_player.draw(self.screen)
        elif self.current_image:
            # Center image in media rect
            img_rect = self.current_image.get_rect()
            img_rect.center = self.media_rect.center
            self.screen.blit(self.current_image, img_rect)
        else:
            # Show placeholder text
            text = self.text_font.render("No image available", True, DARK_GRAY)
            text_rect = text.get_rect(center=self.media_rect.center)
            self.screen.blit(text, text_rect)

        # Draw description area
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.desc_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, self.desc_rect, width=3, border_radius=10)

        # Draw state description
        desc_title = self.subtitle_font.render("Current Scene", True, BLACK)
        self.screen.blit(desc_title, (self.desc_rect.x + 10, self.desc_rect.y + 10))

        desc_rect_text = Rect(
            self.desc_rect.x,
            self.desc_rect.y + 50,
            self.desc_rect.width,
            self.desc_rect.height - 60
        )
        self.draw_text_wrapped(self.screen, self.current_state.description, desc_rect_text, self.small_font)

        # Draw actions area
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.actions_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, self.actions_rect, width=3, border_radius=10)

        # Draw actions title
        actions_title = self.subtitle_font.render("Available Actions", True, BLACK)
        self.screen.blit(actions_title, (self.actions_rect.x + 10, self.actions_rect.y + 10))

        # Check if final state
        if self.text_world.is_final_state(self.current_state):
            final_text = self.text_font.render("THE END", True, RED)
            final_rect = final_text.get_rect(center=(self.actions_rect.centerx, self.actions_rect.centery))
            self.screen.blit(final_text, final_rect)

            # Show quality if available
            quality = self.current_state.metadata.get("quality", 0)
            if quality:
                stars = "⭐" * int(quality * 5)
                quality_text = self.text_font.render(f"Quality: {stars} ({quality})", True, BLACK)
                quality_rect = quality_text.get_rect(center=(self.actions_rect.centerx, self.actions_rect.centery + 40))
                self.screen.blit(quality_text, quality_rect)
        else:
            # Draw action buttons (disabled during video playback)
            if self.video_player.is_playing:
                # Show "Playing video..." message
                playing_text = self.text_font.render("Playing video...", True, DARK_GRAY)
                playing_rect = playing_text.get_rect(center=(self.actions_rect.centerx, self.actions_rect.centery))
                self.screen.blit(playing_text, playing_rect)
            else:
                for button in self.action_buttons:
                    button.draw(self.screen, self.small_font)

        # Draw stats area
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.stats_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, self.stats_rect, width=3, border_radius=10)

        # Draw stats
        stats_title = self.subtitle_font.render("Progress", True, BLACK)
        self.screen.blit(stats_title, (self.stats_rect.x + 10, self.stats_rect.y + 10))

        stats_y = self.stats_rect.y + 50
        stats = [
            f"World: {self.world_name}",
            f"Mode: {self.world_type.upper()}",
            f"Current State: {self.current_state.state_id}",
            f"Steps Taken: {len(self.history)}",
            f"Progress: {self.current_state.metadata.get('progress', 0):.0%}"
        ]

        for stat in stats:
            stat_surf = self.text_font.render(stat, True, BLACK)
            self.screen.blit(stat_surf, (self.stats_rect.x + 20, stats_y))
            stats_y += 30

        pygame.display.flip()

    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            for button in self.action_buttons:
                button.update_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Don't allow clicks during video playback
                if not self.video_player.is_playing:
                    # Check button clicks
                    for button in self.action_buttons:
                        if button.is_clicked(event.pos):
                            self.perform_action(button.action)
                            break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_r:
                # Restart
                self.set_initial_state()

    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                self.handle_event(event)

            # Update video player
            if self.video_player.is_playing:
                self.video_player.update()

                # Check if video finished
                if self.video_player.is_finished() and self.pending_action:
                    # Complete the action transition
                    start_state, action, end_state = self.pending_action
                    self.complete_action(start_state, action, end_state)
                    self.pending_action = None

            # Draw
            self.draw()

            # Cap framerate
            self.clock.tick(60)

        pygame.quit()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Interactive World Explorer Game")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video", type=str, help="Path to video world JSON")
    group.add_argument("--image", type=str, help="Path to image world JSON")
    group.add_argument("--text", type=str, help="Path to text world JSON")

    args = parser.parse_args()

    # Determine world type and path
    if args.video:
        world_type = "video"
        world_path = args.video
    elif args.image:
        world_type = "image"
        world_path = args.image
    else:
        world_type = "text"
        world_path = args.text

    # Check if file exists
    if not Path(world_path).exists():
        print(f"ERROR: File not found: {world_path}")
        return 1

    try:
        game = WorldExplorerGame(world_type, world_path)
        game.run()
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
