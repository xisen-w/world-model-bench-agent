# 🚀 Quick Start - World Explorer Game

## TL;DR

```bash
source venv/bin/activate
python game.py --video worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json
```

**Videos play embedded in the game window!** ✨

## What You Get

🎮 **Playable Game** - Click buttons to make choices
📹 **Embedded Videos** - Smooth playback right in the window
🖼️ **Images** - Beautiful state visualizations  
📊 **Progress Tracking** - See your journey
🌳 **Branching Paths** - Multiple endings based on choices

## Controls

- **Click** action buttons to make choices
- **ESC** to quit
- **R** to restart

## Worlds Available

### Indoor Plant Care 🪴
9 videos showing plant watering and repotting
```bash
python game.py --video worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json
```

## How It Works

1. **Start** at initial state with an image
2. **Choose** an action by clicking a button
3. **Watch** the transition video play (embedded!)
4. **Arrive** at new state automatically
5. **Repeat** until you reach an ending

## Requirements

Already installed in venv:
- ✅ pygame
- ✅ opencv-python  
- ✅ Pillow

## File Structure

```
game.py                 # Main game file
run_game.sh            # Quick launcher
test_game.py           # Test initialization
test_embedded_video.py # Test video playback
GAME_README.md         # Full documentation
```

## Troubleshooting

**Game won't start?**
```bash
source venv/bin/activate
pip install pygame opencv-python Pillow
```

**Videos not playing?**
- Check `generated_videos/` directory exists
- Videos are MP4 format

That's it! Have fun! 🎉
