#!/usr/bin/env python3
"""
Test full world video generation - RESUMABLE version.

This version can resume from where it left off if interrupted by quota limits.
It saves progress after each successful video generation.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import json

sys.path.insert(0, str(Path(__file__).parent))

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

from google import genai
from utils.veo import VeoVideoGenerator
from world_model_bench_agent.video_world_generator import VideoWorldGenerator, VideoWorld
from world_model_bench_agent.image_world_generator import ImageWorld

# Progress tracking
PROGRESS_FILE = "video_generation_progress.json"

def load_progress():
    """Load generation progress."""
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed_transitions": [], "failed_transitions": []}

def save_progress(progress):
    """Save generation progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def transition_key(trans):
    """Create unique key for transition."""
    return f"{trans.start_state_id}_to_{trans.end_state_id}"

# Load the branching image world
print("=" * 70)
print("FULL WORLD VIDEO GENERATION (RESUMABLE)")
print("=" * 70)

image_world_file = "apple_eating_branching_image_world.json"
output_file = "apple_eating_branching_video_world.json"

print(f"\nLoading image world from: {image_world_file}")

if not Path(image_world_file).exists():
    print(f"ERROR: {image_world_file} not found!")
    print("Please run test_full_apple_world.py first to generate the image world.")
    sys.exit(1)

image_world = ImageWorld.load(image_world_file)

print(f"\nImage World Summary:")
print(f"  Name: {image_world.name}")
print(f"  States: {len(image_world.states)}")
print(f"  Transitions: {len(image_world.transitions)}")

# Load progress
progress = load_progress()
completed = set(progress["completed_transitions"])
failed = set(progress["failed_transitions"])

print(f"\n  Progress:")
print(f"    Completed: {len(completed)}/{len(image_world.transitions)}")
print(f"    Failed: {len(failed)}")
print(f"    Remaining: {len(image_world.transitions) - len(completed) - len(failed)}")

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

generator = VideoWorldGenerator(
    veo_client=veo,
    output_dir="generated_videos",
    use_enhanced_prompts=True
)

# Load existing video world if it exists
if Path(output_file).exists():
    print(f"\nLoading existing video world from: {output_file}")
    video_world = VideoWorld.load(output_file)
else:
    print(f"\nCreating new video world...")
    world_name = f"{image_world.name}_videos"
    world_dir = Path("generated_videos") / world_name
    world_dir.mkdir(exist_ok=True, parents=True)

    video_world = VideoWorld(
        name=world_name,
        image_world_source=image_world.name,
        states=image_world.states.copy(),
        generation_metadata={
            "model": veo.veo_model_id,
            "generation_strategy": "all_transitions",
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "number_of_videos_per_transition": 1
        }
    )

print("\n" + "=" * 70)
print("GENERATING VIDEOS (ONE AT A TIME)")
print("=" * 70)

successful = 0
skipped = 0
failed_count = 0

for i, transition in enumerate(image_world.transitions):
    key = transition_key(transition)

    print(f"\nTransition {i+1}/{len(image_world.transitions)}: {key}")
    print(f"  {transition.start_state_id} → {transition.end_state_id}")
    print(f"  Action: {transition.action_description}")

    # Skip if already completed
    if key in completed:
        print(f"  ✓ Already completed, skipping")
        skipped += 1
        continue

    # Skip if previously failed
    if key in failed:
        print(f"  ✗ Previously failed, skipping")
        failed_count += 1
        continue

    try:
        # Find states
        start_state = generator._find_state(image_world.states, transition.start_state_id)
        end_state = generator._find_state(image_world.states, transition.end_state_id)

        if not start_state or not end_state:
            print(f"  ✗ Could not find states, marking as failed")
            failed.add(key)
            progress["failed_transitions"].append(key)
            save_progress(progress)
            failed_count += 1
            continue

        # Generate video
        print(f"  Generating video...")
        world_dir = Path("generated_videos") / video_world.name

        video_transition = generator._generate_transition_video(
            start_state=start_state,
            end_state=end_state,
            action_description=transition.action_description,
            action_id=transition.action_id,
            world_dir=world_dir,
            index=i,
            number_of_videos=1
        )

        # Add to video world
        video_world.transitions.append(video_transition)

        # Mark as completed
        completed.add(key)
        progress["completed_transitions"].append(key)
        save_progress(progress)

        # Save video world after each success
        video_world.save(output_file)

        print(f"  ✓ SUCCESS! Saved to: {video_transition.video_path}")
        successful += 1

    except Exception as e:
        error_msg = str(e)
        print(f"  ✗ ERROR: {error_msg[:100]}...")

        # Check if quota error
        if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
            print(f"\n⚠️  QUOTA LIMIT REACHED")
            print(f"\nProgress saved to: {PROGRESS_FILE}")
            print(f"Run this script again later to resume from transition {i+1}")
            break
        else:
            # Mark as failed for other errors
            failed.add(key)
            progress["failed_transitions"].append(key)
            save_progress(progress)
            failed_count += 1

# Final summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total transitions: {len(image_world.transitions)}")
print(f"Successfully generated: {successful} (this run)")
print(f"Total completed: {len(completed)}")
print(f"Skipped (already done): {skipped}")
print(f"Failed: {failed_count}")
print(f"Remaining: {len(image_world.transitions) - len(completed) - len(failed)}")

if len(completed) == len(image_world.transitions):
    print("\n✅ All videos generated successfully!")
    print(f"Video world saved to: {output_file}")
    # Clean up progress file
    if Path(PROGRESS_FILE).exists():
        Path(PROGRESS_FILE).unlink()
        print(f"Progress file cleaned up")
else:
    remaining = len(image_world.transitions) - len(completed) - len(failed)
    print(f"\n⚠️  {remaining} video(s) still need to be generated")
    print(f"Progress saved to: {PROGRESS_FILE}")
    print(f"\nRun this script again to continue")

if Path(output_file).exists():
    print(f"\nPartial results saved to: {output_file}")
