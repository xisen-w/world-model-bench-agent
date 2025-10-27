#!/usr/bin/env python3
"""
Image World Generator - Convert text worlds to vision worlds.

This module generates consistent images for each state in a world model,
maintaining visual coherence across state transitions.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from world_model_bench_agent.benchmark_curation import World, State, Action, Transition


@dataclass
class ImageState:
    """A state with associated image."""
    state_id: str
    text_description: str
    image_path: Optional[str] = None
    generation_prompt: Optional[str] = None
    parent_state_id: Optional[str] = None
    parent_action_id: Optional[str] = None
    reference_image: Optional[str] = None  # Path to image used as reference
    metadata: Dict = field(default_factory=dict)


@dataclass
class ImageTransition:
    """A transition with optional video."""
    start_state_id: str
    action_id: str
    end_state_id: str
    action_description: str
    video_path: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class ImageWorld:
    """World with images for each state."""
    name: str
    text_world_source: str
    states: List[ImageState] = field(default_factory=list)
    transitions: List[ImageTransition] = field(default_factory=list)
    generation_metadata: Dict = field(default_factory=dict)

    def save(self, filepath: str):
        """Save to JSON file."""
        data = {
            "name": self.name,
            "text_world_source": self.text_world_source,
            "generation_metadata": self.generation_metadata,
            "states": [asdict(s) for s in self.states],
            "transitions": [asdict(t) for t in self.transitions]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(filepath: str) -> 'ImageWorld':
        """Load from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        return ImageWorld(
            name=data["name"],
            text_world_source=data["text_world_source"],
            generation_metadata=data.get("generation_metadata", {}),
            states=[ImageState(**s) for s in data["states"]],
            transitions=[ImageTransition(**t) for t in data["transitions"]]
        )


class ImageWorldGenerator:
    """
    Generates consistent images for text-based worlds.

    Uses Gemini's image generation with image variation to maintain
    visual consistency across state transitions.
    """

    def __init__(
        self,
        veo_client,
        camera_perspective: str = "first_person_ego",
        aspect_ratio: str = "16:9",
        output_dir: str = "generated_images"
    ):
        """
        Initialize image world generator.

        Args:
            veo_client: VeoVideoGenerator client
            camera_perspective: Camera view (first_person_ego, third_person, overhead)
            aspect_ratio: Image aspect ratio
            output_dir: Directory to save generated images
        """
        self.veo = veo_client
        self.camera_perspective = camera_perspective
        self.aspect_ratio = aspect_ratio
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_image_world(
        self,
        text_world: World,
        strategy: str = "canonical_path",
        world_name: Optional[str] = None
    ) -> ImageWorld:
        """
        Convert text world to image world.

        Args:
            text_world: The text-based World object
            strategy: "canonical_path" (main path only) or "full_world" (all states)
            world_name: Name for the image world (default: text_world.name + "_images")

        Returns:
            ImageWorld with generated images
        """
        world_name = world_name or f"{text_world.name}_images"

        # Create output directory for this world
        world_dir = self.output_dir / world_name
        world_dir.mkdir(exist_ok=True)

        # Initialize ImageWorld
        image_world = ImageWorld(
            name=world_name,
            text_world_source=text_world.name,
            generation_metadata={
                "model": self.veo.image_model_id,
                "timestamp": datetime.now().isoformat(),
                "generation_strategy": strategy,
                "aspect_ratio": self.aspect_ratio,
                "camera_perspective": self.camera_perspective
            }
        )

        if strategy == "canonical_path":
            self._generate_canonical_path(text_world, image_world, world_dir)
        elif strategy == "full_world":
            self._generate_full_world(text_world, image_world, world_dir)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return image_world

    def _generate_canonical_path(
        self,
        text_world: World,
        image_world: ImageWorld,
        world_dir: Path
    ):
        """Generate images for the main success path only."""
        print(f"\nGenerating images for canonical path...")

        # Get the main path (initial -> first goal)
        if not text_world.goal_states:
            raise ValueError("World has no goal states")

        paths = text_world.get_successful_paths()
        if not paths:
            raise ValueError("No successful paths found")

        # Use the first successful path
        canonical_path = paths[0]

        print(f"Found canonical path with {len(canonical_path)} transitions")

        # Generate images along the path
        previous_image = None
        previous_state_id = None

        for i, transition in enumerate(canonical_path):
            print(f"\nTransition {i+1}/{len(canonical_path)}")
            print(f"  Action: {transition.action.description}")

            # Generate image for start state (if first transition)
            if i == 0:
                print(f"  Generating initial state image...")
                start_image_state = self._generate_state_image(
                    state=transition.start_state,
                    action=None,
                    previous_image=None,
                    world_dir=world_dir,
                    index=0
                )
                image_world.states.append(start_image_state)
                previous_image = start_image_state.image_path
                previous_state_id = start_image_state.state_id

            # Generate image for end state
            print(f"  Generating next state image (variation)...")
            end_image_state = self._generate_state_image(
                state=transition.end_state,
                action=transition.action,
                previous_image=previous_image,
                world_dir=world_dir,
                index=i+1,
                parent_state_id=previous_state_id,
                parent_action_id=transition.action.action_id
            )
            image_world.states.append(end_image_state)
            previous_image = end_image_state.image_path
            previous_state_id = end_image_state.state_id

            # Record transition
            image_world.transitions.append(ImageTransition(
                start_state_id=transition.start_state.state_id,
                action_id=transition.action.action_id,
                end_state_id=transition.end_state.state_id,
                action_description=transition.action.description
            ))

        print(f"\nGenerated {len(image_world.states)} images for canonical path")

    def _generate_full_world(
        self,
        text_world: World,
        image_world: ImageWorld,
        world_dir: Path
    ):
        """
        Generate images for all reachable states (expensive!).

        Uses breadth-first traversal from initial state to generate
        images for all states and transitions in the world graph.
        """
        print(f"\nGenerating images for full world...")
        print(f"Total states: {len(text_world.states)}")
        print(f"Total transitions: {len(text_world.transitions)}")

        if not text_world.initial_state:
            raise ValueError("World has no initial state")

        # Track which states have been generated
        generated_states = {}  # state_id -> ImageState
        state_to_image = {}  # state_id -> image_path

        # Build adjacency list for transitions
        # Map: (state_id, action_id) -> end_state
        transition_map = {}
        for transition in text_world.transitions:
            key = (transition.start_state.state_id, transition.action.action_id)
            transition_map[key] = transition

        # BFS queue: (state, parent_image_path, parent_state_id, parent_action)
        from collections import deque
        queue = deque()

        # Start with initial state
        initial_state = text_world.initial_state
        print(f"\nGenerating initial state: {initial_state.state_id}")

        initial_image_state = self._generate_state_image(
            state=initial_state,
            action=None,
            previous_image=None,
            world_dir=world_dir,
            index=0
        )

        generated_states[initial_state.state_id] = initial_image_state
        state_to_image[initial_state.state_id] = initial_image_state.image_path
        image_world.states.append(initial_image_state)

        # Enqueue all transitions from initial state
        for transition in text_world.transitions:
            if transition.start_state.state_id == initial_state.state_id:
                queue.append((
                    transition.end_state,
                    initial_image_state.image_path,
                    initial_state.state_id,
                    transition.action
                ))

        # Process queue
        processed_count = 1
        while queue:
            state, parent_image, parent_state_id, action = queue.popleft()

            # Skip if already generated
            if state.state_id in generated_states:
                # Still need to record the transition
                image_world.transitions.append(ImageTransition(
                    start_state_id=parent_state_id,
                    action_id=action.action_id,
                    end_state_id=state.state_id,
                    action_description=action.description
                ))
                continue

            # Generate image for this state
            print(f"\nGenerating state {processed_count}/{len(text_world.states)}: {state.state_id}")
            print(f"  Via action: {action.description}")

            image_state = self._generate_state_image(
                state=state,
                action=action,
                previous_image=parent_image,
                world_dir=world_dir,
                index=processed_count,
                parent_state_id=parent_state_id,
                parent_action_id=action.action_id
            )

            generated_states[state.state_id] = image_state
            state_to_image[state.state_id] = image_state.image_path
            image_world.states.append(image_state)
            processed_count += 1

            # Record transition
            image_world.transitions.append(ImageTransition(
                start_state_id=parent_state_id,
                action_id=action.action_id,
                end_state_id=state.state_id,
                action_description=action.description
            ))

            # Enqueue all outgoing transitions from this state
            for transition in text_world.transitions:
                if transition.start_state.state_id == state.state_id:
                    queue.append((
                        transition.end_state,
                        image_state.image_path,
                        state.state_id,
                        transition.action
                    ))

        print(f"\n" + "=" * 70)
        print(f"Generated {len(image_world.states)} images for full world")
        print(f"Total transitions: {len(image_world.transitions)}")
        print("=" * 70)

    def _generate_state_image(
        self,
        state: State,
        action: Optional[Action],
        previous_image: Optional[str],
        world_dir: Path,
        index: int,
        parent_state_id: Optional[str] = None,
        parent_action_id: Optional[str] = None
    ) -> ImageState:
        """
        Generate image for a single state.

        Args:
            state: The state to generate image for
            action: The action that led to this state (None for initial state)
            previous_image: Path to previous state's image (for variation)
            world_dir: Directory to save images
            index: Index for filename
            parent_state_id: ID of parent state
            parent_action_id: ID of action from parent

        Returns:
            ImageState with generated image
        """
        # Build prompt
        prompt = self._build_state_prompt(state, action)

        # Generate filename
        state_id = state.state_id or f"s{index}"
        filename = f"{state_id}_{index:03d}.png"
        filepath = world_dir / filename

        # Generate image
        if previous_image is None:
            # Initial state - generate from scratch
            print(f"    Prompt: {prompt[:80]}...")
            image = self.veo.generate_image_from_prompt(
                prompt=prompt,
                aspect_ratio=self.aspect_ratio,
                save_path=str(filepath)
            )
        else:
            # Subsequent state - use variation for consistency
            from PIL import Image
            base_image = Image.open(previous_image)
            print(f"    Variation prompt: {prompt[:80]}...")
            image = self.veo.generate_image_variation(
                prompt=prompt,
                base_image=base_image,
                aspect_ratio=self.aspect_ratio
            )
            image.save(str(filepath))

        # Create ImageState
        return ImageState(
            state_id=state_id,
            text_description=state.description,
            image_path=str(filepath),
            generation_prompt=prompt,
            parent_state_id=parent_state_id,
            parent_action_id=parent_action_id,
            reference_image=previous_image,
            metadata=state.metadata.copy()
        )

    def _build_state_prompt(
        self,
        state: State,
        action: Optional[Action] = None
    ) -> str:
        """
        Build image generation prompt for a state.

        Args:
            state: The state to generate
            action: The action that led to this state (for variation prompts)

        Returns:
            Text prompt for image generation
        """
        # Camera perspective prefix
        perspective_map = {
            "first_person_ego": "First-person ego-centric view at eye level (1.6m height)",
            "third_person": "Third-person view from behind and slightly above",
            "overhead": "Overhead bird's-eye view looking down"
        }
        perspective_prefix = perspective_map.get(
            self.camera_perspective,
            "First-person ego-centric view"
        )

        # Build prompt
        if action is None:
            # Initial state - full description
            prompt = f"{perspective_prefix}. {state.description}. Realistic style, clear lighting, detailed."
        else:
            # Variation - STRONGLY emphasize the change
            # Extract key change elements from action
            action_emphasis = f"IMPORTANT VISIBLE CHANGE: {action.description}"
            prompt = f"Same camera angle and scene layout. HOWEVER, {action_emphasis}. The new state: {state.description}. Make the change CLEARLY VISIBLE."

        return prompt

    def generate_state_image_on_demand(
        self,
        text_world: World,
        state: State,
        parent_image_path: Optional[str] = None,
        parent_action: Optional[Action] = None,
        world_name: Optional[str] = None
    ) -> ImageState:
        """
        Generate image for a specific state on-demand.

        Useful for interactive exploration of branching worlds.

        Args:
            text_world: The source text world
            state: State to generate image for
            parent_image_path: Path to parent state's image (for variation)
            parent_action: Action from parent to this state
            world_name: Name for organizing output

        Returns:
            ImageState with generated image
        """
        world_name = world_name or text_world.name
        world_dir = self.output_dir / f"{world_name}_images"
        world_dir.mkdir(exist_ok=True, parents=True)

        # Generate image
        return self._generate_state_image(
            state=state,
            action=parent_action,
            previous_image=parent_image_path,
            world_dir=world_dir,
            index=len(list(world_dir.glob("*.png")))  # Use number of existing images
        )


def load_text_world_and_generate_images(
    text_world_path: str,
    veo_client,
    strategy: str = "canonical_path",
    output_dir: str = "generated_images"
) -> ImageWorld:
    """
    Convenience function to load text world and generate images.

    Args:
        text_world_path: Path to text world JSON file
        veo_client: VeoVideoGenerator client
        strategy: "canonical_path" or "full_world"
        output_dir: Directory to save images

    Returns:
        ImageWorld with generated images
    """
    # Load text world
    text_world = World.load(text_world_path)

    # Generate images
    generator = ImageWorldGenerator(veo_client, output_dir=output_dir)
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy=strategy
    )

    return image_world
