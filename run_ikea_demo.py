#!/usr/bin/env python3
"""
Non-interactive demo viewer for IKEA desk multi-ending world.

Automatically loads the IKEA multi-ending image world and displays:
- The world structure
- All states and their images
- All transitions
- Metadata for each state
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from world_model_bench_agent.benchmark_curation import World
from world_model_bench_agent.image_world_generator import ImageWorld
import subprocess
import os

def open_image(image_path: str):
    """Open image in default viewer."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(image_path)], check=False)
        elif sys.platform == "win32":  # Windows
            os.startfile(str(image_path))
        else:  # Linux
            subprocess.run(["xdg-open", str(image_path)], check=False)
        return True
    except Exception as e:
        print(f"   [Could not open image: {e}]")
        return False

def main():
    print("=" * 70)
    print("🎮 IKEA DESK ASSEMBLY - MULTI-ENDING WORLD DEMO")
    print("=" * 70)

    # Load image world
    image_world_path = "worlds/image_worlds/ikea_desk_multi_ending_image_world.json"
    print(f"\n📂 Loading image world: {image_world_path}")

    try:
        image_world = ImageWorld.load(image_world_path)
        print(f"✅ Image world loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading image world: {e}")
        return 1

    # Load text world
    text_world_path = "worlds/llm_worlds/ikea_desk_multi_ending_world.json"
    print(f"📂 Loading text world: {text_world_path}")

    try:
        text_world = World.load(text_world_path)
        print(f"✅ Text world loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading text world: {e}")
        return 1

    # Display world summary
    print("\n" + "=" * 70)
    print("📊 WORLD SUMMARY")
    print("=" * 70)
    print(f"\nWorld Name: {image_world.name}")
    print(f"Total States: {len(image_world.states)}")
    print(f"Total Transitions: {len(image_world.transitions)}")

    # Categorize states
    initial_states = [s for s in image_world.states if s.parent_state_id is None]
    final_states = [s for s in image_world.states if s.state_id in ['s_perfect', 's_good', 's_acceptable', 's_gave_up', 's_collapsed', 's_wrong_assembly']]
    intermediate_states = [s for s in image_world.states if s not in initial_states and s not in final_states]

    print(f"\nState Breakdown:")
    print(f"  Initial: {len(initial_states)}")
    print(f"  Intermediate: {len(intermediate_states)}")
    print(f"  Final (Endings): {len(final_states)}")

    # Display world structure
    print("\n" + "=" * 70)
    print("🌳 WORLD STRUCTURE")
    print("=" * 70)
    print("""
                                    s0 (unopened box)
                                    /              \\
                            [read manual]      [skip manual]
                                /                          \\
                              s1a                          s1b
                        (prepared, read)          (scattered, skipped)
                              |                             |
                        [follow steps]                   [wing it]
                              |                             |
                              s2a                          s2b
                        (organized)                    (confused)
                              |                        /    |    \\
                       [persist good]           [frustrated] [wrong parts]
                              |                      |        |
                              s3a                   s2c      s3c
                        (aligned)              (frustrated)  (wrong screws)
                              |                  /   \\         |    \\
                       [perfect finish]    [quit] [rush]   [rush] [sloppy]
                              |              |       |        |      |
                          s_perfect      s_gave_up  s3b  s_wrong  s_acceptable
                          (SUCCESS)      (FAILURE)   |   (FAILURE)  (SUCCESS)
                                                     |                |
                                                 s_good           [test]
                                                (SUCCESS)            |
                                                                 s_collapsed
                                                                 (FAILURE)
    """)

    # Display all states with images
    print("\n" + "=" * 70)
    print("🖼️  ALL STATES WITH IMAGES")
    print("=" * 70)

    for i, state in enumerate(image_world.states, 1):
        # Find corresponding text state for description
        text_state = None
        for ts in text_world.states:
            if ts.state_id == state.state_id:
                text_state = ts
                break

        print(f"\n{i}. State ID: {state.state_id}")
        print(f"   Image: {state.image_path}")

        if text_state:
            print(f"   Description: {text_state.description}")

            # Display metadata
            if text_state.metadata:
                print(f"   Metadata:")
                for key, value in text_state.metadata.items():
                    if key == 'assembly_progress':
                        progress_bar = '█' * int(value * 20) + '░' * (20 - int(value * 20))
                        print(f"      {key}: [{progress_bar}] {value*100:.0f}%")
                    elif key == 'quality':
                        stars = '⭐' * int(value * 5)
                        print(f"      {key}: {stars} ({value})")
                    elif key == 'outcome':
                        emoji = '✅' if value == 'success' else '❌'
                        print(f"      {key}: {emoji} {value}")
                    else:
                        print(f"      {key}: {value}")

    # Display all transitions
    print("\n" + "=" * 70)
    print("🔀 ALL TRANSITIONS")
    print("=" * 70)

    for i, trans in enumerate(image_world.transitions, 1):
        print(f"\n{i:2d}. {trans.start_state_id:15s} --[{trans.action_id}]--> {trans.end_state_id}")
        print(f"    Action: {trans.action_description}")
        if hasattr(trans, 'generation_prompt') and trans.generation_prompt:
            print(f"    Prompt: {trans.generation_prompt[:100]}...")

    # Display final endings
    print("\n" + "=" * 70)
    print("🏁 FINAL ENDINGS")
    print("=" * 70)

    endings = {
        's_perfect': {'name': 'Perfect Assembly', 'emoji': '✅', 'quality': 1.0},
        's_good': {'name': 'Good Assembly', 'emoji': '✅', 'quality': 0.8},
        's_acceptable': {'name': 'Acceptable Assembly', 'emoji': '⚠️', 'quality': 0.6},
        's_gave_up': {'name': 'Gave Up', 'emoji': '❌', 'quality': 0.0},
        's_collapsed': {'name': 'Collapsed', 'emoji': '❌', 'quality': 0.0},
        's_wrong_assembly': {'name': 'Wrong Assembly', 'emoji': '❌', 'quality': 0.0}
    }

    for state_id, info in endings.items():
        state = None
        for s in image_world.states:
            if s.state_id == state_id:
                state = s
                break

        if state:
            print(f"\n{info['emoji']} {info['name']} ({state_id})")
            print(f"   Quality: {info['quality']}")
            print(f"   Image: {state.image_path}")

    # Ask if user wants to open images
    print("\n" + "=" * 70)
    print("📸 IMAGE VIEWING")
    print("=" * 70)
    print("\nDo you want to open all images in sequence?")
    print("This will open each state's image in your default viewer.")

    try:
        response = input("\nOpen images? (y/n): ").strip().lower()

        if response == 'y':
            print("\nOpening images in sequence...")
            print("(Close each image to proceed to the next)\n")

            for i, state in enumerate(sorted(image_world.states, key=lambda s: s.state_id), 1):
                if state.image_path and Path(state.image_path).exists():
                    print(f"{i}/{len(image_world.states)}: {state.state_id}")
                    open_image(state.image_path)
                    input("   Press Enter to continue to next image...")

            print("\n✅ All images displayed!")
        else:
            print("\nSkipping image viewing.")

    except EOFError:
        print("\n\n(Running in non-interactive mode - skipping image viewing)")

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print("\nTo interactively explore the world, run:")
    print("  python3 interactive_image_demo.py")
    print("\nAnd select option 5: ikea_desk_multi_ending_image_world.json")

    return 0

if __name__ == "__main__":
    sys.exit(main())
