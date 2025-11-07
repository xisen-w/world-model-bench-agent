# World Organization Refactoring Summary

## Overview

Reorganized the world JSON files into a clean directory structure for better organization and maintainability.

## New Directory Structure

```
worlds/
├── llm_worlds/          # Text-based world definitions (LLM generated)
├── image_worlds/        # Image worlds (worlds with generated images)
└── video_worlds/        # Video worlds (worlds with transition videos)
```

## Changes Made

### 1. Directory Structure Created

```bash
worlds/
├── llm_worlds/          (7 files)
│   ├── apple_eating_branching_world.json
│   ├── coffee_linear_world.json
│   ├── driving_branching_world.json
│   ├── driving_linear_world.json
│   ├── ikea_desk_branching_world.json
│   ├── ikea_desk_multi_ending_world.json
│   └── ikea_desk_world.json
│
├── image_worlds/        (7 files)
│   ├── apple_eating_branching_image_world.json
│   ├── apple_eating_image_world.json
│   ├── coffee_short_image_world.json
│   ├── driving_branching_image_world.json
│   ├── driving_linear_image_world.json
│   ├── ikea_desk_multi_ending_full_image_world.json
│   └── ikea_desk_multi_ending_world_images.json
│
└── video_worlds/        (4 files)
    ├── apple_eating_branching_video_world.json
    ├── apple_eating_world_videos.json
    ├── apple_eating_world_videos_enhanced.json
    └── ikea_desk_partial_video_world.json
```

### 2. Code Updates

#### A. World Save Methods (Auto-directory)

All world save methods now automatically save to the correct directory if given just a filename:

**`World.save()` (benchmark_curation.py)**
- Saves to `worlds/llm_worlds/` by default
- Usage: `world.save("my_world.json")` → saves to `worlds/llm_worlds/my_world.json`

**`ImageWorld.save()` (image_world_generator.py)**
- Saves to `worlds/image_worlds/` by default
- Usage: `image_world.save("my_image_world.json")` → saves to `worlds/image_worlds/my_image_world.json`

**`VideoWorld.save()` (video_world_generator.py)**
- Saves to `worlds/video_worlds/` by default
- Usage: `video_world.save("my_video_world.json")` → saves to `worlds/video_worlds/my_video_world.json`

#### B. Generator Updates

**`LLMWorldGenerator.__init__()` (llm_world_generator.py)**
- Added `output_dir` parameter (default: `"worlds/llm_worlds"`)
- Creates output directory automatically

#### C. Interactive Demo Updates

**`interactive_image_demo.py`**
- `list_image_worlds()` now looks in `worlds/image_worlds/`
- `main()` loads text worlds from `worlds/llm_worlds/`
- Includes fallback to current directory for backward compatibility

**`interactive_video_demo.py`**
- `list_video_worlds()` now looks in `worlds/video_worlds/`
- `main()` loads text worlds from `worlds/llm_worlds/`
- Includes fallback to current directory for backward compatibility

### 3. Backward Compatibility

All loaders include fallback logic:
1. First tries new directory structure (`worlds/*/`)
2. Falls back to current directory if file not found
3. Shows clear error messages with search locations

## Usage Examples

### Creating New Worlds

```python
from world_model_bench_agent.llm_world_generator import LLMWorldGenerator

# LLM World Generator automatically uses worlds/llm_worlds/
generator = LLMWorldGenerator(api_key="your_key")
world = generator.generate_linear_world(...)
world.save("my_world.json")  # Saves to worlds/llm_worlds/my_world.json
```

```python
from world_model_bench_agent.image_world_generator import ImageWorldGenerator

# Image world automatically saves to worlds/image_worlds/
image_world = generator.generate_image_world(...)
image_world.save("my_image_world.json")  # Saves to worlds/image_worlds/my_image_world.json
```

```python
from world_model_bench_agent.video_world_generator import VideoWorldGenerator

# Video world automatically saves to worlds/video_worlds/
video_world = generator.generate_video_world(...)
video_world.save("my_video_world.json")  # Saves to worlds/video_worlds/my_video_world.json
```

### Loading Worlds

```python
# Load from organized directories
world = World.load("worlds/llm_worlds/driving_branching_world.json")
image_world = ImageWorld.load("worlds/image_worlds/driving_branching_image_world.json")
video_world = VideoWorld.load("worlds/video_worlds/ikea_desk_partial_video_world.json")
```

### Running Interactive Demos

```bash
# Image demo - automatically finds worlds in worlds/image_worlds/
python interactive_image_demo.py

# Video demo - automatically finds worlds in worlds/video_worlds/
python interactive_video_demo.py
```

## Benefits

1. **Organization**: Clear separation between world types
2. **Scalability**: Easy to add new worlds without cluttering root directory
3. **Discovery**: Demos automatically find worlds in correct locations
4. **Backward Compatible**: Old scripts still work with fallback logic
5. **Convention**: Clear naming conventions for world types

## Migration Notes

Existing JSON files have been automatically moved to their respective directories. No manual migration needed for existing worlds.

Future world generation will automatically use the new directory structure.

## File Type Conventions

- **LLM Worlds**: `*_world.json` or `*_branching_world.json` or `*_linear_world.json`
  - Pure text-based world definitions
  - Location: `worlds/llm_worlds/`

- **Image Worlds**: `*_image_world.json`
  - Worlds with generated images for states
  - Location: `worlds/image_worlds/`

- **Video Worlds**: `*_video_world.json` or `*_videos.json`
  - Worlds with transition videos
  - Location: `worlds/video_worlds/`
