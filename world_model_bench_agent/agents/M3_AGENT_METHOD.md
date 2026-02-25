# M3-Agent Method for Cube World Challenge

## Overview

M3-Agent (Multimodal Memory-Based Agent) is a framework designed for streaming video understanding with persistent memory. This document describes how to adapt M3-Agent for our Rubik's Cube Layer Twist Challenge.

**Paper**: [M3-Agent: A Multimodal Memory-based Agent for Instruction Execution on Streaming Video](https://arxiv.org/abs/2508.09736)
**Code**: [bytedance-seed/m3-agent](https://github.com/bytedance-seed/m3-agent)

---

## M3-Agent Core Architecture

### 1. Dual-Process System

M3-Agent operates with two parallel processes:

```
┌─────────────────────────────────────────────────────────────────┐
│                        M3-AGENT SYSTEM                          │
├─────────────────────────┬───────────────────────────────────────┤
│   MEMORIZATION PROCESS  │         CONTROL PROCESS               │
│                         │                                       │
│  ┌───────────────┐      │    ┌───────────────────────────┐     │
│  │ Video/Audio   │      │    │    Task/Question Input    │     │
│  │   Stream      │      │    └─────────────┬─────────────┘     │
│  └───────┬───────┘      │                  │                   │
│          │              │                  ▼                   │
│          ▼              │    ┌───────────────────────────┐     │
│  ┌───────────────┐      │    │  Iterative Reasoning Loop │     │
│  │ 30-sec Clips  │      │    │  (up to 5 rounds)         │     │
│  └───────┬───────┘      │    │                           │     │
│          │              │    │  1. Generate reasoning    │     │
│          ▼              │    │  2. Choose action:        │     │
│  ┌───────────────┐      │    │     - [Search] → query    │     │
│  │ Qwen2.5-Omni  │      │    │     - [Answer] → respond  │     │
│  │ (Memorization)│      │    │  3. Append results        │     │
│  └───────┬───────┘      │    └─────────────┬─────────────┘     │
│          │              │                  │                   │
│          ▼              │                  ▼                   │
│  ┌───────────────┐      │    ┌───────────────────────────┐     │
│  │ Memory Graph  │◄─────┼────│   Memory Retrieval        │     │
│  │ (Entity-      │      │    │   (search_node/clip)      │     │
│  │  Centric)     │──────┼───►│                           │     │
│  └───────────────┘      │    └───────────────────────────┘     │
│                         │                                       │
└─────────────────────────┴───────────────────────────────────────┘
```

### 2. Memory Types

M3-Agent maintains two types of memory:

#### Episodic Memory
Concrete observed events with temporal grounding:
```json
{
  "type": "episodic",
  "content": "The right face of the cube was rotated 90° clockwise",
  "timestamp": "00:15-00:18",
  "modality": "video",
  "entity_id": "cube_001"
}
```

#### Semantic Memory
Abstracted knowledge extracted from observations:
```json
{
  "type": "semantic",
  "content": "Rotating R twice (R R) from decision point leads to success",
  "derived_from": ["episodic_001", "episodic_002"],
  "confidence": 0.95
}
```

### 3. Entity-Centric Graph Structure

Memory is organized as a graph where:
- **Nodes**: Individual memory items (episodic or semantic)
- **Edges**: Relationships between memories (temporal, causal, entity-based)
- **Weights**: Activation frequency (higher weight = more reliable)

```
        ┌──────────────┐
        │ CUBE_STATE_0 │
        │ (Initial)    │
        └──────┬───────┘
               │ R_move
        ┌──────┴───────┐
        │              │
        ▼              ▼
┌──────────────┐ ┌──────────────┐
│ CUBE_STATE_1 │ │ CUBE_STATE_2 │
│ (After R)    │ │ (After R alt)│
└──────┬───────┘ └──────────────┘
       │ R_move
       ▼
┌──────────────┐
│ SUCCESS_1    │
│ (R R solved) │
└──────────────┘
```

---

## Adapting M3-Agent for Cube World

### Step 1: Video Preprocessing

Our cube world videos need to be processed similarly to M3-Agent's pipeline:

```python
# Preprocessing pipeline for cube world
class CubeWorldPreprocessor:
    def __init__(self, video_dir: str):
        self.video_dir = video_dir
        self.clips = []

    def segment_videos(self) -> List[Dict]:
        """
        Unlike M3-Agent's 30-sec clips, our videos are transition-based.
        Each video = one action (layer twist).
        """
        segments = []
        for video_file in Path(self.video_dir).glob("*.mov"):
            segments.append({
                "video_path": str(video_file),
                "action_id": self.extract_action_id(video_file.stem),
                "duration": self.get_duration(video_file)
            })
        return segments

    def extract_visual_features(self, video_path: str) -> Dict:
        """Extract cube state from video frames."""
        # Key frames: first frame (before twist), last frame (after twist)
        return {
            "start_frame": self.extract_frame(video_path, 0),
            "end_frame": self.extract_frame(video_path, -1),
            "motion_description": self.describe_rotation(video_path)
        }
```

### Step 2: Memory Generation

Adapt the memorization process for cube manipulation:

```python
class CubeMemorizer:
    """
    Generate episodic and semantic memories from cube manipulation videos.
    """

    def __init__(self, model: str = "Qwen2.5-Omni"):
        self.model = model
        self.episodic_memory = []
        self.semantic_memory = []

    def process_transition(self, video_path: str, action_desc: str,
                          start_state: str, end_state: str) -> Dict:
        """
        Process a single cube transition video.

        Args:
            video_path: Path to transition video
            action_desc: "Twist the right face 90° clockwise (R move)"
            start_state: State before action
            end_state: State after action

        Returns:
            Memory entries (episodic + semantic)
        """
        # Episodic: What happened
        episodic = {
            "id": f"ep_{len(self.episodic_memory)}",
            "type": "episodic",
            "video_path": video_path,
            "action": action_desc,
            "observation": f"Observed: {action_desc}. Cube changed from {start_state} to {end_state}",
            "timestamp": datetime.now().isoformat()
        }

        # Semantic: What can be learned
        semantic = self.extract_semantic(episodic, end_state)

        self.episodic_memory.append(episodic)
        if semantic:
            self.semantic_memory.append(semantic)

        return {"episodic": episodic, "semantic": semantic}

    def extract_semantic(self, episodic: Dict, end_state: str) -> Optional[Dict]:
        """Extract generalizable knowledge from episodic memory."""

        # Check if this is a success or dead-end
        if "success" in end_state.lower():
            return {
                "id": f"sem_{len(self.semantic_memory)}",
                "type": "semantic",
                "knowledge": f"Action sequence leading to {end_state} is valid",
                "derived_from": [episodic["id"]],
                "outcome": "success"
            }
        elif "dead" in end_state.lower():
            return {
                "id": f"sem_{len(self.semantic_memory)}",
                "type": "semantic",
                "knowledge": f"Action sequence leading to {end_state} should be avoided",
                "derived_from": [episodic["id"]],
                "outcome": "failure"
            }
        return None
```

### Step 3: Control Loop

The control process for navigating the cube world:

```python
class CubeController:
    """
    M3-Agent style controller for cube world navigation.
    Uses iterative reasoning with memory retrieval.
    """

    def __init__(self, memory_graph: MemoryGraph, max_rounds: int = 5):
        self.memory = memory_graph
        self.max_rounds = max_rounds
        self.action_history = []

    def decide_action(self, current_state: str, available_actions: List[str]) -> str:
        """
        Iterative decision-making process.

        Steps:
        1. Reason about current state
        2. Search memory for relevant experiences
        3. Choose action based on retrieved knowledge
        """
        context = f"Current state: {current_state}\nAvailable actions: {available_actions}"

        for round_num in range(self.max_rounds):
            # Generate reasoning
            reasoning = self.generate_reasoning(context)

            # Decide: Search or Answer
            action_type, args = self.parse_reasoning(reasoning)

            if action_type == "SEARCH":
                # Query memory
                results = self.memory.search(args)
                context += f"\n\nMemory search results:\n{results}"

            elif action_type == "ANSWER":
                # Return chosen action
                return args

        # Fallback: random action if no decision made
        return random.choice(available_actions)

    def generate_reasoning(self, context: str) -> str:
        """
        Prompt the LLM to reason about the current situation.

        Returns one of:
        - [SEARCH] <query>: Search memory for relevant info
        - [ANSWER] <action>: Choose an action to take
        """
        prompt = f"""
You are navigating a Rubik's cube challenge. Based on the current state and your memory,
decide what to do next.

{context}

Previous actions taken: {self.action_history}

Think step by step:
1. What do I know about this state?
2. Have I seen similar situations before?
3. What actions led to success/failure?

Respond with either:
- [SEARCH] <query> to search your memory
- [ANSWER] <action_id> to choose an action

Your response:
"""
        return self.llm.generate(prompt)
```

### Step 4: Memory Search Tools

Implement search capabilities similar to M3-Agent:

```python
class MemoryGraph:
    """Entity-centric memory graph for cube world."""

    def __init__(self):
        self.nodes = {}  # id -> memory entry
        self.edges = []  # relationships
        self.embeddings = {}  # for semantic search

    def search_node(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant memory nodes.
        Uses embedding similarity.
        """
        query_embedding = self.embed(query)

        scores = []
        for node_id, node in self.nodes.items():
            if node_id in self.embeddings:
                score = cosine_similarity(query_embedding, self.embeddings[node_id])
                scores.append((node_id, score, node))

        # Sort by score and weight
        scores.sort(key=lambda x: x[1] * x[2].get("weight", 1.0), reverse=True)

        return [s[2] for s in scores[:top_k]]

    def search_by_outcome(self, outcome: str) -> List[Dict]:
        """Search for memories with specific outcomes (success/failure)."""
        return [
            node for node in self.nodes.values()
            if node.get("outcome") == outcome
        ]

    def get_action_sequence(self, target_state: str) -> List[str]:
        """
        Find the action sequence that leads to a target state.
        Uses graph traversal.
        """
        # BFS from initial state to target
        from collections import deque

        queue = deque([("s0", [])])
        visited = set()

        while queue:
            current, path = queue.popleft()

            if current == target_state:
                return path

            for edge in self.edges:
                if edge["from"] == current and edge["to"] not in visited:
                    visited.add(edge["to"])
                    queue.append((edge["to"], path + [edge["action"]]))

        return []
```

---

## Implementation Plan for Cube World

### Phase 1: Setup (Day 1)

```bash
# 1. Install M3-Agent dependencies
pip install transformers torch torchvision
pip install qwen-omni-utils  # For memorization model

# 2. Set up API keys
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"  # Optional, for evaluation
```

### Phase 2: Memory Construction (Day 1-2)

1. **Process all cube world videos**:
   ```python
   # Load world definition
   world = load_world_from_json("worlds/video_worlds/cube_world_navigation_maze.json")

   # Build memory from transitions
   memorizer = CubeMemorizer()
   for transition in world.transitions:
       memorizer.process_transition(
           video_path=transition.video_path,
           action_desc=transition.action_description,
           start_state=transition.start_state_id,
           end_state=transition.end_state_id
       )

   # Save memory graph
   memorizer.save("cube_world_memory.json")
   ```

2. **Build entity-centric graph**:
   - Nodes: Each cube state + each action
   - Edges: Transitions between states
   - Weights: Initialize uniformly, update based on exploration

### Phase 3: Control Integration (Day 2-3)

1. **Implement control loop**:
   - Load memory graph
   - Initialize at s0
   - Iteratively: reason → search → decide → act
   - Track action history

2. **Evaluation metrics**:
   - Success rate (% reaching goal states)
   - Path efficiency (optimal vs actual path length)
   - Memory utilization (how often search is used)
   - Dead-end avoidance (# of dead-ends hit)

### Phase 4: Fine-tuning (Day 3-4)

1. **Collect trajectories**:
   - Run agent multiple times
   - Record (state, action, outcome) tuples

2. **Train control policy** (optional):
   - Use DAPO or similar RL approach
   - Reward: +1 for success, -1 for dead-end, -0.1 per step

---

## Key Differences from Original M3-Agent

| Aspect | Original M3-Agent | Cube World Adaptation |
|--------|-------------------|----------------------|
| Video length | Hours of streaming | Short clips (~5-10 sec each) |
| Memory scale | Thousands of entries | ~15-20 memories |
| Entity tracking | Face recognition, speaker ID | Cube state recognition |
| Task type | Open QA, instruction following | Navigation to goal states |
| Real-time | Yes | No (offline evaluation) |
| Modalities | Video + Audio | Video only |

---

## API Configuration

```json
{
  "memorization": {
    "model": "Qwen2.5-Omni",
    "endpoint": "local or API",
    "temperature": 0.3
  },
  "control": {
    "model": "gpt-4o",
    "endpoint": "https://api.openai.com/v1",
    "temperature": 0.7,
    "max_tokens": 1024
  },
  "embedding": {
    "model": "text-embedding-3-small",
    "endpoint": "https://api.openai.com/v1"
  }
}
```

---

## Expected Results

Based on M3-Agent's performance on M3-Bench:

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| Success Rate | 70-90% | Higher with more memory search rounds |
| Path Efficiency | 60-80% | May not always find optimal path |
| Dead-End Rate | 10-30% | Should decrease with semantic memory |
| Avg Reasoning Rounds | 2-3 | Most decisions need 2+ memory queries |

---

## References

1. M3-Agent Paper: https://arxiv.org/abs/2508.09736
2. M3-Agent Code: https://github.com/bytedance-seed/m3-agent
3. Qwen2.5-Omni: https://huggingface.co/Qwen/Qwen2.5-Omni
4. Our Cube World: `worlds/video_worlds/cube_world_navigation_maze.json`
