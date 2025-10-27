#!/usr/bin/env python3
"""
Video World Generator - Generate transition videos for image worlds.

This module takes an ImageWorld and generates videos for each state transition
using Veo's first-frame + last-frame video generation capability.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from world_model_bench_agent.image_world_generator import ImageWorld, ImageState, ImageTransition
from world_model_bench_agent.prompt_enhancer import PromptEnhancer, CinematicStyle


@dataclass
class VideoTransition:
    """A transition with video connecting two states."""
    start_state_id: str
    action_id: str
    end_state_id: str
    action_description: str
    start_image_path: str
    end_image_path: str
    video_path: Optional[str] = None
    generation_prompt: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class VideoWorld:
    """World with videos for each transition."""
    name: str
    image_world_source: str
    states: List[ImageState] = field(default_factory=list)
    transitions: List[VideoTransition] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def save(self, filepath: str):
        """Save to JSON file."""
        data = {
            "name": self.name,
            "image_world_source": self.image_world_source,
            "generation_metadata": self.generation_metadata,
            "states": [asdict(s) for s in self.states],
            "transitions": [asdict(t) for t in self.transitions]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(filepath: str) -> 'VideoWorld':
        """Load from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        return VideoWorld(
            name=data["name"],
            image_world_source=data["image_world_source"],
            generation_metadata=data.get("generation_metadata", {}),
            states=[ImageState(**s) for s in data["states"]],
            transitions=[VideoTransition(**t) for t in data["transitions"]]
        )


class VideoWorldGenerator:
    """
    Generates transition videos for image worlds.

    Uses Veo's first-frame + last-frame video generation to create smooth
    transitions between states, guided by action descriptions.
    """

    def __init__(
        self,
        veo_client,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        output_dir: str = "generated_videos",
        use_enhanced_prompts: bool = True,
        cinematic_style: Optional[CinematicStyle] = None
    ):
        """
        Initialize video world generator.

        Args:
            veo_client: VeoVideoGenerator client
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            resolution: Video resolution (720p or 1080p)
            output_dir: Directory to save generated videos
            use_enhanced_prompts: Whether to use detailed cinematic prompt enhancement
            cinematic_style: Optional custom cinematic style (uses default if None)
        """
        self.veo = veo_client
        self.aspect_ratio = aspect_ratio
        self.resolution = resolution
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Prompt enhancement
        self.use_enhanced_prompts = use_enhanced_prompts
        self.prompt_enhancer = PromptEnhancer(style=cinematic_style)

    def generate_video_world(
        self,
        image_world: ImageWorld,
        strategy: str = "all_transitions",
        world_name: Optional[str] = None,
        number_of_videos: int = 1
    ) -> VideoWorld:
        """
        Convert image world to video world.

        Args:
            image_world: The ImageWorld with images for each state
            strategy: "all_transitions" or "canonical_only" or "selective"
            world_name: Name for the video world (default: image_world.name + "_videos")
            number_of_videos: Number of video variations to generate per transition

        Returns:
            VideoWorld with generated videos
        """
        world_name = world_name or f"{image_world.name}_videos"

        # Create output directory for this world
        world_dir = self.output_dir / world_name
        world_dir.mkdir(exist_ok=True)

        # Initialize VideoWorld
        video_world = VideoWorld(
            name=world_name,
            image_world_source=image_world.name,
            states=image_world.states.copy(),  # Copy states from image world
            generation_metadata={
                "model": self.veo.veo_model_id,
                "timestamp": datetime.now().isoformat(),
                "generation_strategy": strategy,
                "aspect_ratio": self.aspect_ratio,
                "resolution": self.resolution,
                "number_of_videos_per_transition": number_of_videos
            }
        )

        if strategy == "all_transitions":
            self._generate_all_transitions(image_world, video_world, world_dir, number_of_videos)
        elif strategy == "canonical_only":
            self._generate_canonical_transitions(image_world, video_world, world_dir, number_of_videos)
        elif strategy == "selective":
            # User can specify which transitions to generate
            raise NotImplementedError("Selective generation - use generate_transition_on_demand()")
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return video_world

    def _generate_all_transitions(
        self,
        image_world: ImageWorld,
        video_world: VideoWorld,
        world_dir: Path,
        number_of_videos: int
    ):
        """Generate videos for all transitions in the image world."""
        print(f"\nGenerating videos for all {len(image_world.transitions)} transitions...")

        for i, transition in enumerate(image_world.transitions):
            print(f"\nTransition {i+1}/{len(image_world.transitions)}")
            print(f"  {transition.start_state_id} --[{transition.action_description}]--> {transition.end_state_id}")

            # Find start and end states
            start_state = self._find_state(image_world.states, transition.start_state_id)
            end_state = self._find_state(image_world.states, transition.end_state_id)

            if not start_state or not end_state:
                print(f"  WARNING: Could not find states for transition. Skipping.")
                continue

            if not start_state.image_path or not end_state.image_path:
                print(f"  WARNING: Missing images for transition. Skipping.")
                continue

            # Generate video
            video_transition = self._generate_transition_video(
                start_state=start_state,
                end_state=end_state,
                action_description=transition.action_description,
                action_id=transition.action_id,
                world_dir=world_dir,
                index=i,
                number_of_videos=number_of_videos
            )

            video_world.transitions.append(video_transition)

        print(f"\nGenerated {len(video_world.transitions)} transition videos")

    def _generate_canonical_transitions(
        self,
        image_world: ImageWorld,
        video_world: VideoWorld,
        world_dir: Path,
        number_of_videos: int
    ):
        """Generate videos only for transitions in the canonical (main) path."""
        print(f"\nGenerating videos for canonical path transitions only...")

        # Assume canonical path is the sequence of transitions that follow parent-child relationships
        canonical_transitions = []

        # Build parent-child map from states
        for transition in image_world.transitions:
            end_state = self._find_state(image_world.states, transition.end_state_id)
            if end_state and end_state.parent_state_id == transition.start_state_id:
                canonical_transitions.append(transition)

        print(f"Found {len(canonical_transitions)} canonical transitions")

        for i, transition in enumerate(canonical_transitions):
            print(f"\nCanonical Transition {i+1}/{len(canonical_transitions)}")
            print(f"  {transition.start_state_id} --[{transition.action_description}]--> {transition.end_state_id}")

            start_state = self._find_state(image_world.states, transition.start_state_id)
            end_state = self._find_state(image_world.states, transition.end_state_id)

            if not start_state or not end_state:
                continue

            video_transition = self._generate_transition_video(
                start_state=start_state,
                end_state=end_state,
                action_description=transition.action_description,
                action_id=transition.action_id,
                world_dir=world_dir,
                index=i,
                number_of_videos=number_of_videos
            )

            video_world.transitions.append(video_transition)

        print(f"\nGenerated {len(video_world.transitions)} canonical transition videos")

    def _generate_transition_video(
        self,
        start_state: ImageState,
        end_state: ImageState,
        action_description: str,
        action_id: str,
        world_dir: Path,
        index: int,
        number_of_videos: int = 1
    ) -> VideoTransition:
        """
        Generate video for a single transition.

        Args:
            start_state: Starting state with image
            end_state: Ending state with image
            action_description: Description of the action
            action_id: ID of the action
            world_dir: Directory to save videos
            index: Index for filename
            number_of_videos: Number of video variations to generate

        Returns:
            VideoTransition with generated video path
        """
        # Build prompt from action description
        prompt = self._build_video_prompt(action_description, start_state, end_state)

        # Generate filename
        filename = f"{start_state.state_id}_to_{end_state.state_id}_{index:03d}.mp4"
        filepath = world_dir / filename

        print(f"    Prompt: {prompt[:100]}...")
        print(f"    Start image: {start_state.image_path}")
        print(f"    End image: {end_state.image_path}")

        print(f"    Generating video (this may take several minutes)...")
        try:
            # Generate video using Veo's first-frame + last-frame method
            # The veo wrapper will automatically convert file paths to types.Image format
            result = self.veo.generate_video_with_initial_and_end_image(
                prompt=prompt,
                start_image=start_state.image_path,
                end_image=end_state.image_path,
                aspect_ratio=self.aspect_ratio,
                resolution=self.resolution,
                number_of_videos=number_of_videos
            )
        except Exception as e:
            print(f"      ERROR during video generation: {e}")
            raise

        # Download video using Veo's download method
        if result.status == "completed" or result.download_url:
            try:
                print(f"    Downloading video...")
                self.veo.download_video(video_id=result.id, output_path=str(filepath))
                print(f"    SUCCESS: Video saved to {filepath}")
            except Exception as e:
                print(f"    ERROR downloading video: {e}")
                filepath = None
        else:
            print(f"    ERROR: Video generation not completed (status: {result.status})")
            filepath = None

        # Create VideoTransition
        return VideoTransition(
            start_state_id=start_state.state_id,
            action_id=action_id,
            end_state_id=end_state.state_id,
            action_description=action_description,
            start_image_path=start_state.image_path,
            end_image_path=end_state.image_path,
            video_path=str(filepath) if filepath else None,
            generation_prompt=prompt,
            metadata={
                "result_id": result.id,
                "status": result.status,
                "number_of_videos": number_of_videos
            }
        )

    def _build_video_prompt(
        self,
        action_description: str,
        start_state: ImageState,
        end_state: ImageState
    ) -> str:
        """
        Build video generation prompt from action description.

        Args:
            action_description: The action being performed
            start_state: Starting state
            end_state: Ending state

        Returns:
            Text prompt for video generation (simple or enhanced)
        """
        if not self.use_enhanced_prompts:
            # Simple prompt (original behavior)
            prompt = f"{action_description}. "
            prompt += f"Smooth transition showing the action in progress. "
            prompt += f"Starting from: {start_state.text_description[:50]}... "
            prompt += f"Ending at: {end_state.text_description[:50]}..."
            return prompt

        # Enhanced prompt with full structure: initial state + action + final state + details
        # Extract objects from descriptions (simple heuristic - can be improved)
        objects = self._extract_objects_from_states(start_state, end_state)

        # Determine location from state descriptions
        location = self._infer_location(start_state.text_description)

        # Use prompt enhancer for full cinematic transition prompt
        enhanced_prompt = self.prompt_enhancer.enhance_full_transition(
            initial_state=start_state.text_description,
            action=action_description,
            final_state=end_state.text_description,
            objects=objects,
            location=location
        )

        return enhanced_prompt

    def _extract_objects_from_states(
        self,
        start_state: ImageState,
        end_state: ImageState
    ) -> List[str]:
        """
        Extract key objects mentioned in state descriptions.

        Simple heuristic: look for common nouns in descriptions.
        """
        # Common object keywords
        common_objects = [
            'apple', 'knife', 'plate', 'bowl', 'cup', 'bottle', 'glass',
            'fork', 'spoon', 'cutting board', 'table', 'counter',
            'milk', 'water', 'food', 'container', 'lid', 'fridge'
        ]

        combined_text = (start_state.text_description + " " +
                        end_state.text_description).lower()

        found_objects = []
        for obj in common_objects:
            if obj in combined_text:
                found_objects.append(obj)

        # Return unique objects
        return list(set(found_objects))

    def _infer_location(self, state_description: str) -> str:
        """
        Infer scene location from state description.

        Returns contextual location string.
        """
        desc_lower = state_description.lower()

        if any(word in desc_lower for word in ['kitchen', 'counter', 'cutting board', 'stove']):
            return 'domestic kitchen countertop'
        elif any(word in desc_lower for word in ['table', 'dining']):
            return 'dining table'
        elif any(word in desc_lower for word in ['fridge', 'refrigerator']):
            return 'kitchen refrigerator'
        elif any(word in desc_lower for word in ['living room', 'couch', 'sofa']):
            return 'living room'
        elif any(word in desc_lower for word in ['bedroom', 'bed']):
            return 'bedroom'
        elif any(word in desc_lower for word in ['bathroom', 'sink']):
            return 'bathroom'
        else:
            return 'indoor domestic scene'

    def _find_state(self, states: List[ImageState], state_id: str) -> Optional[ImageState]:
        """Find state by ID."""
        for state in states:
            if state.state_id == state_id:
                return state
        return None

    def generate_transition_on_demand(
        self,
        image_world: ImageWorld,
        transition_index: int,
        world_name: Optional[str] = None,
        number_of_videos: int = 1
    ) -> VideoTransition:
        """
        Generate video for a specific transition on-demand.

        Useful for selective generation or interactive exploration.

        Args:
            image_world: The source image world
            transition_index: Index of transition in image_world.transitions
            world_name: Name for organizing output
            number_of_videos: Number of video variations

        Returns:
            VideoTransition with generated video
        """
        world_name = world_name or image_world.name
        world_dir = self.output_dir / f"{world_name}_videos"
        world_dir.mkdir(exist_ok=True, parents=True)

        transition = image_world.transitions[transition_index]
        start_state = self._find_state(image_world.states, transition.start_state_id)
        end_state = self._find_state(image_world.states, transition.end_state_id)

        if not start_state or not end_state:
            raise ValueError(f"Could not find states for transition {transition_index}")

        return self._generate_transition_video(
            start_state=start_state,
            end_state=end_state,
            action_description=transition.action_description,
            action_id=transition.action_id,
            world_dir=world_dir,
            index=transition_index,
            number_of_videos=number_of_videos
        )

    def generate_batch_transitions(
        self,
        image_world: ImageWorld,
        transition_indices: List[int],
        world_name: Optional[str] = None,
        number_of_videos: int = 1
    ) -> List[VideoTransition]:
        """
        Generate videos for a specific set of transitions.

        Args:
            image_world: The source image world
            transition_indices: List of transition indices to generate
            world_name: Name for organizing output
            number_of_videos: Number of video variations per transition

        Returns:
            List of VideoTransitions with generated videos
        """
        world_name = world_name or image_world.name
        world_dir = self.output_dir / f"{world_name}_videos"
        world_dir.mkdir(exist_ok=True, parents=True)

        video_transitions = []

        print(f"\nGenerating {len(transition_indices)} selected transitions...")

        for i, idx in enumerate(transition_indices):
            print(f"\nTransition {i+1}/{len(transition_indices)} (index {idx})")

            transition = image_world.transitions[idx]
            start_state = self._find_state(image_world.states, transition.start_state_id)
            end_state = self._find_state(image_world.states, transition.end_state_id)

            if not start_state or not end_state:
                print(f"  WARNING: Could not find states. Skipping.")
                continue

            video_transition = self._generate_transition_video(
                start_state=start_state,
                end_state=end_state,
                action_description=transition.action_description,
                action_id=transition.action_id,
                world_dir=world_dir,
                index=idx,
                number_of_videos=number_of_videos
            )

            video_transitions.append(video_transition)

        return video_transitions


def load_image_world_and_generate_videos(
    image_world_path: str,
    veo_client,
    strategy: str = "all_transitions",
    output_dir: str = "generated_videos",
    number_of_videos: int = 1
) -> VideoWorld:
    """
    Convenience function to load image world and generate videos.

    Args:
        image_world_path: Path to image world JSON file
        veo_client: VeoVideoGenerator client
        strategy: "all_transitions" or "canonical_only"
        output_dir: Directory to save videos
        number_of_videos: Number of video variations per transition

    Returns:
        VideoWorld with generated videos
    """
    # Load image world
    image_world = ImageWorld.load(image_world_path)

    # Generate videos
    generator = VideoWorldGenerator(veo_client, output_dir=output_dir)
    video_world = generator.generate_video_world(
        image_world=image_world,
        strategy=strategy,
        number_of_videos=number_of_videos
    )

    return video_world
