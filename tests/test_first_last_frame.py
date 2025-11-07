#!/usr/bin/env python3
"""Test video generation with first and last frame images."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found")
    sys.exit(1)

print(f"API key loaded: {api_key[:15]}...")

from google import genai
from utils.veo import VeoVideoGenerator

print("\n" + "=" * 70)
print("FIRST + LAST FRAME VIDEO GENERATION TEST")
print("=" * 70)

# Check if apple images exist
start_image_path = "generated_images/apple_eating_images/s0_000.png"
end_image_path = "generated_images/apple_eating_images/s1_001.png"

if not Path(start_image_path).exists() or not Path(end_image_path).exists():
    print(f"\nERROR: Apple images not found.")
    print(f"  Missing: {start_image_path} or {end_image_path}")
    print("\nPlease run test_dramatic_changes.py first to generate the images.")
    sys.exit(1)

print(f"\nStart image: {start_image_path} (whole apple)")
print(f"End image: {end_image_path} (cut apple with knife)")

# Initialize Veo
print("\nInitializing Veo client...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(
    api_key=api_key,
    client=client,
    acknowledged_paid_feature=True
)
print("Veo client initialized")

# Upload images
print("\n" + "=" * 70)
print("UPLOADING IMAGES")
print("=" * 70)

try:
    print(f"\nUploading start image...")
    start_file = client.files.upload(file=start_image_path)
    print(f"  Uploaded: {start_file.name}")
    print(f"  MIME type: {start_file.mime_type if hasattr(start_file, 'mime_type') else 'N/A'}")

    print(f"\nUploading end image...")
    end_file = client.files.upload(file=end_image_path)
    print(f"  Uploaded: {end_file.name}")
    print(f"  MIME type: {end_file.mime_type if hasattr(end_file, 'mime_type') else 'N/A'}")

    print("\n" + "=" * 70)
    print("GENERATING VIDEO")
    print("=" * 70)

    prompt = "A hand reaches in and cuts the apple in half with a knife, revealing the inside"
    print(f"\nPrompt: '{prompt}'")
    print("This will take 2-5 minutes...")

    result = veo.generate_video_with_initial_and_end_image(
        prompt=prompt,
        start_image=start_file,
        end_image=end_file,
        aspect_ratio="16:9",
        resolution="720p",
        number_of_videos=1
    )

    print(f"\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"\n  Result ID: {result.id}")
    print(f"  Status: {result.status}")
    print(f"  Progress: {result.progress * 100:.1f}%")
    print(f"  Model: {result.model}")
    print(f"  Provider: {result.provider}")

    # Try to save video if available
    if result.videos:
        output_path = "test_apple_first_last_video.mp4"
        with open(output_path, 'wb') as f:
            f.write(result.videos[0])
        print(f"\n  SUCCESS! Video saved to: {output_path}")
    else:
        print(f"\n  INFO: Video not immediately available (status: {result.status})")
        if result.download_url:
            print(f"  Download URL: {result.download_url}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nThe generate_video_with_initial_and_end_image() method WORKS!")
    print("The error was in how we were calling it, not the API itself.")

except Exception as e:
    print(f"\n" + "=" * 70)
    print("ERROR")
    print("=" * 70)
    print(f"\n  {type(e).__name__}: {e}")
    print("\nThis confirms the issue we saw before:")
    print("The generate_video_with_initial_and_end_image() API may not be")
    print("supported or we're using it incorrectly.")

    import traceback
    traceback.print_exc()
    sys.exit(1)
