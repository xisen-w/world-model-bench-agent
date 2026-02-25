"""
Base agent class for video-based world navigation.

All agent implementations should inherit from BaseAgent and implement
the required methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import json


@dataclass
class AgentObservation:
    """Observation received by an agent at each step."""

    state_id: str
    """Current state identifier"""

    state_description: str
    """Text description of current state"""

    state_image_path: Optional[str] = None
    """Path to state image (if available)"""

    available_actions: List[Dict] = field(default_factory=list)
    """List of available actions with descriptions"""

    video_path: Optional[str] = None
    """Path to video showing transition to this state"""

    metadata: Dict = field(default_factory=dict)
    """Additional metadata"""


@dataclass
class AgentAction:
    """Action chosen by an agent."""

    action_id: str
    """Identifier of chosen action"""

    action_description: str
    """Description of the action"""

    reasoning: Optional[str] = None
    """Agent's reasoning for this choice (if available)"""

    confidence: Optional[float] = None
    """Agent's confidence in this choice (0-1)"""

    metadata: Dict = field(default_factory=dict)
    """Additional metadata (e.g., search results used)"""


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Agents must implement:
    - select_action(): Choose an action given current observation
    - reset(): Reset agent state for new episode

    Optionally override:
    - observe(): Process observation (for memory-based agents)
    - update(): Update after receiving outcome
    - get_config(): Return agent configuration
    """

    def __init__(self, name: str = "BaseAgent", config: Dict = None):
        """
        Initialize agent.

        Args:
            name: Agent identifier for logging
            config: Configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.episode_history: List[Dict] = []
        self.total_episodes = 0
        self.current_step = 0

    @abstractmethod
    def select_action(self, observation: AgentObservation) -> AgentAction:
        """
        Select an action given the current observation.

        Args:
            observation: Current state information

        Returns:
            AgentAction with chosen action
        """
        pass

    def observe(self, observation: AgentObservation) -> None:
        """
        Process an observation (optional, for memory-based agents).

        Override this method if your agent needs to build memory
        from observations before decision time.

        Args:
            observation: New observation to process
        """
        pass

    def update(self, observation: AgentObservation, action: AgentAction,
               next_observation: AgentObservation, reward: float) -> None:
        """
        Update agent after receiving transition outcome.

        Override this method if your agent learns from experience.

        Args:
            observation: State before action
            action: Action taken
            next_observation: Resulting state
            reward: Reward received (+1 success, -1 failure, 0 otherwise)
        """
        # Record in episode history
        self.episode_history.append({
            "step": self.current_step,
            "state": observation.state_id,
            "action": action.action_id,
            "next_state": next_observation.state_id,
            "reward": reward
        })
        self.current_step += 1

    def reset(self) -> None:
        """
        Reset agent state for new episode.

        Called at the start of each new episode.
        Override if your agent needs special reset logic.
        """
        self.episode_history = []
        self.current_step = 0
        self.total_episodes += 1

    def get_config(self) -> Dict:
        """
        Return agent configuration for logging/reproducibility.

        Returns:
            Dictionary of agent configuration
        """
        return {
            "name": self.name,
            "class": self.__class__.__name__,
            "config": self.config,
            "total_episodes": self.total_episodes
        }

    def save_state(self, path: str) -> None:
        """Save agent state to file."""
        state = {
            "config": self.get_config(),
            "episode_history": self.episode_history
        }
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self, path: str) -> None:
        """Load agent state from file."""
        with open(path, 'r') as f:
            state = json.load(f)
        self.config = state.get("config", {}).get("config", {})
        self.episode_history = state.get("episode_history", [])


class MemoryBasedAgent(BaseAgent):
    """
    Base class for agents with explicit memory.

    Extends BaseAgent with:
    - Memory storage and retrieval
    - Episodic and semantic memory types
    - Memory search capabilities
    """

    def __init__(self, name: str = "MemoryAgent", config: Dict = None,
                 memory_size: int = 100):
        super().__init__(name, config)
        self.memory_size = memory_size
        self.episodic_memory: List[Dict] = []
        self.semantic_memory: List[Dict] = []

    def add_episodic_memory(self, entry: Dict) -> None:
        """Add entry to episodic memory."""
        entry["memory_id"] = f"ep_{len(self.episodic_memory)}"
        self.episodic_memory.append(entry)

        # Evict oldest if over capacity
        if len(self.episodic_memory) > self.memory_size:
            self.episodic_memory = self.episodic_memory[-self.memory_size:]

    def add_semantic_memory(self, entry: Dict) -> None:
        """Add entry to semantic memory."""
        entry["memory_id"] = f"sem_{len(self.semantic_memory)}"
        self.semantic_memory.append(entry)

    def search_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search memory for relevant entries.

        Override this method with your search implementation
        (e.g., embedding similarity, keyword matching).

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant memory entries
        """
        # Default: simple keyword matching
        results = []

        for entry in self.episodic_memory + self.semantic_memory:
            content = str(entry.get("content", "")).lower()
            if query.lower() in content:
                results.append(entry)

        return results[:top_k]

    def reset(self) -> None:
        """Reset for new episode (preserves long-term memory)."""
        super().reset()
        # Note: Episodic/semantic memory persists across episodes
        # Override if you want to clear memory too


class ReasoningAgent(BaseAgent):
    """
    Base class for agents with explicit reasoning.

    Extends BaseAgent with:
    - Multi-round reasoning loops
    - Tool use (search, etc.)
    - Reasoning trace logging
    """

    def __init__(self, name: str = "ReasoningAgent", config: Dict = None,
                 max_reasoning_rounds: int = 5):
        super().__init__(name, config)
        self.max_reasoning_rounds = max_reasoning_rounds
        self.reasoning_trace: List[Dict] = []

    def reason(self, context: str) -> Dict:
        """
        Perform one round of reasoning.

        Returns:
            Dict with keys:
            - "action_type": "SEARCH" or "ANSWER"
            - "arguments": Query for SEARCH, action_id for ANSWER
            - "reasoning": Explanation
        """
        raise NotImplementedError

    def execute_search(self, query: str) -> str:
        """Execute a search query and return results."""
        raise NotImplementedError

    def select_action(self, observation: AgentObservation) -> AgentAction:
        """
        Multi-round reasoning to select action.
        """
        context = self._build_context(observation)
        self.reasoning_trace = []

        for round_num in range(self.max_reasoning_rounds):
            # Perform reasoning
            result = self.reason(context)

            # Log reasoning trace
            self.reasoning_trace.append({
                "round": round_num,
                **result
            })

            if result["action_type"] == "SEARCH":
                # Execute search and append results
                search_results = self.execute_search(result["arguments"])
                context += f"\n\nSearch results for '{result['arguments']}':\n{search_results}"

            elif result["action_type"] == "ANSWER":
                # Return chosen action
                return AgentAction(
                    action_id=result["arguments"],
                    action_description=self._get_action_desc(
                        observation, result["arguments"]
                    ),
                    reasoning=result.get("reasoning"),
                    metadata={"reasoning_trace": self.reasoning_trace}
                )

        # Fallback if no answer after max rounds
        return self._fallback_action(observation)

    def _build_context(self, observation: AgentObservation) -> str:
        """Build context string from observation."""
        actions_str = "\n".join([
            f"- {a['action_id']}: {a['description']}"
            for a in observation.available_actions
        ])

        return f"""
Current state: {observation.state_description}

Available actions:
{actions_str}

Episode history: {len(self.episode_history)} steps taken
"""

    def _get_action_desc(self, observation: AgentObservation,
                        action_id: str) -> str:
        """Get action description by ID."""
        for action in observation.available_actions:
            if action["action_id"] == action_id:
                return action.get("description", "")
        return ""

    def _fallback_action(self, observation: AgentObservation) -> AgentAction:
        """Fallback action if reasoning fails."""
        import random
        action = random.choice(observation.available_actions)
        return AgentAction(
            action_id=action["action_id"],
            action_description=action.get("description", ""),
            reasoning="Fallback: No decision made after max rounds",
            metadata={"fallback": True}
        )
