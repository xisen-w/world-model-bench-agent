#!/usr/bin/env python3
"""
Test script for LLM World Generator.

Tests the two-step world generation process:
1. Generate linear world from description
2. Expand to branching world with multiple endings
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from the project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Debug: Verify API key is loaded
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print(f"ERROR: GEMINI_KEY not found in environment")
    print(f"Tried loading from: {env_path}")
    print(f"File exists: {env_path.exists()}")
    sys.exit(1)
else:
    print(f"API key loaded successfully (first 10 chars): {api_key[:10]}...")

from world_model_bench_agent.llm_world_generator import LLMWorldGenerator
from world_model_bench_agent.benchmark_curation import print_world_summary


def test_coffee_scenario():
    """Test with coffee making scenario."""
    print("=" * 70)
    print("TEST: Coffee Making Scenario")
    print("=" * 70)

    generator = LLMWorldGenerator()

    # Step 1: Generate linear world
    print("\n" + "=" * 70)
    print("STEP 1: Generating Linear World")
    print("=" * 70)

    linear_world = generator.generate_linear_world(
        scenario="coffee_making",
        initial_description="Kitchen with coffee machine, coffee beans, water, and milk on the counter",
        goal_description="A perfect latte with beautiful latte art in a ceramic cup",
        num_steps=6,
        context="Home coffee making process for a beginner"
    )

    print("\n" + "-" * 70)
    print("Linear World Summary:")
    print("-" * 70)
    print_world_summary(linear_world)

    # Save linear world
    linear_world.save("coffee_linear_world.json")
    print(f"\nLinear world saved to: coffee_linear_world.json")

    # Step 2: Expand to branching world
    print("\n" + "=" * 70)
    print("STEP 2: Expanding to Branching World")
    print("=" * 70)

    branching_world = generator.expand_to_branching_world(
        linear_world=linear_world,
        total_states=25,
        num_endings=6,
        success_endings=4,  # Perfect, Good, Acceptable, Drinkable
        failure_endings=2,  # Burnt coffee, Spilled everywhere
        branching_points=4
    )

    print("\n" + "-" * 70)
    print("Branching World Summary:")
    print("-" * 70)
    print_world_summary(branching_world)

    # Show outcome analysis
    print("\n" + "-" * 70)
    print("Outcome Analysis:")
    print("-" * 70)
    print(f"Total final states: {len(branching_world.get_final_states())}")
    print(f"Goal states (successes): {len(branching_world.goal_states)}")
    print(f"Failure states: {len(branching_world.get_final_states()) - len(branching_world.goal_states)}")

    print("\nGoal States:")
    for i, goal in enumerate(branching_world.goal_states, 1):
        quality = goal.metadata.get("quality", "N/A")
        print(f"  {i}. [{goal.state_id}] Quality: {quality}")
        print(f"      {goal.description[:80]}...")

    print("\nFailure States:")
    all_final = set(branching_world.get_final_states())
    goal_set = set(branching_world.goal_states)
    failures = all_final - goal_set
    for i, failure in enumerate(failures, 1):
        quality = failure.metadata.get("quality", "N/A")
        print(f"  {i}. [{failure.state_id}] Quality: {quality}")
        print(f"      {failure.description[:80]}...")

    # Show path statistics
    successful_paths = branching_world.get_successful_paths()
    failed_paths = branching_world.get_failed_paths()

    print(f"\nPath Statistics:")
    print(f"  Successful paths: {len(successful_paths)}")
    print(f"  Failed paths: {len(failed_paths)}")
    print(f"  Total paths: {len(successful_paths) + len(failed_paths)}")

    # Show decision points
    decision_points = branching_world.get_decision_points()
    if decision_points:
        print(f"\nDecision Points: {len(decision_points)}")
        for i, (state, actions) in enumerate(decision_points[:3], 1):
            print(f"\n  {i}. At: {state.description[:60]}...")
            print(f"     Choices ({len(actions)}):")
            for action in actions[:3]:  # Show first 3 actions
                print(f"       - {action.description[:70]}...")

    # Save branching world
    branching_world.save("coffee_branching_world.json")
    print(f"\nBranching world saved to: coffee_branching_world.json")

    return linear_world, branching_world


def test_ikea_scenario():
    """Test with IKEA assembly scenario."""
    print("\n\n" + "=" * 70)
    print("TEST: IKEA Bookshelf Assembly Scenario")
    print("=" * 70)

    generator = LLMWorldGenerator()

    # Step 1: Generate linear world
    print("\n" + "=" * 70)
    print("STEP 1: Generating Linear World")
    print("=" * 70)

    linear_world = generator.generate_linear_world(
        scenario="ikea_bookshelf_assembly",
        initial_description="Unopened IKEA BILLY bookshelf box with instruction manual",
        goal_description="Fully assembled bookshelf standing upright against the wall, stable and ready to use",
        num_steps=7,
        context="Home furniture assembly by a novice"
    )

    print("\n" + "-" * 70)
    print("Linear World Summary:")
    print("-" * 70)
    print_world_summary(linear_world)

    # Save
    linear_world.save("bookshelf_linear_world.json")
    print(f"\nLinear world saved to: bookshelf_linear_world.json")

    # Step 2: Expand
    print("\n" + "=" * 70)
    print("STEP 2: Expanding to Branching World")
    print("=" * 70)

    branching_world = generator.expand_to_branching_world(
        linear_world=linear_world,
        total_states=30,
        num_endings=7,
        success_endings=4,
        failure_endings=3,
        branching_points=5
    )

    print_world_summary(branching_world)

    # Save
    branching_world.save("bookshelf_branching_world.json")
    print(f"\nBranching world saved to: bookshelf_branching_world.json")

    return linear_world, branching_world


def test_quick_generate():
    """Test the quick_generate convenience function."""
    print("\n\n" + "=" * 70)
    print("TEST: Quick Generate (Cooking Pasta)")
    print("=" * 70)

    from world_model_bench_agent.llm_world_generator import quick_generate

    world = quick_generate(
        scenario="cooking_pasta",
        initial="Uncooked pasta, pot, water, salt, and tomato sauce on the counter",
        goal="Plate of perfectly cooked pasta with sauce, ready to eat",
        linear_steps=5,
        total_states=18
    )

    print("\n" + "-" * 70)
    print("Generated World Summary:")
    print("-" * 70)
    print_world_summary(world)

    world.save("pasta_world.json")
    print(f"\nWorld saved to: pasta_world.json")

    return world


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("LLM WORLD GENERATOR TEST SUITE")
    print("=" * 70)
    print("\nThis will test the automated world generation using Gemini LLM.")
    print("It will make several API calls (estimated cost: < $0.01)")

    # Check if running interactively
    import sys
    if sys.stdin.isatty():
        response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
        if response != "yes":
            print("Test cancelled.")
            return 0
    else:
        print("\nNon-interactive mode detected. Add '--yes' flag to proceed.")
        if "--yes" not in sys.argv:
            print("Test cancelled. Run with --yes flag to proceed.")
            return 0
        print("Proceeding with tests...")

    try:
        # Test 1: Coffee making
        coffee_linear, coffee_branching = test_coffee_scenario()

        # Test 2: IKEA assembly
        ikea_linear, ikea_branching = test_ikea_scenario()

        # Test 3: Quick generate
        pasta_world = test_quick_generate()

        # Summary
        print("\n\n" + "=" * 70)
        print("TEST SUITE COMPLETE")
        print("=" * 70)
        print("\nGenerated Worlds:")
        print("  1. Coffee Making:")
        print(f"     - Linear: {len(coffee_linear.states)} states")
        print(f"     - Branching: {len(coffee_branching.states)} states, "
              f"{len(coffee_branching.get_successful_paths())} success paths, "
              f"{len(coffee_branching.get_failed_paths())} failure paths")
        print("  2. IKEA Bookshelf:")
        print(f"     - Linear: {len(ikea_linear.states)} states")
        print(f"     - Branching: {len(ikea_branching.states)} states")
        print("  3. Cooking Pasta:")
        print(f"     - Branching: {len(pasta_world.states)} states")

        print("\nGenerated Files:")
        print("  - coffee_linear_world.json")
        print("  - coffee_branching_world.json")
        print("  - bookshelf_linear_world.json")
        print("  - bookshelf_branching_world.json")
        print("  - pasta_world.json")

        print("\nAll tests passed successfully!")
        print("\nYou can now:")
        print("  1. Explore the generated worlds with: python world_model_bench_agent/interactive_demo.py")
        print("  2. Use them for video generation with VEO")
        print("  3. Create more worlds with different scenarios")

        return 0

    except Exception as e:
        print(f"\n\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
