#!/usr/bin/env python3
"""
LLM World Generator - Generate complete worlds using Gemini LLM.

This module provides automated world generation in two steps:
1. Generate a linear world from high-level description
2. Expand linear world into branching world with multiple endings
"""

import os
import json
import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import numpy as np

from world_model_bench_agent.benchmark_curation import (
    World,
    State,
    Action,
    Transition,
    StateActionGenerator
)


class LLMWorldGenerator:
    """
    Uses Gemini LLM to automatically generate complete World scenarios.

    Two-step generation process:
    1. generate_linear_world(): Creates a simple linear path
    2. expand_to_branching_world(): Adds branches, alternatives, and multiple endings
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

    # ========================================================================
    # Step 1: Generate Linear World
    # ========================================================================

    def generate_linear_world(
        self,
        scenario: str,
        initial_description: str,
        goal_description: str,
        num_steps: int = 5,
        context: Optional[str] = None
    ) -> World:
        """
        Generate a simple linear world with a single path from start to goal.

        Args:
            scenario: Name/type of the scenario (e.g., "coffee_making")
            initial_description: Description of the starting state
            goal_description: Description of the goal state
            num_steps: Number of intermediate steps (not counting start/goal)
            context: Optional additional context for the LLM

        Returns:
            World object with a single linear path

        Example:
            world = generator.generate_linear_world(
                scenario="coffee_making",
                initial_description="Kitchen with coffee machine, beans, water, milk",
                goal_description="Perfect latte coffee in a cup",
                num_steps=5
            )
        """
        print(f"\nGenerating linear world for scenario: {scenario}")
        print(f"Steps: {num_steps + 2} (including start and goal)")

        # Build prompt
        prompt = self._build_linear_world_prompt(
            scenario=scenario,
            initial_description=initial_description,
            goal_description=goal_description,
            num_steps=num_steps,
            context=context
        )

        # Call LLM
        print("Calling Gemini LLM...")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        # Parse response
        print("Parsing LLM response...")
        data = self._parse_json_response(response.text)

        # Build World
        print("Building World object...")
        world = self._construct_linear_world(scenario, data)

        print(f"Linear world created: {len(world.states)} states, {len(world.transitions)} transitions")
        return world

    def _build_linear_world_prompt(
        self,
        scenario: str,
        initial_description: str,
        goal_description: str,
        num_steps: int,
        context: Optional[str]
    ) -> str:
        """Build the prompt for linear world generation."""
        prompt = f"""You are a world model generator. Generate a linear sequence of states and actions for the following scenario.

Scenario: {scenario}
Initial State: {initial_description}
Goal State: {goal_description}
Number of intermediate steps: {num_steps}
"""
        if context:
            prompt += f"Additional Context: {context}\n"

        prompt += f"""
Generate a detailed state-action sequence with exactly {num_steps + 2} states (including initial and goal).

Requirements:
1. Each state should have:
   - id: Unique identifier (s0, s1, s2, ...)
   - description: Detailed, specific description of what the state looks like
   - progress: Progress value from 0.0 (initial) to 1.0 (goal)

2. Each action should have:
   - id: Unique identifier (a0, a1, a2, ...)
   - description: Clear description of the action being performed
   - from_state: ID of the starting state
   - to_state: ID of the ending state
   - action_type: Category (e.g., preparation, processing, finishing)

3. The sequence should be:
   - Logical and realistic
   - Progress smoothly from initial to goal
   - Have clear causal relationships

Output ONLY valid JSON in this exact format:
{{
  "states": [
    {{"id": "s0", "description": "...", "progress": 0.0}},
    {{"id": "s1", "description": "...", "progress": 0.2}},
    ...
    {{"id": "s{num_steps + 1}", "description": "...", "progress": 1.0}}
  ],
  "actions": [
    {{"id": "a0", "description": "...", "from_state": "s0", "to_state": "s1", "action_type": "..."}},
    {{"id": "a1", "description": "...", "from_state": "s1", "to_state": "s2", "action_type": "..."}},
    ...
  ]
}}

JSON:"""
        return prompt

    def _construct_linear_world(self, scenario: str, data: Dict) -> World:
        """Construct a World object from parsed JSON data."""
        world = World(
            name=f"{scenario}_linear",
            description=f"Linear world for {scenario}"
        )

        # Create states
        states_map = {}
        for state_data in data["states"]:
            state = State(
                description=state_data["description"],
                state_id=state_data["id"],
                metadata={"progress": state_data["progress"]}
            )
            states_map[state.state_id] = state

        # Create transitions
        for action_data in data["actions"]:
            action = Action(
                description=action_data["description"],
                action_id=action_data["id"],
                action_type=action_data.get("action_type", "action")
            )

            start = states_map[action_data["from_state"]]
            end = states_map[action_data["to_state"]]

            world.add_transition(start, action, end)

        # Set initial and goal states
        world.initial_state = states_map["s0"]
        final_state_id = f"s{len(data['states']) - 1}"
        world.add_goal_state(states_map[final_state_id])

        return world

    # ========================================================================
    # Step 2: Expand to Branching World
    # ========================================================================

    def expand_to_branching_world(
        self,
        linear_world: World,
        total_states: int = 20,
        num_endings: int = 5,
        success_endings: int = 3,
        failure_endings: int = 2,
        branching_points: int = 3
    ) -> World:
        """
        Expand a linear world into a branching world with multiple paths and endings.

        Args:
            linear_world: The base linear world to expand
            total_states: Target total number of states
            num_endings: Total number of ending states
            success_endings: Number of successful endings (goals)
            failure_endings: Number of failure endings
            branching_points: Number of decision/branching points to create

        Returns:
            Expanded World with branches, alternatives, and multiple endings

        Example:
            branching = generator.expand_to_branching_world(
                linear_world=linear,
                total_states=25,
                num_endings=6,
                success_endings=4,
                failure_endings=2,
                branching_points=4
            )
        """
        print(f"\nExpanding linear world to branching world")
        print(f"Target: {total_states} states, {num_endings} endings ({success_endings} success, {failure_endings} failure)")

        # Create new world based on linear world
        branching_world = World(
            name=linear_world.name.replace("_linear", "_branching"),
            description=f"Branching world with multiple paths and endings"
        )

        # Copy linear path as the canonical path
        print("Copying canonical path...")
        self._copy_linear_path(linear_world, branching_world)

        # Step 1: Select branching points
        print(f"Selecting {branching_points} branching points...")
        linear_path = self._get_linear_path_states(linear_world)
        branch_states = self._select_branching_points(linear_path, branching_points)

        # Step 2: Generate ending states
        print(f"Generating {num_endings} ending states...")
        success_states, failure_states = self._generate_ending_states(
            scenario=linear_world.name,
            num_success=success_endings,
            num_failure=failure_endings,
            canonical_goal=linear_world.goal_state
        )

        # Add endings to world
        for state in success_states:
            branching_world.add_goal_state(state)
        for state in failure_states:
            branching_world.add_final_state(state, is_goal=False)

        # Step 3: Generate branches from branching points
        print("Generating deviation paths...")
        for i, branch_state in enumerate(branch_states):
            # Find the original action from this state
            original_action = self._get_action_from_state(linear_world, branch_state)

            if not original_action:
                continue

            # Generate 1-2 alternative actions
            num_alternatives = min(2, (num_endings - len(success_states)))
            for j in range(num_alternatives):
                deviation_type = ["risky", "shortcut", "mistake"][j % 3]

                # Generate alternative action
                alt_action = self._generate_alternative_action(
                    state=branch_state,
                    original_action=original_action,
                    deviation_type=deviation_type,
                    scenario=linear_world.name
                )

                # Choose a target ending
                if j == 0 and success_states:
                    # First alternative might lead to success
                    target_ending = success_states[i % len(success_states)]
                else:
                    # Other alternatives lead to failure
                    if failure_states:
                        target_ending = failure_states[j % len(failure_states)]
                    else:
                        continue

                # Generate deviation path
                deviation_path = self._generate_deviation_path(
                    branch_state=branch_state,
                    alternative_action=alt_action,
                    target_ending=target_ending,
                    scenario=linear_world.name,
                    max_steps=min(5, (total_states - len(branching_world.states)) // branching_points)
                )

                # Add deviation path to world
                for transition in deviation_path:
                    branching_world.add_transition(
                        transition.start_state,
                        transition.action,
                        transition.end_state
                    )

        print(f"Branching world created: {len(branching_world.states)} states, {len(branching_world.transitions)} transitions")
        print(f"Success paths: {len(branching_world.get_successful_paths())}")
        print(f"Failure paths: {len(branching_world.get_failed_paths())}")

        return branching_world

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _copy_linear_path(self, source: World, target: World):
        """Copy the linear path from source to target world."""
        target.initial_state = source.initial_state

        for transition in source.transitions:
            target.add_transition(
                transition.start_state,
                transition.action,
                transition.end_state
            )

    def _get_linear_path_states(self, world: World) -> List[State]:
        """Extract the ordered list of states from a linear world."""
        if not world.initial_state:
            return []

        path = [world.initial_state]
        current = world.initial_state

        while True:
            next_states = world.get_next_states(current)
            if not next_states:
                break
            current = next_states[0]
            path.append(current)

        return path

    def _select_branching_points(
        self,
        linear_path: List[State],
        num_points: int
    ) -> List[State]:
        """
        Intelligently select branching points from the linear path.

        Strategy:
        - Avoid first and last states
        - Distribute evenly along the path
        - Prefer states with medium progress (0.2-0.8)
        """
        if len(linear_path) <= 2:
            return []

        # Exclude first and last
        candidates = linear_path[1:-1]

        if len(candidates) <= num_points:
            return candidates

        # Evenly distribute
        indices = np.linspace(0, len(candidates) - 1, num_points, dtype=int)
        return [candidates[i] for i in indices]

    def _get_action_from_state(self, world: World, state: State) -> Optional[Action]:
        """Get the first action that can be performed from a state."""
        actions = world.get_possible_actions(state)
        return actions[0] if actions else None

    def _generate_alternative_action(
        self,
        state: State,
        original_action: Action,
        deviation_type: str,
        scenario: str
    ) -> Action:
        """
        Generate an alternative action using LLM.

        Args:
            state: Current state
            original_action: The canonical action
            deviation_type: Type of deviation (risky/shortcut/mistake)
            scenario: Scenario context
        """
        prompt = f"""Generate an alternative action for this state.

Scenario: {scenario}
Current State: {state.description}
Original Action (correct path): {original_action.description}

Generate an ALTERNATIVE action of type: {deviation_type}

- risky: A risky shortcut that might work but could cause problems
- shortcut: Skip some steps to save time, might affect quality
- mistake: A common mistake that people make, leading to failure

Output ONLY valid JSON:
{{
  "description": "Clear description of the alternative action",
  "action_type": "action type category",
  "risk_level": "low/medium/high",
  "likely_outcome": "success/partial_success/failure"
}}

JSON:"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        data = self._parse_json_response(response.text)

        return Action(
            description=data["description"],
            action_type=data.get("action_type", deviation_type),
            metadata={
                "deviation_type": deviation_type,
                "risk_level": data.get("risk_level", "medium"),
                "likely_outcome": data.get("likely_outcome", "unknown")
            }
        )

    def _generate_ending_states(
        self,
        scenario: str,
        num_success: int,
        num_failure: int,
        canonical_goal: Optional[State]
    ) -> Tuple[List[State], List[State]]:
        """
        Generate multiple ending states (success and failure).

        Args:
            scenario: Scenario name
            num_success: Number of success endings to generate
            num_failure: Number of failure endings to generate
            canonical_goal: The original goal state for reference

        Returns:
            (success_states, failure_states)
        """
        prompt = f"""Generate ending states for scenario: {scenario}

Generate {num_success} success endings and {num_failure} failure endings.

Success endings should have different quality levels:
- Perfect (quality: 1.0)
- Good (quality: 0.8)
- Acceptable (quality: 0.6)
- etc.

Failure endings should have different failure reasons:
- Gave up halfway
- Critical error/damage
- Wrong result/unusable
- etc.

"""
        if canonical_goal:
            prompt += f"Reference goal state: {canonical_goal.description}\n"

        prompt += """
Output ONLY valid JSON:
{
  "success_endings": [
    {
      "id": "s_perfect",
      "description": "Detailed description of perfect outcome",
      "quality": 1.0,
      "reason": "Why this outcome is achieved"
    },
    ...
  ],
  "failure_endings": [
    {
      "id": "s_failure1",
      "description": "Detailed description of failure",
      "quality": 0.2,
      "reason": "Why this failure occurred"
    },
    ...
  ]
}

JSON:"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        data = self._parse_json_response(response.text)

        success_states = []
        for ending in data.get("success_endings", [])[:num_success]:
            state = State(
                description=ending["description"],
                state_id=ending["id"],
                metadata={
                    "quality": ending["quality"],
                    "outcome": "success",
                    "reason": ending.get("reason", "")
                }
            )
            success_states.append(state)

        failure_states = []
        for ending in data.get("failure_endings", [])[:num_failure]:
            state = State(
                description=ending["description"],
                state_id=ending["id"],
                metadata={
                    "quality": ending["quality"],
                    "outcome": "failure",
                    "reason": ending.get("reason", "")
                }
            )
            failure_states.append(state)

        return success_states, failure_states

    def _generate_deviation_path(
        self,
        branch_state: State,
        alternative_action: Action,
        target_ending: State,
        scenario: str,
        max_steps: int = 5
    ) -> List[Transition]:
        """
        Generate a path from branch_state to target_ending.

        Args:
            branch_state: Where the deviation starts
            alternative_action: The first action of deviation
            target_ending: The target ending state
            scenario: Scenario context
            max_steps: Maximum steps in the path

        Returns:
            List of transitions forming the deviation path
        """
        prompt = f"""Generate a path from a branching state to an ending state.

Scenario: {scenario}
Starting State: {branch_state.description}
First Action: {alternative_action.description}
Target Ending: {target_ending.description}
Maximum Steps: {max_steps}

Generate a sequence of {max_steps} or fewer steps that:
1. Starts with the given alternative action
2. Progresses logically towards the target ending
3. Each step should be realistic and causal

Output ONLY valid JSON:
{{
  "path": [
    {{
      "action": "Description of action (first one should match the alternative_action)",
      "resulting_state": "Description of state after this action",
      "progress": "Progress value 0.0-1.0"
    }},
    ...
  ]
}}

The last resulting_state should lead to or BE the target ending.

JSON:"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        data = self._parse_json_response(response.text)

        # Build transitions
        transitions = []
        current_state = branch_state
        current_action = alternative_action

        for i, step in enumerate(data.get("path", [])[:max_steps]):
            # Create next state (or use target ending if last step)
            if i == len(data["path"]) - 1 or step["resulting_state"] == target_ending.description:
                next_state = target_ending
            else:
                next_state = State(
                    description=step["resulting_state"],
                    state_id=f"{branch_state.state_id}_alt_{i}",
                    metadata={"progress": step.get("progress", 0.5)}
                )

            # Create action (first one is the alternative_action we already have)
            if i > 0:
                current_action = Action(
                    description=step["action"],
                    action_id=f"{alternative_action.action_id}_{i}"
                )

            # Create transition
            transition = Transition(
                start_state=current_state,
                action=current_action,
                end_state=next_state
            )
            transitions.append(transition)

            current_state = next_state
            if current_state == target_ending:
                break

        return transitions

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Args:
            response_text: Raw text from LLM

        Returns:
            Parsed JSON dictionary
        """
        # Remove markdown code blocks if present
        text = response_text.strip()

        # Try to find JSON between ```json and ```
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            # Try to find JSON between ``` and ```
            json_match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)

        # Find JSON object or array
        if not text.startswith('{') and not text.startswith('['):
            # Try to find first { or [
            start = min(
                text.find('{') if '{' in text else len(text),
                text.find('[') if '[' in text else len(text)
            )
            if start < len(text):
                text = text[start:]

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response text: {text[:500]}...")
            raise ValueError(f"Failed to parse JSON from LLM response: {e}")

    def _validate_world(self, world: World) -> bool:
        """
        Validate that the generated world is well-formed.

        Checks:
        - Has initial state
        - Has at least one goal state
        - All states are reachable from initial
        - No orphaned states

        Returns:
            True if valid, raises ValueError if invalid
        """
        if not world.initial_state:
            raise ValueError("World has no initial state")

        if not world.goal_states:
            raise ValueError("World has no goal states")

        # Check reachability
        reachable = self._get_reachable_states(world)
        all_states = set(world.states)

        orphaned = all_states - reachable
        if orphaned:
            print(f"Warning: {len(orphaned)} orphaned states found: {[s.state_id for s in orphaned]}")

        return True

    def _get_reachable_states(self, world: World) -> Set[State]:
        """Get all states reachable from initial state."""
        if not world.initial_state:
            return set()

        reachable = {world.initial_state}
        queue = [world.initial_state]

        while queue:
            current = queue.pop(0)
            next_states = world.get_next_states(current)

            for next_state in next_states:
                if next_state not in reachable:
                    reachable.add(next_state)
                    queue.append(next_state)

        return reachable


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_generate(
    scenario: str,
    initial: str,
    goal: str,
    linear_steps: int = 5,
    total_states: int = 20,
    api_key: Optional[str] = None
) -> World:
    """
    Quick one-shot generation of a branching world.

    Args:
        scenario: Scenario name
        initial: Initial state description
        goal: Goal state description
        linear_steps: Steps in linear path
        total_states: Total states in branching world
        api_key: Optional API key

    Returns:
        Fully generated branching world
    """
    generator = LLMWorldGenerator(api_key=api_key)

    # Step 1: Linear
    linear = generator.generate_linear_world(
        scenario=scenario,
        initial_description=initial,
        goal_description=goal,
        num_steps=linear_steps
    )

    # Step 2: Branching
    branching = generator.expand_to_branching_world(
        linear_world=linear,
        total_states=total_states,
        num_endings=6,
        success_endings=3,
        failure_endings=3,
        branching_points=3
    )

    return branching
