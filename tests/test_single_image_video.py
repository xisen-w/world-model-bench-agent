#!/usr/bin/env python3
"""Test simpler video generation - image-to-video (single image start)."""

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

print("=" * 70)
print("SIMPLE VIDEO TEST - Image-to-Video")
print("=" * 70)

# Initialize Veo
print("\nInitializing Veo...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(api_key=api_key, client=client, acknowledged_paid_feature=True)

# Upload the first apple image
print("\nUploading apple image...")
image_path = "generated_images/apple_eating_images/s0_000.png"
uploaded_file = client.files.upload(file=image_path)
print(f"Uploaded: {uploaded_file.name}")

# Generate video from this single image
print("\nGenerating video from image...")
print("Prompt: 'A hand reaches in and cuts the apple in half with a knife'")
print("This will take 2-5 minutes...")

try:
    result = veo.generate_video_with_image(
        prompt="A hand reaches in and cuts the apple in half with a knife, revealing the inside",
        start_image=uploaded_file,
        aspect_ratio="16:9",
        resolution="720p",
        number_of_videos=1
    )

    print(f"\n  Result ID: {result.id}")
    print(f"  Status: {result.status}")
    print(f"  Progress: {result.progress * 100:.1f}%")

    # Download video
    if result.videos:
        with open("test_apple_single_video.mp4", 'wb') as f:
            f.write(result.videos[0])
        print(f"\nSUCCESS! Video saved to: test_apple_single_video.mp4")
    else:
        print("\nERROR: No video data returned")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
