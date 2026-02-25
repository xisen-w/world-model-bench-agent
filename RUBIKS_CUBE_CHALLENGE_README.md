# Rubik's Cube Rotation Challenge

## What This Is

A **physical Rubik's cube manipulation** challenge where agents must choose sequences of cube rotations to reach solved configurations. This is **NOT** a virtual maze - it's about rotating a real Rubik's cube on a desk!

## The Challenge

You hold a physical Rubik's cube and need to find the correct sequence of rotations to solve it. The challenge has:

- **15 cube configurations** (states) - different orientations and color arrangements
- **15 rotation actions** - physical manipulations (rotate right, left, up, down)
- **4 branching decision points** - where multiple rotation choices are available
- **3 solution paths** - different rotation sequences that solve the cube
- **4 dead-end configurations** - rotations that lead to unsolvable states

## Core Concept

```
Starting Configuration
         ↓
    [Rotate Cube]
         ↓
  Decision Point #1: Choose rotation direction
    / | \ \
   /  |  \ \
Right Up Down Right(alt)
  ↓    ↓   ✗    ↓
...   ...  Dead-End  ...
  ↓    ↓           ↓
Solved! or Dead-End or Continue...
```

## The Actions

All actions are **physical cube rotations**:

- **Rotate Right**: Turn the cube clockwise (viewing from top)
- **Rotate Left**: Turn the cube counterclockwise
- **Rotate Up**: Tilt the cube backward (top face comes toward you)
- **Rotate Down**: Tilt the cube forward (bottom face comes toward you)
- **Combinations**: Some actions combine rotations (e.g., left-down)

## State Descriptions

Each state describes:
1. **Current cube configuration** - what the cube looks like
2. **Visible faces** - which colors/patterns are showing
3. **Available rotations** - what moves you can make next
4. **Orientation** - how the cube is positioned

**NO hints** about whether a move is "correct" or "wrong" - agents must learn through exploration!

## Success vs Failure

### Success States (3 total)
When the cube reaches a **solved configuration**:
- Specific color patterns align correctly
- Faces match solution criteria
- Challenge complete!

**UI shows**: "✓ SUCCESS!" in green

### Dead-End States (4 total)
When rotation sequence leads to **unsolvable configuration**:
- Color pattern doesn't match any solution
- No valid rotation continues from here
- Must backtrack and try different path

**UI shows**: "✗ DEAD END" in red

Both show a "🔄 Retry" button to start over.

## The Three Solution Paths

### Path 1: Double Right (3 rotations)
```
Start → Right Rotation → Right Rotation → SOLVED!
```
Straightforward, consistent rightward rotations.

### Path 2: Up-Left (3 rotations) ⭐ OPTIMAL
```
Start → Rotate Up → Rotate Left → SOLVED!
```
Shortest path! Change perspective then left.

### Path 3: Up-Triple-Right (5 rotations)
```
Start → Up → Right → Right → Right → SOLVED!
```
Longest but tests commitment to strategy.

## The Recovery Loop 🔄

Special feature at Decision Point (after first rotation):
```
Right Rotation → Down (Dead-End ✗)
              ↓
              Left Recovery
              ↓
        LOOPS BACK to Decision Point!
              ↓
        Try different rotation
```

Tests agent memory: Do they remember the failed path?

## What Makes This Challenging

### For Humans:
- Physical 3D reasoning about cube rotations
- Remembering which sequences work
- Understanding how rotations change visible faces
- No hints about correct vs incorrect moves

### For AI Agents:
- **Visual understanding** of cube configurations from video
- **Spatial reasoning** about 3D rotations and transformations
- **State recognition** - "Have I seen this configuration before?"
- **Strategy learning** - Which rotation sequences lead to solutions?
- **No labels** - Must learn purely from outcomes

## Game Controls

**Play the challenge:**
```bash
python game.py --video worlds/video_worlds/cube_world_navigation_maze.json
```

**Controls:**
- **Click action buttons** to rotate the cube
- **Watch videos** showing the physical rotation
- **Click "🔄 Retry"** button at end states to restart
- **Press 'R'** key anytime to restart
- **Press 'ESC'** to quit

## Video Format

Each video shows:
- Your hands manipulating the physical cube
- The rotation being performed
- The resulting cube configuration
- Real desktop environment

**15 videos total**, one for each rotation action.

## Example Gameplay

**State: Starting Configuration**
```
Description: "You're holding a Rubik's cube at the starting
             configuration. Your hands are positioned to
             make the first move."

Actions Available:
1. "Pick up the cube and make the first rotation"
```

**After First Rotation: Decision Point**
```
Description: "The cube is in a new configuration. You have
             several rotation options..."

Actions Available:
1. "Rotate the cube to the right"
2. "Rotate the cube to the right" (alternate angle)
3. "Rotate the cube downward"
4. "Rotate the cube upward"
```

**Success State**
```
Description: "The cube has reached a target configuration!
             The colors align in a specific pattern."

UI: ✓ SUCCESS! Exit found!
    [🔄 Retry Cube Challenge]
```

**Dead-End State**
```
Description: "This cube configuration is a dead end. The
             color pattern here doesn't lead to any valid
             solution paths."

UI: ✗ DEAD END - No further solutions
    [🔄 Retry Cube Challenge]
```

## Testing Scenarios

### Scenario 1: Optimal Discovery
Can the agent find the 3-rotation solution?

### Scenario 2: Dead-End Recovery
After hitting a dead-end, can it backtrack and choose differently?

### Scenario 3: Loop Detection
Does it recognize when it returns to a previous configuration?

### Scenario 4: Strategy Consistency
Can it commit to a multi-rotation strategy (triple-right path)?

## Why This Matters for AI

This challenge tests **embodied physical reasoning**:

- **Not simulation** - Real physical object manipulation
- **Multimodal** - Video + text + spatial reasoning required
- **Branching decisions** - Must plan ahead
- **No supervision** - Learn from success/failure outcomes only
- **State space exploration** - Must map configuration possibilities

Perfect for evaluating:
- Vision-language models understanding physical manipulation
- Spatial reasoning in 3D
- Sequential decision-making
- Learning from exploration

## File Structure

```
worlds/video_worlds/cube_world_navigation_maze.json
├── 15 cube configuration states
├── 15 rotation action descriptions
├── Video paths for each rotation
└── Success/failure state labels

worlds/llm_worlds/cube_world_recorded_gameplay.json
├── Text-only companion file
└── Enables game navigation logic

experiments/recorded_videos/cube_world/
├── grand_start.mov
├── turn_right.mov, turn_left.mov
├── turn_up.mov, turn_down.mov
├── recover_right_*.mov
├── *_success_end.mov (3 solutions)
└── *_dead_end.mov (4 failures)

generated_images/cube_world_states/
└── 15 key frames (one per state)
```

## Comparison to Other Benchmarks

| Benchmark | Domain | Success Paths | Branching | Physical? |
|-----------|--------|---------------|-----------|-----------|
| Indoor Plant | Procedural Task | 3 | Yes | Yes |
| IKEA Desk | Assembly | 2 | Limited | Yes |
| **Rubik's Cube** | **3D Manipulation** | **3** | **High** | **Yes** ✓ |

**Unique features:**
- Physical object rotation (not just state changes)
- 4 decision points with 2-4 options each
- Recovery loop that returns to earlier state
- Pure 3D spatial reasoning required

## Next Steps

1. **Test with vision models** - Can GPT-4V/Claude understand the rotations?
2. **Evaluate planning** - Do agents plan ahead or act greedily?
3. **Measure efficiency** - How quickly do they find optimal paths?
4. **Test generalization** - Can they handle different starting configurations?

---

**This is a test of embodied AI reasoning about physical 3D objects!** 🎲
