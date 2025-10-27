#!/usr/bin/env python3
"""Test if the Gemini API key works."""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    from google import genai

    print("\nInitializing client...")
    client = genai.Client(api_key=api_key)

    print("Making test API call to Gemini...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="Say hello in one word"
    )

    print(f"\nSUCCESS! Response: {response.text}")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}")
    print(f"Message: {e}")

    # Try alternative model
    print("\n\nTrying with gemini-1.5-flash instead...")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Say hello in one word"
        )
        print(f"SUCCESS with gemini-1.5-flash! Response: {response.text}")
    except Exception as e2:
        print(f"Also failed: {e2}")
