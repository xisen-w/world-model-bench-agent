"""
Benchmark Curation for Action-Conditioned World Model (AC-World).

This module provides the core data structures and utilities for creating
benchmark datasets that test temporal planning and scene consistency.

Core Concepts:
- State: A textual description of the current world state
- Action: A textual description of an action taken
- Transition: (state_t, action_t) -> state_{t+1}
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# Core Data Types
# ============================================================================

@dataclass
class State:
    """Represents a discrete state in the world."""

    description: str
    """Textual description of the state"""

    state_id: Optional[str] = None
    """Unique identifier for this state"""

    metadata: Dict = field(default_factory=dict)
    """Additional metadata (e.g., object positions, properties)"""

    def __str__(self) -> str:
        return self.description

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "description": self.description,
            "state_id": self.state_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> State:
        """Create State from dictionary."""
        return cls(
            description=data["description"],
            state_id=data.get("state_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Action:
    """Represents an action that transforms one state to another."""

    description: str
    """Textual description of the action"""

    action_id: Optional[str] = None
    """Unique identifier for this action"""

    action_type: Optional[str] = None
    """Category of action (e.g., 'assembly', 'movement', 'manipulation')"""

    metadata: Dict = field(default_factory=dict)
    """Additional metadata (e.g., required tools, duration)"""

    def __str__(self) -> str:
        return self.description

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "description": self.description,
            "action_id": self.action_id,
            "action_type": self.action_type,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> Action:
        """Create Action from dictionary."""
        return cls(
            description=data["description"],
            action_id=data.get("action_id"),
            action_type=data.get("action_type"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Transition:
    """Represents a state transition: (state_t, action_t) -> state_{t+1}"""

    start_state: State
    """The initial state"""

    action: Action
    """The action performed"""

    end_state: State
    """The resulting state after the action"""

    transition_id: Optional[str] = None
    """Unique identifier for this transition"""

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "transition_id": self.transition_id,
            "start_state": self.start_state.to_dict(),
            "action": self.action.to_dict(),
            "end_state": self.end_state.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> Transition:
        """Create Transition from dictionary."""
        return cls(
            start_state=State.from_dict(data["start_state"]),
            action=Action.from_dict(data["action"]),
            end_state=State.from_dict(data["end_state"]),
            transition_id=data.get("transition_id")
        )


@dataclass
class World:
    """Represents a complete world scenario with multiple transitions."""

    name: str
    """Name of the world scenario (e.g., 'IKEA_desk_assembly')"""

    description: str
    """Description of the overall scenario"""

    states: List[State] = field(default_factory=list)
    """All states in this world"""

    actions: List[Action] = field(default_factory=list)
    """All possible actions in this world"""

    transitions: List[Transition] = field(default_factory=list)
    """State transitions forming the world trajectory"""

    initial_state: Optional[State] = None
    """The starting state"""

    goal_state: Optional[State] = None
    """The target/final state"""

    def add_transition(self, start: State, action: Action, end: State) -> Transition:
        """Add a new transition to the world."""
        transition = Transition(
            start_state=start,
            action=action,
            end_state=end,
            transition_id=f"t_{len(self.transitions)}"
        )
        self.transitions.append(transition)

        # Track unique states and actions
        if start not in self.states:
            self.states.append(start)
        if end not in self.states:
            self.states.append(end)
        if action not in self.actions:
            self.actions.append(action)

        return transition

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "states": [s.to_dict() for s in self.states],
            "actions": [a.to_dict() for a in self.actions],
            "transitions": [t.to_dict() for t in self.transitions],
            "initial_state": self.initial_state.to_dict() if self.initial_state else None,
            "goal_state": self.goal_state.to_dict() if self.goal_state else None
        }

    def save(self, filepath: str) -> None:
        """Save world to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> World:
        """Load world from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        world = cls(
            name=data["name"],
            description=data["description"]
        )

        world.states = [State.from_dict(s) for s in data["states"]]
        world.actions = [Action.from_dict(a) for a in data["actions"]]
        world.transitions = [Transition.from_dict(t) for t in data["transitions"]]

        if data.get("initial_state"):
            world.initial_state = State.from_dict(data["initial_state"])
        if data.get("goal_state"):
            world.goal_state = State.from_dict(data["goal_state"])

        return world


# ============================================================================
# Predefined IKEA Desk Assembly World
# ============================================================================

def create_ikea_desk_world() -> World:
    """
    Create a benchmark world for IKEA desk assembly.

    This simulates the process of assembling a simple IKEA desk with:
    - Unboxing components
    - Organizing parts
    - Assembling the frame
    - Attaching the tabletop
    - Final adjustments

    Returns:
        A World object representing the complete assembly process
    """
    world = World(
        name="IKEA_desk_assembly",
        description="Assembly process for a simple IKEA desk (MICKE or similar model)"
    )

    # Define states
    s0 = State(
        description="Unopened IKEA desk box on the floor",
        state_id="s0",
        metadata={"components_visible": False, "assembly_progress": 0.0}
    )

    s1 = State(
        description="Box opened with all components laid out on the floor: 4 legs, 1 tabletop, 1 drawer unit, screws, Allen key",
        state_id="s1",
        metadata={"components_visible": True, "assembly_progress": 0.1}
    )

    s2 = State(
        description="Components sorted and organized by type: legs in one pile, hardware separated, instructions visible",
        state_id="s2",
        metadata={"components_organized": True, "assembly_progress": 0.2}
    )

    s3 = State(
        description="Two legs attached to the drawer unit forming one side of the desk frame",
        state_id="s3",
        metadata={"partial_assembly": True, "assembly_progress": 0.4}
    )

    s4 = State(
        description="All four legs attached to the drawer unit, creating a stable base frame",
        state_id="s4",
        metadata={"frame_complete": True, "assembly_progress": 0.6}
    )

    s5 = State(
        description="Tabletop placed on the frame but not secured, desk is upright but unstable",
        state_id="s5",
        metadata={"tabletop_placed": True, "assembly_progress": 0.8}
    )

    s6 = State(
        description="Completed desk with tabletop secured to the frame, all screws tightened, desk is stable and ready to use",
        state_id="s6",
        metadata={"assembly_complete": True, "assembly_progress": 1.0}
    )

    # Define actions
    a0 = Action(
        description="Open the box and remove all components",
        action_id="a0",
        action_type="unboxing",
        metadata={"tools_required": ["hands"], "duration": "5 minutes"}
    )

    a1 = Action(
        description="Sort components by type and lay out the instruction manual",
        action_id="a1",
        action_type="organization",
        metadata={"tools_required": ["hands"], "duration": "3 minutes"}
    )

    a2 = Action(
        description="Attach two legs to the drawer unit using screws and Allen key",
        action_id="a2",
        action_type="assembly",
        metadata={"tools_required": ["Allen key"], "duration": "10 minutes"}
    )

    a3 = Action(
        description="Attach the remaining two legs to complete the base frame",
        action_id="a3",
        action_type="assembly",
        metadata={"tools_required": ["Allen key"], "duration": "10 minutes"}
    )

    a4 = Action(
        description="Flip the frame upright and place the tabletop on the frame",
        action_id="a4",
        action_type="positioning",
        metadata={"tools_required": ["hands"], "duration": "5 minutes"}
    )

    a5 = Action(
        description="Secure the tabletop to the frame with screws and tighten all connections",
        action_id="a5",
        action_type="assembly",
        metadata={"tools_required": ["Allen key", "screwdriver"], "duration": "15 minutes"}
    )

    # Create transitions (the assembly sequence)
    world.add_transition(s0, a0, s1)  # Unbox
    world.add_transition(s1, a1, s2)  # Organize
    world.add_transition(s2, a2, s3)  # Partial assembly
    world.add_transition(s3, a3, s4)  # Complete frame
    world.add_transition(s4, a4, s5)  # Add tabletop
    world.add_transition(s5, a5, s6)  # Finalize

    # Set initial and goal states
    world.initial_state = s0
    world.goal_state = s6

    return world


# ============================================================================
# Gemini LLM Integration for State/Action Generation
# ============================================================================

class StateActionGenerator:
    """
    Uses Gemini LLM to generate states and infer actions from state transitions.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator with Gemini API.

        Args:
            api_key: Google AI API key. If None, reads from GEMINI_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_KEY not found. Please set it in .env or pass it directly.")

        # Initialize Gemini client
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = "gemini-2.0-flash-exp"
        except ImportError:
            raise ImportError("google-genai package not found. Install with: pip install google-genai")

    def generate_next_state(
        self,
        current_state: State,
        action: Action,
        context: Optional[str] = None
    ) -> State:
        """
        Generate the next state given a current state and action using Gemini.

        Args:
            current_state: The current state
            action: The action being performed
            context: Optional context about the world/scenario

        Returns:
            The predicted next state
        """
        prompt = self._build_next_state_prompt(current_state, action, context)

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        next_state_desc = response.text.strip()

        return State(
            description=next_state_desc,
            metadata={"generated_by": "gemini", "source_action": action.description}
        )

    def infer_action(
        self,
        start_state: State,
        end_state: State,
        context: Optional[str] = None
    ) -> Action:
        """
        Infer the action that transforms start_state into end_state using Gemini.

        Args:
            start_state: The initial state
            end_state: The resulting state
            context: Optional context about the world/scenario

        Returns:
            The inferred action
        """
        prompt = self._build_action_inference_prompt(start_state, end_state, context)

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        action_desc = response.text.strip()

        return Action(
            description=action_desc,
            metadata={"generated_by": "gemini", "inference_type": "state_transition"}
        )

    def generate_intermediate_states(
        self,
        start_state: State,
        goal_state: State,
        num_steps: int = 3,
        context: Optional[str] = None
    ) -> List[Tuple[State, Action]]:
        """
        Generate a sequence of intermediate states and actions from start to goal.

        Args:
            start_state: The initial state
            goal_state: The target state
            num_steps: Number of intermediate steps
            context: Optional context about the world/scenario

        Returns:
            List of (state, action) tuples forming a path from start to goal
        """
        prompt = self._build_trajectory_prompt(start_state, goal_state, num_steps, context)

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        # Parse the response to extract states and actions
        trajectory = self._parse_trajectory_response(response.text)

        return trajectory

    def _build_next_state_prompt(
        self,
        current_state: State,
        action: Action,
        context: Optional[str]
    ) -> str:
        """Build prompt for next state generation."""
        base_prompt = f"""You are a world model that predicts state transitions.

Current State: {current_state.description}
Action Taken: {action.description}
"""
        if context:
            base_prompt += f"Context: {context}\n"

        base_prompt += """
Task: Describe the resulting state after performing this action. Be specific and detailed about what changed.

Next State:"""

        return base_prompt

    def _build_action_inference_prompt(
        self,
        start_state: State,
        end_state: State,
        context: Optional[str]
    ) -> str:
        """Build prompt for action inference."""
        base_prompt = f"""You are a world model that infers actions from state transitions.

Initial State: {start_state.description}
Final State: {end_state.description}
"""
        if context:
            base_prompt += f"Context: {context}\n"

        base_prompt += """
Task: Infer the minimal action(s) that would transform the initial state into the final state. Provide a clear, concise action description.

Action:"""

        return base_prompt

    def _build_trajectory_prompt(
        self,
        start_state: State,
        goal_state: State,
        num_steps: int,
        context: Optional[str]
    ) -> str:
        """Build prompt for trajectory generation."""
        base_prompt = f"""You are a world model that plans action sequences.

Initial State: {start_state.description}
Goal State: {goal_state.description}
"""
        if context:
            base_prompt += f"Context: {context}\n"

        base_prompt += f"""
Task: Generate a sequence of exactly {num_steps} steps to transition from the initial state to the goal state. For each step, provide:
1. The action to perform
2. The resulting state after that action

Format your response as:
Step 1:
Action: [action description]
State: [state description]

Step 2:
Action: [action description]
State: [state description]

... and so on.

Trajectory:"""

        return base_prompt

    def _parse_trajectory_response(self, response_text: str) -> List[Tuple[State, Action]]:
        """Parse trajectory response into (state, action) tuples."""
        trajectory = []
        lines = response_text.strip().split('\n')

        current_action = None
        current_state = None

        for line in lines:
            line = line.strip()
            if line.startswith("Action:"):
                current_action = Action(description=line.replace("Action:", "").strip())
            elif line.startswith("State:"):
                current_state = State(description=line.replace("State:", "").strip())

                if current_action and current_state:
                    trajectory.append((current_state, current_action))
                    current_action = None
                    current_state = None

        return trajectory


# ============================================================================
# Utility Functions
# ============================================================================

def save_world_to_json(world: World, filepath: str) -> None:
    """
    Save a world to a JSON file.

    Args:
        world: The World object to save
        filepath: Path to the output JSON file
    """
    world.save(filepath)
    print(f"World saved to: {filepath}")


def load_world_from_json(filepath: str) -> World:
    """
    Load a world from a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        The loaded World object
    """
    world = World.load(filepath)
    print(f"World loaded from: {filepath}")
    return world


def print_world_summary(world: World) -> None:
    """Print a summary of the world."""
    print(f"\nWorld: {world.name}")
    print(f"Description: {world.description}")
    print(f"States: {len(world.states)}")
    print(f"Actions: {len(world.actions)}")
    print(f"Transitions: {len(world.transitions)}")

    if world.initial_state:
        print(f"\nInitial State: {world.initial_state.description}")
    if world.goal_state:
        print(f"Goal State: {world.goal_state.description}")

    print(f"\nTransition Sequence:")
    for i, transition in enumerate(world.transitions):
        print(f"  {i+1}. [{transition.start_state.state_id}] -> "
              f"[{transition.action.description}] -> "
              f"[{transition.end_state.state_id}]")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional

    # Create the IKEA desk assembly world
    print("Creating IKEA desk assembly world...")
    ikea_world = create_ikea_desk_world()

    # Print summary
    print_world_summary(ikea_world)

    # Save to JSON
    output_path = "ikea_desk_world.json"
    save_world_to_json(ikea_world, output_path)

    # Example: Using Gemini to generate states and actions
    print("\n" + "="*70)
    print("Testing Gemini LLM Integration")
    print("="*70)

    try:
        generator = StateActionGenerator()

        # Test 1: Infer action between two states
        print("\nTest 1: Inferring action from state transition")
        print("-" * 50)
        s1 = ikea_world.states[0]  # Unopened box
        s2 = ikea_world.states[1]  # Box opened

        inferred_action = generator.infer_action(
            s1, s2,
            context="IKEA desk assembly process"
        )
        print(f"Start: {s1.description}")
        print(f"End: {s2.description}")
        print(f"Inferred Action: {inferred_action.description}")

        # Test 2: Generate next state from action
        print("\n\nTest 2: Generating next state from action")
        print("-" * 50)
        current = ikea_world.states[2]  # Components organized
        action = ikea_world.actions[2]  # Attach two legs

        predicted_next = generator.generate_next_state(
            current, action,
            context="IKEA desk assembly process"
        )
        print(f"Current: {current.description}")
        print(f"Action: {action.description}")
        print(f"Predicted Next State: {predicted_next.description}")
        print(f"Actual Next State: {ikea_world.states[3].description}")

    except ValueError as e:
        print(f"\nSkipping Gemini tests: {e}")
        print("To enable Gemini integration, set GEMINI_KEY in your .env file")
