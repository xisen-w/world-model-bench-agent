# Action-Conditioned World Model Benchmark (AC-World)

## Problem Formulation

**Title:** Action-Conditioned World Model Benchmark (AC-World): Testing Temporal Planning and Scene Consistency

**Goal:** To evaluate an agent's ability to understand, plan, and execute a sequence of actions that transition a system (or scene) from an initial observation to a desired final observation, while maintaining temporal and causal coherence.

## Core Problem Setup

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

## Benchmark Setup & API Prompting Format

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

## Optional "Video-Time Prompting" Schema

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

## Mini Experiment Designs

| Experiment ID | Type | Input | Output | Goal | Metric |
|---------------|------|-------|--------|------|--------|
| E1 | Forward Simulation | $O_t, A_t$ | $\hat{O}_{t+1}$ | Predict next scene | CLIP/SSIM |
| E2 | Action Inference | $O_t, O_{t+1}$ | $\hat{A}_t$ | Identify cause action | Action accuracy |
| E3 | Goal-Conditioned Planning | $O_{start}, O_{goal}$ | $\hat{A}_{1:T}$ | Generate causal chain | GAS (Goal Achievement Similarity) |
| E4 | Temporal Memory Test | $O_{1:T}$ | $\hat{A}_{1:T}$ | Recall actions from context | Temporal consistency |
| E5 | Action-to-Description | $A_t$ | Textual caption | Translate actions to scene dynamics | BLEU / Caption-Scene Sim. |

## Open Research Questions

1. **Action Abstraction Scope:** Should the action set be symbolic (e.g., "stand up", "move left") or continuous (vectorized joint motions)?

2. **Cross-Modal Representation:** How do we align action embeddings with visual transitions?
   - e.g., CLIP-like alignment between $(O_t, A_t, O_{t+1})$ triplets

3. **Temporal Credit Assignment:** How to backtrack errors when an action early in the sequence causes a distant visual mismatch?

4. **Compositionality Test:** Can the model generalize unseen $(O_{start}, O_{goal})$ pairs by recombining known action primitives?

## Suggested Testing Prompts (with Expected Results)

| Prompt | Expected Output | Evaluation Idea |
|--------|----------------|-----------------|
| "Initial: cup on table. Goal: cup on shelf." | "Pick up cup → Raise hand → Place on shelf." | Test high-level symbolic planning |
| "Initial: car stopped at light. Goal: car at intersection." | "Accelerate → Steer forward." | Checks temporal planning and motion reasoning |
| "Initial: empty plate. Goal: plate with food." | "Pick up food → Place on plate." | Tests object-interaction reasoning |
| "Observation1: ball on ground. Observation2: ball in air." | "Throw ball." | Simple action inference |
| "Observation1: dark room. Observation2: bright room." | "Turn on light." | Contextual causal inference |

## Next Step Suggestions

- Start with synthetic image pairs (CLEVR, Physion) for controllable action space
- Extend to video caption datasets (Something-Something-V2, Ego4D)
- Define a simple JSON interface for prompt-action evaluation (e.g., `{"obs_start": "...", "obs_goal": "...", "actions": ["..."]}`)

## Implementation

Would you like me to generate the prompt templates and evaluator functions (Python + OpenAI API) for this benchmark next — including the JSON evaluation schema and similarity scoring setup?

## Project Structure

```
world_model_bench_agent/
├── README.md                       # This file
├── QUICK_START_VISION.md          # Quick start for vision world pipeline
├── VISION_WORLD_DESIGN.md         # System design for image/video worlds
├── PROGRESS_SUMMARY.md            # Current implementation status
├── API_KEY_SETUP.md               # Guide to fix API key issues
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (API keys)
│
├── world_model_bench_agent/       # Core benchmark system
│   ├── benchmark_curation.py           # World model data structures
│   ├── llm_world_generator.py          # Text world generation with LLM
│   ├── image_world_generator.py        # Image generation for states (NEW)
│   ├── interactive_demo.py             # Interactive world exploration
│   ├── test_generator.py               # Test text world generation
│   └── test_image_generator.py         # Test image generation (NEW)
│
├── utils/                         # Video/image generation utilities
│   ├── veo.py                          # Google Veo 3.1 + Gemini integration
│   ├── unified_interface.py            # Unified API wrapper
│   └── tests/
│       └── test_veo.py                 # Comprehensive Veo test suite
│
├── generated_images/              # Output directory for images
│   └── [world_name]_images/
│       ├── s0_000.png
│       └── ...
│
└── examples/                      # Usage examples
    ├── example_usage.py
    └── example_veo_usage.py
```

## NEW: Vision World Pipeline

We've implemented a complete pipeline to convert text-based worlds into vision-based worlds:

### Text → Image → Video Pipeline

**Phase 1: Text World Generation** (IMPLEMENTED)
```bash
python world_model_bench_agent/test_generator.py --yes
```
- Generates branching worlds with LLM (20-30 states)
- Multiple success and failure endings
- Action-conditioned state transitions

**Phase 2: Image World Generation** (IMPLEMENTED)
```bash
python world_model_bench_agent/test_image_generator.py --yes
```
- Generates consistent images for each state
- Uses image variation for visual consistency
- Maintains camera perspective (ego-centric)

**Phase 3: Video Generation** (IMPLEMENTED)
```bash
python world_model_bench_agent/test_video_generator.py --yes
```
- Generates videos for state transitions
- Uses Veo's first-frame + last-frame interpolation
- Action descriptions as video prompts
- ~$0.05-$0.10 per video, 2-5 minutes generation time

### Key Features

1. **Visual Consistency**: Uses `generate_image_variation()` to maintain:
   - Same camera angle across states
   - Consistent scene style
   - Recognizable objects and environment

2. **Efficient Generation**:
   - Canonical path strategy (main success path only)
   - On-demand generation for branches
   - Lazy loading and caching

3. **Cost Effective**:
   - Text world: ~$0.001
   - Image world (20 states): ~$0.04
   - Video world (20 transitions): ~$1-2

### Quick Start

See `QUICK_START_VISION.md` for detailed instructions.

```python
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.benchmark_curation import World

# Load text world
text_world = World.load("coffee_branching_world.json")

# Generate images
image_gen = ImageWorldGenerator(veo_client)
image_world = image_gen.generate_image_world(
    text_world=text_world,
    strategy="canonical_path"
)
image_world.save("coffee_image_world.json")

# Generate videos
video_gen = VideoWorldGenerator(veo_client)
video_world = video_gen.generate_video_world(
    image_world=image_world,
    strategy="canonical_only"
)
video_world.save("coffee_video_world.json")
```

## Testing Veo Video Generation

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install google-genai python-dotenv pillow requests
   ```

2. **Set up API key:**
   Create a `.env` file in the project root:
   ```bash
   GEMINI_KEY=your_google_ai_api_key_here
   ```

3. **Activate virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### Running the Test Suite

The comprehensive test suite (`utils/tests/test_veo.py`) covers all Veo capabilities:

```bash
cd world_model_bench_agent
python utils/tests/test_veo.py
```

### Test Coverage

The test suite includes 10 tests organized in the following categories:

#### Non-API Tests (Always Run)
1. **Initialization Test** - Verifies client setup with google-genai SDK
2. **Supported Features** - Lists all available Veo capabilities
3. **Paid Feature Guard** - Ensures acknowledgement before API calls
4. **Helper Methods** - Tests config builders and utilities
5. **Routing Logic** - Validates smart method selection

#### API Tests (Requires User Confirmation)
6. **Image Generation** - Tests Gemini 2.5 Flash image generation
7. **Prompt-Only Video** - Generates video from text prompt only
8. **Image-to-Video** - Generates image, then creates video from it
9. **First-Last Frame Video** - Creates video bridging two keyframes
10. **Reference-Based Video** - Uses reference images to guide generation

### Test Workflow

When you run the test suite:

1. **Non-API tests run automatically** (no charges)
2. **API tests prompt for confirmation** before making paid API calls
3. **Each API test shows:**
   - What it will test
   - Estimated time (video generation takes several minutes)
   - Warning about potential charges

Example output:
```
======================================================================
  TEST 7: Image-to-Video Generation (API Call)
======================================================================

WARNING: This test will make actual API calls to Google Veo.
This will incur charges on your account and may take several minutes.
Do you want to proceed? (yes/no): yes

7a. Generating initial image with Gemini...
   Image generated and saved to test_start_image.png

7b. Generating video from the image...
   Result ID: operations/abc123...
   Status: completed
   Progress: 100.0%

7c. Downloading generated video...
   Downloaded to: test_image_to_video.mp4
   SUCCESS: Image-to-video generation works
```

### Generated Test Files

After running the full test suite, you'll find:

- `test_output_image.png` - Basic image generation
- `test_output_video.mp4` - Prompt-only video
- `test_start_image.png` - Start frame for image-to-video
- `test_image_to_video.mp4` - Image-to-video result
- `test_first_frame.png`, `test_last_frame.png` - Keyframes
- `test_first_last_video.mp4` - Keyframe interpolation video
- `test_ref_1.png`, `test_ref_2.png` - Reference images
- `test_reference_video.mp4` - Reference-guided video

### Running Individual Tests

You can modify `test_veo.py` to run only specific tests by commenting out unwanted test calls in the `main()` function.

### Test Configuration

Key configurations in the test suite:

```python
# Model IDs (in utils/veo.py)
DEFAULT_VEO_MODEL_ID = "veo-3.1-fast-generate-preview"
DEFAULT_IMAGE_MODEL_ID = "gemini-2.5-flash-image"

# Polling settings
poll_interval_seconds = 20        # Check status every 20 seconds
operation_timeout_seconds = 1200  # 20 minute timeout
```

### Important Notes

- Video generation is a **paid feature** and requires acknowledgement
- Each video generation can take **several minutes** to complete
- The test suite uses **polling** to wait for video completion
- All tests use **720p resolution** by default to reduce costs
- You can skip any API test by typing "no" when prompted


