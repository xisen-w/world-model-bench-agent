#!/usr/bin/env python3
"""Test enhanced prompt generation for video world."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

sys.path.insert(0, str(script_dir))

# Load environment
env_path = script_dir / ".env"
load_dotenv(env_path)

from world_model_bench_agent.image_world_generator import ImageWorld, ImageState
from world_model_bench_agent.video_world_generator import VideoWorldGenerator
from world_model_bench_agent.prompt_enhancer import PromptEnhancer
from utils.veo import VeoVideoGenerator
from google import genai

print("=" * 70)
print("TESTING ENHANCED PROMPT GENERATION")
print("=" * 70)

# Load the apple_eating world
world_file = script_dir / "apple_eating_image_world.json"
image_world = ImageWorld.load(str(world_file))

print(f"\nLoaded world: {image_world.name}")
print(f"States: {len(image_world.states)}")

# Get first transition
first_trans = image_world.transitions[0]
start_state = None
end_state = None

for state in image_world.states:
    if state.state_id == first_trans.start_state_id:
        start_state = state
    if state.state_id == first_trans.end_state_id:
        end_state = state

print(f"\nFirst transition:")
print(f"  {first_trans.start_state_id} --> {first_trans.end_state_id}")
print(f"  Action: {first_trans.action_description}")

# Test simple prompt
print("\n" + "=" * 70)
print("SIMPLE PROMPT (original)")
print("=" * 70)

simple_prompt = f"{first_trans.action_description}. "
simple_prompt += f"Smooth transition showing the action in progress. "
simple_prompt += f"Starting from: {start_state.text_description[:50]}... "
simple_prompt += f"Ending at: {end_state.text_description[:50]}..."

print(f"\n{simple_prompt}")
print(f"\nLength: {len(simple_prompt)} characters")

# Test enhanced prompt
print("\n" + "=" * 70)
print("ENHANCED PROMPT (with cinematic details)")
print("=" * 70)

enhancer = PromptEnhancer()
enhanced_prompt = enhancer.enhance_action_description(
    action=first_trans.action_description,
    context="domestic kitchen countertop"
)

print(f"\n{enhanced_prompt}")
print(f"\nLength: {len(enhanced_prompt)} characters")

# Show comparison
print("\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)
print(f"\nSimple prompt length: {len(simple_prompt)} chars")
print(f"Enhanced prompt length: {len(enhanced_prompt)} chars")
print(f"Enhancement factor: {len(enhanced_prompt) / len(simple_prompt):.1f}x")

# Test video generation with enhanced prompts
print("\n" + "=" * 70)
print("GENERATING VIDEO WITH ENHANCED PROMPTS")
print("=" * 70)

response = input("\nDo you want to generate a video with enhanced prompts? (yes/no): ").strip().lower()

if response == "yes":
    # Initialize Veo client
    print("\nInitializing Veo client...")
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        print("ERROR: GEMINI_KEY not found")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    veo_client = VeoVideoGenerator(
        api_key=api_key,
        client=client,
        acknowledged_paid_feature=True
    )

    # Initialize video generator WITH enhanced prompts
    video_gen_enhanced = VideoWorldGenerator(
        veo_client=veo_client,
        aspect_ratio="16:9",
        resolution="720p",
        output_dir="generated_videos_enhanced",
        use_enhanced_prompts=True  # Enable enhanced prompts
    )

    print("\nGenerating video with ENHANCED prompts...")
    try:
        video_world = video_gen_enhanced.generate_video_world(
            image_world=image_world,
            strategy="all_transitions"
        )

        video_world.save("apple_eating_world_videos_enhanced.json")

        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nGenerated {len(video_world.transitions)} videos with enhanced prompts")
        for trans in video_world.transitions:
            if trans.video_path:
                print(f"  - {trans.video_path}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nSkipping video generation")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
