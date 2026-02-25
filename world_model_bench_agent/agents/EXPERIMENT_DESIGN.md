# Experiment Design: Video-Based Agent Evaluation on Cube World

## Overview

This document outlines the comprehensive experimental design for evaluating different agent architectures on the Rubik's Cube Layer Twist Challenge. We compare multiple approaches ranging from naive baselines to state-of-the-art video understanding agents.

---

## Table of Contents

1. [Evaluation Framework](#1-evaluation-framework)
2. [Agent Approaches](#2-agent-approaches)
   - 2.1 [Naive Baseline](#21-naive-baseline-random--heuristic)
   - 2.2 [Single-Frame VLM](#22-single-frame-vlm)
   - 2.3 [MovieChat (Sparse Memory)](#23-moviechat-sparse-memory)
   - 2.4 [M3-Agent (Entity-Centric Memory)](#24-m3-agent-entity-centric-memory)
   - 2.5 [Sorative Video Methods](#25-sorative-video-methods)
   - 2.6 [Our Approach (TBD)](#26-our-approach-tbd)
3. [Metrics & Evaluation](#3-metrics--evaluation)
4. [Experimental Protocol](#4-experimental-protocol)
5. [Implementation Timeline](#5-implementation-timeline)

---

## 1. Evaluation Framework

### 1.1 Task Definition

**Goal**: Navigate the Rubik's cube state space by choosing layer twists to reach one of 3 success configurations while avoiding 4 dead-ends.

**Input**:
- Video of current cube state
- Available action descriptions (layer twists)
- Optionally: history of previous actions/states

**Output**:
- Selected action from available choices
- (Optional) Reasoning/justification

### 1.2 Challenge Characteristics

| Aspect | Description |
|--------|-------------|
| State Space | 15 unique cube configurations |
| Action Space | 15 layer twist actions (R, L, U, D moves) |
| Branching Factor | 1-4 actions per state |
| Success States | 3 (different solution sequences) |
| Failure States | 4 (dead-ends) |
| Special Features | 1 recovery loop (R→L returns to decision point) |
| Optimal Path Length | 3 transitions |
| Maximum Path Length | 5 transitions |

### 1.3 Test Modes

```
┌─────────────────────────────────────────────────────────────┐
│                     EVALUATION MODES                         │
├─────────────────────┬───────────────────────────────────────┤
│   MODE 1: SINGLE    │   Agent sees ONE state at a time      │
│   EPISODE           │   No explicit memory between calls     │
│                     │   Tests: Immediate reasoning           │
├─────────────────────┼───────────────────────────────────────┤
│   MODE 2: FULL      │   Agent has full episode context      │
│   CONTEXT           │   All previous states/actions visible  │
│                     │   Tests: Trajectory planning           │
├─────────────────────┼───────────────────────────────────────┤
│   MODE 3: STREAMING │   Agent receives states incrementally  │
│   VIDEO             │   Must maintain own memory             │
│                     │   Tests: Online learning/memory        │
├─────────────────────┼───────────────────────────────────────┤
│   MODE 4: MULTI-    │   Agent learns from multiple attempts  │
│   EPISODE           │   Can transfer knowledge across runs   │
│                     │   Tests: Meta-learning                 │
└─────────────────────┴───────────────────────────────────────┘
```

---

## 2. Agent Approaches

### 2.1 Naive Baseline (Random + Heuristic)

**Purpose**: Establish lower bound for comparison

#### 2.1.1 Random Agent

```python
class RandomAgent:
    """Uniformly random action selection."""

    def select_action(self, state: str, actions: List[str]) -> str:
        return random.choice(actions)
```

**Expected Performance**:
- Success Rate: ~27% (3/11 terminal states are success)
- Avg Steps to Terminal: ~3.5
- No learning capability

#### 2.1.2 Heuristic Agent

```python
class HeuristicAgent:
    """Rule-based agent with simple preferences."""

    def __init__(self):
        self.avoid_down = True  # D moves often lead to dead-ends
        self.prefer_consistency = True  # Prefer same direction

    def select_action(self, state: str, actions: List[str], history: List[str]) -> str:
        # Avoid D moves (heuristic from human analysis)
        non_down = [a for a in actions if "bottom" not in a.lower()]
        if non_down:
            actions = non_down

        # Prefer continuing same direction
        if history:
            last_dir = self.extract_direction(history[-1])
            same_dir = [a for a in actions if last_dir in a.lower()]
            if same_dir:
                return random.choice(same_dir)

        return random.choice(actions)
```

**Expected Performance**:
- Success Rate: ~50-60%
- Exploits simple patterns but can't reason

---

### 2.2 Single-Frame VLM

**Purpose**: Test if visual understanding alone is sufficient

#### 2.2.1 Architecture

```
┌────────────────┐     ┌─────────────────┐     ┌────────────────┐
│ Current State  │────►│  Vision-Language │────►│ Action Choice  │
│ (Image/Frame)  │     │  Model (GPT-4V)  │     │                │
└────────────────┘     └─────────────────┘     └────────────────┘
```

#### 2.2.2 Implementation

```python
class SingleFrameVLMAgent:
    """Uses GPT-4V or Claude to analyze current frame only."""

    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    def select_action(self, state_image: str, state_desc: str,
                     actions: List[Dict]) -> str:
        prompt = f"""
You are solving a Rubik's cube challenge. You see the current cube configuration.

Current state: {state_desc}

Available actions:
{self._format_actions(actions)}

Based on the visual appearance of the cube and your understanding of Rubik's cube mechanics,
which action should you take? Consider:
1. What colors/patterns are visible?
2. Which layer twist might help reach a solved state?

Respond with just the action_id of your choice.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": state_image}}
                    ]
                }
            ]
        )

        return self._parse_action_id(response.choices[0].message.content)
```

**Models to Test**:
- GPT-4o
- Claude 3.5 Sonnet
- Gemini 1.5 Pro
- LLaVA-OneVision

**Expected Performance**:
- Success Rate: ~40-60%
- Limited by lack of temporal reasoning
- May struggle with visually similar states

---

### 2.3 MovieChat (Sparse Memory)

**Purpose**: Test sparse video memory approach for long videos

**Paper**: [MovieChat: From Dense Token to Sparse Memory](https://arxiv.org/abs/2307.16449)
**Code**: [rese1f/MovieChat](https://github.com/rese1f/MovieChat)

#### 2.3.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MOVIECHAT ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Frame N-k   │    │   Frame N    │    │  Frame N+k   │  │
│  │    ....      │    │  (Current)   │    │    ....      │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │          │
│         └─────────┬─────────┴─────────┬─────────┘          │
│                   │                   │                    │
│                   ▼                   ▼                    │
│         ┌─────────────────┐  ┌─────────────────┐          │
│         │  Visual Encoder │  │  Token Merger   │          │
│         │  (Dense Tokens) │  │  (Compression)  │          │
│         └────────┬────────┘  └────────┬────────┘          │
│                  │                    │                   │
│                  └────────┬───────────┘                   │
│                           │                               │
│                           ▼                               │
│                  ┌─────────────────┐                      │
│                  │  Sparse Memory  │                      │
│                  │  (Key moments)  │                      │
│                  └────────┬────────┘                      │
│                           │                               │
│                           ▼                               │
│                  ┌─────────────────┐                      │
│                  │  LLM Decoder    │                      │
│                  │  (Vicuna/LLaVA) │                      │
│                  └────────┬────────┘                      │
│                           │                               │
│                           ▼                               │
│                      [Response]                           │
│                                                           │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3.2 Adaptation for Cube World

```python
class MovieChatAgent:
    """
    Sparse memory approach - compress video history into key moments.
    """

    def __init__(self, memory_size: int = 5):
        self.memory_size = memory_size
        self.sparse_memory = []  # Key frames/states
        self.visual_encoder = load_visual_encoder()
        self.llm = load_vicuna()

    def update_memory(self, frame: np.ndarray, state_desc: str):
        """Add frame to sparse memory with compression."""
        # Encode frame
        features = self.visual_encoder(frame)

        # Token merging - keep only distinctive features
        merged = self.merge_tokens(features, threshold=0.8)

        # Update sparse memory
        self.sparse_memory.append({
            "features": merged,
            "description": state_desc,
            "timestamp": len(self.sparse_memory)
        })

        # Evict oldest if over capacity
        if len(self.sparse_memory) > self.memory_size:
            self.sparse_memory = self.sparse_memory[-self.memory_size:]

    def select_action(self, current_frame: np.ndarray,
                     actions: List[str]) -> str:
        """Query sparse memory and decide."""
        # Build context from sparse memory
        memory_context = self._build_context()

        # Current frame features
        current_features = self.visual_encoder(current_frame)

        # Generate response
        response = self.llm.generate(
            memory_features=memory_context,
            current_features=current_features,
            query=f"Choose action: {actions}"
        )

        return response
```

**Modes**:
- **Global Mode**: Full episode context compressed
- **Breakpoint Mode**: Query at specific decision points

**Expected Performance**:
- Success Rate: ~50-70%
- Better than single-frame due to temporal context
- May lose fine details due to compression

---

### 2.4 M3-Agent (Entity-Centric Memory)

**Purpose**: Test structured memory with entity tracking

**See**: [M3_AGENT_METHOD.md](./M3_AGENT_METHOD.md) for full details

#### 2.4.1 Key Features

```
┌─────────────────────────────────────────────────────────────┐
│                    M3-AGENT FEATURES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✓ Dual Process (Memorization + Control)                    │
│  ✓ Entity-Centric Graph Structure                           │
│  ✓ Episodic + Semantic Memory                               │
│  ✓ Iterative Reasoning (up to 5 rounds)                     │
│  ✓ Memory Search Tools (search_node, search_clip)           │
│  ✓ Weight-Based Conflict Resolution                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.4.2 Expected Performance

- Success Rate: ~70-90%
- Excellent at avoiding known dead-ends
- Can learn from previous episodes
- Memory overhead scales with episodes

---

### 2.5 Sorative Video Methods

**Purpose**: Test story-aware video understanding

#### 2.5.1 Video-LLaVA Style (Narrative Understanding)

```python
class NarrativeVideoAgent:
    """
    Treats cube manipulation as a narrative/story.
    Understands cause-effect relationships.
    """

    def __init__(self):
        self.narrative_model = load_video_llava()
        self.story_buffer = []

    def observe(self, video_clip: str, action_desc: str):
        """Add clip to narrative understanding."""
        self.story_buffer.append({
            "video": video_clip,
            "action": action_desc,
            "narrative": self._generate_narrative(video_clip)
        })

    def _generate_narrative(self, video: str) -> str:
        """Generate story-like description of video."""
        return self.narrative_model.describe(
            video,
            prompt="Describe what happens in this video as part of a story about solving a puzzle."
        )

    def select_action(self, current_state: str, actions: List[str]) -> str:
        """Use narrative understanding to predict next action."""
        story_so_far = "\n".join([
            f"Chapter {i+1}: {entry['narrative']}"
            for i, entry in enumerate(self.story_buffer)
        ])

        prompt = f"""
The story so far:
{story_so_far}

Current situation: {current_state}

What should happen next to reach a successful conclusion?
Available choices:
{actions}

Choose the action that best continues this story toward success.
"""
        return self.narrative_model.generate(prompt)
```

#### 2.5.2 Temporal Grounding Methods

```python
class TemporalGroundingAgent:
    """
    Uses timestamps and temporal relationships.
    """

    def __init__(self):
        self.temporal_graph = nx.DiGraph()
        self.timestamps = {}

    def add_observation(self, state_id: str, timestamp: float, video_clip: str):
        """Add temporally grounded observation."""
        self.timestamps[state_id] = timestamp
        self.temporal_graph.add_node(state_id, time=timestamp, video=video_clip)

    def temporal_query(self, query: str) -> List[Dict]:
        """Query by temporal relationships."""
        # e.g., "What happened before the dead-end?"
        # e.g., "What was different 3 steps ago?"
        pass
```

**Expected Performance**:
- Success Rate: ~60-80%
- Good at understanding causal chains
- May overfit to narrative structure

---

### 2.6 Our Approach (TBD)

**Purpose**: Novel approach developed specifically for this benchmark

#### 2.6.1 Placeholder Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OUR APPROACH (TBD)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Key Ideas to Explore:                                      │
│                                                             │
│  1. State Prediction:                                       │
│     - Predict next state before seeing video                │
│     - Compare prediction vs reality                         │
│     - Use prediction error for learning                     │
│                                                             │
│  2. Action-Conditioned Memory:                              │
│     - Index memories by (state, action) pairs               │
│     - Fast lookup of "what happens if I do X from here?"   │
│                                                             │
│  3. World Model Integration:                                │
│     - Build internal model of cube state space              │
│     - Plan using learned transition dynamics                │
│                                                             │
│  4. Counterfactual Reasoning:                               │
│     - "What would have happened if I chose differently?"   │
│     - Learn from hypothetical alternatives                  │
│                                                             │
│  5. Active Exploration:                                     │
│     - Prioritize unexplored regions of state space          │
│     - Information gain as exploration bonus                 │
│                                                             │
│  Implementation: [To be developed]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2.6.2 Design Principles

1. **Efficiency**: Minimize API calls / inference cost
2. **Sample Efficiency**: Learn from few episodes
3. **Interpretability**: Explainable decision process
4. **Generalization**: Transfer to new cube challenges

---

## 3. Metrics & Evaluation

### 3.1 Primary Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Success Rate** | % of episodes reaching goal state | `successes / total_episodes` |
| **Path Efficiency** | Optimality of solution path | `optimal_length / actual_length` |
| **Dead-End Rate** | % of episodes hitting dead-ends | `dead_ends / total_episodes` |
| **Avg Episode Length** | Mean steps per episode | `sum(steps) / episodes` |

### 3.2 Secondary Metrics

| Metric | Description |
|--------|-------------|
| **First-Try Success** | Success without hitting any dead-end |
| **Recovery Rate** | Success after hitting dead-end (using loop) |
| **Memory Utilization** | For memory-based agents: search frequency |
| **Reasoning Depth** | For iterative agents: avg reasoning rounds |
| **API Cost** | Total tokens / API calls used |

### 3.3 Evaluation Protocol

```python
def evaluate_agent(agent, world, n_episodes: int = 100) -> Dict:
    """Standard evaluation protocol."""

    results = {
        "successes": 0,
        "failures": 0,
        "dead_ends": 0,
        "total_steps": 0,
        "paths": []
    }

    for episode in range(n_episodes):
        state = world.initial_state
        path = [state.state_id]
        steps = 0

        while not world.is_terminal(state):
            actions = world.get_available_actions(state)
            chosen = agent.select_action(state, actions)
            state = world.apply_action(state, chosen)
            path.append(state.state_id)
            steps += 1

            if steps > 20:  # Prevent infinite loops
                break

        # Record results
        results["paths"].append(path)
        results["total_steps"] += steps

        if state.state_id in world.goal_state_ids:
            results["successes"] += 1
        elif state.state_id in world.failure_state_ids:
            results["dead_ends"] += 1
            results["failures"] += 1
        else:
            results["failures"] += 1  # Timeout

    # Compute metrics
    results["success_rate"] = results["successes"] / n_episodes
    results["dead_end_rate"] = results["dead_ends"] / n_episodes
    results["avg_steps"] = results["total_steps"] / n_episodes

    return results
```

---

## 4. Experimental Protocol

### 4.1 Experiment Matrix

| Agent | Mode 1 (Single) | Mode 2 (Full Context) | Mode 3 (Streaming) | Mode 4 (Multi-Episode) |
|-------|-----------------|----------------------|-------------------|----------------------|
| Random | ✓ | N/A | N/A | N/A |
| Heuristic | ✓ | ✓ | N/A | N/A |
| Single-Frame VLM | ✓ | ✓ | N/A | N/A |
| MovieChat | ✓ | ✓ | ✓ | N/A |
| M3-Agent | ✓ | ✓ | ✓ | ✓ |
| Our Approach | ✓ | ✓ | ✓ | ✓ |

### 4.2 Ablation Studies

1. **Memory Size**: 0, 3, 5, 10, 20 entries
2. **Search Rounds**: 1, 3, 5 iterations
3. **Memory Type**: Episodic only vs Episodic+Semantic
4. **Model Size**: 7B vs 70B LLM backends
5. **Vision Encoder**: CLIP vs SigLIP vs DINOv2

### 4.3 Statistical Analysis

- **N = 100 episodes** per agent per mode
- **3 random seeds** for variance estimation
- **Paired t-tests** for significance (p < 0.05)
- **Bootstrap confidence intervals** for metrics

---

## 5. Implementation Timeline

### Week 1: Baselines

```
Day 1-2: Random + Heuristic agents
Day 3-4: Single-Frame VLM (GPT-4o, Claude)
Day 5:   Evaluation framework setup
```

### Week 2: Memory Agents

```
Day 1-2: MovieChat integration
Day 3-5: M3-Agent implementation
```

### Week 3: Our Approach

```
Day 1-3: Architecture design
Day 4-5: Initial implementation
```

### Week 4: Experiments & Analysis

```
Day 1-2: Full experiment runs
Day 3-4: Analysis & visualization
Day 5:   Paper writing / documentation
```

---

## 6. File Structure

```
world_model_bench_agent/agents/
├── M3_AGENT_METHOD.md          # Detailed M3-Agent documentation
├── EXPERIMENT_DESIGN.md        # This file
├── __init__.py
├── base_agent.py               # Abstract base class
├── random_agent.py             # Random baseline
├── heuristic_agent.py          # Rule-based agent
├── vlm_agent.py                # Single-frame VLM
├── moviechat_agent.py          # MovieChat implementation
├── m3_agent.py                 # M3-Agent implementation
├── our_agent.py                # Our custom approach
├── evaluation.py               # Evaluation framework
└── utils/
    ├── memory.py               # Memory utilities
    ├── video.py                # Video processing
    └── prompts.py              # Prompt templates
```

---

## 7. API Requirements

### Required APIs

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| OpenAI GPT-4o | VLM agent, M3-Agent control | ~$5-10/experiment |
| OpenAI Embeddings | Memory search | ~$0.50/experiment |
| Claude 3.5 Sonnet | Alternative VLM | ~$5-10/experiment |
| Gemini 1.5 Pro | Evaluation, memorization | ~$2-5/experiment |

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export GEMINI_API_KEY="..."
export HUGGINGFACE_TOKEN="..."
```

---

## 8. References

1. **M3-Agent**: https://arxiv.org/abs/2508.09736
2. **MovieChat**: https://arxiv.org/abs/2307.16449
3. **Video-LLaVA**: https://arxiv.org/abs/2311.10122
4. **LLaVA-OneVision**: https://arxiv.org/abs/2408.03326
5. **Our Cube World**: `worlds/video_worlds/cube_world_navigation_maze.json`

---

## Appendix A: Quick Start

```python
# Run baseline evaluation
from agents import RandomAgent, HeuristicAgent, evaluate_agent
from world_model_bench_agent.benchmark_curation import load_world_from_json

# Load world
world = load_world_from_json("worlds/video_worlds/cube_world_navigation_maze.json")

# Evaluate random baseline
random_agent = RandomAgent()
results = evaluate_agent(random_agent, world, n_episodes=100)
print(f"Random Success Rate: {results['success_rate']:.2%}")

# Evaluate heuristic
heuristic_agent = HeuristicAgent()
results = evaluate_agent(heuristic_agent, world, n_episodes=100)
print(f"Heuristic Success Rate: {results['success_rate']:.2%}")
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-21*
