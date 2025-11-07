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

@dataclass(eq=True, frozen=False)
class State:
    """Represents a discrete state in the world."""

    description: str
    """Textual description of the state"""

    state_id: Optional[str] = None
    """Unique identifier for this state"""

    metadata: Dict = field(default_factory=dict, compare=False)
    """Additional metadata (e.g., object positions, properties)"""

    def __hash__(self):
        """Make State hashable based on state_id or description."""
        return hash(self.state_id or self.description)

    def __eq__(self, other):
        """States are equal if they have the same ID or description."""
        if not isinstance(other, State):
            return False
        if self.state_id and other.state_id:
            return self.state_id == other.state_id
        return self.description == other.description

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
class Transition: # Agents might be llm-based, we can see the visaul effectiveness. # Expand the world model idea. 
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

    goal_states: List[State] = field(default_factory=list)
    """The target/goal states (successful endpoints)"""

    final_states: List[State] = field(default_factory=list)
    """All possible final states (including failures)"""

    @property
    def goal_state(self) -> Optional[State]:
        """Backward compatibility: returns the first goal state."""
        return self.goal_states[0] if self.goal_states else None

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

    def add_goal_state(self, state: State) -> None:
        """Add a state to the list of goal states (successful endpoints)."""
        if state not in self.goal_states:
            self.goal_states.append(state)
        if state not in self.final_states:
            self.final_states.append(state)

    def add_final_state(self, state: State, is_goal: bool = False) -> None:
        """
        Add a state to the list of final states.

        Args:
            state: The final state to add
            is_goal: If True, also add to goal_states (successful outcome)
        """
        if state not in self.final_states:
            self.final_states.append(state)
        if is_goal and state not in self.goal_states:
            self.goal_states.append(state)

    def is_goal_state(self, state: State) -> bool:
        """Check if a state is a goal (successful endpoint)."""
        return state in self.goal_states

    def is_final_state(self, state: State) -> bool:
        """
        Check if a state is a final state (no outgoing transitions).

        Can be either explicitly marked or auto-detected.
        """
        # Check explicit list first
        if state in self.final_states:
            return True

        # Auto-detect: no outgoing transitions
        for transition in self.transitions:
            if transition.start_state == state:
                return False
        return True

    def get_final_states(self, auto_detect: bool = True) -> List[State]:
        """
        Get all final states (endpoints with no outgoing transitions).

        Args:
            auto_detect: If True, automatically detect states with no outgoing edges

        Returns:
            List of all final states
        """
        if not auto_detect:
            return self.final_states.copy()

        # Combine explicit and auto-detected
        final = set(self.final_states)

        for state in self.states:
            if self.is_final_state(state):
                final.add(state)

        return list(final)

    # ========================================================================
    # Branching / Graph Structure Methods
    # ========================================================================

    def get_possible_actions(self, state: State) -> List[Action]:
        """
        Get all possible actions that can be performed from a given state.

        This enables branching: one state can have multiple action choices.

        Args:
            state: The state to query

        Returns:
            List of actions that can be performed from this state
        """
        actions = []
        for transition in self.transitions:
            if transition.start_state == state:
                actions.append(transition.action)
        return actions

    def get_next_states(self, state: State, action: Optional[Action] = None) -> List[State]:
        """
        Get possible next states from a given state.

        Args:
            state: The current state
            action: Optional action filter. If provided, only returns states
                   reachable via this action. If None, returns all next states.

        Returns:
            List of states reachable from the current state
        """
        next_states = []
        for transition in self.transitions:
            if transition.start_state == state:
                if action is None or transition.action == action:
                    next_states.append(transition.end_state)
        return next_states

    def get_decision_points(self) -> List[Tuple[State, List[Action]]]:
        """
        Find all states where multiple actions are possible (branching points).

        These are critical for testing model decision-making capabilities.

        Returns:
            List of (state, possible_actions) tuples where len(actions) > 1
        """
        decision_points = []
        checked_states = set()

        for state in self.states:
            if state in checked_states:
                continue

            possible_actions = self.get_possible_actions(state)
            if len(possible_actions) > 1:
                decision_points.append((state, possible_actions))

            checked_states.add(state)

        return decision_points

    def get_all_paths(
        self,
        start: Optional[State] = None,
        goals: Optional[List[State]] = None,
        max_depth: int = 20,
        to_any_final: bool = False
    ) -> List[List[Transition]]:
        """
        Find all possible paths from start to goal state(s) using DFS.

        This is useful for:
        - Generating all possible video sequences
        - Testing different action sequences
        - Benchmark dataset creation

        Args:
            start: Starting state (defaults to world.initial_state)
            goals: List of goal states (defaults to world.goal_states). If single
                  State provided, wraps in list. If None, uses world.goal_states
            max_depth: Maximum path length to prevent infinite loops
            to_any_final: If True, paths terminate at ANY final state (not just goals)

        Returns:
            List of paths, where each path is a list of transitions
        """
        start = start or self.initial_state
        if not start:
            return []

        # Handle goals parameter
        if goals is None:
            goals = self.goal_states if self.goal_states else []
        elif isinstance(goals, State):
            goals = [goals]

        # If to_any_final, use all final states as targets
        if to_any_final:
            goals = self.get_final_states()

        if not goals:
            return []

        all_paths = []
        goal_set = set(goals)

        def dfs(current_state: State, current_path: List[Transition], visited: set):
            # Base case: reached any goal/final state
            if current_state in goal_set:
                all_paths.append(current_path.copy())
                return

            # Base case: max depth reached
            if len(current_path) >= max_depth:
                return

            # Explore all possible next transitions
            for transition in self.transitions:
                if transition.start_state == current_state:
                    # Avoid cycles (visiting same state twice)
                    if transition.end_state not in visited:
                        visited.add(transition.end_state)
                        current_path.append(transition)

                        dfs(transition.end_state, current_path, visited)

                        # Backtrack
                        current_path.pop()
                        visited.remove(transition.end_state)

        dfs(start, [], {start})
        return all_paths

    def get_successful_paths(self, start: Optional[State] = None) -> List[List[Transition]]:
        """
        Get all paths from start to ANY goal state (successful outcomes only).

        Args:
            start: Starting state (defaults to world.initial_state)

        Returns:
            List of paths that reach goal states
        """
        return self.get_all_paths(start=start, goals=self.goal_states)

    def get_failed_paths(self, start: Optional[State] = None) -> List[List[Transition]]:
        """
        Get all paths from start to failure states (non-goal final states).

        Args:
            start: Starting state (defaults to world.initial_state)

        Returns:
            List of paths that reach failure states
        """
        all_final = set(self.get_final_states())
        goal_set = set(self.goal_states)
        failure_states = list(all_final - goal_set)

        if not failure_states:
            return []

        return self.get_all_paths(start=start, goals=failure_states)

    def get_canonical_path(self) -> List[Transition]:
        """
        Get the canonical (primary/default) path from initial to goal state.

        If multiple paths exist, returns the shortest one.

        Returns:
            List of transitions forming the canonical path
        """
        all_paths = self.get_all_paths()
        if not all_paths:
            return []

        # Return shortest path as canonical
        return min(all_paths, key=len)

    def to_linear_path(self, path_id: str = "canonical") -> List[Transition]:
        """
        Extract a specific linear path from the branching structure.

        Args:
            path_id: Identifier for which path to extract
                    - "canonical": shortest path
                    - "path_0", "path_1", etc.: specific path by index

        Returns:
            List of transitions forming the requested path
        """
        if path_id == "canonical":
            return self.get_canonical_path()

        # Handle "path_N" format
        if path_id.startswith("path_"):
            try:
                index = int(path_id.split("_")[1])
                all_paths = self.get_all_paths()
                if 0 <= index < len(all_paths):
                    return all_paths[index]
            except (IndexError, ValueError):
                pass

        return []

    def get_branching_factor(self) -> float:
        """
        Calculate the average branching factor of the world.

        Branching factor = average number of actions per state.

        Returns:
            Average number of possible actions per state
        """
        if not self.states:
            return 0.0

        total_branches = sum(
            len(self.get_possible_actions(state))
            for state in self.states
        )
        return total_branches / len(self.states)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "states": [s.to_dict() for s in self.states],
            "actions": [a.to_dict() for a in self.actions],
            "transitions": [t.to_dict() for t in self.transitions],
            "initial_state": self.initial_state.to_dict() if self.initial_state else None,
            "goal_states": [s.to_dict() for s in self.goal_states],
            "final_states": [s.to_dict() for s in self.final_states],
            # Backward compatibility
            "goal_state": self.goal_state.to_dict() if self.goal_state else None
        }

    def save(self, filepath: str) -> None:
        """Save world to JSON file. If path doesn't include directory, saves to worlds/llm_worlds/."""
        from pathlib import Path
        filepath_obj = Path(filepath)

        # If just a filename, save to worlds/llm_worlds/
        if filepath_obj.parent == Path('.'):
            filepath_obj = Path('worlds/llm_worlds') / filepath_obj
            filepath_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath_obj, 'w') as f:
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

        # Load new format (multiple goals/finals)
        if data.get("goal_states"):
            world.goal_states = [State.from_dict(s) for s in data["goal_states"]]
        elif data.get("goal_state"):  # Backward compatibility
            world.goal_states = [State.from_dict(data["goal_state"])]

        if data.get("final_states"):
            world.final_states = [State.from_dict(s) for s in data["final_states"]]

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
    world.add_goal_state(s6)

    return world


def create_branching_ikea_world() -> World:
    """
    Create a branching IKEA desk assembly world with multiple action choices.

    This demonstrates how one state can have multiple possible actions,
    creating a graph structure with decision points.

    Returns:
        A World object with branching paths
    """
    world = World(
        name="IKEA_desk_assembly_branching",
        description="Assembly process with multiple method choices at decision points"
    )

    # Define states
    s0 = State(
        description="Unopened IKEA desk box on the floor",
        state_id="s0",
        metadata={"components_visible": False, "assembly_progress": 0.0}
    )

    # Branching point 1: Different ways to open the box
    s1a = State(
        description="Box carefully opened with scissors, all components neatly laid out",
        state_id="s1a",
        metadata={"opening_method": "scissors", "assembly_progress": 0.1}
    )

    s1b = State(
        description="Box torn open with hands, some components scattered",
        state_id="s1b",
        metadata={"opening_method": "hands", "assembly_progress": 0.1}
    )

    # Both converge to organized state
    s2 = State(
        description="Components sorted and organized, instructions visible",
        state_id="s2",
        metadata={"components_organized": True, "assembly_progress": 0.2}
    )

    # Branching point 2: Different assembly orders
    s3a = State(
        description="Started by attaching legs to drawer unit (bottom-up approach)",
        state_id="s3a",
        metadata={"assembly_approach": "bottom_up", "assembly_progress": 0.4}
    )

    s3b = State(
        description="Started by assembling the tabletop frame first (top-down approach)",
        state_id="s3b",
        metadata={"assembly_approach": "top_down", "assembly_progress": 0.4}
    )

    # Both eventually reach completed state
    s4 = State(
        description="All major components assembled, desk taking shape",
        state_id="s4",
        metadata={"assembly_progress": 0.7}
    )

    s5 = State(
        description="Completed desk with all screws tightened, ready to use",
        state_id="s5",
        metadata={"assembly_complete": True, "assembly_progress": 1.0}
    )

    # Define actions for branching point 1 (opening the box)
    a0a = Action(
        description="Carefully open box with scissors along the tape lines",
        action_id="a0a",
        action_type="unboxing",
        metadata={"tool": "scissors", "difficulty": "easy"}
    )

    a0b = Action(
        description="Tear open the box with hands quickly",
        action_id="a0b",
        action_type="unboxing",
        metadata={"tool": "hands", "difficulty": "medium"}
    )

    # Actions to converge from different opening methods
    a1_org = Action(
        description="Sort and organize all components by type",
        action_id="a1_org",
        action_type="organization"
    )

    # Define actions for branching point 2 (assembly order)
    a2a = Action(
        description="Attach legs to drawer unit first (bottom-up)",
        action_id="a2a",
        action_type="assembly",
        metadata={"approach": "bottom_up"}
    )

    a2b = Action(
        description="Assemble tabletop frame first (top-down)",
        action_id="a2b",
        action_type="assembly",
        metadata={"approach": "top_down"}
    )

    # Actions to complete assembly from different approaches
    a3a = Action(
        description="Continue bottom-up assembly: add remaining parts",
        action_id="a3a",
        action_type="assembly"
    )

    a3b = Action(
        description="Continue top-down assembly: attach to base",
        action_id="a3b",
        action_type="assembly"
    )

    # Final action
    a4 = Action(
        description="Tighten all screws and perform final checks",
        action_id="a4",
        action_type="finishing"
    )

    # Create branching transitions
    # Branch 1: Opening the box (2 choices)
    world.add_transition(s0, a0a, s1a)  # Open with scissors
    world.add_transition(s0, a0b, s1b)  # Tear with hands

    # Converge: Both opening methods lead to organized state
    world.add_transition(s1a, a1_org, s2)
    world.add_transition(s1b, a1_org, s2)

    # Branch 2: Assembly approach (2 choices)
    world.add_transition(s2, a2a, s3a)  # Bottom-up
    world.add_transition(s2, a2b, s3b)  # Top-down

    # Continue assembly from both approaches
    world.add_transition(s3a, a3a, s4)
    world.add_transition(s3b, a3b, s4)

    # Final step
    world.add_transition(s4, a4, s5)

    # Set initial and goal states
    world.initial_state = s0
    world.add_goal_state(s5)

    return world


def create_multi_ending_ikea_world() -> World:
    """
    Create an IKEA desk assembly world with multiple possible endings.

    This includes:
    - Multiple success states (goals) with different quality levels
    - Multiple failure states (non-goals)
    - Branching paths that lead to different outcomes

    Returns:
        A World with diverse endpoints including successes and failures
    """
    world = World(
        name="IKEA_desk_assembly_multi_ending",
        description="Assembly process with multiple possible outcomes (successes and failures)"
    )

    # Initial state
    s0 = State(
        description="Unopened IKEA desk box with instruction manual on top",
        state_id="s0",
        metadata={"assembly_progress": 0.0}
    )

    # Early decision: Read instructions or skip?
    s1a = State(
        description="Box opened, components laid out, instruction manual read carefully",
        state_id="s1a",
        metadata={"instructions_read": True, "assembly_progress": 0.1}
    )

    s1b = State(
        description="Box torn open, components scattered, instruction manual tossed aside",
        state_id="s1b",
        metadata={"instructions_read": False, "assembly_progress": 0.1}
    )

    # Middle states
    s2a = State(
        description="Following instructions step-by-step, all parts organized by number",
        state_id="s2a",
        metadata={"following_instructions": True, "assembly_progress": 0.3}
    )

    s2b = State(
        description="Attempting assembly by intuition, some confusion about which parts go where",
        state_id="s2b",
        metadata={"following_instructions": False, "assembly_progress": 0.2}
    )

    s2c = State(
        description="Frustrated and confused, considering giving up",
        state_id="s2c",
        metadata={"frustration_level": "high", "assembly_progress": 0.15}
    )

    s3a = State(
        description="Desk frame assembled correctly, checking alignment before final tightening",
        state_id="s3a",
        metadata={"assembly_quality": "high", "assembly_progress": 0.7}
    )

    s3b = State(
        description="Desk frame assembled but some parts seem loose, continuing anyway",
        state_id="s3b",
        metadata={"assembly_quality": "medium", "assembly_progress": 0.6}
    )

    s3c = State(
        description="Desk frame assembled incorrectly, using wrong screws in some places",
        state_id="s3c",
        metadata={"assembly_quality": "low", "assembly_progress": 0.5}
    )

    # SUCCESS STATES (GOALS)
    s_perfect = State(
        description="Perfect assembly: desk is stable, all screws tight, perfectly aligned, looks professional",
        state_id="s_perfect",
        metadata={"assembly_complete": True, "quality": 1.0, "outcome": "success"}
    )

    s_good = State(
        description="Good assembly: desk is functional and stable, minor cosmetic imperfections",
        state_id="s_good",
        metadata={"assembly_complete": True, "quality": 0.8, "outcome": "success"}
    )

    s_acceptable = State(
        description="Acceptable assembly: desk works but wobbles slightly, some screws could be tighter",
        state_id="s_acceptable",
        metadata={"assembly_complete": True, "quality": 0.6, "outcome": "success"}
    )

    # FAILURE STATES (NOT GOALS)
    s_gave_up = State(
        description="Gave up halfway: partially assembled desk on floor, tools scattered, person walking away defeated",
        state_id="s_gave_up",
        metadata={"assembly_complete": False, "quality": 0.2, "outcome": "failure"}
    )

    s_collapsed = State(
        description="Structural failure: desk collapsed when weight was placed on it, critical screws were missing",
        state_id="s_collapsed",
        metadata={"assembly_complete": False, "quality": 0.1, "outcome": "failure"}
    )

    s_wrong_assembly = State(
        description="Wrong assembly: followed wrong instructions, desk looks strange and parts don't fit properly",
        state_id="s_wrong_assembly",
        metadata={"assembly_complete": False, "quality": 0.3, "outcome": "failure"}
    )

    # Define actions
    a_read_carefully = Action(
        description="Open box carefully and read instruction manual thoroughly",
        action_id="a_read",
        action_type="preparation"
    )

    a_skip_instructions = Action(
        description="Tear open box and toss instructions aside, attempt assembly by intuition",
        action_id="a_skip",
        action_type="preparation"
    )

    a_follow_steps = Action(
        description="Methodically follow each instruction step, double-checking each connection",
        action_id="a_follow",
        action_type="assembly"
    )

    a_wing_it = Action(
        description="Try to figure it out without instructions, guessing which parts connect",
        action_id="a_wing",
        action_type="assembly"
    )

    a_get_frustrated = Action(
        description="Become frustrated with confusing parts, consider giving up",
        action_id="a_frustrate",
        action_type="emotional"
    )

    a_give_up = Action(
        description="Throw hands up in frustration and walk away from half-assembled desk",
        action_id="a_quit",
        action_type="termination"
    )

    a_continue_carefully = Action(
        description="Take a breath, re-read instructions, continue methodically",
        action_id="a_persist_good",
        action_type="assembly"
    )

    a_rush_completion = Action(
        description="Rush to finish without checking, just want to be done",
        action_id="a_rush",
        action_type="assembly"
    )

    a_use_wrong_parts = Action(
        description="Use whatever screws fit, not checking part numbers",
        action_id="a_wrong_parts",
        action_type="assembly"
    )

    a_final_tighten = Action(
        description="Carefully tighten all screws, check stability, adjust alignment",
        action_id="a_perfect_finish",
        action_type="finishing"
    )

    a_quick_finish = Action(
        description="Quickly tighten main screws, skip detailed checks",
        action_id="a_quick_finish",
        action_type="finishing"
    )

    a_sloppy_finish = Action(
        description="Loosely tighten screws, desk wobbles but seems okay",
        action_id="a_sloppy_finish",
        action_type="finishing"
    )

    a_test_weight = Action(
        description="Place heavy object on desk to test stability",
        action_id="a_test",
        action_type="testing"
    )

    # Build branching structure
    # Initial choice: read vs skip
    world.add_transition(s0, a_read_carefully, s1a)
    world.add_transition(s0, a_skip_instructions, s1b)

    # Path 1: Careful approach → Perfect outcome
    world.add_transition(s1a, a_follow_steps, s2a)
    world.add_transition(s2a, a_continue_carefully, s3a)
    world.add_transition(s3a, a_final_tighten, s_perfect)

    # Path 2: Skip instructions → Confusion → Either give up or continue poorly
    world.add_transition(s1b, a_wing_it, s2b)
    world.add_transition(s2b, a_get_frustrated, s2c)

    # From frustration, can give up or persist
    world.add_transition(s2c, a_give_up, s_gave_up)  # FAILURE
    world.add_transition(s2c, a_rush_completion, s3b)

    # Path 3: Rush to completion → Acceptable or poor outcome
    world.add_transition(s3b, a_quick_finish, s_good)  # SUCCESS (but not perfect)
    world.add_transition(s3b, a_sloppy_finish, s_acceptable)  # SUCCESS (barely)

    # Path 4: Wrong parts → Wrong assembly
    world.add_transition(s2b, a_use_wrong_parts, s3c)
    world.add_transition(s3c, a_rush_completion, s_wrong_assembly)  # FAILURE

    # Path 5: Sloppy finish → Test → Collapse
    world.add_transition(s3c, a_sloppy_finish, s_acceptable)  # Might work
    world.add_transition(s_acceptable, a_test_weight, s_collapsed)  # Or might fail!

    # Set initial state
    world.initial_state = s0

    # Mark goal states (successful outcomes)
    world.add_goal_state(s_perfect)
    world.add_goal_state(s_good)
    world.add_goal_state(s_acceptable)

    # Mark all final states (including failures)
    world.add_final_state(s_perfect, is_goal=True)
    world.add_final_state(s_good, is_goal=True)
    world.add_final_state(s_acceptable, is_goal=True)
    world.add_final_state(s_gave_up, is_goal=False)
    world.add_final_state(s_collapsed, is_goal=False)
    world.add_final_state(s_wrong_assembly, is_goal=False)

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

    # Demonstrate branching world capabilities
    print("\n" + "="*70)
    print("Testing Branching World Capabilities")
    print("="*70)

    print("\nCreating branching IKEA world with decision points...")
    branching_world = create_branching_ikea_world()

    print_world_summary(branching_world)

    # Show branching statistics
    print(f"\nBranching Statistics:")
    print(f"  Average branching factor: {branching_world.get_branching_factor():.2f}")

    # Show decision points
    decision_points = branching_world.get_decision_points()
    print(f"  Number of decision points: {len(decision_points)}")

    if decision_points:
        print(f"\nDecision Points:")
        for i, (state, actions) in enumerate(decision_points, 1):
            print(f"\n  {i}. State: {state.description}")
            print(f"     Possible actions ({len(actions)}):")
            for action in actions:
                print(f"       - {action.description}")

    # Show all possible paths
    all_paths = branching_world.get_all_paths()
    print(f"\nTotal possible paths from start to goal: {len(all_paths)}")

    for i, path in enumerate(all_paths):
        print(f"\n  Path {i+1} ({len(path)} steps):")
        for j, transition in enumerate(path, 1):
            print(f"    {j}. [{transition.start_state.state_id}] "
                  f"--[{transition.action.description}]--> "
                  f"[{transition.end_state.state_id}]")

    # Show canonical path
    canonical = branching_world.get_canonical_path()
    print(f"\nCanonical path (shortest): {len(canonical)} steps")

    # Save branching world
    branching_output = "ikea_desk_branching_world.json"
    save_world_to_json(branching_world, branching_output)

    # Demonstrate multi-ending world
    print("\n" + "="*70)
    print("Testing Multi-Ending World (Success & Failure States)")
    print("="*70)

    print("\nCreating IKEA world with multiple possible endings...")
    multi_world = create_multi_ending_ikea_world()

    print_world_summary(multi_world)

    # Show success vs failure breakdown
    print(f"\nOutcome Analysis:")
    print(f"  Total final states: {len(multi_world.get_final_states())}")
    print(f"  Goal states (successes): {len(multi_world.goal_states)}")
    print(f"  Failure states: {len(multi_world.get_final_states()) - len(multi_world.goal_states)}")

    print(f"\nGoal States (Successful Outcomes):")
    for i, goal in enumerate(multi_world.goal_states, 1):
        quality = goal.metadata.get("quality", "N/A")
        print(f"  {i}. [{goal.state_id}] {goal.description}")
        print(f"      Quality: {quality}")

    print(f"\nFailure States (Unsuccessful Outcomes):")
    all_final = set(multi_world.get_final_states())
    goal_set = set(multi_world.goal_states)
    failures = all_final - goal_set
    for i, failure in enumerate(failures, 1):
        quality = failure.metadata.get("quality", "N/A")
        print(f"  {i}. [{failure.state_id}] {failure.description}")
        print(f"      Quality: {quality}")

    # Show path statistics
    successful_paths = multi_world.get_successful_paths()
    failed_paths = multi_world.get_failed_paths()

    print(f"\nPath Statistics:")
    print(f"  Successful paths (reach goals): {len(successful_paths)}")
    print(f"  Failed paths (reach failures): {len(failed_paths)}")
    print(f"  Total paths: {len(successful_paths) + len(failed_paths)}")

    # Show some example paths
    if successful_paths:
        print(f"\nExample Successful Path (to {successful_paths[0][-1].end_state.state_id}):")
        for j, transition in enumerate(successful_paths[0], 1):
            print(f"  {j}. {transition.action.description}")

    if failed_paths:
        print(f"\nExample Failed Path (to {failed_paths[0][-1].end_state.state_id}):")
        for j, transition in enumerate(failed_paths[0], 1):
            print(f"  {j}. {transition.action.description}")

    # Show decision points
    decision_points = multi_world.get_decision_points()
    if decision_points:
        print(f"\nCritical Decision Points: {len(decision_points)}")
        for i, (state, actions) in enumerate(decision_points[:3], 1):  # Show first 3
            print(f"\n  {i}. At: {state.description[:60]}...")
            print(f"     Choices ({len(actions)}):")
            for action in actions:
                print(f"       - {action.description}")

    # Save multi-ending world
    multi_output = "ikea_desk_multi_ending_world.json"
    save_world_to_json(multi_world, multi_output)
