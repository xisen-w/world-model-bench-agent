# Interactive Video Bench - 10 Generated Worlds

## 🎉 Success! All 10 Worlds Generated

✅ **10 branching worlds** successfully created  
✅ **155 unique states** across all worlds  
✅ **186 state transitions** with action descriptions  
✅ **49 total paths** from initial to goal states  
✅ **Generation cost:** ~$0.10 (Gemini 2.0 Flash Lite)  
✅ **Generation time:** ~5 minutes  

---

## 📋 Quick Summary Table

| # | World Name | States | Transitions | Paths | Branches | Domain |
|---|------------|--------|-------------|-------|----------|---------|
| 1 | 🍳 **Scrambled Eggs Cooking** | 15 | 19 | 5 | 5 | Cooking |
| 2 | ☕ **Pour-Over Coffee** | 16 | 18 | 4 | 4 | Beverage |
| 3 | 🍽️ **Formal Table Setting** | 15 | 19 | 6 | 5 | Etiquette |
| 4 | 📚 **Desk Organization** | 14 | 19 | 5 | 6 | Organization |
| 5 | ♻️ **Recycling Sorting** | 16 | 19 | 6 | 5 | Environment |
| 6 | 🪛 **IKEA Assembly** | 15 | 19 | 5 | 5 | Assembly |
| 7 | 🎁 **Gift Wrapping** | 17 | 18 | 4 | 4 | Crafts |
| 8 | 🎒 **Travel Packing** | 15 | 19 | 6 | 5 | Planning |
| 9 | 🌱 **Plant Care** | 16 | 18 | 4 | 4 | Gardening |
| 10 | 🧪 **Science Experiment** | 16 | 18 | 4 | 4 | Education |

**Total:** 155 states, 186 transitions, 49 paths

---

## 🚀 Quick Start

### View All Worlds Summary
```bash
python visualize_world_summary.py
```

### View Specific World Details
```bash
python visualize_world_summary.py worlds/llm_worlds/home_cooking_scrambled_eggs_branching_world.json
```

### Load and Use a World in Code
```python
from world_model_bench_agent.benchmark_curation import World

# Load the world
world = World.load("worlds/llm_worlds/home_cooking_scrambled_eggs_branching_world.json")

# Explore the world
print(f"Initial: {world.initial_state.description}")
print(f"Goals: {len(world.goal_states)}")

# Get available actions from initial state
actions = world.get_available_actions(world.initial_state)
for action in actions:
    print(f"  - {action.description}")

# Get all paths from start to goal
paths = world.get_all_paths()
print(f"Total paths: {len(paths)}")
```

---

## 📊 Example World: Home Cooking (Scrambled Eggs)

### Structure Overview
```
Initial State (s0)
  └─> Clean kitchen with ingredients ready
       │
       ├─> [CANONICAL PATH] Heat pan → Add eggs → Cook → Serve
       │   └─> Success: Perfect scrambled eggs ✅
       │
       ├─> [COLD PAN MISTAKE] Add eggs too early
       │   ├─> Recover: Add more oil, adjust heat
       │   │   └─> Success: Acceptable eggs ✅
       │   └─> Continue mistake: Don't recover
       │       └─> Failure: Sticky, burnt eggs ❌
       │
       ├─> [OVERCOOKING] Leave on heat too long
       │   ├─> Recover: Remove early, add moisture
       │   │   └─> Success: Good eggs (slightly dry) ✅
       │   └─> Continue: Keep cooking
       │       └─> Failure: Burnt eggs ❌
       │
       └─> [TIMING ERROR] Add salt too early
           └─> Adjust: Add water, re-season
               └─> Success: Acceptable eggs ✅
```

### Branching Points (5)
1. **s1 (After heating pan):** 3 choices
   - Wait for proper heat ✓
   - Add eggs too early ⚠️
   - Overheat the pan ⚠️

2. **s3 (Eggs prepared):** 3 choices
   - Pour eggs at right time ✓
   - Add salt prematurely ⚠️
   - Skip scallions ⚠️

3. **s5 (During cooking):** 3 choices
   - Stir gently ✓
   - Overcook ⚠️
   - Stir too vigorously ⚠️

4. **s8 (Before plating):** 3 choices
   - Season and plate ✓
   - Over-season ⚠️
   - Plate without seasoning ⚠️

5. **s1_alt_0 (Recovery point):** 2 choices
   - Add oil and reduce heat ✓
   - Continue with mistake ❌

### Ending States (5)
| State ID | Type | Description |
|----------|------|-------------|
| `s_perfect` | ✅ Success | Perfect golden eggs, fluffy, moist |
| `s_good` | ✅ Success | Mostly golden, slightly overcooked |
| `s_acceptable` | ✅ Success | Pale yellow, slightly dry, edible |
| `f_critical_error` | ❌ Failure | Burnt and blackened, inedible |
| `f_minor_error` | ❌ Failure | Sticky, unpleasant texture |

---

## 🎯 Design Features

### 1. Action-Focused (Not Pixel-Perfect)
- Focus on **what action to take**, not exact object positions
- Visual consistency: object **presence** > pixel-level tracking
- Suitable for overhead/egocentric camera views

### 2. Branching & Intervention
- **3-5 branching points** per world
- Multiple valid paths to success
- Error **recovery mechanisms**
- Real-time intervention opportunities

### 3. Low Visual Complexity
- Simple props and environments
- Minimal object count (3-8 key objects)
- Clear state differentiation
- Suitable for single-camera recording

### 4. Quantifiable Metrics
- **Goal Achievement:** Did the agent reach a success state?
- **Sequence Coherence:** How close to optimal path?
- **Violation Count:** Safety and rule violations
- **Recovery Index:** Can recover from mistakes?
- **Efficiency:** Time and steps used

### 5. Error Taxonomy
```
Mistakes
├─> Recoverable Errors (soft failures)
│   ├─> Wrong timing → Adjust and continue
│   ├─> Wrong order → Reorder or skip
│   └─> Parameter error → Recalibrate
│
└─> Critical Errors (hard failures)
    ├─> Safety violations → Cannot recover
    ├─> Destructive actions → Restart needed
    └─> Missing constraints → Invalid state
```

---

## 📐 Evaluation Metrics (Unified)

### Primary Metrics

1. **Goal Achievement Rate (GAR)**
   ```
   GAR = (# successful completions) / (# total attempts)
   ```

2. **Sequence Edit Distance (SED)**
   ```
   SED = LevenshteinDistance(agent_path, optimal_path)
   Normalized by allowing parallel-safe action reordering
   ```

3. **Violation Count (VC)**
   ```
   VC = # hard violations + 0.5 × # soft violations
   ```

4. **Recovery Index (RI)**
   ```
   RI = (# recovered errors) / (# total errors made)
   ```

5. **Time/Step Efficiency (TSE)**
   ```
   TSE = optimal_steps / actual_steps
   ```

### Secondary Metrics

6. **Next-Action Accuracy (NAA)**
   - Top-1 accuracy: Correct next action
   - Top-k accuracy: Correct action in top-k

7. **N-Step Planning Consistency**
   - Can agent predict next N states accurately?

8. **Human Acceptability Score (HAS)**
   - Expert rating on 0-10 scale
   - Threshold τ for "acceptable" (e.g., τ ≥ 7)

---

## 🗂️ File Structure

```
worlds/llm_worlds/
│
├── Linear Worlds (baseline single-path)
│   ├── home_cooking_scrambled_eggs_linear_world.json
│   ├── pour_over_coffee_brewing_linear_world.json
│   ├── formal_dining_table_setting_linear_world.json
│   ├── desk_room_organization_linear_world.json
│   ├── waste_recycling_sorting_linear_world.json
│   ├── simple_ikea_bookshelf_assembly_linear_world.json
│   ├── gift_box_wrapping_linear_world.json
│   ├── weekend_trip_backpack_packing_linear_world.json
│   ├── indoor_plant_watering_repotting_linear_world.json
│   └── water_oil_density_experiment_linear_world.json
│
└── Branching Worlds (multi-path with recovery)
    ├── home_cooking_scrambled_eggs_branching_world.json
    ├── pour_over_coffee_brewing_branching_world.json
    ├── formal_dining_table_setting_branching_world.json
    ├── desk_room_organization_branching_world.json
    ├── waste_recycling_sorting_branching_world.json
    ├── simple_ikea_bookshelf_assembly_branching_world.json
    ├── gift_box_wrapping_branching_world.json
    ├── weekend_trip_backpack_packing_branching_world.json
    ├── indoor_plant_watering_repotting_branching_world.json
    └── water_oil_density_experiment_branching_world.json
```

---

## 🔄 Next Steps

### Option 1: Use Text-Only Worlds (Current State)
- ✅ **Ready to use** for text-based benchmarking
- Suitable for LLM action prediction
- No visual generation needed
- Cost: $0 (already generated)

### Option 2: Generate Images
```bash
# Generate images for each state
python world_model_bench_agent/test_image_generator.py \
  --world worlds/llm_worlds/home_cooking_scrambled_eggs_branching_world.json \
  --strategy full_world
```
- **Cost:** ~$0.04 per world × 10 = $0.40
- **Time:** ~2-3 minutes per world
- **Output:** ~15 images per world (PNG format)

### Option 3: Generate Videos
```bash
# Generate videos for each transition
python world_model_bench_agent/test_video_generator.py \
  --world <image_world_file> \
  --strategy all_transitions
```
- **Cost:** ~$1-2 per world × 10 = $10-20
- **Time:** ~30-60 minutes per world
- **Output:** ~18 videos per world (MP4 format)

### Option 4: Build Interactive Benchmark
1. Create video-based interactive UI
2. Implement "Graph-of-Video" navigation
3. Add agent inference API
4. Collect human baseline data
5. Run benchmark evaluation

---

## 📖 World Descriptions

### 1. 🍳 Home Cooking - Scrambled Eggs
**Complexity:** Medium  
**Key Challenges:** Heat management, timing, texture control  
**Recovery Opportunities:** Cold pan → add oil; overcooked → add water  
**Success Criteria:** Golden, fluffy, moist eggs with scallions  

### 2. ☕ Pour-Over Coffee Brewing
**Complexity:** Medium-High  
**Key Challenges:** Water temperature, grind size, pour timing  
**Recovery Opportunities:** Over-extraction → faster pour; under → slower  
**Success Criteria:** Aromatic, well-extracted coffee, proper bloom  

### 3. 🍽️ Formal Table Setting
**Complexity:** Low-Medium  
**Key Challenges:** Position accuracy, order constraints  
**Recovery Opportunities:** Wrong placement → move; missing → substitute  
**Success Criteria:** Utensils in correct positions, proper spacing  

### 4. 📚 Desk Organization
**Complexity:** High  
**Key Challenges:** Multiple valid strategies, interruptions  
**Recovery Opportunities:** Container shortage → reprioritize  
**Success Criteria:** All items categorized and stored, clean surface  

### 5. ♻️ Recycling Sorting
**Complexity:** Medium  
**Key Challenges:** Classification, contamination detection  
**Recovery Opportunities:** Mis-sorted → move to correct bin  
**Success Criteria:** All items correctly sorted, no contamination  

### 6. 🪛 IKEA Bookshelf Assembly
**Complexity:** Medium-High  
**Key Challenges:** Sequence constraints, orientation errors  
**Recovery Opportunities:** Wrong panel → disassemble and redo  
**Success Criteria:** Stable structure, all parts correctly installed  

### 7. 🎁 Gift Wrapping
**Complexity:** Medium  
**Key Challenges:** Paper size estimation, aesthetics  
**Recovery Opportunities:** Tear → patch; gap → add tape  
**Success Criteria:** Smooth paper, neat edges, ribbon bow  

### 8. 🎒 Travel Packing
**Complexity:** High  
**Key Challenges:** Weight/volume constraints, prioritization  
**Recovery Opportunities:** Overweight → swap items  
**Success Criteria:** Checklist complete, within limits  

### 9. 🌱 Plant Care (Watering & Repotting)
**Complexity:** Medium  
**Key Challenges:** Water amount, soil quality, root handling  
**Recovery Opportunities:** Over-watered → improve drainage  
**Success Criteria:** Healthy plant in new pot, proper moisture  

### 10. 🧪 Science Experiment (Oil-Water Density)
**Complexity:** Low  
**Key Challenges:** Sequence order, mixing control  
**Recovery Opportunities:** Over-mixed → wait and re-separate  
**Success Criteria:** Clear oil-water separation, visible layers  

---

## 🛠️ Development Tools

### Visualization
```bash
# Summary of all worlds
python visualize_world_summary.py

# Detailed view of specific world
python visualize_world_summary.py worlds/llm_worlds/<world>.json
```

### World Generation (if you want to create more)
```bash
# Generate new linear world
python -c "
from world_model_bench_agent.llm_world_generator import LLMWorldGenerator
gen = LLMWorldGenerator()
world = gen.generate_linear_world(
    scenario='your_scenario',
    initial_description='...',
    goal_description='...',
    num_steps=7
)
world.save('your_world.json')
"

# Expand to branching
python -c "
from world_model_bench_agent.llm_world_generator import LLMWorldGenerator
from world_model_bench_agent.benchmark_curation import World
gen = LLMWorldGenerator()
linear = World.load('your_world.json')
branching = gen.expand_to_branching_world(linear, branching_points=4)
branching.save('your_world_branching.json')
"
```

---

## 📚 API Reference

### Core Classes

```python
from world_model_bench_agent.benchmark_curation import World, State, Action, Transition

# Load world
world = World.load("world.json")

# Access states
initial = world.initial_state
goals = world.goal_states

# Get available actions from a state
actions = world.get_available_actions(state)

# Execute action
next_state = world.get_next_state(state, action)

# Get all paths
paths = world.get_all_paths()  # List[List[Transition]]

# Visualize
world.visualize_graph("graph.png")
```

---

## ✨ Key Achievements

✅ **Domain Diversity:** 10 different everyday scenarios  
✅ **Branching Structure:** Average 4.7 branching points per world  
✅ **Multiple Endings:** 3 success + 1-2 failure endings per world  
✅ **Recovery Paths:** Error correction opportunities in all worlds  
✅ **Low Visual Load:** Suitable for single-camera overhead recording  
✅ **Quantifiable Metrics:** 8 standardized evaluation metrics  
✅ **Production Ready:** All worlds validated and tested  

---

## 📞 Support & Documentation

- **Full Summary:** `INTERACTIVE_VIDEO_BENCH_WORLDS_SUMMARY.md`
- **Generation Scripts:** `generate_10_interactive_worlds.py`, `expand_linear_to_branching.py`
- **Visualization:** `visualize_world_summary.py`
- **Core Framework:** `world_model_bench_agent/benchmark_curation.py`

---

## 🎓 Citation

If you use these worlds in research, please cite:

```
@misc{interactive_video_bench_2025,
  title={Interactive Video Bench: 10 Branching Worlds for Action Planning},
  author={World Model Bench Agent Framework},
  year={2025},
  note={Generated using Gemini 2.0 Flash Lite LLM}
}
```

---

**Generated:** November 6, 2025  
**Framework:** AC-World (Action-Conditioned World Model Benchmark)  
**Status:** ✅ Production Ready







