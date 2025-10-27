#!/usr/bin/env python3
"""Test video generation with correct image format."""

import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import io

sys.path.insert(0, str(Path(__file__).parent))

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

from google import genai
from google.genai import types

print("=" * 70)
print("CORRECT FORMAT TEST: Image-to-Video with types.Image()")
print("=" * 70)

# Check if apple images exist
start_image_path = "generated_images/apple_eating_images/s0_000.png"
end_image_path = "generated_images/apple_eating_images/s1_001.png"

if not Path(start_image_path).exists() or not Path(end_image_path).exists():
    print(f"\nERROR: Apple images not found.")
    sys.exit(1)

print(f"\nStart image: {start_image_path}")
print(f"End image: {end_image_path}")

# Load and convert images to bytes
print("\nLoading images...")
start_im = Image.open(start_image_path)
end_im = Image.open(end_image_path)

# Convert to bytes
start_bytes_io = io.BytesIO()
start_im.save(start_bytes_io, format='PNG')
start_image_bytes = start_bytes_io.getvalue()

end_bytes_io = io.BytesIO()
end_im.save(end_bytes_io, format='PNG')
end_image_bytes = end_bytes_io.getvalue()

print(f"Start image bytes: {len(start_image_bytes)} bytes")
print(f"End image bytes: {len(end_image_bytes)} bytes")

# Initialize client
print("\nInitializing Gemini client...")
client = genai.Client(api_key=api_key)

# Create types.Image objects
print("\nCreating types.Image objects...")
start_image_obj = types.Image(image_bytes=start_image_bytes, mime_type="image/png")
end_image_obj = types.Image(image_bytes=end_image_bytes, mime_type="image/png")

print(f"Start image object type: {type(start_image_obj)}")
print(f"End image object type: {type(end_image_obj)}")

# Generate video
print("\n" + "=" * 70)
print("GENERATING VIDEO")
print("=" * 70)

VEO_MODEL_ID = "veo-3.1-fast-generate-preview"
prompt = "A hand reaches in and cuts the apple in half with a knife, revealing the inside"
negative_prompt = "ugly, low quality, blurry"
aspect_ratio = "16:9"
resolution = "720p"

print(f"\nModel: {VEO_MODEL_ID}")
print(f"Prompt: {prompt}")
print(f"Aspect ratio: {aspect_ratio}")
print(f"Resolution: {resolution}")

try:
    # Try with just start image first
    print("\nCalling generate_videos with start image...")
    operation = client.models.generate_videos(
        model=VEO_MODEL_ID,
        prompt=prompt,
        image=start_image_obj,
        config=types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            negative_prompt=negative_prompt,
        ),
    )

    print(f"\nOperation created: {operation.name}")
    print(f"Done: {operation.done}")

    # Poll for completion
    print("\nWaiting for video generation (2-5 minutes)...")
    poll_count = 0
    while not operation.done:
        time.sleep(20)
        poll_count += 1
        operation = client.operations.get(operation)
        print(f"  Poll {poll_count}: {operation.done}, metadata: {operation.metadata if hasattr(operation, 'metadata') else 'N/A'}")

    print("\n" + "=" * 70)
    print("VIDEO GENERATED!")
    print("=" * 70)

    print(f"\nResult: {operation.result}")

    if hasattr(operation.result, 'generated_videos'):
        print(f"Generated videos: {len(operation.result.generated_videos)}")

        for n, generated_video in enumerate(operation.result.generated_videos):
            output_path = f'test_correct_format_video{n}.mp4'
            print(f"\nSaving video {n} to {output_path}...")

            # Download and save
            video_file = client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            print(f"  SUCCESS! Video saved to {output_path}")
    else:
        print("No generated_videos in result")

    print("\n" + "=" * 70)
    print("SUCCESS! IMAGE-TO-VIDEO WORKS WITH CORRECT FORMAT!")
    print("=" * 70)

except Exception as e:
    print(f"\n" + "=" * 70)
    print("ERROR")
    print("=" * 70)
    print(f"\n{type(e).__name__}: {e}")

    import traceback
    traceback.print_exc()
    sys.exit(1)
