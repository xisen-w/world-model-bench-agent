# Quick Start - Vision World Pipeline

## Prerequisites

1. **Valid API Key** (REQUIRED)
   - Get from: https://aistudio.google.com/
   - Update `.env`: `GEMINI_KEY=your_key_here`
   - Test with: `python test_api_key.py`

2. **Dependencies**
   ```bash
   source venv/bin/activate
   pip install google-genai python-dotenv pillow numpy
   ```

## Complete Pipeline (3 Phases)

### Phase 1: Generate Text World

```bash
# Generate text world with LLM
python world_model_bench_agent/test_generator.py --yes
```

**Output**:
- `coffee_branching_world.json` (text world with 25 states, 6 endings)
- `bookshelf_branching_world.json`
- `pasta_world.json`

**What it does**:
1. Generates linear path (6 steps)
2. Expands to branching world (multiple paths and endings)
3. Creates success states (high quality outcomes)
4. Creates failure states (low quality outcomes)

### Phase 2: Generate Images for States

```bash
# Convert text world to image world
python world_model_bench_agent/test_image_generator.py --yes
```

**Output**:
- `coffee_image_world.json` (JSON with image pointers)
- `generated_images/coffee_images/s0_000.png` (actual images)
- `generated_images/coffee_images/s1_001.png`
- ... one image per state in canonical path

**What it does**:
1. Loads text world JSON
2. Generates initial state image from scratch
3. For each transition, generates next state using image variation
4. Maintains visual consistency (same camera, style, perspective)

### Phase 3: Generate Videos for Transitions

```bash
# Convert image world to video world
python world_model_bench_agent/test_video_generator.py --yes
```

**Output**:
- `coffee_video_world.json` (JSON with video pointers)
- `generated_videos/coffee_videos/s0_to_s1_000.mp4` (actual videos)
- `generated_videos/coffee_videos/s1_to_s2_001.mp4`
- ... one video per transition

**What it does**:
1. Loads image world JSON
2. For each transition, loads start and end images
3. Uses action description as video prompt
4. Generates video with Veo's first-frame + last-frame interpolation
5. Saves videos and creates VideoWorld JSON

**Cost & Time**:
- ~$0.05-$0.10 per video
- ~2-5 minutes per video
- For 5 transitions: $0.25-$0.50, 10-25 minutes

## Usage Examples

### Example 1: Complete Pipeline (Text → Image → Video)

```python
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.benchmark_curation import World, State, Action, Transition
from utils.veo import VeoVideoGenerator
from google import genai

# 1. Create simple text world
s0 = State(description="Empty cup on table", state_id="s0")
s1 = State(description="Cup filled with hot water", state_id="s1")
s2 = State(description="Tea bag steeping in cup", state_id="s2")

a0 = Action(description="Pour hot water into cup", action_id="a0")
a1 = Action(description="Place tea bag in cup", action_id="a1")

world = World(
    name="tea_making",
    states=[s0, s1, s2],
    actions=[a0, a1],
    transitions=[
        Transition(s0, a0, s1),
        Transition(s1, a1, s2)
    ],
    initial_state=s0,
    goal_states=[s2]
)

# 2. Initialize Veo
client = genai.Client(api_key="your_key")
veo = VeoVideoGenerator(api_key="your_key", client=client, acknowledged_paid_feature=True)

# 3. Generate images
image_gen = ImageWorldGenerator(veo)
image_world = image_gen.generate_image_world(world, strategy="canonical_path")
image_world.save("tea_image_world.json")

# 4. Generate videos
video_gen = VideoWorldGenerator(veo)
video_world = video_gen.generate_video_world(image_world, strategy="canonical_only")
video_world.save("tea_video_world.json")
```

### Example 2: Load and Generate Videos

```python
from world_model_bench_agent.video_world_generator import load_image_world_and_generate_videos

# Load existing image world and generate videos
video_world = load_image_world_and_generate_videos(
    image_world_path="coffee_image_world.json",
    veo_client=veo,
    strategy="canonical_only"
)

video_world.save("coffee_video_world.json")
```

### Example 3: Selective Video Generation

```python
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

# Load image world
image_world = ImageWorld.load("coffee_image_world.json")

# Generate video for specific transition
video_gen = VideoWorldGenerator(veo)

# Option A: Single transition
video_transition = video_gen.generate_transition_on_demand(
    image_world=image_world,
    transition_index=0  # First transition
)

# Option B: Batch of transitions
video_transitions = video_gen.generate_batch_transitions(
    image_world=image_world,
    transition_indices=[0, 2, 4]  # Selected transitions
)
```

## Data Structures

### Text World JSON
```json
{
  "name": "coffee_making",
  "states": [
    {"state_id": "s0", "description": "Kitchen counter..."}
  ],
  "actions": [
    {"action_id": "a0", "description": "Grind beans"}
  ],
  "transitions": [
    {"start_state": "s0", "action": "a0", "end_state": "s1"}
  ]
}
```

### Image World JSON
```json
{
  "name": "coffee_making_images",
  "text_world_source": "coffee_making",
  "states": [
    {
      "state_id": "s0",
      "text_description": "Kitchen counter...",
      "image_path": "generated_images/coffee_images/s0_000.png",
      "generation_prompt": "First-person view: Kitchen counter...",
      "reference_image": null
    },
    {
      "state_id": "s1",
      "text_description": "Coffee beans ground...",
      "image_path": "generated_images/coffee_images/s1_001.png",
      "generation_prompt": "Same view, beans now ground...",
      "reference_image": "generated_images/coffee_images/s0_000.png"
    }
  ]
}
```

### Video World JSON
```json
{
  "name": "coffee_making_videos",
  "image_world_source": "coffee_making_images",
  "states": [...],  // Same as image world
  "transitions": [
    {
      "start_state_id": "s0",
      "action_id": "a0",
      "end_state_id": "s1",
      "action_description": "Grind coffee beans",
      "start_image_path": "generated_images/coffee_images/s0_000.png",
      "end_image_path": "generated_images/coffee_images/s1_001.png",
      "video_path": "generated_videos/coffee_videos/s0_to_s1_000.mp4",
      "generation_prompt": "Grind coffee beans. Smooth transition...",
      "metadata": {
        "result_id": "operations/xyz...",
        "status": "completed"
      }
    }
  ]
}
```

## Key Parameters

### Image Generation

```python
ImageWorldGenerator(
    veo_client,
    camera_perspective="first_person_ego",  # or "third_person", "overhead"
    aspect_ratio="16:9",
    output_dir="generated_images"
)
```

### Generation Strategies

- `"canonical_path"`: Only main success path (cheap, fast)
- `"full_world"`: All reachable states (expensive, not yet implemented)
- On-demand: Generate as needed during exploration

## Cost Management

### Estimated Costs

| Task | API Calls | Cost |
|------|-----------|------|
| Text world (LLM) | 10-15 | $0.001 |
| Image world (5 states) | 5 | $0.01 |
| Image world (20 states) | 20 | $0.04 |
| Video (per transition) | 1 | $0.05-0.10 |

### Tips to Save Money

1. **Start with canonical path only** (not full world)
2. **Test with small worlds first** (3-5 states)
3. **Use 720p instead of 1080p** for images
4. **Generate videos only for key transitions**
5. **Cache and reuse generated assets**

## Troubleshooting

### API Key Invalid
```bash
# Test your key
python test_api_key.py

# If invalid, get new key from:
# https://aistudio.google.com/
```

### Import Errors
```bash
# Make sure venv is activated
source venv/bin/activate

# Install missing dependencies
pip install google-genai python-dotenv pillow numpy
```

### Image Consistency Issues

If images don't look consistent:
1. Check that `strategy="canonical_path"` is used
2. Verify `camera_perspective` is consistent
3. Try adding more detailed prompts
4. Use lower temperature in generation config

### Out of Memory

If generating many images:
1. Generate in batches
2. Use canonical path instead of full world
3. Clear image cache periodically

## Next Steps

After generating image worlds:

1. **Validate visual consistency**
   - Open images in sequence
   - Check if transitions make sense
   - Verify camera angle is consistent

2. **Extend interactive demo**
   - Display images during exploration
   - Show before/after for each action

3. **Generate videos**
   - Use image pairs to create transition videos
   - Test video quality

4. **Test AI systems**
   - Action inference from image pairs
   - Goal-conditioned planning
   - Next-frame prediction

## Examples Directory

Check `examples/` for more usage patterns:
- `example_usage.py`: General usage
- `example_veo_usage.py`: Veo-specific examples

## Documentation

- `VISION_WORLD_DESIGN.md`: System architecture
- `PROGRESS_SUMMARY.md`: What's implemented
- `API_KEY_SETUP.md`: Fix API key issues
- `README.md`: Project overview
