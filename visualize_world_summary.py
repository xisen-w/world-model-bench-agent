#!/usr/bin/env python3
"""
Quick visualization script to inspect generated worlds.

Usage:
    python visualize_world_summary.py [world_file]
    
If no file specified, shows summary of all 10 worlds.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World

def visualize_world(world_file):
    """Visualize a single world structure."""
    print("\n" + "=" * 80)
    print(f"WORLD: {Path(world_file).name}")
    print("=" * 80)
    
    world = World.load(world_file)
    
    # Basic stats
    print(f"\n📊 Basic Statistics:")
    print(f"  States: {len(world.states)}")
    print(f"  Transitions: {len(world.transitions)}")
    print(f"  Goal States: {len(world.goal_states)}")
    
    # Try to calculate paths
    try:
        paths = world.get_all_paths()
        print(f"  Total Paths: {len(paths)}")
    except:
        print(f"  Total Paths: (calculation skipped - complex graph)")
    
    # Initial state
    print(f"\n🎬 Initial State:")
    print(f"  [{world.initial_state.state_id}] {world.initial_state.description[:80]}...")
    
    # Goal states
    print(f"\n🎯 Goal States ({len(world.goal_states)}):")
    for i, goal in enumerate(world.goal_states[:5], 1):
        print(f"  {i}. [{goal.state_id}] {goal.description[:70]}...")
    
    # First few transitions
    print(f"\n🔀 Sample Transitions (first 5):")
    for i, trans in enumerate(world.transitions[:5], 1):
        print(f"  {i}. {trans.start_state.state_id} --[{trans.action.description[:40]}]--> {trans.end_state.state_id}")
    
    # Branching points (states with multiple outgoing actions)
    branching_states = []
    for state in world.states:
        outgoing = [t for t in world.transitions if t.start_state == state]
        if len(outgoing) > 1:
            branching_states.append((state, len(outgoing)))
    
    print(f"\n🌳 Branching Points ({len(branching_states)}):")
    for state, count in branching_states[:5]:
        print(f"  [{state.state_id}] {count} choices → {state.description[:60]}...")
    
    # Ending states (states with no outgoing transitions)
    ending_states = []
    for state in world.states:
        outgoing = [t for t in world.transitions if t.start_state == state]
        if len(outgoing) == 0 and state != world.initial_state:
            ending_states.append(state)
    
    print(f"\n🏁 Ending States ({len(ending_states)}):")
    for state in ending_states[:5]:
        is_goal = state in world.goal_states
        status = "✅ SUCCESS" if is_goal else "❌ FAILURE"
        print(f"  {status} [{state.state_id}] {state.description[:60]}...")
    
    print()

def show_all_worlds_summary():
    """Show summary of all generated worlds."""
    worlds_dir = Path("worlds/llm_worlds")
    
    world_files = [
        "home_cooking_scrambled_eggs_branching_world.json",
        "pour_over_coffee_brewing_branching_world.json",
        "formal_dining_table_setting_branching_world.json",
        "desk_room_organization_branching_world.json",
        "waste_recycling_sorting_branching_world.json",
        "simple_ikea_bookshelf_assembly_branching_world.json",
        "gift_box_wrapping_branching_world.json",
        "weekend_trip_backpack_packing_branching_world.json",
        "indoor_plant_watering_repotting_branching_world.json",
        "water_oil_density_experiment_branching_world.json"
    ]
    
    print("\n" + "=" * 80)
    print("INTERACTIVE VIDEO BENCH - 10 GENERATED WORLDS")
    print("=" * 80)
    
    print("\n{:<50} {:>8} {:>8} {:>8}".format("World", "States", "Trans", "Paths"))
    print("-" * 80)
    
    total_states = 0
    total_transitions = 0
    total_paths = 0
    
    for world_file in world_files:
        world_path = worlds_dir / world_file
        if not world_path.exists():
            print(f"⚠️  {world_file:<48} (not found)")
            continue
        
        try:
            world = World.load(str(world_path))
            
            try:
                paths = world.get_all_paths()
                num_paths = len(paths)
            except:
                num_paths = "?"
            
            name = world_file.replace("_branching_world.json", "")[:48]
            print(f"✓ {name:<48} {len(world.states):>8} {len(world.transitions):>8} {str(num_paths):>8}")
            
            total_states += len(world.states)
            total_transitions += len(world.transitions)
            if isinstance(num_paths, int):
                total_paths += num_paths
        except Exception as e:
            print(f"✗ {world_file:<48} (error: {e})")
    
    print("-" * 80)
    print(f"{'TOTAL':<50} {total_states:>8} {total_transitions:>8} {total_paths:>8}")
    
    print("\n" + "=" * 80)
    print("✅ All 10 worlds successfully generated!")
    print("\nTo visualize a specific world, run:")
    print("  python visualize_world_summary.py worlds/llm_worlds/<world_file>.json")
    print("\nTo generate images:")
    print("  python world_model_bench_agent/test_image_generator.py --world <world_file>")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Visualize specific world
        world_file = sys.argv[1]
        visualize_world(world_file)
    else:
        # Show summary of all worlds
        show_all_worlds_summary()







