# Action-Conditioned World Model Benchmark (AC-World)

## 🎯 Problem Formulation

**Title:** Action-Conditioned World Model Benchmark (AC-World): Testing Temporal Planning and Scene Consistency

**Goal:** To evaluate an agent's ability to understand, plan, and execute a sequence of actions that transition a system (or scene) from an initial observation to a desired final observation, while maintaining temporal and causal coherence.

## 🧩 Core Problem Setup

We define a world model $W$ that maps observations and actions to next observations:

$$
O_{t+1} = W(O_t, A_t)
$$

and an agent policy $\pi$ that maps observations to actions:

$$
A_t = \pi(O_t)
$$

The Action-Conditioned Stream Agent is tested under two regimes:

### Option 1: Planning from Sequential Observations

**Input:** $O_t, O_{t+1}$  
**Output:** Predicted action $A_t$  
**Objective:** Can the agent infer the most probable action(s) that transform Observation$_t$ into Observation$_{t+1}$?

**Benchmark Tasks:**
- Given two consecutive frames from a procedural environment (e.g., moving a block), generate plausible action(s)
- Measure semantic plausibility or reconstruction error after replaying predicted actions

**Evaluation Metrics:**
- Action Accuracy (vs ground truth)
- Temporal Coherence (whether the generated next frame fits causally)
- Semantic Alignment (CLIP similarity or latent similarity)

### Option 2: Inverse Planning (Goal-Conditioned)

**Input:** $O_{start}, O_{goal}$  
**Output:** Sequence of actions $A_1, A_2, …, A_T$  
**Objective:** Can the agent plan a sequence of actions that transition from start to goal state?

**Benchmark Tasks:**
- Predict intermediate frames or descriptions
- Compare generated "final state" against the target final observation

**Evaluation Metrics:**
- Goal Achievement Similarity (GAS): CLIP/SSIM between generated final and target
- Action Sequence Coherence: smoothness + logical feasibility of the action chain
- Trajectory Length Optimality

## 🧪 Benchmark Setup & API Prompting Format

We design the following API-style interface for both training and evaluation:

### Prompt Template

**System Instruction:**
```
You are an action-conditioned world model. You observe a sequence of frames from a continuous environment and must output the most plausible sequence of actions that could have produced the observed transition.
```

### Example (Option 1 — Sequential Prediction)

**Input:**
```
Observation_t: A man sitting on a chair.
Observation_t+1: The man is standing next to the chair.

Task: Infer the minimal action(s) taken.
```

**Expected Output:**
```json
["stand up"]
```

**Expected Result:**
- Action: "stand up"
- Transition Validity: ✓ (Observation$_{t+1}$ is plausible after performing 'stand up')

### Example (Option 2 — Goal-Conditioned Planning)

**Input:**
```
Initial Observation: A closed door.
Goal Observation: The door is open.

Task: Generate a minimal sequence of actions to achieve the goal.
```

**Expected Output:**
```json
[
  "Walk to the door",
  "Turn the handle",
  "Pull the door open"
]
```

**Evaluation:**
- Generated Final Scene (by simulating actions) ≈ Target Final Scene
  - CLIP similarity = 0.91
  - Trajectory length = 3 (optimal)

## 📹 Optional "Video-Time Prompting" Schema

You can encode temporal structure explicitly, to simulate stream reasoning:

```
[Time 0s] Observation: A person is sitting at a desk.
[Action]: Stand up.
[Time 1s] Observation: The person is now standing.
[Action]: Walk forward.
[Time 2s] Observation: The person reaches the door.
```

This allows you to test autoregressive temporal reasoning:
$$
O_{t+1} = f(O_t, A_t)
$$

## 🧩 Mini Experiment Designs

| Experiment ID | Type | Input | Output | Goal | Metric |
|---------------|------|-------|--------|------|--------|
| E1 | Forward Simulation | $O_t, A_t$ | $\hat{O}_{t+1}$ | Predict next scene | CLIP/SSIM |
| E2 | Action Inference | $O_t, O_{t+1}$ | $\hat{A}_t$ | Identify cause action | Action accuracy |
| E3 | Goal-Conditioned Planning | $O_{start}, O_{goal}$ | $\hat{A}_{1:T}$ | Generate causal chain | GAS (Goal Achievement Similarity) |
| E4 | Temporal Memory Test | $O_{1:T}$ | $\hat{A}_{1:T}$ | Recall actions from context | Temporal consistency |
| E5 | Action-to-Description | $A_t$ | Textual caption | Translate actions to scene dynamics | BLEU / Caption-Scene Sim. |

## 💡 Open Research Questions

1. **Action Abstraction Scope:** Should the action set be symbolic (e.g., "stand up", "move left") or continuous (vectorized joint motions)?

2. **Cross-Modal Representation:** How do we align action embeddings with visual transitions?
   - e.g., CLIP-like alignment between $(O_t, A_t, O_{t+1})$ triplets

3. **Temporal Credit Assignment:** How to backtrack errors when an action early in the sequence causes a distant visual mismatch?

4. **Compositionality Test:** Can the model generalize unseen $(O_{start}, O_{goal})$ pairs by recombining known action primitives?

## 🧠 Suggested Testing Prompts (with Expected Results)

| Prompt | Expected Output | Evaluation Idea |
|--------|----------------|-----------------|
| "Initial: cup on table. Goal: cup on shelf." | "Pick up cup → Raise hand → Place on shelf." | Test high-level symbolic planning |
| "Initial: car stopped at light. Goal: car at intersection." | "Accelerate → Steer forward." | Checks temporal planning and motion reasoning |
| "Initial: empty plate. Goal: plate with food." | "Pick up food → Place on plate." | Tests object-interaction reasoning |
| "Observation1: ball on ground. Observation2: ball in air." | "Throw ball." | Simple action inference |
| "Observation1: dark room. Observation2: bright room." | "Turn on light." | Contextual causal inference |

## 🧭 Next Step Suggestions

- Start with synthetic image pairs (CLEVR, Physion) for controllable action space
- Extend to video caption datasets (Something-Something-V2, Ego4D)
- Define a simple JSON interface for prompt-action evaluation (e.g., `{"obs_start": "...", "obs_goal": "...", "actions": ["..."]}`)

## 🔧 Implementation

Would you like me to generate the prompt templates and evaluator functions (Python + OpenAI API) for this benchmark next — including the JSON evaluation schema and similarity scoring setup?

## 📁 Project Structure

```
video_gen/
├── README.md (this file)
├── utils/           # Video generation utilities
│   ├── __init__.py
│   ├── sora.py      # OpenAI Sora integration
│   ├── runway.py    # Runway ML integration
│   ├── stable_diffusion.py  # Stability AI integration
│   └── unified_interface.py # Unified API wrapper
└── experiments/     # Benchmark experiments
    ├── __init__.py
    └── ac_world_benchmark.py
```


