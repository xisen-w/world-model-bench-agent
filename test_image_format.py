#!/usr/bin/env python3
"""Test what format uploaded files and generated images are in."""

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
from google.genai import types

print("=" * 70)
print("TESTING IMAGE OBJECT FORMATS")
print("=" * 70)

client = genai.Client(api_key=api_key)

# Test 1: Generate an image and inspect its format
print("\n1. Generating an image with Gemini...")
result = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A simple red apple on a white table",
)

print(f"\nResult type: {type(result)}")
print(f"Result attributes: {[x for x in dir(result) if not x.startswith('_')]}")

# Try to find the images
if hasattr(result, 'candidates'):
    print(f"Candidates: {result.candidates}")
    if result.candidates and hasattr(result.candidates[0], 'content'):
        content = result.candidates[0].content
        print(f"Content: {content}")
        if hasattr(content, 'parts'):
            print(f"Parts: {content.parts}")
            for i, part in enumerate(content.parts):
                print(f"\nPart {i}: {type(part)}")
                print(f"Part attributes: {[x for x in dir(part) if not x.startswith('_')]}")
                if hasattr(part, 'inline_data'):
                    print(f"  inline_data: {part.inline_data}")
else:
    print("No generated images found")

# Test 2: Upload a file and inspect its format
print("\n\n2. Uploading a file...")
if Path("generated_images/apple_eating_images/s0_000.png").exists():
    uploaded = client.files.upload(file="generated_images/apple_eating_images/s0_000.png")
    print(f"\nUploaded file type: {type(uploaded)}")
    print(f"Uploaded file name: {uploaded.name}")
    print(f"Uploaded file attributes: {dir(uploaded)}")

    if hasattr(uploaded, 'mime_type'):
        print(f"  mime_type: {uploaded.mime_type}")
    if hasattr(uploaded, 'bytes_base64_encoded'):
        print(f"  bytes_base64_encoded: exists")
    if hasattr(uploaded, '_image_bytes'):
        print(f"  _image_bytes: exists")
    if hasattr(uploaded, 'uri'):
        print(f"  uri: {uploaded.uri}")
else:
    print("Apple image not found, skipping upload test")

# Test 3: Create an Image object manually from file bytes
print("\n\n3. Creating Image object from file bytes...")
if Path("generated_images/apple_eating_images/s0_000.png").exists():
    import base64

    with open("generated_images/apple_eating_images/s0_000.png", "rb") as f:
        image_bytes = f.read()

    # Try creating an Image object
    try:
        # Check if types.Image exists
        if hasattr(types, 'Image'):
            img_obj = types.Image(
                bytes_base64_encoded=base64.b64encode(image_bytes).decode('utf-8'),
                mime_type="image/png"
            )
            print(f"\nCreated Image object type: {type(img_obj)}")
            print(f"Image object attributes: {dir(img_obj)}")
            print("SUCCESS: Can create Image objects with base64")
        else:
            print("\nNO types.Image available")

            # Try alternate approach
            print("Trying alternate Image creation...")
            print(f"Available in types: {[x for x in dir(types) if 'image' in x.lower()]}")

    except Exception as e:
        print(f"\nError creating Image: {e}")
else:
    print("Apple image not found")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
