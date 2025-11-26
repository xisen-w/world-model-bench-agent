# World Explorer Game 🎮

An interactive pygame-based game for exploring world scenarios with **embedded video playback**!

## Features

✅ **Embedded Video Playback** - Videos play directly in the game window (no external player needed!)
✅ **Real-time Video Player** - Smooth playback with progress bar
✅ **Interactive UI** - Click action buttons to make choices
✅ **Multi-modal Support** - Works with video, image, or text-only worlds
✅ **Automatic State Transitions** - Seamlessly transitions after video finishes
✅ **Visual Progress Tracking** - See your journey through the world

## Installation

```bash
# Install required packages
pip install pygame opencv-python Pillow

# Or use the venv
source venv/bin/activate
```

## Usage

### Video World (with embedded playback)
```bash
python game.py --video worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json
```

### Image World
```bash
python game.py --image worlds/image_worlds/indoor_plant_watering_repotting_branching_egocentric_image_world.json
```

### Text-Only World
```bash
python game.py --text worlds/llm_worlds/indoor_plant_watering_repotting_branching_egocentric_world.json
```

### Quick Launcher
```bash
./run_game.sh
```

## Controls

- **Left Click** - Select actions
- **ESC** - Quit game
- **R** - Restart from beginning

## How It Works

### Video Playback
When you select an action in video mode:

1. ✨ **Video loads** - The transition video is loaded into the embedded player
2. ▶️ **Video plays** - Smooth playback at original FPS with progress bar
3. 🎬 **Auto-transition** - When video finishes, automatically moves to next state
4. 🔒 **Buttons disabled** - Can't click during playback (prevents skipping)

### Architecture

```
┌─────────────────────────────────────┐
│         Media Area (800x600)        │
│  ┌───────────────────────────────┐  │
│  │  Video Player / Image Display │  │
│  │    (OpenCV + Pygame)          │  │
│  └───────────────────────────────┘  │
│           Progress Bar              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       Scene Description            │
│  Current state text...             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Available Actions             │
│  ┌───────────────────────────────┐ │
│  │  [Action Button 1]            │ │
│  │  [Action Button 2]            │ │
│  │  [Action Button 3]            │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         Progress Stats             │
│  Steps: 5  Progress: 60%          │
└─────────────────────────────────────┘
```

## Video Player Features

- **OpenCV Integration** - Uses cv2 for robust video decoding
- **Frame-accurate Timing** - Respects original video FPS
- **Automatic Scaling** - Fits videos to window while preserving aspect ratio
- **Progress Bar** - Visual feedback on playback progress
- **Graceful Fallback** - Uses external player if OpenCV not available

## Technical Details

### Video Player Class
- Loads MP4 videos using OpenCV
- Decodes frames on-the-fly
- Converts BGR→RGB and resizes to fit display
- Updates at original FPS (e.g., 24fps)
- Automatic cleanup when finished

### Performance
- 60 FPS UI updates
- Video frames decoded based on original FPS
- Efficient numpy/pygame surface conversion
- Low memory footprint (one frame at a time)

## Testing

```bash
# Test game initialization
python test_game.py

# Test embedded video playback
python test_embedded_video.py
```

## Worlds Available

1. **Indoor Plant Care** - Learn to water and repot plants (video/image/text)
2. **Apple Eating** - Simple eating scenario (video/image/text)
3. **IKEA Desk Assembly** - Multi-ending furniture assembly (video/image/text)

## Troubleshooting

### Video not playing?
- Make sure opencv-python is installed: `pip install opencv-python`
- Check that video files exist in `generated_videos/` directory
- If OpenCV not available, game will fall back to external player

### Low FPS?
- Videos play at their original FPS (usually 24fps)
- UI runs at 60fps independently

### Images not showing?
- Install Pillow: `pip install Pillow`

## Future Enhancements

- ⏯️ Play/Pause controls
- ⏪⏩ Skip forward/backward
- 🔊 Audio support
- 📹 Fullscreen video mode
- 💾 Save/Load game state

## Credits

Built with:
- **Pygame** - Game framework
- **OpenCV** - Video decoding
- **Pillow** - Image processing
- **NumPy** - Array operations

Enjoy exploring the worlds! 🌟
