#!/usr/bin/env python3
"""
Generate 10 Interactive Worlds for Interactive Video Bench.

Focus on action planning, branching paths, and error recovery.
Low visual tracking requirements, high interaction and intervention opportunities.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.llm_world_generator import LLMWorldGenerator

def generate_all_worlds():
    """Generate all 10 interactive worlds."""
    
    # Initialize generator
    print("=" * 80)
    print("INTERACTIVE VIDEO BENCH - WORLD GENERATION")
    print("=" * 80)
    print("\nInitializing LLM World Generator...")
    
    try:
        generator = LLMWorldGenerator(output_dir="worlds/llm_worlds")
        print("✓ Generator initialized successfully\n")
    except Exception as e:
        print(f"✗ Error initializing generator: {e}")
        print("\nPlease ensure:")
        print("  1. You have a .env file with GEMINI_KEY=your_api_key")
        print("  2. Or set the GEMINI_KEY environment variable")
        return
    
    # Define all 10 scenarios
    scenarios = [
        # 1. Home cooking basics
        {
            "scenario": "home_cooking_scrambled_eggs",
            "initial_description": "Clean kitchen with wok/pan, eggs, scallions, salt, oil on the counter. Stove is off.",
            "goal_description": "Perfectly cooked scrambled eggs with scallions served on a plate, golden and fluffy.",
            "num_steps": 8,
            "context": """This is a cooking task with multiple intervention points:
- Can rescue if eggs are added before pan is hot (sticky pan → add oil/reduce heat)
- Can adjust if salt added too early (add water/second seasoning)
- Can recover if eggs overcooked (reduce heat/add water)
Include branching paths for: pan temperature mistakes, timing errors, ingredient order changes.""",
            "branching_paths": 4,
            "failure_paths": 2
        },
        
        # 2. Coffee/tea brewing
        {
            "scenario": "pour_over_coffee_brewing",
            "initial_description": "Coffee station with whole beans, grinder, pour-over dripper, filter, kettle with hot water (90-96°C), scale, and cup.",
            "goal_description": "Freshly brewed pour-over coffee in the cup, aromatic and well-extracted, with grounds in the filter.",
            "num_steps": 7,
            "context": """This is a parameter-sensitive brewing task:
- Can adjust if water too hot (over-extraction → wait, or compensate with faster pour)
- Can modify grind size mid-process if flow is wrong
- Can rescue under/over-extraction by adjusting pour speed
Include branches for: water temperature variations, grind size adjustments, pour timing changes.""",
            "branching_paths": 3,
            "failure_paths": 2
        },
        
        # 3. Oxford formal table setting
        {
            "scenario": "formal_dining_table_setting",
            "initial_description": "Bare dining table with tablecloth, 3 forks, 3 knives, 2 spoons, dinner plate, water glass, and wine glass available nearby.",
            "goal_description": "Properly set formal table with utensils in correct positions: forks left (outside-in order), knives right (blades in), glasses upper right, plate centered.",
            "num_steps": 6,
            "context": """This is a rule-based placement task with constraint satisfaction:
- Can correct if utensils placed in wrong order
- Can fix if items are positioned incorrectly
- Can recover from missing items by substitution
Include branches for: wrong placement order, position errors, constraint violations and corrections.""",
            "branching_paths": 4,
            "failure_paths": 2
        },
        
        # 4. Room organization
        {
            "scenario": "desk_room_organization",
            "initial_description": "Messy desk with scattered papers, cables, books, stationery, trash, and some storage boxes on the side.",
            "goal_description": "Organized desk with papers filed, cables bundled, books on shelf/in box, stationery in holder, trash removed, clean surface.",
            "num_steps": 7,
            "context": """This is a flexible planning task with multiple valid paths:
- Can change strategy mid-task (papers first vs cables first)
- Can handle interruptions (new items added)
- Can adapt to container shortage (reorganize priorities)
Include branches for: different prioritization orders, container/storage limitations, mid-task interruptions.""",
            "branching_paths": 5,
            "failure_paths": 1
        },
        
        # 5. Recycling sorting
        {
            "scenario": "waste_recycling_sorting",
            "initial_description": "Mixed waste pile containing: plastic bottles, paper, cardboard, metal cans, food-stained items. Four bins labeled: Paper, Plastic, Metal, Contaminated/Trash.",
            "goal_description": "All items correctly sorted into appropriate bins with no contamination. Paper in paper bin, plastic in plastic, metal in metal, contaminated in trash.",
            "num_steps": 6,
            "context": """This is a classification and correction task:
- Can correct mis-sorted items when noticed
- Can handle ambiguous items (composite materials)
- Can clean contaminated items or discard
Include branches for: misclassification and correction, contamination handling, composite material decisions.""",
            "branching_paths": 4,
            "failure_paths": 2
        },
        
        # 6. IKEA-style assembly
        {
            "scenario": "simple_ikea_bookshelf_assembly",
            "initial_description": "Unassembled bookshelf parts laid out: 4 panels, 8 dowels, 8 screws, 1 screwdriver, assembly instruction sheet showing 5 major steps.",
            "goal_description": "Completed bookshelf standing upright, all panels connected, stable structure, all dowels and screws properly installed.",
            "num_steps": 8,
            "context": """This is a sequence-constrained assembly task:
- Can detect and fix reversed panels
- Can backtrack if wrong piece installed
- Can substitute if parts are missing (use extra screws vs dowels)
Include branches for: assembly order variations, mistake detection and rework, missing part workarounds.""",
            "branching_paths": 4,
            "failure_paths": 2
        },
        
        # 7. Gift wrapping
        {
            "scenario": "gift_box_wrapping",
            "initial_description": "Unwrapped gift box, wrapping paper roll, scissors, tape dispenser, ribbon on the table.",
            "goal_description": "Beautifully wrapped gift with smooth paper, neat edges, no gaps, decorated with tied ribbon bow on top.",
            "num_steps": 7,
            "context": """This is a flexible craft task with recovery options:
- Can add patches if paper tears
- Can use extra tape if first attempt has gaps
- Can re-cut paper if size is wrong
Include branches for: paper size errors and adjustments, tear repairs, tape placement strategies.""",
            "branching_paths": 3,
            "failure_paths": 2
        },
        
        # 8. Travel packing
        {
            "scenario": "weekend_trip_backpack_packing",
            "initial_description": "Empty backpack (40L capacity), checklist on table showing: clothes (2 sets), toiletries, chargers, documents, medicine, water bottle. Items scattered on bed.",
            "goal_description": "Backpack packed efficiently with all checklist items, weight distributed well, easy-access items on top, within airline carry-on limits.",
            "num_steps": 7,
            "context": """This is a constraint-satisfaction packing task:
- Can reorganize if weight exceeds limit
- Can swap items if needed (bulky jacket → thin one)
- Can adapt to new requirements (liquid restrictions)
Include branches for: weight/volume constraint violations, item substitutions, priority reordering.""",
            "branching_paths": 4,
            "failure_paths": 2
        },
        
        # 9. Indoor plant care
        {
            "scenario": "indoor_plant_watering_repotting",
            "initial_description": "Small potted plant with dry soil (slightly wilted leaves), moisture meter, watering can with water, larger pot, fresh potting soil bag, hand trowel.",
            "goal_description": "Healthy plant in new larger pot with fresh moist soil, proper drainage, plant positioned correctly, excess water drained.",
            "num_steps": 7,
            "context": """This is a threshold-aware care task:
- Can rescue if over-watered (improve drainage, wait)
- Can adjust soil if too compacted
- Can handle root problems discovered during repotting
Include branches for: watering amount errors, soil quality issues, root damage handling.""",
            "branching_paths": 3,
            "failure_paths": 2
        },
        
        # 10. Safe home science experiment
        {
            "scenario": "water_oil_density_experiment",
            "initial_description": "Clear container, measuring cup with water, small bottle of cooking oil, food coloring drops, spoon for stirring on the table.",
            "goal_description": "Successful density demonstration showing distinct water (colored) and oil layers, with clear separation visible. Observations recorded.",
            "num_steps": 6,
            "context": """This is a process-driven experimental task:
- Can correct if order is wrong (oil first vs water first)
- Can re-do if mixed too vigorously
- Can adjust if measurements are off
Include branches for: sequence variations, mixing intensity errors, measurement corrections.""",
            "branching_paths": 3,
            "failure_paths": 1
        }
    ]
    
    # Generate each world
    generated_worlds = []
    
    for i, spec in enumerate(scenarios, 1):
        print("\n" + "=" * 80)
        print(f"GENERATING WORLD {i}/10: {spec['scenario']}")
        print("=" * 80)
        
        try:
            # Step 1: Generate linear world
            print(f"\n[Step 1/{spec.get('num_steps', 5)}] Generating linear world...")
            linear_world = generator.generate_linear_world(
                scenario=spec["scenario"],
                initial_description=spec["initial_description"],
                goal_description=spec["goal_description"],
                num_steps=spec["num_steps"],
                context=spec.get("context")
            )
            
            # Save linear world
            linear_filename = f"{spec['scenario']}_linear_world.json"
            linear_world.save(linear_filename)
            print(f"✓ Linear world saved: {linear_filename}")
            
            # Step 2: Expand to branching world
            print(f"\n[Step 2/2] Expanding to branching world...")
            branching_world = generator.expand_to_branching_world(
                linear_world=linear_world,
                total_states=20,
                num_endings=5,
                success_endings=3,
                failure_endings=spec.get("failure_paths", 2),
                branching_points=spec.get("branching_paths", 3)
            )
            
            # Save branching world
            branching_filename = f"{spec['scenario']}_branching_world.json"
            branching_world.save(branching_filename)
            print(f"✓ Branching world saved: {branching_filename}")
            
            # Print summary
            print(f"\n✓ COMPLETED: {spec['scenario']}")
            print(f"  States: {len(branching_world.states)}")
            print(f"  Transitions: {len(branching_world.transitions)}")
            print(f"  Goal states: {len(branching_world.goal_states)}")
            print(f"  Paths: {len(branching_world.get_all_paths())}")
            
            generated_worlds.append({
                "scenario": spec["scenario"],
                "linear_file": linear_filename,
                "branching_file": branching_filename,
                "success": True
            })
            
        except Exception as e:
            print(f"\n✗ ERROR generating {spec['scenario']}: {e}")
            generated_worlds.append({
                "scenario": spec["scenario"],
                "success": False,
                "error": str(e)
            })
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    
    successful = sum(1 for w in generated_worlds if w["success"])
    print(f"\nSuccessfully generated: {successful}/10 worlds")
    
    if successful > 0:
        print("\nGenerated files:")
        for world in generated_worlds:
            if world["success"]:
                print(f"  ✓ {world['scenario']}")
                print(f"    - {world['linear_file']}")
                print(f"    - {world['branching_file']}")
    
    if successful < 10:
        print(f"\nFailed: {10 - successful} worlds")
        for world in generated_worlds:
            if not world["success"]:
                print(f"  ✗ {world['scenario']}: {world.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("Next steps:")
    print("  1. Review generated worlds in worlds/llm_worlds/")
    print("  2. Generate images: python generate_images_for_world.py <world_file>")
    print("  3. Generate videos: python generate_videos_for_world.py <image_world_file>")
    print("=" * 80)

if __name__ == "__main__":
    generate_all_worlds()

