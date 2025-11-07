#!/usr/bin/env python3
"""
Expand already-generated linear worlds to branching worlds.

This script takes the 10 linear worlds that were already generated
and expands them into branching worlds with multiple paths and endings.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.llm_world_generator import LLMWorldGenerator
from world_model_bench_agent.benchmark_curation import World

def expand_all_linear_worlds():
    """Expand all linear worlds to branching worlds."""
    
    print("=" * 80)
    print("EXPAND LINEAR WORLDS TO BRANCHING WORLDS")
    print("=" * 80)
    print("\nInitializing LLM World Generator...")
    
    try:
        generator = LLMWorldGenerator(output_dir="worlds/llm_worlds")
        print("✓ Generator initialized successfully\n")
    except Exception as e:
        print(f"✗ Error initializing generator: {e}")
        return
    
    # Define linear world files (in worlds/llm_worlds/ directory)
    base_dir = "worlds/llm_worlds"
    linear_worlds = [
        {
            "file": f"{base_dir}/home_cooking_scrambled_eggs_linear_world.json",
            "branching_paths": 4,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/pour_over_coffee_brewing_linear_world.json",
            "branching_paths": 3,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/formal_dining_table_setting_linear_world.json",
            "branching_paths": 4,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/desk_room_organization_linear_world.json",
            "branching_paths": 5,
            "failure_paths": 1
        },
        {
            "file": f"{base_dir}/waste_recycling_sorting_linear_world.json",
            "branching_paths": 4,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/simple_ikea_bookshelf_assembly_linear_world.json",
            "branching_paths": 4,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/gift_box_wrapping_linear_world.json",
            "branching_paths": 3,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/weekend_trip_backpack_packing_linear_world.json",
            "branching_paths": 4,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/indoor_plant_watering_repotting_linear_world.json",
            "branching_paths": 3,
            "failure_paths": 2
        },
        {
            "file": f"{base_dir}/water_oil_density_experiment_linear_world.json",
            "branching_paths": 3,
            "failure_paths": 1
        }
    ]
    
    expanded_worlds = []
    
    for i, spec in enumerate(linear_worlds, 1):
        print("\n" + "=" * 80)
        print(f"EXPANDING WORLD {i}/10: {spec['file']}")
        print("=" * 80)
        
        try:
            # Load linear world
            print(f"\nLoading linear world: {spec['file']}")
            if not os.path.exists(spec['file']):
                raise FileNotFoundError(f"File not found: {spec['file']}")
            
            linear_world = World.load(spec['file'])
            print(f"✓ Loaded: {len(linear_world.states)} states, {len(linear_world.transitions)} transitions")
            
            # Expand to branching world
            print(f"\nExpanding to branching world...")
            print(f"  - Branching points: {spec['branching_paths']}")
            print(f"  - Failure endings: {spec['failure_paths']}")
            print(f"  - Success endings: 3")
            
            branching_world = generator.expand_to_branching_world(
                linear_world=linear_world,
                total_states=20,
                num_endings=5,
                success_endings=3,
                failure_endings=spec['failure_paths'],
                branching_points=spec['branching_paths']
            )
            
            # Save branching world
            branching_filename = spec['file'].replace('_linear_world.json', '_branching_world.json')
            branching_world.save(branching_filename)
            print(f"\n✓ Branching world saved: {branching_filename}")
            
            # Print summary
            print(f"\n✓ COMPLETED")
            print(f"  Total states: {len(branching_world.states)}")
            print(f"  Total transitions: {len(branching_world.transitions)}")
            print(f"  Goal states: {len(branching_world.goal_states)}")
            
            # Try to get paths (may be slow for large worlds)
            try:
                paths = branching_world.get_all_paths()
                print(f"  Total paths: {len(paths)}")
            except:
                print(f"  Total paths: (calculation skipped - complex graph)")
            
            expanded_worlds.append({
                "file": spec['file'],
                "branching_file": branching_filename,
                "success": True
            })
            
        except Exception as e:
            print(f"\n✗ ERROR expanding {spec['file']}: {e}")
            import traceback
            traceback.print_exc()
            expanded_worlds.append({
                "file": spec['file'],
                "success": False,
                "error": str(e)
            })
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print("EXPANSION COMPLETE")
    print("=" * 80)
    
    successful = sum(1 for w in expanded_worlds if w["success"])
    print(f"\nSuccessfully expanded: {successful}/10 worlds")
    
    if successful > 0:
        print("\nGenerated branching world files:")
        for world in expanded_worlds:
            if world["success"]:
                print(f"  ✓ {world['branching_file']}")
    
    if successful < 10:
        print(f"\nFailed: {10 - successful} worlds")
        for world in expanded_worlds:
            if not world["success"]:
                print(f"  ✗ {world['file']}: {world.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("Next steps:")
    print("  1. Review generated branching worlds")
    print("  2. Generate images: python world_model_bench_agent/test_image_generator.py --world <world_file>")
    print("  3. Generate videos: python world_model_bench_agent/test_video_generator.py --world <image_world_file>")
    print("=" * 80)

if __name__ == "__main__":
    expand_all_linear_worlds()

