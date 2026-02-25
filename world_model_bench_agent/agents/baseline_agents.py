"""
Baseline Agents for Cube World Benchmark.

This module provides baseline agent implementations:
1. RandomAgent - Uniformly random action selection (lower bound)
2. HeuristicAgent - Rule-based with simple preferences
3. NaiveVLMAgent - Single-frame VLM WITH memory of past observations

All agents receive VISUAL input (video/image) + action list.
"""

import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

# Import visual understanding from m3_agent
try:
    from .m3_agent import VisualUnderstanding, HAS_OPENAI, HAS_ANTHROPIC
except ImportError:
    from m3_agent import VisualUnderstanding, HAS_OPENAI, HAS_ANTHROPIC

if HAS_OPENAI:
    from openai import OpenAI

if HAS_ANTHROPIC:
    import anthropic


# =============================================================================
# Random Agent (Lower Bound Baseline)
# =============================================================================

class RandomAgent:
    """
    Uniformly random action selection.

    Purpose: Establish lower bound for comparison.
    No visual understanding, no memory, no learning.

    Expected Performance:
    - Success Rate: ~27% (3/11 terminal states are success)
    - Avg Steps to Terminal: ~3.5
    """

    def __init__(self, seed: Optional[int] = None):
        self.name = "RandomAgent"
        self.rng = random.Random(seed)
        self.action_history: List[str] = []
        self.episode_count = 0

    def select_action(
        self,
        available_actions: List[Dict],
        state_image_path: str = None,
        state_video_path: str = None,
        **kwargs
    ) -> Dict:
        """
        Randomly select an action (ignores visual input).

        Args:
            available_actions: List of available actions
            state_image_path: Ignored
            state_video_path: Ignored

        Returns:
            Dict with action_id
        """
        action = self.rng.choice(available_actions)
        action_id = action["action_id"]

        self.action_history.append(action_id)

        return {
            "action_id": action_id,
            "reasoning": "Random selection",
            "used_visual": False
        }

    def reset_episode(self):
        """Reset for new episode."""
        self.action_history = []
        self.episode_count += 1

    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "episode_count": self.episode_count,
            "total_actions": len(self.action_history)
        }


# =============================================================================
# Heuristic Agent (Rule-Based Baseline)
# =============================================================================

class HeuristicAgent:
    """
    Rule-based agent with simple preferences.

    Heuristics:
    1. Avoid D (down) moves - they often lead to dead-ends
    2. Prefer consistency - continue same direction if possible
    3. Avoid repeating the reverse of last action

    Expected Performance:
    - Success Rate: ~50-60%
    - Exploits simple patterns but can't reason visually
    """

    def __init__(self, seed: Optional[int] = None):
        self.name = "HeuristicAgent"
        self.rng = random.Random(seed)
        self.action_history: List[str] = []
        self.episode_count = 0

        # Heuristic settings
        self.avoid_down = True
        self.prefer_consistency = True
        self.avoid_reverse = True

    def _extract_direction(self, action_id: str) -> Optional[str]:
        """Extract direction from action_id (e.g., 'a1_turn_right' -> 'right')."""
        action_lower = action_id.lower()
        for direction in ['right', 'left', 'up', 'down', 'top', 'bottom']:
            if direction in action_lower:
                return direction
        return None

    def _is_reverse(self, action1: str, action2: str) -> bool:
        """Check if two actions are reverses of each other."""
        opposites = {
            'right': 'left', 'left': 'right',
            'up': 'down', 'down': 'up',
            'top': 'bottom', 'bottom': 'top'
        }
        dir1 = self._extract_direction(action1)
        dir2 = self._extract_direction(action2)
        if dir1 and dir2:
            return opposites.get(dir1) == dir2
        return False

    def select_action(
        self,
        available_actions: List[Dict],
        state_image_path: str = None,
        state_video_path: str = None,
        **kwargs
    ) -> Dict:
        """
        Select action using heuristics (ignores visual input).

        Args:
            available_actions: List of available actions
            state_image_path: Ignored
            state_video_path: Ignored

        Returns:
            Dict with action_id and reasoning
        """
        candidates = available_actions.copy()
        reasoning_steps = []

        # Heuristic 1: Avoid D (down/bottom) moves
        if self.avoid_down:
            non_down = [a for a in candidates
                       if 'down' not in a['action_id'].lower()
                       and 'bottom' not in a['action_id'].lower()]
            if non_down:
                candidates = non_down
                reasoning_steps.append("Avoided down moves")

        # Heuristic 2: Avoid reverse of last action
        if self.avoid_reverse and self.action_history:
            last_action = self.action_history[-1]
            non_reverse = [a for a in candidates
                         if not self._is_reverse(a['action_id'], last_action)]
            if non_reverse:
                candidates = non_reverse
                reasoning_steps.append(f"Avoided reverse of {last_action}")

        # Heuristic 3: Prefer consistency (same direction)
        if self.prefer_consistency and self.action_history:
            last_dir = self._extract_direction(self.action_history[-1])
            if last_dir:
                same_dir = [a for a in candidates
                          if last_dir in a['action_id'].lower()]
                if same_dir:
                    candidates = same_dir
                    reasoning_steps.append(f"Preferred {last_dir} direction")

        # Select from remaining candidates
        action = self.rng.choice(candidates)
        action_id = action["action_id"]

        self.action_history.append(action_id)

        return {
            "action_id": action_id,
            "reasoning": " -> ".join(reasoning_steps) if reasoning_steps else "No heuristics applied",
            "used_visual": False,
            "candidates_remaining": len(candidates)
        }

    def reset_episode(self):
        """Reset for new episode."""
        self.action_history = []
        self.episode_count += 1

    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "episode_count": self.episode_count,
            "total_actions": len(self.action_history)
        }


# =============================================================================
# Naive VLM Agent (Single-Frame with Memory)
# =============================================================================

@dataclass
class FrameMemory:
    """Memory entry for a single frame observation."""
    step: int
    image_path: str
    description: str  # VLM-generated description
    action_taken: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class NaiveVLMAgent:
    """
    Single-frame VLM agent WITH memory of past observations.

    This is the "naive" baseline that:
    1. Uses VLM to understand current frame
    2. Maintains memory of past frame descriptions (NOT raw images)
    3. Uses memory context to inform decisions

    Key difference from M3-Agent:
    - Simpler memory (list of descriptions, not entity-centric graph)
    - No semantic memory extraction
    - No multi-round reasoning with search
    - Just: see frame → recall past → decide

    Memory is stored as TEXT DESCRIPTIONS of key frames, not raw images.
    This is more token-efficient than sending all past images.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        memory_size: int = 10,
        visual_model: str = None
    ):
        """
        Initialize naive VLM agent.

        Args:
            model: LLM for decision making
            memory_size: Max number of past observations to remember
            visual_model: VLM for frame description (defaults to model)
        """
        self.name = "NaiveVLMAgent"
        self.model = model
        self.memory_size = memory_size

        # Visual understanding layer
        self.visual = VisualUnderstanding(model=visual_model or model)

        # Memory: list of frame descriptions
        self.frame_memory: List[FrameMemory] = []
        self.action_history: List[str] = []
        self.current_step = 0
        self.episode_count = 0

        # LLM client
        if "gpt" in model.lower() and HAS_OPENAI:
            self.client = OpenAI()
            self.provider = "openai"
        elif "claude" in model.lower() and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic()
            self.provider = "anthropic"
        else:
            self.client = None
            self.provider = None

    def _describe_current_state(
        self,
        state_image_path: str = None,
        state_video_path: str = None
    ) -> str:
        """Use VLM to describe current state."""
        if state_video_path and Path(state_video_path).exists():
            analysis = self.visual.describe_video(state_video_path)
            return analysis.get("synthesis", "Could not analyze video")
        elif state_image_path and Path(state_image_path).exists():
            return self.visual.describe_frame(
                state_image_path,
                prompt="Describe the Rubik's cube state. What colors are visible? What is the cube's orientation?"
            )
        return "No visual input provided"

    def _build_memory_context(self) -> str:
        """Build context string from frame memory."""
        if not self.frame_memory:
            return "No previous observations."

        context_lines = ["Previous observations:"]
        for mem in self.frame_memory:
            action_str = f" -> Took action: {mem.action_taken}" if mem.action_taken else ""
            context_lines.append(f"  Step {mem.step}: {mem.description}{action_str}")

        return "\n".join(context_lines)

    def _add_to_memory(self, image_path: str, description: str, action_taken: str = None):
        """Add observation to memory."""
        entry = FrameMemory(
            step=self.current_step,
            image_path=image_path or "",
            description=description,
            action_taken=action_taken
        )
        self.frame_memory.append(entry)

        # Evict oldest if over capacity
        if len(self.frame_memory) > self.memory_size:
            self.frame_memory = self.frame_memory[-self.memory_size:]

    def _call_llm(self, prompt: str) -> str:
        """Call LLM for decision."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            return "NO_LLM_AVAILABLE"

    def select_action(
        self,
        available_actions: List[Dict],
        state_image_path: str = None,
        state_video_path: str = None,
        **kwargs
    ) -> Dict:
        """
        Select action using VLM + memory.

        Process:
        1. Describe current state using VLM
        2. Build context from memory of past observations
        3. Ask LLM to choose action based on current + memory
        4. Store current observation in memory

        Args:
            available_actions: List of available actions
            state_image_path: Path to current state image
            state_video_path: Path to transition video

        Returns:
            Dict with action_id and reasoning
        """
        # Step 1: Describe current state
        current_description = self._describe_current_state(
            state_image_path, state_video_path
        )

        # Step 2: Build memory context
        memory_context = self._build_memory_context()

        # Step 3: Build decision prompt
        actions_str = "\n".join([
            f"  - {a['action_id']}: {a.get('description', '')}"
            for a in available_actions
        ])

        prompt = f"""You are navigating a Rubik's cube challenge. Based on your visual observations and memory, choose the best action.

CURRENT OBSERVATION (Step {self.current_step}):
{current_description}

MEMORY OF PAST OBSERVATIONS:
{memory_context}

AVAILABLE ACTIONS:
{actions_str}

Based on what you see now and what you remember from before:
1. What patterns do you notice?
2. Have you seen similar states before? What happened?
3. Which action is most likely to lead to success?

Respond with the action_id of your choice on the first line, then explain your reasoning."""

        # Step 4: Get LLM decision
        response = self._call_llm(prompt)

        # Parse action from response
        action_id = self._parse_action_id(response, available_actions)

        # Step 5: Store in memory (with action taken)
        # Update previous entry with action taken
        if self.frame_memory:
            self.frame_memory[-1].action_taken = action_id

        # Add current observation to memory
        self._add_to_memory(
            image_path=state_image_path or state_video_path,
            description=current_description
        )

        self.action_history.append(action_id)
        self.current_step += 1

        return {
            "action_id": action_id,
            "reasoning": response,
            "current_description": current_description,
            "memory_size": len(self.frame_memory),
            "used_visual": True
        }

    def _parse_action_id(self, response: str, available_actions: List[Dict]) -> str:
        """Parse action_id from LLM response."""
        valid_ids = [a["action_id"] for a in available_actions]

        # Try to find action_id in response
        response_lower = response.lower()
        for aid in valid_ids:
            if aid.lower() in response_lower:
                return aid

        # Fallback: first line might be the action
        first_line = response.strip().split('\n')[0].strip()
        for aid in valid_ids:
            if aid.lower() in first_line.lower():
                return aid

        # Last resort: random
        return random.choice(valid_ids)

    def reset_episode(self):
        """Reset for new episode (clears memory)."""
        self.frame_memory = []
        self.action_history = []
        self.current_step = 0
        self.episode_count += 1

    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "episode_count": self.episode_count,
            "memory_size": len(self.frame_memory),
            "total_actions": len(self.action_history)
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_random_agent(seed: int = None) -> RandomAgent:
    """Create a random baseline agent."""
    return RandomAgent(seed=seed)


def create_heuristic_agent(seed: int = None) -> HeuristicAgent:
    """Create a heuristic baseline agent."""
    return HeuristicAgent(seed=seed)


def create_naive_vlm_agent(
    model: str = "gpt-4o",
    memory_size: int = 10
) -> NaiveVLMAgent:
    """Create a naive VLM agent with frame memory."""
    return NaiveVLMAgent(model=model, memory_size=memory_size)


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    print("Baseline Agents for Cube World")
    print("=" * 50)

    # Test Random Agent
    random_agent = RandomAgent(seed=42)
    actions = [
        {"action_id": "a1_turn_right", "description": "R move"},
        {"action_id": "a2_turn_left", "description": "L move"},
    ]
    result = random_agent.select_action(actions)
    print(f"Random: {result['action_id']}")

    # Test Heuristic Agent
    heuristic_agent = HeuristicAgent(seed=42)
    result = heuristic_agent.select_action(actions)
    print(f"Heuristic: {result['action_id']} ({result['reasoning']})")

    # Test Naive VLM Agent (without actual visual input)
    naive_agent = NaiveVLMAgent(model="gpt-4o", memory_size=5)
    print(f"Naive VLM Agent created: memory_size={naive_agent.memory_size}")

    print("\nAll agents ready!")
