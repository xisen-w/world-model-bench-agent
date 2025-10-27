# Progress Summary - AC-World Benchmark Project

## What We've Built

### 1. LLM World Generator (IMPLEMENTED)
Location: `world_model_bench_agent/llm_world_generator.py`

**Two-step automated world generation**:
- Step 1: Generate linear world from high-level description
- Step 2: Expand to branching world with multiple endings (success + failure)

**Features**:
- JSON-structured prompts for reliable LLM output
- Quality scoring for each ending state
- Branching point selection and deviation path generation
- Support for 20-30 state worlds with 5-7 different endings

**Status**: Implementation complete, but **BLOCKED by invalid API key**

### 2. Image World Generator (IMPLEMENTED)
Location: `world_model_bench_agent/image_world_generator.py`

**Converts text worlds to vision worlds**:
- Generates consistent images for each state
- Uses Gemini's image variation for visual consistency
- Maintains ego-centric camera perspective
- Supports canonical path (efficient) or full world generation

**Key Classes**:
- `ImageWorldGenerator`: Main generator class
- `ImageWorld`: Data structure with image pointers
- `ImageState`: State with associated image path
- `ImageTransition`: Transition with optional video

**Image Consistency Strategy**:
1. Generate initial state image from full prompt
2. Use `generate_image_variation()` for subsequent states
3. Pass previous image as reference to maintain style/perspective
4. Include camera perspective in prompts

**Status**: Fully implemented, ready to test with valid API key

### 3. Video World Generator (IMPLEMENTED)
Location: `world_model_bench_agent/video_world_generator.py`

**Converts image worlds to video worlds**:
- Generates transition videos between states
- Uses Veo's first-frame + last-frame video generation
- Action descriptions as video prompts
- Supports all/canonical/selective transition generation

**Key Classes**:
- `VideoWorldGenerator`: Main generator class
- `VideoWorld`: Data structure with video pointers
- `VideoTransition`: Transition with video path and metadata

**Video Generation Strategy**:
1. Load start and end state images
2. Build prompt from action description
3. Use `generate_video_with_initial_and_end_image()`
4. Save video and metadata

**Generation Modes**:
- `all_transitions`: Generate videos for all transitions
- `canonical_only`: Only main success path transitions
- `generate_transition_on_demand()`: Single transition
- `generate_batch_transitions()`: Selected transitions

**Status**: Fully implemented, ready to test with valid API key

### 4. Core World Model System (COMPLETE)
Location: `world_model_bench_agent/benchmark_curation.py`

**Data Structures**:
- `State`: World states with descriptions and metadata
- `Action`: Actions that cause transitions
- `Transition`: State-action-state triplets
- `World`: Complete world with branching graph structure

**Key Features**:
- Multiple endpoint support (goal_states vs final_states)
- Graph algorithms (path finding, decision points)
- Success/failure path extraction
- JSON serialization

### 5. Interactive Demo (COMPLETE)
Location: `world_model_bench_agent/interactive_demo.py`

**Features**:
- Interactive CLI exploration of worlds
- State display, action selection, outcome tracking
- Shows successful/failed paths

**Status**: Works for text worlds, can be extended for image worlds

### 6. Veo Video Generation (COMPLETE)
Location: `utils/veo.py`

**Capabilities**:
- Image generation from prompts
- Image variation (image-to-image editing)
- Video from prompt only
- Video from image (image-to-video)
- Video from first+last frame (keyframe interpolation)
- Reference-based video generation

**Status**: Fully tested and working

## File Structure

```
world_model_bench_agent/
├── PROGRESS_SUMMARY.md           # This file
├── VISION_WORLD_DESIGN.md        # Design doc for vision world system
├── API_KEY_SETUP.md              # Guide to fix API key issues
├── README.md                     # Project overview
│
├── world_model_bench_agent/
│   ├── benchmark_curation.py           # Core world model (COMPLETE)
│   ├── llm_world_generator.py          # Text world generation (BLOCKED)
│   ├── image_world_generator.py        # Vision world generation (NEW)
│   ├── interactive_demo.py             # Interactive exploration (COMPLETE)
│   ├── test_generator.py               # Test LLM generation (BLOCKED)
│   └── test_image_generator.py         # Test image generation (NEW)
│
├── utils/
│   ├── veo.py                    # Veo video generation (COMPLETE)
│   └── tests/test_veo.py         # Comprehensive tests (COMPLETE)
│
└── generated_images/             # Output directory for images
    └── [world_name]_images/
        ├── s0_000.png
        ├── s1_001.png
        └── ...
```

## Current Status

### What's Working

1. Core world model system with branching graphs
2. Interactive text-based exploration
3. Veo video generation (all modes tested)
4. Image world generator implementation

### What's Blocked

**Primary Blocker**: Invalid Gemini API Key

The API key in `.env` is returning:
```
400 INVALID_ARGUMENT. API Key not found. Please pass a valid API key.
```

**What needs fixing**:
1. Get a new valid API key from [Google AI Studio](https://aistudio.google.com/)
2. Update `.env` file with new key
3. Test with `python test_api_key.py`

See `API_KEY_SETUP.md` for detailed instructions.

### What Can't Be Tested Until API Key Fixed

1. LLM world generation (text worlds from descriptions)
2. Image world generation (images for states)
3. Full end-to-end pipeline

## System Design - Vision to Video Pipeline

### Current Architecture

```
Phase 1: Text Generation (LLM)
  Input:  High-level scenario description
  Output: Branching text world with 20-30 states

Phase 2: Image Generation (NEW)
  Input:  Text world JSON
  Output: Image world JSON with consistent images

Phase 3: Video Generation (FUTURE)
  Input:  Image world JSON
  Output: Video world with transition videos
```

### Image Consistency Approach

**Strategy**: Use `generate_image_variation()` for sequential consistency

```python
# Initial state - generate from scratch
initial_img = veo.generate_image_from_prompt(
    "First-person view: Kitchen counter with coffee machine, beans, water"
)

# Next state - variation maintains style
next_img = veo.generate_image_variation(
    prompt="Same view, coffee beans now ground in grinder",
    base_image=initial_img
)
```

**Why this works**:
- Gemini maintains visual style when given reference image
- Camera angle stays consistent
- Scene elements remain recognizable
- Only state-specific changes are applied

### Testing Protocol for AI

Once images are generated, we can test AI systems:

**Test 1: Action Inference**
```
Input:  [Image_t, Image_t+1]
Task:   What action caused this transition?
Metric: Action accuracy
```

**Test 2: Goal-Conditioned Planning**
```
Input:  [Image_start, Image_goal]
Task:   Generate action sequence to reach goal
Metric: Path correctness, goal achievement similarity
```

**Test 3: Next-Frame Prediction**
```
Input:  [Image_t, Action_t]
Task:   Predict Image_t+1
Metric: CLIP similarity, SSIM
```

## Cost Estimates

### Per World Costs

**Text World Generation** (LLM):
- Linear generation: 1 API call (~$0.0001)
- Branching expansion: 5-10 API calls (~$0.001)
- **Total: < $0.001 per world**

**Image World Generation** (Image):
- Initial image: $0.003
- Variations (19 images): $0.038
- **Total: ~$0.04 per world**

**Video World Generation** (Video):
- 20 transition videos: $1-2 per world
- **Total: $1-2 per world**

### Batch Costs

**10 test worlds**:
- Text: $0.01
- Images: $0.40
- Videos: $10-20
- **Total: $10-20 for complete benchmark**

## Next Steps

### Immediate (Once API Key Fixed)

1. Test LLM world generator
   ```bash
   source venv/bin/activate
   python world_model_bench_agent/test_generator.py --yes
   ```

2. Test image world generator
   ```bash
   python world_model_bench_agent/test_image_generator.py --yes
   ```

3. Validate visual consistency of generated images

### Phase 2 (After Images Work)

1. Implement `VideoWorldGenerator` class
   - Generate transition videos using first-frame + last-frame
   - Save video paths to VideoWorld JSON

2. Update interactive demo for image/video worlds
   - Display images during exploration
   - Play videos for transitions

3. Create benchmark evaluation scripts
   - Test AI systems with generated worlds
   - Compute metrics (action accuracy, goal achievement)

### Phase 3 (Full Pipeline)

1. Generate 10-20 diverse scenarios
   - Coffee making, IKEA assembly, cooking, etc.
   - Various difficulty levels

2. Create evaluation suite
   - Action inference tests
   - Planning tests
   - Prediction tests

3. Document and release benchmark

## Key Insights from Design

### Q: One image or multiple per state?
**A**: One image per state (for now)
- Simpler, cheaper
- Sufficient for 2D visual consistency
- Can extend to multi-view later

### Q: How to handle branching?
**A**: Generate images for canonical path first
- Lazy generation for alternate paths
- Cache generated images
- On-demand generation during exploration

### Q: How to maintain consistency?
**A**: Image variation + camera prompts
- Use previous image as reference
- Include camera perspective in every prompt
- Gemini maintains style automatically

## What Makes This Novel

1. **Action-Conditioned Visual Consistency**: Most benchmarks have either:
   - Static images (no transitions)
   - Videos (but no structured state space)
   - We have both: structured states + visual continuity

2. **Branching Visual Worlds**: Most vision benchmarks are linear
   - We support multiple paths and endings
   - Tests planning and decision-making

3. **Ego-Centric Perspective**: Maintains first-person view
   - More suitable for embodied AI testing
   - Matches human experience

4. **Automated Generation**: LLM + Vision model pipeline
   - Can generate unlimited scenarios
   - Scalable and customizable

## Contact

Current blocker: API key issue
See `API_KEY_SETUP.md` for resolution steps.

Once resolved, all systems are ready to test!
