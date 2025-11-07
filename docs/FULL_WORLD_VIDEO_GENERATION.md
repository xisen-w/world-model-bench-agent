# Full World Video Generation - Complete Guide

## Overview
The video world generator already supports generating videos for ALL transitions in branching worlds through the `all_transitions` strategy. This document explains how to use it with branching worlds.

## Video Generation Strategies

### 1. `all_transitions` (Full World)
- **What it does**: Generates videos for ALL transitions in the world graph
- **Use case**: Complete branching worlds with multiple paths
- **Cost**: Highest (one video per transition)
- **Time**: Longest (~8 min per transition)

### 2. `canonical_only`
- **What it does**: Generates videos only for the main success path
- **Use case**: Quick testing, single path scenarios
- **Cost**: Lower (only canonical path transitions)
- **Time**: Faster (fewer transitions)

### 3. `selective` (On-demand)
- **What it does**: Generate specific transitions manually
- **Use case**: Interactive exploration, debugging
- **Methods**: `generate_transition_on_demand()`, `generate_batch_transitions()`

## Usage with Branching Apple World

### Prerequisites
1. Generated image world with branching paths
   ```bash
   python test_full_apple_world.py
   ```
   This creates `apple_eating_branching_image_world.json` with 8 states and 7 transitions.

### Generate All Videos (Full World)

**Interactive version** (with confirmation):
```bash
source venv/bin/activate
python test_full_video_world.py
```

**Automated version** (no prompts):
```bash
source venv/bin/activate
python test_full_video_world_auto.py
```

**Programmatic usage**:
```python
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

# Load image world
image_world = ImageWorld.load("apple_eating_branching_image_world.json")

# Generate videos for ALL transitions
generator = VideoWorldGenerator(veo_client=veo)
video_world = generator.generate_video_world(
    image_world=image_world,
    strategy="all_transitions",  # Use all_transitions for full world
    number_of_videos=1
)

# Save result
video_world.save("apple_eating_branching_video_world.json")
```

## Branching World Structure

The apple eating branching world has the following structure:

```
                    s0 (whole apple)
                    /                \
            [a0a: cut]            [a0b: bite]
                /                          \
        s1a (cut apple)              s1b (bitten apple)
        /              \             /              \
  [a1a: eat]      [a1b: save]  [a1c: bite]    [a1d: slice]
      |                |             |              |
    s2a             s2b            s2c            s2d
   (eaten)      (saved half)    (eaten)       (sliced)
   [GOAL]            |          [GOAL]
                [a2a: eat]
                     |
                   s3a
              (saved & eaten)
                  [GOAL]
```

### All 7 Transitions Generated:
1. **s0 → s1a**: Cut the apple in half
2. **s0 → s1b**: Take a bite from apple
3. **s1a → s2a**: Eat the cut apple slices (GOAL)
4. **s1a → s2b**: Save one half in container
5. **s1b → s2c**: Continue biting until core remains (GOAL)
6. **s1b → s2d**: Slice the bitten apple
7. **s2b → s3a**: Eat the remaining half (GOAL)

## Strategy Comparison

### Example: Canonical vs All Transitions

**Canonical Only** (canonical_only):
- Generates: 2-3 videos (main path only)
- Example: s0 → s1a → s2a
- Cost: ~$0.20-0.30
- Time: ~16-24 minutes

**All Transitions** (all_transitions):
- Generates: 7 videos (all paths)
- Includes all branching possibilities
- Cost: ~$0.70
- Time: ~56 minutes

## Implementation Details

### How `all_transitions` Works

The `_generate_all_transitions()` method:

1. Iterates through ALL transitions in `image_world.transitions`
2. For each transition:
   - Finds start and end state images
   - Builds video generation prompt
   - Generates video using Veo's first-frame + last-frame method
   - Downloads and saves the video
3. Records all VideoTransition objects with paths

**Key code** (video_world_generator.py:164-203):
```python
def _generate_all_transitions(self, image_world, video_world, world_dir, number_of_videos):
    """Generate videos for all transitions in the image world."""
    for i, transition in enumerate(image_world.transitions):
        # Find states
        start_state = self._find_state(image_world.states, transition.start_state_id)
        end_state = self._find_state(image_world.states, transition.end_state_id)

        # Generate video
        video_transition = self._generate_transition_video(
            start_state=start_state,
            end_state=end_state,
            action_description=transition.action_description,
            action_id=transition.action_id,
            world_dir=world_dir,
            index=i,
            number_of_videos=number_of_videos
        )

        video_world.transitions.append(video_transition)
```

### Enhanced Prompts

The video generator supports enhanced cinematic prompts:

```python
generator = VideoWorldGenerator(
    veo_client=veo,
    use_enhanced_prompts=True,  # Enable enhanced prompts
    cinematic_style=CinematicStyle(...)  # Optional custom style
)
```

Enhanced prompts include:
- Detailed camera instructions
- Lighting and composition guidance
- Smooth motion descriptions
- Object tracking and continuity

## Files Generated

### Output Structure
```
apple_eating_branching_video_world.json         # Video world metadata
generated_videos/
  apple_eating_branching_images_videos/
    s0_to_s1a_000.mp4     # Cut the apple
    s0_to_s1b_001.mp4     # Bite the apple
    s1a_to_s2a_002.mp4    # Eat cut slices
    s1a_to_s2b_003.mp4    # Save one half
    s1b_to_s2c_004.mp4    # Continue biting
    s1b_to_s2d_005.mp4    # Slice bitten apple
    s2b_to_s3a_006.mp4    # Eat remaining half
```

### JSON Structure
```json
{
  "name": "apple_eating_branching_images_videos",
  "image_world_source": "apple_eating_branching_images",
  "generation_metadata": {
    "model": "veo-2.0",
    "generation_strategy": "all_transitions",
    "timestamp": "...",
    "number_of_videos_per_transition": 1
  },
  "states": [...],  // All 8 states from image world
  "transitions": [  // All 7 video transitions
    {
      "start_state_id": "s0",
      "action_id": "a0a",
      "end_state_id": "s1a",
      "action_description": "Cut the apple in half...",
      "start_image_path": "...",
      "end_image_path": "...",
      "video_path": "generated_videos/.../s0_to_s1a_000.mp4",
      "generation_prompt": "..."
    },
    // ... 6 more transitions
  ]
}
```

## Cost & Time Estimates

### Single Video
- **Generation time**: 7-10 minutes
- **Cost**: ~$0.10 per video
- **Resolution**: 720p or 1080p
- **Duration**: ~5-8 seconds
- **Aspect ratio**: 16:9 (configurable)

### Full Branching World (7 transitions)
- **Total time**: ~56 minutes (7 videos × 8 min)
- **Total cost**: ~$0.70 (7 videos × $0.10)
- **Total storage**: ~70-140 MB (7 videos × 10-20 MB)

### Optimization Tips
1. **Generate overnight**: Long generation times
2. **Use canonical_only first**: Test with fewer videos
3. **Selective generation**: Use `generate_batch_transitions()` for specific paths
4. **Monitor costs**: Each video costs money

## Testing

### Quick Test (Dry Run)
```python
# Just load and verify structure (no generation)
image_world = ImageWorld.load("apple_eating_branching_image_world.json")
print(f"Would generate {len(image_world.transitions)} videos")
print(f"Estimated cost: ${len(image_world.transitions) * 0.10:.2f}")
```

### Test One Transition
```python
# Generate just one transition to test
generator = VideoWorldGenerator(veo_client=veo)
video_transition = generator.generate_transition_on_demand(
    image_world=image_world,
    transition_index=0,  # First transition only
    number_of_videos=1
)
```

### Test Canonical Path Only
```bash
python -c "
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

image_world = ImageWorld.load('apple_eating_branching_image_world.json')
generator = VideoWorldGenerator(veo_client=veo)
video_world = generator.generate_video_world(
    image_world=image_world,
    strategy='canonical_only'  # Only main path
)
video_world.save('test_canonical_only.json')
"
```

## Troubleshooting

### Issue: "No transitions found"
- Check that image world has `transitions` array
- Verify transitions have valid state IDs

### Issue: "Missing images for transition"
- Ensure all states have `image_path` populated
- Check that image files exist on disk

### Issue: "Video generation timeout"
- Veo generation can take 10+ minutes
- Increase timeout if needed
- Check Veo API status

### Issue: "Download failed"
- Video might still be processing
- Check `result.status` before downloading
- Retry after waiting longer

## Comparison Table

| Feature | Image World Generator | Video World Generator |
|---------|----------------------|----------------------|
| **Input** | Text World | Image World |
| **Output** | Images for states | Videos for transitions |
| **Full world strategy** | `full_world` | `all_transitions` |
| **Canonical strategy** | `canonical_path` | `canonical_only` |
| **Implementation** | BFS traversal | Iterate transitions |
| **Already implemented?** | ✅ (just added) | ✅ (already exists) |

## Next Steps

1. **Run the test**: `python test_full_video_world_auto.py`
2. **Verify output**: Check `generated_videos/` directory
3. **Inspect videos**: View the generated MP4 files
4. **Validate JSON**: Load `apple_eating_branching_video_world.json`

## Summary

The video world generator **already supports full branching worlds** via the `all_transitions` strategy! No implementation changes were needed. The generator:

- ✅ Handles all transitions in branching worlds
- ✅ Generates videos for every path
- ✅ Maintains parent-child relationships
- ✅ Supports enhanced prompts
- ✅ Records all metadata

Simply use `strategy="all_transitions"` to generate videos for all connecting paths in your branching world!
