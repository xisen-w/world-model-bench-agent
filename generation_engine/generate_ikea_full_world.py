#!/usr/bin/env python3
"""
Generate complete IKEA desk assembly world with ALL paths and endings.

This creates the full branching world with:
- 14 states
- 15 transitions
- 3 success endings (perfect, good, acceptable)
- 3 failure endings (gave up, collapsed, wrong assembly)
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World

# Load the text world
print("=" * 70)
print("IKEA DESK ASSEMBLY - FULL WORLD GENERATION")
print("=" * 70)

world_file = "ikea_desk_multi_ending_world.json"
print(f"\nLoading world from: {world_file}")
text_world = World.load(world_file)

print(f"\nWorld Summary:")
print(f"  Name: {text_world.name}")
print(f"  States: {len(text_world.states)}")
print(f"  Actions: {len(text_world.actions)}")
print(f"  Transitions: {len(text_world.transitions)}")
print(f"  Initial State: {text_world.initial_state.state_id}")
print(f"  Goal States: {[s.state_id for s in text_world.goal_states]}")
print(f"  Final States: {[s.state_id for s in text_world.final_states]}")

# Analyze paths
paths = text_world.get_all_paths()
print(f"\n  Total Paths to Success: {len(paths)}")
for i, path in enumerate(paths, 1):
    path_states = [text_world.initial_state.state_id]
    for t in path:
        path_states.append(t.end_state.state_id)
    print(f"    Path {i}: {' → '.join(path_states)} ({len(path)} transitions)")

# Count endings
success_endings = [s for s in text_world.final_states if s.metadata.get('outcome') == 'success']
failure_endings = [s for s in text_world.final_states if s.metadata.get('outcome') == 'failure']
print(f"\n  Success Endings: {len(success_endings)}")
for s in success_endings:
    quality = s.metadata.get('quality', 0)
    print(f"    - {s.state_id}: {s.description[:50]}... (quality: {quality})")
print(f"\n  Failure Endings: {len(failure_endings)}")
for s in failure_endings:
    quality = s.metadata.get('quality', 0)
    print(f"    - {s.state_id}: {s.description[:50]}... (quality: {quality})")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Generate images for FULL WORLD
print("\n" + "=" * 70)
print("GENERATING IMAGES FOR FULL WORLD")
print("=" * 70)
print(f"\nThis will generate {len(text_world.states)} images")
print(f"Estimated cost: ~${len(text_world.states) * 0.0024:.3f}")
print(f"Estimated time: ~{len(text_world.states) * 15} seconds")
print("\nStarting generation...")

generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images",
    camera_perspective="first_person_ego",
    aspect_ratio="16:9"
)

try:
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy="full_world"  # Generate ALL states
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nGenerated {len(image_world.states)} images:")

    # Group by category
    initial_states = [s for s in image_world.states if s.parent_state_id is None]
    intermediate_states = [s for s in image_world.states if s.parent_state_id and s.state_id not in [fs.state_id for fs in text_world.final_states]]
    final_states = [s for s in image_world.states if s.state_id in [fs.state_id for fs in text_world.final_states]]

    print(f"\n  Initial State ({len(initial_states)}):")
    for s in initial_states:
        print(f"    [{s.state_id}] {s.text_description[:60]}...")

    print(f"\n  Intermediate States ({len(intermediate_states)}):")
    for s in intermediate_states:
        print(f"    [{s.state_id}] {s.text_description[:60]}...")
        print(f"        from {s.parent_state_id} via {s.parent_action_id}")

    print(f"\n  Final States ({len(final_states)}):")
    for s in final_states:
        outcome = "SUCCESS" if any(fs.state_id == s.state_id and fs.metadata.get('outcome') == 'success' for fs in text_world.final_states) else "FAILURE"
        print(f"    [{s.state_id}] {outcome}: {s.text_description[:60]}...")

    print(f"\n\nGenerated {len(image_world.transitions)} transitions:")
    for trans in image_world.transitions:
        print(f"  {trans.start_state_id} --[{trans.action_id}]--> {trans.end_state_id}")

    # Save the image world
    output_file = "ikea_desk_multi_ending_full_image_world.json"
    image_world.save(output_file)
    print(f"\n\nSaved to: {output_file}")

    print("\nImages saved to:")
    print(f"  generated_images/{image_world.name}/")

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(f"✓ Expected states: {len(text_world.states)}")
    print(f"✓ Generated states: {len(image_world.states)}")
    print(f"✓ Expected transitions: {len(text_world.transitions)}")
    print(f"✓ Generated transitions: {len(image_world.transitions)}")

    if len(image_world.states) == len(text_world.states):
        print("\n✅ All states generated successfully!")
    else:
        print(f"\n⚠️  State count mismatch!")

    if len(image_world.transitions) == len(text_world.transitions):
        print("✅ All transitions recorded successfully!")
    else:
        print(f"⚠️  Transition count mismatch!")

    print("\n" + "=" * 70)
    print("WORLD STRUCTURE")
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
                                             [quick/sloppy]        |
                                                  |            [test]
                                           s_good/acceptable     |
                                            (SUCCESS)        s_collapsed
                                                            (FAILURE)
    """)

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
