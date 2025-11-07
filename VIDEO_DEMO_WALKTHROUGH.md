# 🎬 Video Demo Walkthrough - IKEA Desk Assembly

## How to Run

```bash
cd /Users/wangxiang/Desktop/my_workspace/memory/world_model_bench_agent
python interactive_video_demo.py
```

## What You'll See

### 1. World Selection
```
🎬 CINEMATIC WORLD EXPLORER
======================================================================

🎬 AVAILABLE CINEMATIC WORLDS
======================================================================
1. ikea_desk_partial_video_world.json

Select (1-1) or 'q': 1
```

### 2. Game Introduction
```
📂 Loading: ikea_desk_partial_video_world.json
✅ Loaded successfully!

🎬 CINEMATIC WORLD EXPLORER: IKEA_desk_assembly_multi_ending
======================================================================

Assembly process with multiple possible outcomes (successes and failures)

📊 Production Stats:
  Scenes: 15
  Actions: 13
  Videos: 8 (available out of 15 total transitions)

🎯 Possible Endings:
  [s_perfect] ⭐⭐⭐⭐⭐ Quality: 1.0
  [s_good] ⭐⭐⭐⭐ Quality: 0.8
  [s_acceptable] ⭐⭐⭐ Quality: 0.6

🎬 Press Enter to start the movie...
```

### 3. Scene 1 - Initial State
```
======================================================================
🎬 CURRENT SCENE
======================================================================

🏷️  State: s0
📝 Unopened IKEA desk box with instruction manual on top

📊 Status:
   Progress: [                    ] 0%

🎞️  Scene: 1

📷 Current Frame: s0_000.png
   [Frame displayed] <- Image opens in your viewer!

----------------------------------------------------------------------
🎬 WHAT HAPPENS NEXT? (Choose Your Action)
----------------------------------------------------------------------

1. 📖 Open box carefully and read instruction manual thoroughly
   🎥 Video available!

2. 🗑️ Tear open box and toss instructions aside, attempt assembly by intuition
   🎥 Video available!

----------------------------------------------------------------------
🎬 Choose scene (1-2) or 'q' to quit:
```

### 4. Path 1: Perfect Assembly Route (with videos!)

#### Choice 1: Read Manual
```
🎬 Choose scene (1-2): 1

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
🎬 ACTION: Open box carefully and read instruction manual thoroughly
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

🎥 Playing transition video...
🎬 Playing video: s0_to_s1a_000.mp4
   [Opening video player...]
   ▶️  Video playing in viewer

⏸️  Press Enter when video finishes...
```
**Video shows**: Box being carefully opened, manual being read

#### Scene 2: Manual Read
```
======================================================================
🎬 CURRENT SCENE
======================================================================

🏷️  State: s1a
📝 Box opened, components laid out, instruction manual read carefully

📊 Status:
   Progress: [██                  ] 10%

🎞️  Scene: 2

📷 Current Frame: s1a_001.png

----------------------------------------------------------------------
🎬 WHAT HAPPENS NEXT?
----------------------------------------------------------------------

1. 🧘 Methodically follow each instruction step, double-checking each connection
   🎥 Video available!

🎬 Choose scene (1-1): 1
```

#### Choice 2: Follow Instructions
```
🎥 Playing transition video...
🎬 Playing video: s1a_to_s2a_002.mp4
   ▶️  Video playing in viewer
```
**Video shows**: Following instructions step by step, organizing parts

#### Scene 3: Following Steps
```
🏷️  State: s2a
📝 Following instructions step-by-step, all parts organized by number

📊 Status:
   Progress: [██████              ] 30%

1. 🧘 Take a breath, re-read instructions, continue methodically
   🎥 Video available!
```

#### Choice 3: Persist
```
🎥 Playing transition video...
🎬 Playing video: s2a_to_s3a_004.mp4
```
**Video shows**: Careful assembly, checking alignment

#### Scene 4: Nearly Complete
```
🏷️  State: s3a
📝 Desk frame assembled correctly, checking alignment before final tightening

📊 Status:
   Progress: [██████████████      ] 70%

1. ✨ Carefully tighten all screws, check stability, adjust alignment
   🎥 Video available!
```

#### Choice 4: Perfect Finish
```
🎥 Playing transition video...
🎬 Playing video: s3a_to_s_perfect_007.mp4
```
**Video shows**: Final tightening, checking stability, perfect result

#### Final Scene: Success!
```
======================================================================
🎬 THE END
======================================================================

🎉 SUCCESS! ⭐⭐⭐⭐⭐
Quality Score: 1.0

🏆 PERFECT ENDING!
You achieved the best possible outcome!

Final Scene: Perfect assembly: desk is stable, all screws tight,
perfectly aligned, looks professional

Total Scenes: 5

----------------------------------------------------------------------
🎞️  YOUR MOVIE
----------------------------------------------------------------------

Scene 1:
  🎬 Open box carefully and read instruction manual thoroughly
  📍 s0 → s1a

Scene 2:
  🎬 Methodically follow each instruction step, double-checking each connection
  📍 s1a → s2a

Scene 3:
  🎬 Take a breath, re-read instructions, continue methodically
  📍 s2a → s3a

Scene 4:
  🎬 Carefully tighten all screws, check stability, adjust alignment
  📍 s3a → s_perfect

======================================================================
🎬 CREDITS ROLL
======================================================================

Thank you for watching 'IKEA_desk_assembly_multi_ending'!

🎥 Your choices created a unique story!
```

## Path 2: Failure Route (Skip Manual → Give Up)

If you choose option 2 at the start and continue down that path:

```
Scene 1: Skip manual → s1b 🎥 VIDEO
Scene 2: Wing it → s2b 🎥 VIDEO
Scene 3: Get frustrated → s2c 🎥 VIDEO
Scene 4: Give up → s_gave_up 📸 NO VIDEO (quota limit)

💔 BAD ENDING
Quality Score: 0.2
😞 You gave up too soon...
```

## Available Video Paths

### With Full Videos (8 transitions):
1. ✅ **Perfect Path**: s0 → s1a → s2a → s3a → s_perfect (4 videos)
2. ✅ **Skip → Wing It**: s0 → s1b → s2b (2 videos)
3. ✅ **Frustration**: s2b → s2c (1 video)
4. ✅ **Wrong Parts**: s2b → s3c (1 video)

### Without Videos (7 transitions):
- s2c → s_gave_up (no video)
- s2c → s3b (no video)
- s3c → s_wrong_assembly (no video)
- s3c → s_acceptable (no video)
- s3b → s_good (no video)
- s3b → s_acceptable (no video)
- s_acceptable → s_collapsed (no video)

## Best Experience

For the most cinematic experience with all videos available, follow the **Perfect Assembly Route**:

1. Choose "Read manual" 🎥
2. Choose "Follow steps" 🎥
3. Choose "Persist" 🎥
4. Choose "Perfect finish" 🎥

All 4 transition videos available! Complete cinematic experience! 🎬

## Alternative Paths with Videos

**Chaos Path** (videos available):
1. Skip manual 🎥 → s1b
2. Wing it 🎥 → s2b
3. Get frustrated 🎥 → s2c
4. [No more videos after this]

**Wrong Parts Path** (videos available):
1. Skip manual 🎥 → s1b
2. Wing it 🎥 → s2b
3. Use wrong parts 🎥 → s3c
4. [No more videos after this]

## Features Demonstrated

✅ **Video Playback**: Auto-opens videos in default player
✅ **Progress Bars**: Visual progress tracking
✅ **Quality Stars**: Shows ending quality visually
✅ **Cinematic UI**: Movie-themed interface
✅ **Path History**: Shows your complete journey
✅ **Multiple Endings**: 6 different outcomes
✅ **Partial Video Support**: Gracefully handles missing videos

## System Requirements

- macOS/Windows/Linux
- Python 3.7+
- Default video player (QuickTime, Windows Media Player, etc.)
- ~10 MB of videos in generated_videos folder

## Files Used

- `ikea_desk_partial_video_world.json` - Video world metadata
- `ikea_desk_multi_ending_world.json` - Text world logic
- `generated_videos/IKEA_desk_assembly_multi_ending_images_videos/` - 8 MP4 files
- `generated_images/IKEA_desk_assembly_multi_ending_images/` - 15 PNG files

Enjoy your interactive IKEA desk assembly movie experience! 🎬🏗️
