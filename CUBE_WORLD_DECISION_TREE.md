# Cube World Navigation - Decision Tree Visualization

## Overview
A maze-like navigation world with multiple branching paths, dead-ends, and three successful exit routes.

## Decision Tree Structure

```
START: Grand Start
    │
    ▼
[STATE 0] New Start (Non-Cheat Observation)
    │
    ├─────────────────┬─────────────────┬─────────────────┐
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
[TRACK 1]        [TRACK 2]        [TRACK 3]        [TRACK 4]
Recover          Turn Right       Turn Down        Turn Up
Right #1         (Clean)          (Dead-End)       (Back on Track)
    │                 │                                  │
    ▼                 ├────────┬─────────                ├────────┬─────────┐
Recover                │        │                        │        │         │
Right #2               ▼        ▼                        ▼        ▼         ▼
    │             [2.1]    [2.2]                    [4.1]    [4.2]     [4.3]
    ▼             Turn     Turn                     Turn     Direct    Turn
✓ SUCCESS #1      Down     Left                     Right    Turn      Left-Down
  (Recover        DEAD     Recovery                  │        Left      DEAD-END
   Path)          END      Loop                      ├──┬──   │
                   ✗        │                        │  │  ▼  ▼
                            └───►[LOOPS BACK]        ▼  ▼  ✓ SUCCESS #2
                                 to Decision         Turn Turn   (Direct)
                                 Point ──┐           Right Down
                                         │           Again  DEAD
                                         │             │     END
                                         └────────◄───┘     ✗
                                         (Get another
                                          chance!)
                                                    Turn
                                                    Right
                                                    3rd Time
                                                      │
                                                      ▼
                                                    ✓ SUCCESS #3
                                                      (Right Path)
```

## Navigation Summary

### Success Paths (3 Total)
1. **SUCCESS #1 - Recover Path**: Track 1 → Recover Right #1 → Recover Right #2 → END
2. **SUCCESS #2 - Direct Left**: Track 4 → Turn Up → Direct Turn Left → END
3. **SUCCESS #3 - Triple Right**: Track 4 → Turn Up → Turn Right → Turn Right Again → Turn Right 3rd → END

### Dead-Ends (4 Total)
1. **DEAD-END #1**: Track 2 → Turn Right → Turn Down (2.1)
2. **DEAD-END #2**: Track 3 → Turn Down
3. **DEAD-END #3**: Track 4 → Turn Up → Turn Right → Turn Right Again → Turn Down
4. **DEAD-END #4**: Track 4 → Turn Up → Turn Left-Down (4.3)

### Recovery Loop Path 🔄
- **Track 2.2**: Turn Right → Turn Left → **LOOPS BACK to Decision Point**
- This creates a recurring loop! Agents can learn from their mistake and try again
- The loop rewards course correction and gives a second chance at navigation
- Tests agent memory: Can they remember the dead-end and choose differently?

## State Count
- **Total States**: 18 unique states
- **Initial State**: 1 (Grand Start)
- **Success States**: 3
- **Failure States**: 4 (dead-ends)
- **Intermediate States**: 10

## Transition Count
- **Total Transitions**: 17 (including all branches)

## Video Files Mapping

| Video File | State Role |
|-----------|-----------|
| `grand_start.mov` | Initial state (S0) |
| `new_start_non_cheat_observation.mov` | First decision point (S1) |
| `recover_right_1.mov` | Track 1 transition (S1→S2) |
| `recover_right_2_final_step_success_end.mov` | Track 1 success (S2→S_success_1) |
| `real_turn_right_instead_initial_state_same_with_recover_right_1_both_clean_start.mov` | Track 2 start (S1→S3) |
| `turn_down_dead_end_initial_state_is_turn_right_so_this_is_after.mov` | Track 2.1 dead-end (S3→S_dead_1) |
| `turn_left_so_effectively_we_are_back_on_track_initial_state_turn_right.mov` | Track 2.2 recovery (S3→S4) |
| `turn_down_dead_end_initial_state_turn_left.mov` | Track 3 dead-end (S1→S_dead_2) |
| `turn_up_back_on_track.mov` | Track 4 start (S1→S5) |
| `turn_right.mov` | Track 4.1 first turn (S5→S6) |
| `turn_right_again.mov` | Track 4.1 second turn (S6→S7) |
| `turn_down_another_dead_end.mov` | Track 4.1.1 dead-end (S7→S_dead_3) |
| `turn_right_the_third_time_success_end.mov` | Track 4.1.2 success (S7→S_success_3) |
| `direct_turn_left_success_end_initial_state_turn_up.mov` | Track 4.2 success (S5→S_success_2) |
| `turn_left_down_dead-end.mov` | Track 4.3 dead-end (S5→S_dead_4) |

## Complexity Analysis

### Branching Factor
- **From S1 (Main Decision Point)**: 4 branches
- **From S3 (Track 2)**: 2 branches
- **From S5 (Track 4)**: 3 branches
- **From S7 (Track 4.1 Again)**: 2 branches

### Path Complexity
- **Shortest Success Path**: 2 transitions (S1 → S5 → S_success_2)
- **Longest Success Path**: 4 transitions (S1 → S5 → S6 → S7 → S_success_3)
- **Total Explorable Paths**: 11 unique trajectories

### Agent Challenge Level
- **Difficulty**: Medium-High
- **Key Challenges**:
  - Multiple decision points requiring spatial reasoning
  - Dead-ends that look similar to valid paths
  - Need for backtracking/memory in Track 2.2
  - Three distinct success strategies

## Recommended Agent Evaluation Metrics

1. **Path Efficiency**: Did the agent find the shortest path?
2. **Dead-End Avoidance**: How many dead-ends were explored?
3. **Recovery Capability**: Can the agent handle Track 2.2 recovery?
4. **Goal Achievement**: Which success state was reached?
5. **Decision Quality**: Optimal choices at each branching point?
