# Interactive World Explorer Demos 🎮

Two interactive game-like demos to explore world scenarios visually!

## 🖼️ Image Demo (`interactive_image_demo.py`)

Explore worlds with **static images** for each state.

### Features
- 📸 Automatically opens images in your default viewer
- 🎯 Visual progress tracking with progress bars and stars
- 🎨 Emoji-enhanced interface
- 🗺️ Shows complete path history

### How to Play
```bash
python interactive_image_demo.py
```

1. Select an image world (e.g., `ikea_desk_multi_ending_full_image_world.json`)
2. See the current state image
3. Choose actions from the menu
4. Watch your journey unfold with images
5. Reach a goal state or failure state

### Example Session
```
🎮 VISUAL WORLD EXPLORER: IKEA_desk_assembly_multi_ending
📊 World Statistics:
  States: 15
  Images: 15

🎯 Goals:
  [s_perfect] ⭐⭐⭐⭐⭐ Quality: 1.0
  [s_good] ⭐⭐⭐⭐ Quality: 0.8
  [s_acceptable] ⭐⭐⭐ Quality: 0.6

📷 Image: s0_000.png [opens in viewer]

⚡ AVAILABLE ACTIONS:
1. 📚 Open box carefully and read instruction manual
2. 🗑️ Tear open box and toss instructions aside

Choose an action (1-2):
```

## 🎬 Video Demo (`interactive_video_demo.py`)

Explore worlds with **transition videos** showing actions in motion!

### Features
- 🎥 Plays videos of transitions between states
- 📹 Shows both start/end frames AND transition videos
- 🎞️ Cinematic presentation
- 🏆 Multiple endings based on your choices

### How to Play
```bash
python interactive_video_demo.py
```

1. Select a video world (e.g., `ikea_desk_multi_ending_video_world.json`)
2. See current state image
3. Choose an action
4. **Watch the video** of your action playing out!
5. Continue until you reach an ending

### Example Session
```
🎬 CINEMATIC WORLD EXPLORER
📊 Production Stats:
  Scenes: 15
  Videos: 8 (available)

🎬 WHAT HAPPENS NEXT?
1. 📖 Open box carefully and read manual
   🎥 Video available!
2. 🗑️ Tear open box and skip instructions
   🎥 Video available!

🎬 Choose scene (1-2): 1

🎥 Playing transition video...
   ▶️  Video playing in viewer
⏸️  Press Enter when video finishes...
```

## 🎮 Available Worlds

### IKEA Desk Assembly (Full World)
- **Image World**: `ikea_desk_multi_ending_full_image_world.json`
- **Video World**: `ikea_desk_multi_ending_video_world.json` (partial)
- **States**: 15
- **Endings**: 6 (3 success, 3 failure)
- **Features**: Multiple quality levels, emotional paths, recovery options

### Apple Eating (Branching)
- **Image World**: `apple_eating_branching_image_world.json`
- **Video World**: `apple_eating_branching_video_world.json` (partial)
- **States**: 8
- **Endings**: 3 success paths
- **Features**: Cut vs bite, save vs eat all

## 🎯 Gameplay Tips

### For Best Outcome (Perfect Assembly)
1. 📚 Read the manual carefully
2. 🔨 Follow instructions methodically
3. 🧘 Take your time, double-check
4. ✨ Perfect finish with careful tightening

### For Failure (What NOT to do)
1. 🗑️ Skip the instructions
2. 💨 Rush through assembly
3. 😤 Give up when frustrated
4. 🧪 Test a poorly-made desk

## 📊 Understanding Quality Levels

| Quality | Stars | Outcome | Description |
|---------|-------|---------|-------------|
| 1.0 | ⭐⭐⭐⭐⭐ | Perfect | Professional, stable, aligned |
| 0.8 | ⭐⭐⭐⭐ | Good | Functional, minor imperfections |
| 0.6 | ⭐⭐⭐ | Acceptable | Works but wobbles |
| 0.3 | ⭐ | Wrong | Looks strange, doesn't fit |
| 0.2 | | Gave Up | Abandoned halfway |
| 0.1 | | Collapsed | Structural failure |

## 🛠️ Technical Details

### Requirements
- Python 3.7+
- PIL/Pillow (for image handling)
- Default image/video viewer on your system
  - macOS: Uses `open`
  - Windows: Uses `startfile`
  - Linux: Uses `xdg-open`

### File Structure
```
world_model_bench_agent/
├── interactive_image_demo.py       # Image-based game
├── interactive_video_demo.py       # Video-based game
├── ikea_desk_multi_ending_world.json                    # Text world
├── ikea_desk_multi_ending_full_image_world.json         # Image world
├── ikea_desk_multi_ending_video_world.json              # Video world (partial)
├── generated_images/
│   └── IKEA_desk_assembly_multi_ending_images/          # 15 images
└── generated_videos/
    └── IKEA_desk_assembly_multi_ending_images_videos/   # 8 videos (partial)
```

## 🎨 Features Comparison

| Feature | Image Demo | Video Demo |
|---------|-----------|------------|
| State Images | ✅ | ✅ |
| Transition Videos | ❌ | ✅ |
| Progress Bars | ✅ | ✅ |
| Quality Stars | ✅ | ✅ |
| Path History | ✅ | ✅ |
| Auto Image Open | ✅ | ✅ |
| Auto Video Play | ❌ | ✅ |
| Cinematic Feel | Medium | High |
| Speed | Fast | Slower (videos) |

## 🚀 Quick Start

### Image Demo (Fastest)
```bash
python interactive_image_demo.py
# Select IKEA world
# Choose option 1 (read manual) for best outcome
```

### Video Demo (Most Immersive)
```bash
python interactive_video_demo.py
# Select IKEA video world
# Watch videos play between choices
# Note: Only partial videos available (8/15)
```

## 🎮 Example Playthrough

### Perfect Assembly Route
1. Start: s0 (unopened box) 📦
2. Action: Read manual 📚 → s1a
3. Action: Follow steps 🔨 → s2a
4. Action: Persist methodically 🧘 → s3a
5. Action: Perfect finish ✨ → s_perfect 🏆
6. **Result**: Quality 1.0, PERFECT!

### Failure Route (Giving Up)
1. Start: s0 (unopened box) 📦
2. Action: Skip manual 🗑️ → s1b
3. Action: Wing it 🤷 → s2b
4. Action: Get frustrated 😤 → s2c
5. Action: Quit 🚪 → s_gave_up 😞
6. **Result**: Quality 0.2, FAILURE

## 📝 Notes

- **Video Availability**: Only 8/15 videos generated due to API quota
  - Transitions 1-8 have videos
  - Transitions 9-15 show images only
- **Image Quality**: All 15 states have images
- **Auto-Open**: Images/videos open in default system viewer
- **Interactive**: Press Enter to continue after videos play

## 🎯 Future Enhancements

- [ ] In-terminal image preview (ASCII art)
- [ ] Inline video player
- [ ] Save/load game progress
- [ ] Leaderboard for best quality achieved
- [ ] Time tracking
- [ ] Replay mode
- [ ] Compare different paths side-by-side

## 🐛 Troubleshooting

**Images/videos don't open?**
- Check default viewer settings
- Verify files exist in generated_images/videos folders

**"No image worlds found"?**
- Run `generate_ikea_full_world.py` first

**"No video worlds found"?**
- Run `generate_ikea_videos.py` first
- Note: May hit quota limits

## 🎉 Enjoy!

Have fun exploring different paths and outcomes! Try to achieve the perfect assembly, or see all the ways things can go wrong! 🎮🏗️
