# Interactive Video Bench - 10 Generated Worlds Summary

## Overview

Successfully generated **10 interactive branching worlds** for the Interactive Video Bench benchmark, focused on action planning with error recovery and intervention opportunities.

**Generation Date:** November 6, 2025  
**Total Generation Time:** ~5 minutes  
**Cost:** ~$0.10 (using Gemini 2.0 Flash Lite)

---

## Design Philosophy

These worlds are designed for **Interactive Video Benchmarking** with:

✅ **Action-focused planning** (not pixel-perfect object tracking)  
✅ **Branching decision points** with multiple valid paths  
✅ **Error recovery mechanisms** (mistakes can be corrected)  
✅ **Low visual complexity** (overhead/egocentric views, minimal props)  
✅ **Clear evaluation metrics** (goal achievement, sequence coherence, recovery ability)

---

## Generated Worlds Summary

### 1. 🍳 Home Cooking - Scrambled Eggs
**File:** `home_cooking_scrambled_eggs_branching_world.json`

- **States:** 15 | **Transitions:** 19 | **Paths:** 5
- **Branching Points:** 4 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Heat management errors (cold pan → sticky eggs)
- Salt timing variations
- Overcooking recovery strategies
- Temperature adjustment interventions

**Atomic Actions:** Heat pan → Add oil → Crack eggs → Stir → Add scallions → Season → Plate

**Metrics:** Goal success rate, violation count (burning, undercooking), recovery index, texture quality

---

### 2. ☕ Pour-Over Coffee Brewing
**File:** `pour_over_coffee_brewing_branching_world.json`

- **States:** 16 | **Transitions:** 18 | **Paths:** 4
- **Branching Points:** 3 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Water temperature variations (too hot/cold)
- Grind size adjustments
- Pour speed and timing modifications
- Over/under-extraction recovery

**Atomic Actions:** Grind beans → Heat water → Wet filter → Bloom → Pour stages → Finish

**Metrics:** Extraction quality, parameter compliance (±tolerances), timing efficiency

---

### 3. 🍽️ Formal Dining Table Setting
**File:** `formal_dining_table_setting_branching_world.json`

- **States:** 15 | **Transitions:** 19 | **Paths:** 6
- **Branching Points:** 4 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Utensil placement order violations
- Position error corrections
- Missing item substitutions
- Symmetry and spacing adjustments

**Atomic Actions:** Spread tablecloth → Place plate → Arrange forks → Arrange knives → Position glasses

**Metrics:** Constraint satisfaction rate, positional accuracy, correction efficiency

---

### 4. 📚 Desk & Room Organization
**File:** `desk_room_organization_branching_world.json`

- **States:** 14 | **Transitions:** 19 | **Paths:** 5
- **Branching Points:** 5 | **Success Endings:** 3 | **Failure Endings:** 1

**Key Features:**
- Multiple valid organization strategies
- Mid-task interruptions and adaptations
- Container shortage handling
- Priority reordering flexibility

**Atomic Actions:** Sort items → Categorize → Box/bin → Label → Arrange → Clean surface

**Metrics:** Coverage completeness, space efficiency, strategy coherence, time compliance

---

### 5. ♻️ Waste Recycling Sorting
**File:** `waste_recycling_sorting_branching_world.json`

- **States:** 16 | **Transitions:** 19 | **Paths:** 6
- **Branching Points:** 4 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Misclassification detection and correction
- Contaminated item handling
- Composite material decisions
- Real-time error recovery

**Atomic Actions:** Identify item → Classify → Choose bin → Place → Handle exceptions

**Metrics:** Classification accuracy, contamination avoidance, correction step count, compliance rate

---

### 6. 🪛 IKEA Bookshelf Assembly
**File:** `simple_ikea_bookshelf_assembly_branching_world.json`

- **States:** 15 | **Transitions:** 19 | **Paths:** 5
- **Branching Points:** 4 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Panel orientation mistakes
- Assembly sequence variations
- Backtracking and rework paths
- Missing part workarounds

**Atomic Actions:** Read instructions → Sort parts → Align pieces → Insert dowels → Screw → Test stability

**Metrics:** Structural integrity, rework count, sequence optimality, time efficiency

---

### 7. 🎁 Gift Box Wrapping
**File:** `gift_box_wrapping_branching_world.json`

- **States:** 17 | **Transitions:** 18 | **Paths:** 4
- **Branching Points:** 3 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Paper size estimation errors
- Tear and gap repairs
- Tape placement strategies
- Aesthetic recovery techniques

**Atomic Actions:** Measure → Cut paper → Wrap → Fold → Tape → Tie ribbon → Decorate

**Metrics:** Aesthetic quality score, material waste, repair success rate, time control

---

### 8. 🎒 Weekend Trip Packing
**File:** `weekend_trip_backpack_packing_branching_world.json`

- **States:** 15 | **Transitions:** 19 | **Paths:** 6
- **Branching Points:** 4 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Weight/volume constraint violations
- Item substitution strategies
- Priority reordering (TSA restrictions)
- Checklist coverage optimization

**Atomic Actions:** Review checklist → Sort by category → Pack layers → Distribute weight → Organize pockets → Verify

**Metrics:** Checklist coverage, constraint compliance (weight/size), substitution quality, accessibility

---

### 9. 🌱 Indoor Plant Care (Watering & Repotting)
**File:** `indoor_plant_watering_repotting_branching_world.json`

- **States:** 16 | **Transitions:** 18 | **Paths:** 4
- **Branching Points:** 3 | **Success Endings:** 3 | **Failure Endings:** 2

**Key Features:**
- Over/under-watering recovery
- Soil quality adjustments
- Root problem interventions
- Drainage optimization

**Atomic Actions:** Check moisture → Water (measured) → Prepare pot → Add soil → Transfer plant → Settle → Drain

**Metrics:** Moisture threshold compliance, survival rate, intervention success, post-care health

---

### 10. 🧪 Home Science Experiment (Oil-Water Density)
**File:** `water_oil_density_experiment_branching_world.json`

- **States:** 16 | **Transitions:** 18 | **Paths:** 4
- **Branching Points:** 3 | **Success Endings:** 3 | **Failure Endings:** 1

**Key Features:**
- Sequence order variations
- Over-mixing recovery
- Measurement correction
- Temperature effects

**Atomic Actions:** Prepare container → Measure water → Add coloring → Measure oil → Pour → Observe → Record

**Metrics:** Result accuracy (visible separation), procedure compliance, correction efficiency, conclusion validity

---

## Statistics Summary

| Metric | Min | Max | Average |
|--------|-----|-----|---------|
| **States** | 14 | 17 | 15.5 |
| **Transitions** | 18 | 19 | 18.7 |
| **Paths** | 4 | 6 | 5.0 |
| **Branching Points** | 3 | 5 | 3.8 |
| **Success Endings** | 3 | 3 | 3.0 |
| **Failure Endings** | 1 | 2 | 1.8 |

**Total Unique States across all worlds:** ~155  
**Total Transitions:** ~187  
**Total Possible Paths:** ~49

---

## World Structure

Each branching world includes:

### States
- **Initial State (s0):** Clean starting point
- **Linear Path States (s1-s9):** Canonical success path
- **Branch States (s1_alt_*):** Deviation points
- **Success States (s_perfect, etc.):** Multiple successful endings with quality variations
- **Failure States (f_*):** Recoverable and non-recoverable failures

### Actions
- **Primary Actions:** Core sequence steps
- **Alternative Actions:** Deviations (shortcuts, mistakes, risky)
- **Recovery Actions:** Error correction steps

### Metadata
- **Progress:** 0.0 to 1.0 tracking completion
- **Quality:** Success/failure outcome scores
- **Reasoning:** Why success/failure occurred

---

## Evaluation Metrics (Unified Across Worlds)

### 1. Goal Achievement Rate
- Percentage of runs reaching any success state
- Quality score of the achieved ending

### 2. Sequence Edit Distance
- Deviation from optimal path
- Allows for valid reordering (parallel-safe actions)

### 3. Violation Count
- Hard constraint violations (safety, rules)
- Soft constraint violations (quality degradation)

### 4. Recovery Index
- Ability to complete after errors
- Number of correction steps needed
- Success rate after intervention

### 5. Efficiency Metrics
- Time/step budget compliance
- Resource utilization
- Path optimality

### 6. Next-Action Accuracy
- Top-1/Top-k next action prediction
- N-step planning consistency

### 7. Human Acceptability
- Expert rating (τ threshold)
- Aesthetic/quality assessment

---

## File Locations

```
worlds/llm_worlds/
├── home_cooking_scrambled_eggs_branching_world.json          (29 KB)
├── pour_over_coffee_brewing_branching_world.json             (30 KB)
├── formal_dining_table_setting_branching_world.json          (39 KB)
├── desk_room_organization_branching_world.json               (37 KB)
├── waste_recycling_sorting_branching_world.json              (41 KB)
├── simple_ikea_bookshelf_assembly_branching_world.json       (37 KB)
├── gift_box_wrapping_branching_world.json                    (31 KB)
├── weekend_trip_backpack_packing_branching_world.json        (36 KB)
├── indoor_plant_watering_repotting_branching_world.json      (36 KB)
└── water_oil_density_experiment_branching_world.json         (34 KB)

Total: ~350 KB for all 10 worlds
```

---

## Next Steps

### Phase 1: Image Generation (Optional)
Generate consistent images for each state using Gemini 2.5 Flash:

```bash
python world_model_bench_agent/test_image_generator.py \
  --world worlds/llm_worlds/home_cooking_scrambled_eggs_branching_world.json \
  --strategy full_world
```

**Estimated Cost:** ~$0.04 per world × 10 = $0.40  
**Estimated Time:** ~2-3 minutes per world

### Phase 2: Video Generation (Optional)
Generate videos for state transitions using Google Veo:

```bash
python world_model_bench_agent/test_video_generator.py \
  --world [image_world_file] \
  --strategy all_transitions
```

**Estimated Cost:** ~$1-2 per world × 10 = $10-20  
**Estimated Time:** ~30-60 minutes per world

### Phase 3: Benchmark Implementation
1. Create interactive video interface (Graph-of-Video)
2. Implement metadata schema (PDDL-lite format)
3. Build evaluation harness
4. Design human annotation interface
5. Collect baseline agent performance

---

## Usage Examples

### Load a World
```python
from world_model_bench_agent.benchmark_curation import World

world = World.load("worlds/llm_worlds/home_cooking_scrambled_eggs_branching_world.json")

print(f"States: {len(world.states)}")
print(f"Transitions: {len(world.transitions)}")
print(f"Goal states: {len(world.goal_states)}")

# Get all possible paths
paths = world.get_all_paths()
print(f"Total paths from start to goal: {len(paths)}")
```

### Visualize World Graph
```python
world.visualize_graph(output_file="cooking_graph.png")
```

### Query State Transitions
```python
initial_state = world.initial_state
next_actions = world.get_available_actions(initial_state)

for action in next_actions:
    next_state = world.get_next_state(initial_state, action)
    print(f"{initial_state.state_id} --[{action.description}]--> {next_state.state_id}")
```

---

## Technical Details

### Generation Pipeline
1. **Linear World Generation** (Step 1)
   - LLM: Gemini 2.0 Flash Lite
   - Input: Scenario description + initial/goal states
   - Output: Linear sequence (8-10 states)
   - Cost: ~$0.001 per world

2. **Branching Expansion** (Step 2)
   - Algorithm: BFS-based branch insertion
   - Branching point selection: Evenly distributed
   - Alternative action generation: LLM-based
   - Path generation: Targeted to endings
   - Cost: ~$0.009 per world

### Quality Assurance
- All worlds validated for:
  - ✓ Graph connectivity (all goals reachable)
  - ✓ State uniqueness (no duplicate states)
  - ✓ Action causality (logical transitions)
  - ✓ Metadata completeness (progress, quality, reasoning)

---

## Design Principles Verified

✅ **Low Visual Burden:** Overhead/egocentric views, simple props  
✅ **High Interactivity:** 3-5 branching points per world  
✅ **Error Recovery:** 1-2 failure paths with correction opportunities  
✅ **Soft Consistency:** Object presence > pixel-level tracking  
✅ **Quantifiable Metrics:** Goal achievement, violations, recovery, efficiency  
✅ **Domain Diversity:** Cooking, assembly, organization, experiments, care  

---

## Contact & Attribution

**Project:** World Model Bench Agent  
**Framework:** Action-Conditioned World Model (AC-World)  
**Generated by:** LLM World Generator (Gemini 2.0 Flash Lite)  
**Date:** November 6, 2025

**Repository:** `/Users/wangxiang/Desktop/my_workspace/memory/world_model_bench_agent/`

---

## References

- Original design based on "Interactive Video Bench" requirements
- Focus on action planning vs. object tracking
- Inspired by: Something-Something-V2, Ego4D, Physion
- Evaluation metrics adapted from goal-conditioned RL benchmarks

---

**End of Summary**







