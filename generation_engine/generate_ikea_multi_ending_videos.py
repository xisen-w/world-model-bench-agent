#!/usr/bin/env python3
"""
Generate videos for IKEA desk assembly multi-ending world.

This creates videos for all transitions in the multi-ending world with:
- 3 success endings (perfect, good, acceptable)
- 3 failure endings (gave up, collapsed, wrong assembly)
- All intermediate transitions
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
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.image_world_generator import ImageWorld

# Load the IKEA multi-ending image world
print("=" * 70)
print("IKEA DESK ASSEMBLY - MULTI-ENDING VIDEO GENERATION")
print("=" * 70)

# Try to find the image world file
possible_paths = [
    "worlds/image_worlds/ikea_desk_multi_ending_image_world.json",
    "ikea_desk_multi_ending_image_world.json",
    "ikea_desk_multi_ending_full_image_world.json"
]

image_world_file = None
for path in possible_paths:
    if Path(path).exists():
        image_world_file = path
        break

if not image_world_file:
    print(f"ERROR: Could not find IKEA multi-ending image world JSON!")
    print(f"Tried: {possible_paths}")
    print("\nPlease run generate_ikea_multi_ending_images.py first.")
    sys.exit(1)

print(f"\nLoading image world from: {image_world_file}")
image_world = ImageWorld.load(image_world_file)

print(f"\nImage World Summary:")
print(f"  Name: {image_world.name}")
print(f"  States: {len(image_world.states)}")
print(f"  Transitions: {len(image_world.transitions)}")

# Analyze the structure
print(f"\n  State Details:")
initial_states = [s for s in image_world.states if s.parent_state_id is None]
intermediate_states = [s for s in image_world.states if s.parent_state_id and s.state_id not in ['s_perfect', 's_good', 's_acceptable', 's_gave_up', 's_collapsed', 's_wrong']]
final_states = [s for s in image_world.states if s.state_id in ['s_perfect', 's_good', 's_acceptable', 's_gave_up', 's_collapsed', 's_wrong']]

print(f"    Initial: {len(initial_states)}")
print(f"    Intermediate: {len(intermediate_states)}")
print(f"    Final (endings): {len(final_states)}")

print(f"\n  All Transitions to Generate:")
for i, trans in enumerate(image_world.transitions, 1):
    print(f"    {i:2d}. {trans.start_state_id:15s} --[{trans.action_id}]--> {trans.end_state_id}")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Generate videos for ALL TRANSITIONS
print("\n" + "=" * 70)
print("GENERATING VIDEOS FOR ALL TRANSITIONS")
print("=" * 70)
print(f"\nThis will generate {len(image_world.transitions)} videos")
print(f"Estimated time: ~{len(image_world.transitions) * 8} minutes (assuming 8 min per video)")
print(f"Estimated cost: ~${len(image_world.transitions) * 0.10:.2f} (assuming $0.10 per video)")
print("\nStarting generation...")

generator = VideoWorldGenerator(
    veo_client=veo,
    output_dir="generated_videos",
    aspect_ratio="16:9",
    resolution="720p",
    use_enhanced_prompts=True  # Use cinematic prompt enhancement
)

try:
    video_world = generator.generate_video_world(
        image_world=image_world,
        strategy="all_transitions",  # Generate ALL transitions including all endings
        number_of_videos=1
    )

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)

    print(f"\nGenerated {len(video_world.transitions)} videos:")
    successful = 0
    failed = 0

    for i, video_trans in enumerate(video_world.transitions, 1):
        status = "✓" if video_trans.video_path else "✗"
        if video_trans.video_path:
            successful += 1
        else:
            failed += 1

        print(f"  {status} {i:2d}. {video_trans.start_state_id:15s} → {video_trans.end_state_id}")
        if video_trans.video_path:
            print(f"        Video: {video_trans.video_path}")

    # Save the video world
    output_file = "ikea_desk_multi_ending_video_world.json"
    video_world.save(output_file)
    print(f"\n\nSaved video world to: {output_file}")

    print("\nVideos saved to:")
    print(f"  generated_videos/{video_world.name}/")

    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    print(f"Total transitions: {len(image_world.transitions)}")
    print(f"Videos generated: {successful}")
    print(f"Failed: {failed}")
    if len(image_world.transitions) > 0:
        print(f"Success rate: {successful/len(image_world.transitions)*100:.1f}%")

    if successful == len(image_world.transitions):
        print("\n✅ All videos generated successfully!")
    else:
        print(f"\n⚠️  {failed} video(s) failed to generate")

    print("\n" + "=" * 70)
    print("WORLD STRUCTURE WITH VIDEOS")
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
                      quality=1.0    quality=0 [quick]  quality=0  quality=0.6
                                                  |                   |
                                              s_good              [test]
                                            (SUCCESS)               |
                                            quality=0.8         s_collapsed
                                                               (FAILURE)
                                                               quality=0

    All transitions now have videos connecting the states!
    """)

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
