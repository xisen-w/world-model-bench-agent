# Vision World Generator - System Design

## Problem Statement

**Goal**: Convert text-based worlds into vision worlds with consistent images across states.

**Key Challenges**:
1. **Visual Consistency**: Same camera angle, same ego-centric view, same scene style
2. **State Transitions**: How to generate images that reflect action-conditioned changes
3. **Scalability**: Generating images for branching worlds (20-30 states)
4. **Cost Management**: Each image generation costs money

## System Architecture

### Phase 1: Text World → Image World

```
Input:  World (JSON with text descriptions)
Process: Generate images for each state
Output: ImageWorld (JSON with image pointers)
```

### Phase 2: Image World → Video World

```
Input:  ImageWorld + Transitions
Process: Generate videos between state pairs
Output: VideoWorld (JSON with video pointers)
```

## Design Decisions

### Q1: One Image or Multiple Images per State?

**Decision**: **One image per state** (for now)

**Rationale**:
- Simpler to implement
- Easier to maintain consistency
- Lower cost
- Can extend to multi-view later

**Alternative Considered**: Multiple camera angles per state
- Would be better for 3D reconstruction
- But adds 3-5x cost and complexity

### Q2: How to Maintain Visual Consistency?

**Strategy A: Reference-Based Generation** (RECOMMENDED)

1. Generate initial state image from scratch
2. For subsequent states, use `generate_image_variation(prompt, base_image)`
   - Pass previous image as reference
   - Add delta prompt describing the change
   - Gemini maintains style/perspective consistency

**Example**:
```python
# Initial state
initial_img = veo.generate_image_from_prompt(
    "First-person view of a kitchen counter with coffee machine, beans, water, milk"
)

# Next state (after action: "grind coffee beans")
next_img = veo.generate_image_variation(
    prompt="Same view, but now coffee beans are being ground in the grinder",
    base_image=initial_img
)
```

**Strategy B: Style Reference + Prompt**

Use reference images to lock in style:
```python
veo.generate_video_with_references(
    prompt="Kitchen counter with ground coffee",
    reference_images=[initial_img],
    reference_type="style"
)
```

**Strategy C: Detailed Prompt Engineering**

Include camera/style instructions in every prompt:
```
"First-person ego-centric view from 1.6m height, 16:9 aspect ratio,
realistic style, kitchen counter visible, [STATE DESCRIPTION]"
```

**Recommendation**: **Use Strategy A (image variation)** as primary method, with Strategy C (consistent prompts) as fallback.

### Q3: Linear Path vs Full Graph?

**Decision**: **Generate images only for reachable states**

For branching worlds with 25 states:
- Don't generate all 25 images upfront
- Generate images on-demand during exploration
- Cache generated images for reuse

**Optimization**: Pre-generate images for the "canonical path" (main success path)

## Data Schema

### ImageWorld JSON Structure

```json
{
  "name": "coffee_making_image_world",
  "text_world_source": "coffee_branching_world.json",
  "generation_metadata": {
    "model": "gemini-2.5-flash-image",
    "timestamp": "2025-10-27T10:30:00Z",
    "generation_strategy": "image_variation",
    "aspect_ratio": "16:9",
    "camera_perspective": "first_person_ego"
  },
  "states": [
    {
      "state_id": "s0",
      "text_description": "Kitchen with coffee machine...",
      "image_path": "images/coffee_world/s0_initial.png",
      "generation_prompt": "First-person view of kitchen counter...",
      "parent_state_id": null,
      "parent_action_id": null
    },
    {
      "state_id": "s1",
      "text_description": "Coffee beans being ground...",
      "image_path": "images/coffee_world/s1_grinding.png",
      "generation_prompt": "Same view, coffee beans ground in grinder",
      "parent_state_id": "s0",
      "parent_action_id": "a0",
      "reference_image": "images/coffee_world/s0_initial.png"
    }
  ],
  "transitions": [
    {
      "start_state_id": "s0",
      "action_id": "a0",
      "end_state_id": "s1",
      "action_description": "Grind coffee beans",
      "video_path": null  // Populated in Phase 2
    }
  ]
}
```

## Implementation Plan

### Class: ImageWorldGenerator

```python
class ImageWorldGenerator:
    def __init__(self, veo_client, api_key):
        self.veo = veo_client

    def generate_image_world(
        self,
        text_world: World,
        output_dir: str,
        strategy: str = "image_variation",
        camera_perspective: str = "first_person_ego",
        aspect_ratio: str = "16:9"
    ) -> ImageWorld:
        """
        Convert text world to image world.

        Process:
        1. Load text world
        2. Extract canonical path (start -> goal)
        3. Generate initial image
        4. For each transition:
           - Generate variation based on action
           - Save image
           - Record metadata
        5. Return ImageWorld object
        """

    def _generate_initial_image(self, state: State) -> PIL.Image:
        """Generate first image with full prompt."""

    def _generate_next_image(
        self,
        state: State,
        action: Action,
        previous_image: PIL.Image
    ) -> PIL.Image:
        """Generate next image using variation."""

    def _build_state_prompt(self, state: State, action: Optional[Action] = None) -> str:
        """Build prompt for image generation."""
```

### Key Methods

1. **generate_canonical_path_images()**
   - Generate images for main success path only
   - Most important for testing AI

2. **generate_full_world_images()**
   - Generate all reachable states
   - Expensive, for complete benchmarks

3. **generate_on_demand(state_id)**
   - Generate image for specific state
   - Used during interactive exploration

## Testing Protocol

### How to Test AI with Image Worlds?

**Test 1: Action Prediction from Image Pairs**
```
Input:  [Image_t, Image_t+1]
Task:   Predict action that caused transition
Eval:   Compare predicted action to ground truth
```

**Test 2: Goal-Conditioned Planning**
```
Input:  [Image_start, Image_goal]
Task:   Generate action sequence
Eval:   Simulate actions, compare final image to goal
```

**Test 3: Next-Frame Prediction**
```
Input:  [Image_t, Action_t]
Task:   Predict Image_t+1
Eval:   CLIP/SSIM similarity to ground truth
```

## Cost Estimation

**Gemini 2.5 Flash Image Pricing** (approximate):
- ~$0.003 per image generation
- ~$0.002 per image variation

**For a typical world** (20 states):
- Initial image: $0.003
- 19 variations: 19 × $0.002 = $0.038
- **Total: ~$0.04 per world**

**For 10 test worlds**: ~$0.40

## Phase 2: Video Generation

Once image world is ready:

```python
class VideoWorldGenerator:
    def generate_transition_videos(
        self,
        image_world: ImageWorld,
        transitions: List[str]  # Which transitions to generate
    ) -> VideoWorld:
        """
        Generate videos for state transitions.

        Uses Veo's first-frame + last-frame generation:
        video = veo.generate_video_with_initial_and_end_image(
            start_image=state_t_image,
            end_image=state_t+1_image,
            prompt=action_description
        )
        """
```

**Video Generation is MUCH more expensive**:
- ~$0.05 - $0.10 per 5-second video
- 20 transitions = $1-2 per world

## Interactive Demo Extension

Update `interactive_demo.py`:

```python
class ImageWorldExplorer(InteractiveWorldExplorer):
    def display_state(self):
        # Show image instead of just text
        if self.current_state.image_path:
            img = Image.open(self.current_state.image_path)
            img.show()  # Or display in terminal with rich
        print(f"Description: {self.current_state.description}")
```

## Next Steps

1. **Implement ImageWorldGenerator** class
2. **Test with simple world** (5 states, linear path)
3. **Validate visual consistency** manually
4. **Extend to branching worlds**
5. **Add video generation** (Phase 2)

## Open Questions

1. Should we generate images for ALL states or just canonical path?
   - **Recommendation**: Start with canonical path only

2. How to handle branching? Generate images for alternate paths on-demand?
   - **Recommendation**: Yes, lazy generation with caching

3. Should we use 720p or 1080p for images?
   - **Recommendation**: 720p (16:9) to save costs during testing

4. How to prompt for ego-centric view consistency?
   - **Recommendation**: Add "first-person view, camera at eye level (1.6m)" to every prompt
