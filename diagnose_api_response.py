#!/usr/bin/env python3
"""
Diagnose what the Gemini API is returning when image generation fails.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    print("ERROR: GEMINI_KEY not found in .env file")
    sys.exit(1)

from google import genai
from google.genai import types

print("=" * 80)
print("🔍 DIAGNOSING GEMINI API IMAGE VARIATION RESPONSE")
print("=" * 80)

# Initialize client
client = genai.Client(api_key=api_key)

# Load the existing image that worked
base_image_path = "generated_images/coffee_making_egocentric/s1_001.png"
print(f"\n📂 Loading base image: {base_image_path}")

if not Path(base_image_path).exists():
    print(f"❌ Base image not found at: {base_image_path}")
    sys.exit(1)

base_image = Image.open(base_image_path)
print(f"✅ Loaded: {base_image.size} ({base_image.mode})")

# Try a simple variation
prompt = """A close-up view of coffee steeping in a French press on a kitchen counter.
The lid is now on the French press. A timer is visible nearby.
Maintain the same kitchen setting, lighting, and composition as the original image."""

print(f"\n📝 Test prompt: {prompt[:100]}...")

# Configure using types.GenerateContentConfig
try:
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspectRatio="16:9")
    )
except TypeError:
    # Fallback for older SDK versions
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9")
    )

print("\n🚀 Calling API with gemini-2.5-flash-image...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, base_image],
        config=config,
    )

    print("✅ API call completed!")

    # Inspect response structure
    print("\n" + "=" * 80)
    print("📊 RESPONSE STRUCTURE")
    print("=" * 80)

    print(f"\nResponse type: {type(response)}")
    print(f"Response attributes: {dir(response)}")

    # Check for parts
    print("\n🔍 Checking for 'parts' attribute...")
    parts = getattr(response, "parts", None)
    print(f"Parts: {parts}")

    # Check for candidates
    print("\n🔍 Checking for 'candidates' attribute...")
    if hasattr(response, "candidates"):
        candidates = getattr(response, "candidates")
        print(f"Candidates: {candidates}")
        print(f"Number of candidates: {len(candidates) if candidates else 0}")

        if candidates:
            print(f"\n🔍 First candidate:")
            first_candidate = candidates[0]
            print(f"  Type: {type(first_candidate)}")
            print(f"  Attributes: {dir(first_candidate)}")

            # Check finish_reason
            if hasattr(first_candidate, "finish_reason"):
                finish_reason = first_candidate.finish_reason
                print(f"  Finish reason: {finish_reason}")
                print(f"  Finish reason type: {type(finish_reason)}")

            # Check content
            if hasattr(first_candidate, "content"):
                content = first_candidate.content
                print(f"\n  Content: {content}")
                print(f"  Content type: {type(content)}")

                if hasattr(content, "parts"):
                    content_parts = content.parts
                    print(f"  Content.parts: {content_parts}")
                    print(f"  Number of parts: {len(content_parts) if content_parts else 0}")

                    if content_parts:
                        print(f"\n  First part:")
                        first_part = content_parts[0]
                        print(f"    Type: {type(first_part)}")
                        print(f"    Attributes: {dir(first_part)}")

                        # Check for image data
                        if hasattr(first_part, "inline_data"):
                            print(f"    ✅ Has inline_data")
                            inline_data = first_part.inline_data
                            print(f"    inline_data type: {type(inline_data)}")
                            if hasattr(inline_data, "data"):
                                data_length = len(inline_data.data) if inline_data.data else 0
                                print(f"    Data length: {data_length} bytes")
                        else:
                            print(f"    ❌ No inline_data")

                        if hasattr(first_part, "text"):
                            print(f"    Text: {first_part.text[:200] if first_part.text else 'None'}...")

            # Check safety ratings
            if hasattr(first_candidate, "safety_ratings"):
                print(f"\n  Safety ratings: {first_candidate.safety_ratings}")

    # Try to extract image using the same method as veo.py
    print("\n" + "=" * 80)
    print("🔧 TRYING TO EXTRACT IMAGE (same as veo.py)")
    print("=" * 80)

    parts = getattr(response, "parts", None)
    if parts is None and hasattr(response, "candidates"):
        candidates = getattr(response, "candidates") or []
        if candidates:
            parts = getattr(candidates[0].content, "parts", None)

    if not parts:
        print("❌ No parts found in response")
    else:
        print(f"✅ Found {len(parts)} part(s)")

        for i, part in enumerate(parts):
            print(f"\n  Part {i}:")
            print(f"    Has as_image: {hasattr(part, 'as_image')}")
            print(f"    Has inline_data: {hasattr(part, 'inline_data')}")
            print(f"    Has inlineData: {hasattr(part, 'inlineData')}")
            print(f"    Has text: {hasattr(part, 'text')}")

            if hasattr(part, "text") and part.text:
                print(f"    Text content: {part.text[:500]}")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🏁 DIAGNOSIS COMPLETE")
print("=" * 80)
