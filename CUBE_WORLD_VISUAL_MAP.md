# Cube World Navigation - Visual Path Map

## Complete Decision Tree (Compact View)

```
                                    ┌──────────────┐
                                    │ S0: GRAND    │
                                    │ START        │
                                    └──────┬───────┘
                                           │ a0_initial
                                           ▼
                        ┌──────────────────────────────────────┐
                        │ S1: FIRST DECISION POINT             │
                        │ (4 paths diverge from here)          │
                        └──┬──────────┬──────────┬─────────┬──┘
                           │          │          │         │
              ┌────────────┘          │          │         └──────────┐
              │                       │          │                    │
              │ a1                    │ a3       │ a6                 │ a7
              │ recover_right_1       │ right    │ down               │ up
              ▼                       ▼          ▼                    ▼
        ┌──────────┐           ┌──────────┐  ┌──────────┐      ┌──────────────┐
        │ S2:      │           │ S3:      │  │ S_DEAD_2 │      │ S5: UPPER    │
        │ TRACK 1  │           │ TRACK 2  │  │ ✗ FAIL   │      │ LEVEL        │
        │ Recovery │           │ Clean    │  └──────────┘      │ (3 branches) │
        └────┬─────┘           └────┬─────┘                    └──┬────┬───┬──┘
             │ a2                   │ a4/a5                        │    │   │
             │ recover_right_2      ├─────┬─────┐                 │    │   │
             ▼                      │     │     │                 │    │   │
      ┌────────────┐                │     │     │         ┌───────┘    │   └────────┐
      │ S_SUCCESS_1│                │     │     │         │            │            │
      │ ✓ RECOVER  │                │     │     │         │ a8         │ a12        │ a13
      │   PATH     │                │     │     │         │ right      │ direct_left│ left_down
      └────────────┘                ▼     ▼     ▼         ▼            ▼            ▼
                              ┌──────┐ ┌──────┐  ┌──────┐ ┌──────────┐ ┌──────────┐
                              │DEAD_1│ │ S4   │  │ S6   │ │S_SUCCESS2│ │ S_DEAD_4 │
                              │✗DOWN │ │LOOP  │  │RIGHT │ │✓ DIRECT  │ │ ✗ FAIL   │
                              │      │ │BACK  │  │TRACK │ │   LEFT   │ │          │
                              └──────┘ └──┬───┘  └──┬───┘ └──────────┘ └──────────┘
                                          │ a14     │
                                          │ loop    │
                                          └─────►S1─┘
                                             🔄 RECURSIVE LOOP
                                                             │ a9
                                                             │ right_again
                                                             ▼
                                                        ┌──────────┐
                                                        │ S7:      │
                                                        │ DOUBLE   │
                                                        │ RIGHT    │
                                                        └────┬─────┘
                                                             │ a10/a11
                                                    ┌────────┴────────┐
                                                    │                 │
                                           a10      ▼                 ▼      a11
                                           down  ┌──────────┐    ┌──────────────┐
                                                 │ S_DEAD_3 │    │ S_SUCCESS_3  │
                                                 │ ✗ FAIL   │    │ ✓ TRIPLE     │
                                                 │          │    │    RIGHT     │
                                                 └──────────┘    └──────────────┘
```

## The Recovery Loop 🔄

**Track 2.2 creates a unique learning opportunity:**

```
S1 (Decision Point)
 │
 └─→ S3 (Turn Right)
      │
      └─→ [Choice A: Turn Down → DEAD_1 ✗]
      │
      └─→ [Choice B: Turn Left → S4 Recovery]
           │
           └─→ LOOPS BACK to S1!
               (Second chance with memory)
```

This loop tests:
- **Memory**: Can the agent remember the dead-end?
- **Learning**: Will they make a different choice the second time?
- **Infinite loop detection**: Does the agent realize they're in a cycle?
- **Strategy adjustment**: Can they change tactics based on experience?

An optimal agent should:
1. Try S1 → S3 → Dead_1 (first attempt)
2. Backtrack and try S1 → S3 → S4 (recovery)
3. Recognize S1 when looping back
4. Choose a different path (S2, S5, or even avoid S3 again)

## Path Analysis Table

| Path ID | Route | Transitions | Result | Difficulty | Strategy |
|---------|-------|-------------|--------|------------|----------|
| **P1** | S0→S1→S2→Success1 | 3 | ✓ SUCCESS | Easy | Recovery/Correction |
| **P2** | S0→S1→S5→Success2 | 3 | ✓ SUCCESS | Easy | Direct/Efficient |
| **P3** | S0→S1→S5→S6→S7→Success3 | 5 | ✓ SUCCESS | Medium | Commitment/Patience |
| **D1** | S0→S1→S3→Dead1 | 3 | ✗ DEAD-END | - | Wrong Turn Down |
| **D2** | S0→S1→Dead2 | 2 | ✗ DEAD-END | - | Initial Wrong Choice |
| **D3** | S0→S1→S5→S6→S7→Dead3 | 5 | ✗ DEAD-END | - | Almost Success |
| **D4** | S0→S1→S5→Dead4 | 3 | ✗ DEAD-END | - | Wrong Slope |
| **R1** | S0→S1→S3→S4→S1 | 5 | 🔄 LOOP | - | Recovery Loop (Second Chance) |

## Decision Point Breakdown

### Decision Point 1: S1 (Initial Crossroads)
```
From S1, you have 4 choices:
  ┌─────────────────────────────────────────┐
  │ Choice A: Recover Right #1              │ → Leads to SUCCESS #1 (2 steps)
  │ Choice B: Turn Right (Clean)            │ → Branches to Dead-End or Recovery
  │ Choice C: Turn Down                     │ → DEAD-END immediately
  │ Choice D: Turn Up                       │ → Best choice, 3 sub-options
  └─────────────────────────────────────────┘

Optimal: Choice D (Turn Up) - opens most possibilities
Trap: Choice C (Turn Down) - instant failure
```

### Decision Point 2: S3 (Track 2 Fork)
```
From S3, you have 2 choices:
  ┌─────────────────────────────────────────┐
  │ Choice A: Turn Down                     │ → DEAD-END
  │ Choice B: Turn Left                     │ → Back on track (Recovery)
  └─────────────────────────────────────────┘

Optimal: Choice B (Turn Left) - recovery capability test
Trap: Choice A (Turn Down) - misleading path
```

### Decision Point 3: S5 (Upper Level)
```
From S5, you have 3 choices:
  ┌─────────────────────────────────────────┐
  │ Choice A: Turn Right                    │ → Long path, 2 more decisions needed
  │ Choice B: Direct Turn Left              │ → SUCCESS #2 (SHORTEST!)
  │ Choice C: Turn Left-Down                │ → DEAD-END
  └─────────────────────────────────────────┘

Optimal: Choice B (Direct Left) - fastest success
Alternative: Choice A (Turn Right) - if you want the challenge
Trap: Choice C (Left-Down) - looks similar to B but wrong
```

### Decision Point 4: S7 (Double Right Position)
```
From S7, you have 2 choices:
  ┌─────────────────────────────────────────┐
  │ Choice A: Turn Right (3rd time)         │ → SUCCESS #3
  │ Choice B: Turn Down                     │ → DEAD-END
  └─────────────────────────────────────────┘

Optimal: Choice A (Right again) - commit to strategy
Trap: Choice B (Turn Down) - so close to success but fails
```

## Success Path Comparison

### Path 1: The Recovery Route
```
Steps: S0 → S1 → S2 → Success1
Length: 3 transitions
Time: Short
Strategy: "Trust the corrective path"
Best for: Cautious agents, recovery-oriented
Key insight: Sometimes the path that looks like a correction IS the answer
```

### Path 2: The Direct Route ⭐ OPTIMAL
```
Steps: S0 → S1 → S5 → Success2
Length: 3 transitions
Time: Short
Strategy: "Go up, then immediately left"
Best for: Efficient agents, decisive
Key insight: After gaining elevation, trust the direct option
```

### Path 3: The Commitment Route
```
Steps: S0 → S1 → S5 → S6 → S7 → Success3
Length: 5 transitions
Time: Long
Strategy: "Right, right, and right again"
Best for: Patient agents, consistent strategy
Key insight: Sometimes success requires multiple consistent choices
```

## Dead-End Analysis

| Dead-End | Location | Transitions to Reach | What Went Wrong |
|----------|----------|---------------------|-----------------|
| Dead_1 | After Track 2 | 3 | Turned down instead of left from right path |
| Dead_2 | Track 3 | 2 | Chose down immediately at first decision |
| Dead_3 | After Double Right | 5 | Got greedy, turned down instead of 3rd right |
| Dead_4 | Track 4 Upper | 3 | Confused left-down with direct-left |

## Agent Evaluation Criteria

### 1. Exploration Efficiency
- **Optimal**: Find success in ≤3 transitions (Path 1 or 2)
- **Good**: Find success in ≤5 transitions (Path 3)
- **Poor**: Hit 2+ dead-ends before success
- **Failed**: Cannot find any success path

### 2. Decision Quality Score
```
Points system:
  S1→S5 (Turn Up): +10 points (best initial choice)
  S1→S2 (Recover Right): +8 points (good initial choice)
  S1→S3 (Turn Right Clean): +5 points (leads to recovery test)
  S1→Dead2 (Turn Down): +0 points (instant fail)

  S5→Success2 (Direct Left): +10 points (optimal)
  S5→S6 (Turn Right): +7 points (long but valid)
  S5→Dead4 (Left-Down): +0 points (trap)

  S3→S4 (Recovery Left): +10 points (recovery ability)
  S3→Dead1 (Down): +0 points (failed recovery)

  S7→Success3 (3rd Right): +10 points (commitment)
  S7→Dead3 (Down): +0 points (gave up too early)
```

### 3. Recovery Capability
- **Test case**: Track 2 (S1→S3)
- **Challenge**: After turning right, can agent recover by turning left?
- **Success**: Agent navigates S3→S4 (recovery corridor)
- **Failure**: Agent hits Dead_1

### 4. Strategy Consistency
- **Test case**: Triple-Right path (Track 4.1)
- **Challenge**: Can agent commit to same direction 3x?
- **Success**: Agent navigates S5→S6→S7→Success3
- **Failure**: Agent wavers and hits Dead_3

## Recommended Test Scenarios

### Scenario 1: Optimal Path Discovery
```
Goal: Find the shortest path to success
Success criteria: Agent chooses S1→S5→Success2
Time limit: 3 transitions maximum
```

### Scenario 2: Recovery Test
```
Goal: Recover from sub-optimal choice
Setup: Force agent to take S1→S3
Success criteria: Agent finds S3→S4 recovery path
```

### Scenario 3: Patience Test
```
Goal: Complete the longest success path
Success criteria: Agent navigates full S1→S5→S6→S7→Success3
Challenge: Don't give up and take Dead_3
```

### Scenario 4: Dead-End Resilience
```
Goal: Hit a dead-end and successfully backtrack
Setup: Agent hits any dead-end
Success criteria: Agent backtracks and finds success on retry
```

## Video File Reference

| State/Transition | Video File | Duration |
|-----------------|-----------|----------|
| S0→S1 | grand_start.mov | Intro |
| S1 observation | new_start_non_cheat_observation.mov | - |
| S1→S2 | recover_right_1.mov | - |
| S2→Success1 | recover_right_2_final_step_success_end.mov | - |
| S1→S3 | real_turn_right_instead...mov | - |
| S3→Dead1 | turn_down_dead_end_initial_state_is_turn_right...mov | - |
| S3→S4 | turn_left_so_effectively_we_are_back_on_track...mov | - |
| S1→Dead2 | turn_down_dead_end_initial_state_turn_left.mov | - |
| S1→S5 | turn_up_back_on_track.mov | - |
| S5→S6 | turn_right.mov | - |
| S6→S7 | turn_right_again.mov | - |
| S7→Dead3 | turn_down_another_dead_end.mov | - |
| S7→Success3 | turn_right_the_third_time_success_end.mov | - |
| S5→Success2 | direct_turn_left_success_end_initial_state_turn_up.mov | - |
| S5→Dead4 | turn_left_down_dead-end.mov | - |

## Implementation Notes

This world JSON is ready to be used with your game engine:

```bash
python game.py --video worlds/video_worlds/cube_world_navigation_maze.json
```

Or test with the interactive demo:

```bash
python interactive_video_demo.py worlds/video_worlds/cube_world_navigation_maze.json
```

## Statistical Summary

- **Total States**: 15 (1 start + 10 intermediate + 3 success + 4 failure)
- **Total Transitions**: 14
- **Success Rate**: 27.3% (3 success states / 11 terminal states)
- **Average Path Length**: 3.67 transitions
- **Branching Factor**: 2.5 average branches per decision
- **Maximum Depth**: 5 transitions (longest path)
- **Minimum Depth**: 3 transitions (shortest paths)

## Agent Capability Requirements

To successfully navigate this world, an agent needs:

1. **Spatial Reasoning**: Understand 3D maze geometry
2. **Decision Making**: Evaluate options at branching points
3. **Memory**: Remember previous states for backtracking
4. **Pattern Recognition**: Identify visual/geometric cues
5. **Strategy Formulation**: Choose between efficiency vs exploration
6. **Error Recovery**: Backtrack from dead-ends
7. **Goal Persistence**: Continue despite failures
