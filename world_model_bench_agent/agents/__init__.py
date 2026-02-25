"""
Agent implementations for video-based world navigation.

This module provides various agent architectures for playing the
Rubik's Cube Layer Twist Challenge and similar video-based benchmarks.

Agent Types (Implemented):
- RandomAgent: Baseline random action selection (lower bound)
- HeuristicAgent: Rule-based decision making
- NaiveVLMAgent: Single-frame VLM with frame memory
- M3StyleAgent: Entity-centric multimodal memory (M3-Agent style)

Agent Types (TBD):
- MovieChatAgent: Sparse memory video understanding
- CustomAgent: Our novel approach

See EXPERIMENT_DESIGN.md for full documentation.
See M3_AGENT_CHECKLIST.md for M3-Agent reconstruction comparison.
"""

from .base_agent import BaseAgent, MemoryBasedAgent, ReasoningAgent
from .m3_agent import (
    M3StyleAgent,
    MemoryGraph,
    MemoryNode,
    CubeWorldMemorizer,
    M3AgentController,
    VisualUnderstanding,
    create_m3_agent,
)
from .baseline_agents import (
    RandomAgent,
    HeuristicAgent,
    NaiveVLMAgent,
    create_random_agent,
    create_heuristic_agent,
    create_naive_vlm_agent,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "MemoryBasedAgent",
    "ReasoningAgent",
    # Baseline agents
    "RandomAgent",
    "HeuristicAgent",
    "NaiveVLMAgent",
    # M3-Agent style
    "M3StyleAgent",
    "MemoryGraph",
    "MemoryNode",
    "CubeWorldMemorizer",
    "M3AgentController",
    "VisualUnderstanding",
    # Factory functions
    "create_random_agent",
    "create_heuristic_agent",
    "create_naive_vlm_agent",
    "create_m3_agent",
]
