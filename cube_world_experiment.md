# Cube World Agent Benchmark Experiment

Comprehensive evaluation of video-based agents on the Rubik's Cube Layer Twist Challenge.

---

## Experiment Overview

**Goal**: Compare different agent architectures' ability to navigate the cube world using **visual input only** (videos/images of cube states).

**Key Question**: Which memory and reasoning strategies are most effective for video-based sequential decision making?

---

## Agents Under Test

| # | Agent | Memory Type | Visual Input | Expected Success Rate |
|---|-------|-------------|--------------|----------------------|
| 1 | **RandomAgent** | None | No | ~27% (baseline) |
| 2 | **HeuristicAgent** | Action history | No | ~50-60% |
| 3 | **NaiveVLMAgent** | Frame descriptions (list) | Yes | ~60-70% |
| 4 | **M3StyleAgent** | Entity-centric graph | Yes | ~75-85% (best) |

---

## World Structure

**Cube World**: `worlds/video_worlds/cube_world_navigation_maze.json`

- **Initial State**: s1
- **States**: 15 total (s1-s15)
- **Transitions**: 15 actions (layer twists: R, L, U, D)
- **Success States**: 3 (s9, s11, s15)
- **Dead-End States**: 4 (s5, s7, s13, s14)
- **Decision Points**: States with 2-4 available actions

### Success Paths

```
Path 1: s1 → s2 → s8 → s9 [SUCCESS] (3 steps, optimal)
Path 2: s1 → s3 → s10 → s11 [SUCCESS] (3 steps, optimal)
Path 3: s1 → s4 → s6 → s12 → s15 [SUCCESS] (4 steps)
```

---

## Experiment Protocol

### Phase 1: Single Episode Evaluation

**Setup**: Each agent plays ONE episode starting from s1

**Process**:
1. Agent receives: current state VIDEO/IMAGE + available actions (text list)
2. Agent chooses action using its strategy
3. Simulator transitions to next state
4. Repeat until terminal state (success/dead-end) or max steps (10)

**Metrics**:
- Terminal state reached (success/dead-end/timeout)
- Path length (number of actions taken)
- Decisions at each state (action chosen + reasoning if available)

### Phase 2: Multiple Runs (Statistical)

**Setup**: Each agent plays 20 episodes (multiple starting conditions)

**Starting Conditions**:
- 10 runs from s1 (standard start)
- 5 runs from s2 (mid-path start)
- 5 runs from s3 (alternative path)

**Metrics**:
- Success rate (% reaching success states)
- Average path length to success
- Dead-end rate (% reaching dead-ends)
- Timeout rate (% exceeding max steps)
- Consistency (variance in performance)

### Phase 3: Memory & Learning Analysis

**Setup**: Only for memory-based agents (NaiveVLM, M3Style)

**Test Memory Utilization**:
- Track memory searches performed
- Analyze which memories were retrieved
- Evaluate memory's impact on decisions

**Test Learning**:
- Run episode 1-5 (initial learning)
- Run episode 6-10 (with accumulated memory)
- Compare performance improvement

---

## Data Collection

### Per Decision Log

```json
{
  "episode_id": "m3_ep_001",
  "step": 3,
  "current_state": "s2",
  "state_image": "path/to/s2.png",
  "available_actions": ["a7_turn_up", "a8_turn_right"],
  "agent_decision": {
    "action_id": "a7_turn_up",
    "reasoning": "Searching memory... found similar state before...",
    "visual_description": "Cube shows red on top, blue on front...",
    "memory_searches": 2,
    "confidence": 0.85
  },
  "next_state": "s8",
  "timestamp": "2025-02-25T12:34:56"
}
```

### Episode Summary

```json
{
  "episode_id": "m3_ep_001",
  "agent": "M3StyleAgent",
  "start_state": "s1",
  "terminal_state": "s9",
  "outcome": "success",
  "path": ["s1", "s2", "s8", "s9"],
  "actions": ["a2_turn_right", "a7_turn_up", "a9_turn_right"],
  "path_length": 3,
  "total_time": 12.5,
  "visual_used": true,
  "memory_stats": {
    "total_searches": 6,
    "unique_memories_accessed": 12
  }
}
```

---

## Evaluation Metrics

### Primary Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Success Rate** | % episodes reaching success states | Maximize |
| **Path Efficiency** | Avg path length for successful episodes | Minimize (optimal: 3) |
| **Dead-End Rate** | % episodes reaching dead-ends | Minimize |
| **Timeout Rate** | % episodes exceeding max steps | Minimize |

### Secondary Metrics (VLM Agents Only)

| Metric | Definition |
|--------|------------|
| **Visual Accuracy** | Quality of visual descriptions (manual review) |
| **Memory Utilization** | Avg memory searches per decision |
| **Reasoning Quality** | Coherence and relevance of reasoning (manual review) |
| **API Cost** | Total API tokens used per episode |

---

## Expected Results

### Hypothesis

**H1**: Memory-based agents (NaiveVLM, M3Style) will significantly outperform non-memory agents (Random, Heuristic)

**H2**: M3StyleAgent will show best performance due to:
- Entity-centric memory organization
- Semantic knowledge extraction
- Multi-round reasoning with memory search

**H3**: Visual understanding provides ~20-30% improvement over heuristics

### Predicted Performance

```
Agent               Success Rate    Avg Path (Success)    Dead-End Rate
------------------------------------------------------------------
RandomAgent         27%             ~4.5                  40%
HeuristicAgent      55%             ~4.0                  30%
NaiveVLMAgent       68%             ~3.8                  20%
M3StyleAgent        82%             ~3.2                  12%
```

---

## Implementation Requirements

### Core Components

1. **ExperimentRunner** - Main orchestrator
   - Loads world and agents
   - Runs episodes
   - Collects metrics

2. **WorldSimulator** - State machine
   - Manages current state
   - Validates actions
   - Transitions between states
   - Determines terminal conditions

3. **ResultsLogger** - Data collection
   - Logs every decision
   - Saves episode summaries
   - Tracks aggregate metrics

4. **Visualizer** - Results display
   - Success rate comparison chart
   - Path visualization
   - Memory utilization graphs

### File Structure

```
experiments/
├── run_cube_world_experiment.py     # Main runner
├── world_simulator.py               # State machine
├── results_logger.py                # Data collection
└── results/
    ├── logs/                        # Per-decision logs
    │   ├── random_ep001.json
    │   ├── m3_ep001.json
    │   └── ...
    ├── summaries/                   # Episode summaries
    │   ├── random_summary.json
    │   └── m3_summary.json
    └── analysis/                    # Aggregate results
        ├── comparison.json
        └── visualizations/
            ├── success_rates.png
            └── path_lengths.png
```

---

## Running the Experiment

### Quick Start

```bash
# Activate environment
source venv/bin/activate

# Run full experiment (all agents, 20 episodes each)
python experiments/run_cube_world_experiment.py

# Run specific agent
python experiments/run_cube_world_experiment.py --agent m3

# Run quick test (1 episode per agent)
python experiments/run_cube_world_experiment.py --quick
```

### Configuration

```python
# experiments/config.py
EXPERIMENT_CONFIG = {
    "episodes_per_agent": 20,
    "max_steps_per_episode": 10,
    "starting_states": {
        "s1": 10,  # 10 episodes from s1
        "s2": 5,   # 5 episodes from s2
        "s3": 5    # 5 episodes from s3
    },
    "agents": {
        "random": {"enabled": True, "seed": 42},
        "heuristic": {"enabled": True, "seed": 42},
        "naive_vlm": {"enabled": True, "model": "gpt-4o", "memory_size": 10},
        "m3": {"enabled": True, "model": "gpt-4o", "use_visual": True}
    },
    "output_dir": "experiments/results"
}
```

---

## Analysis Plan

### Quantitative Analysis

1. **Success Rate Comparison**
   - Bar chart: agent vs success rate
   - Statistical significance test (chi-square)

2. **Path Efficiency**
   - Box plot: path lengths by agent
   - Optimal path percentage

3. **Failure Analysis**
   - Where do agents get stuck?
   - Which decision points are hardest?

### Qualitative Analysis (VLM Agents)

1. **Visual Understanding Quality**
   - Sample 20 visual descriptions
   - Rate accuracy (1-5 scale)
   - Identify common failure modes

2. **Reasoning Quality**
   - Sample 20 reasoning traces
   - Evaluate coherence and relevance
   - Compare NaiveVLM vs M3Style reasoning

3. **Memory Usage Patterns**
   - Which memories are most accessed?
   - Does memory improve over time?
   - M3Style: episodic vs semantic memory usage

---

## Timeline

| Day | Activity |
|-----|----------|
| Day 1 | Implement WorldSimulator, ExperimentRunner |
| Day 2 | Run Phase 1 (single episode per agent) |
| Day 3 | Run Phase 2 (20 episodes per agent) |
| Day 4 | Quantitative analysis |
| Day 5 | Qualitative analysis (manual review) |
| Day 6 | Write-up and visualization |

---

## Success Criteria

✅ Experiment succeeds if:
1. All 4 agents complete at least 15/20 episodes each
2. M3StyleAgent achieves >70% success rate
3. Clear performance ranking emerges
4. Results support or refute hypotheses

---

## Next Steps After Experiment

Based on results:
1. Identify failure modes → design improvements
2. Ablation study on M3-Agent components
3. Design novel "CustomAgent" combining best strategies
4. Scale to more complex worlds
