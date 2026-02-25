# Rubik's Cube Layer Notation Guide

## Standard Notation

Each action in this challenge is a **single 90° layer twist** using standard Rubik's cube notation:

| Notation | Layer | Direction | Description |
|----------|-------|-----------|-------------|
| **R** | Right | Clockwise | Right face rotates 90° clockwise (when viewing that face) |
| **L** | Left | Clockwise | Left face rotates 90° clockwise |
| **U** | Upper | Clockwise | Top face rotates 90° clockwise |
| **D** | Down | Clockwise | Bottom face rotates 90° clockwise |
| **F** | Front | Clockwise | Front face rotates 90° clockwise |
| **B** | Back | Clockwise | Back face rotates 90° clockwise |

### Counter-clockwise moves:
- **R'** = Right face 90° counter-clockwise
- **L'** = Left face 90° counter-clockwise
- etc.

## The Three Solution Sequences

### Solution 1: Double Right (R R)
```
Starting state
    ↓ R (Twist right face 90° clockwise)
Intermediate state
    ↓ R (Twist right face 90° clockwise again)
✓ SOLVED!
```
**Length**: 2 moves
**Sequence**: R R
**Videos**: recover_right_1.mov → recover_right_2_final_step_success_end.mov

---

### Solution 2: Top-Left (U L) ⭐ OPTIMAL
```
Starting state
    ↓ U (Twist top face 90° clockwise)
Intermediate state
    ↓ L (Twist left face 90° clockwise)
✓ SOLVED!
```
**Length**: 2 moves (shortest!)
**Sequence**: U L
**Videos**: turn_up_back_on_track.mov → direct_turn_left_success_end_initial_state_turn_up.mov

---

### Solution 3: Top + Triple Right (U R R R)
```
Starting state
    ↓ U (Twist top face 90° clockwise)
After U
    ↓ R (Twist right face 90° clockwise)
After U R
    ↓ R (Twist right face 90° clockwise)
After U R R
    ↓ R (Twist right face 90° clockwise)
✓ SOLVED!
```
**Length**: 4 moves (longest)
**Sequence**: U R R R
**Videos**: turn_up_back_on_track.mov → turn_right.mov → turn_right_again.mov → turn_right_the_third_time_success_end.mov

---

## The Four Dead-End Sequences

### Dead-End 1: Right-Down (R D)
```
Start → R → D → ✗ DEAD END
```
After twisting right face then bottom face, configuration is unsolvable.

### Dead-End 2: Just Down (D)
```
Start → D → ✗ DEAD END
```
Twisting bottom face from start leads nowhere.

### Dead-End 3: Top-Double Right-Down (U R R D)
```
Start → U → R → R → D → ✗ DEAD END
```
So close! Three right twists would have solved it, but down was wrong.

### Dead-End 4: Top-Left-Down (U L D)
```
Start → U → L → D → ✗ DEAD END
```
After U L, adding D creates unsolvable configuration.

---

## The Recovery Loop 🔄

Special sequence that returns to starting decision point:

```
Start
  ↓ R (Right face twist)
State after R
  ↓ D (Bottom face twist)
  ✗ DEAD END #1

  OR

  ↓ L (Left face twist)
State after R L
  ↓ (automatic continuation)
LOOPS BACK to starting decision point!
```

Sequence: **R L** returns you to the beginning with new knowledge.

---

## Action Descriptions in Game

When you play, actions are described as:

**Old (vague):**
- "Turn right" ← Which layer? Which direction?

**New (precise):**
- "Twist the right face 90° clockwise (R move)" ✓
- "Twist the top face 90° clockwise (U move)" ✓
- "Twist the left face 90° clockwise (L move)" ✓

---

## Example Gameplay

### Starting Position
```
State: "Starting configuration. Ready for first layer twist."

Available moves:
1. "Pick up the cube to begin"
```

### After First Move
```
State: "After the first move, multiple layer twists possible:
        right face (R), left face (L), top face (U), or
        bottom face (D)."

Available moves:
1. "Twist the right face 90° clockwise (R move)"
2. "Twist the right face 90° clockwise (R move)" [alternate]
3. "Twist the bottom face 90° clockwise (D move)"
4. "Twist the top face 90° clockwise (U move)"
```

### Success State
```
State: "Success! After U L sequence, the cube has reached
        a solved configuration."

UI: ✓ SUCCESS!
    [🔄 Retry Challenge]
```

---

## Why This Notation Matters

### For Players:
- **Clear and unambiguous** - "R" means exactly one thing
- **Standard worldwide** - Used by all cubers globally
- **Precise** - No confusion about which layer or direction

### For AI Agents:
- **Learnable patterns** - R R vs R L have predictable effects
- **Transferable knowledge** - If trained on cube notation elsewhere
- **Compositional** - Can reason about move sequences (R R R = R³)

### For Research:
- **Reproducible** - Anyone can verify the sequences
- **Comparable** - Standard benchmark notation
- **Extendable** - Can add R', 180° moves, middle layers later

---

## Quick Reference Card

| Video Name | Layer Move | Notation |
|------------|-----------|----------|
| recover_right_1.mov | Right face clockwise | R |
| recover_right_2_*.mov | Right face clockwise | R |
| turn_right.mov | Right face clockwise | R |
| turn_right_again.mov | Right face clockwise | R |
| turn_right_the_third_*.mov | Right face clockwise | R |
| turn_left_*.mov | Left face clockwise | L |
| turn_up_*.mov | Top face clockwise | U |
| turn_down_*.mov | Bottom face clockwise | D |

---

## Testing the Challenge

```bash
python game.py --video worlds/video_worlds/cube_world_navigation_maze.json
```

Try to find all three solutions:
- ✓ R R (2 moves)
- ✓ U L (2 moves) ← shortest!
- ✓ U R R R (4 moves)

And avoid the dead-ends:
- ✗ R D
- ✗ D
- ✗ U R R D
- ✗ U L D

Good luck! 🎲
