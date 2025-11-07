#!/usr/bin/env python3
"""
Generate images for cloth folding and sorting multi-ending world.

This creates images for all states in the cloth folding world with:
- 3 success endings (perfect, organized, acceptable)
- 3 failure endings (gave up, stuffed drawers, avalanche)
- All intermediate states showing folding progression
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
    print("ERROR: GEMINI_KEY not found in .env file")
    sys.exit(1)

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.image_world_generator import ImageWorldGenerator
from world_model_bench_agent.benchmark_curation import World

# Load the cloth folding text world
print("=" * 70)
print("CLOTH FOLDING AND SORTING - IMAGE GENERATION")
print("=" * 70)

text_world_file = "worlds/llm_worlds/cloth_folding_multi_ending_world.json"
print(f"\nLoading text world from: {text_world_file}")

if not Path(text_world_file).exists():
    print(f"ERROR: {text_world_file} not found!")
    sys.exit(1)

text_world = World.load(text_world_file)

print(f"\nText World Summary:")
print(f"  Name: {text_world.name}")
print(f"  States: {len(text_world.states)}")
print(f"  Actions: {len(text_world.actions)}")
print(f"  Transitions: {len(text_world.transitions)}")

# Display world structure
print("\n" + "=" * 70)
print("WORLD STRUCTURE")
print("=" * 70)
print("""
                                s0 (messy pile on bed)
                                /              \\
                        [sort carefully]    [skip sorting]
                            /                          \\
                          s1a                          s1b
                    (sorted by category)        (random grabbing)
                          |                             |
                    [fold methodical]            [fold random]
                          |                             |
                          s2a                          s2b
                    (professional folds)        (inconsistent)
                          |                        /    |    \\
                   [persist quality]        [frustrated] [sloppy]
                          |                      |        |
                          s3a                   s2c      s3b
                    (beautifully folded)    (frustrated) (unstable)
                      /       \\               /   \\         |    \\
              [perfect]    [good]      [quit] [rush]    [quick] [move]
                  |           |          |       |         |      |
              s_perfect  s_organized  s_gave_up s3c   s_acceptable s_avalanche
              (SUCCESS)   (SUCCESS)   (FAILURE)  |     (SUCCESS)  (FAILURE)
              quality=1.0 quality=0.8 quality=0.2 |    quality=0.6 quality=0.1
                                                  |
                                           [acceptable]
                                               or |
                                            [stuff]
                                               |  |
                                          s_acceptable s_stuffed
                                          (SUCCESS) (FAILURE)
                                          quality=0.6 quality=0.3
""")

# Initialize Veo and Image Generator
print("\nInitializing Veo and Image Generator...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

generator = ImageWorldGenerator(
    veo_client=veo,
    output_dir="generated_images",
    camera_perspective="first_person_ego",  # Single-person first-person egocentric view
    aspect_ratio="16:9",
    use_advanced_generation=True,  # Use advanced 5-step VLM/LLM pipeline with JSON logging
    llm_client=veo  # Use same veo client for LLM calls
)

# Generate images for the full world
print("\n" + "=" * 70)
print("GENERATING IMAGES FOR ALL STATES")
print("=" * 70)
print(f"\nThis will generate {len(text_world.states)} images")
print(f"Estimated time: ~{len(text_world.states) * 3} minutes (assuming 3 min per image)")
print("\nStarting generation...")

try:
    image_world = generator.generate_image_world(
        text_world=text_world,
        strategy="full_world",  # Generate ALL states, not just canonical path
        world_name=None  # Will auto-generate with timestamp
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nGenerated {len(image_world.states)} images:")
    for i, state in enumerate(image_world.states, 1):
        status = "✓" if state.image_path else "✗"
        print(f"  {status} {i:2d}. {state.state_id:20s} - {state.image_path}")

    # Save the image world
    output_file = "cloth_folding_multi_ending_image_world.json"
    image_world.save(output_file)
    print(f"\n\nSaved image world to: {output_file}")

    # Also save to worlds/image_worlds/ directory
    worlds_dir = Path("worlds/image_worlds")
    worlds_dir.mkdir(parents=True, exist_ok=True)
    worlds_output = worlds_dir / output_file
    image_world.save(str(worlds_output))
    print(f"Also saved to: {worlds_output}")

    print("\nImages saved to:")
    print(f"  {image_world.states[0].image_path.split('/')[0]}/{image_world.name}/")

    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    print(f"Total states: {len(text_world.states)}")
    print(f"Images generated: {len([s for s in image_world.states if s.image_path])}")
    print(f"Transitions: {len(image_world.transitions)}")
    print(f"Success endings: 3 (perfect, organized, acceptable)")
    print(f"Failure endings: 3 (gave up, stuffed, avalanche)")

    print("\n✅ All images generated successfully!")
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. View the world interactively:")
    print("   python3 interactive_image_demo.py")
    print("   (Select the cloth_folding_multi_ending_image_world.json)")
    print("\n2. Generate videos for transitions:")
    print("   python3 generate_cloth_folding_videos.py")
    print("\n3. View non-interactively:")
    print("   python3 run_cloth_folding_demo.py")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
