#!/usr/bin/env python3
"""
Quick test script for Azure OpenAI API.

This script tests the Azure OpenAI API utilities without
needing all dependencies installed.

Usage:
    python test_azure_api.py
    python test_azure_api.py path/to/test/image.png
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables manually
env_file = project_root / ".env"
if env_file.exists():
    print(f"Loading environment from: {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"').strip("'")
                os.environ[key.strip()] = value
    print("✅ Environment loaded")
else:
    print(f"⚠️  .env file not found at {env_file}")

print()

# Try to import and test
try:
    from utils.azure_openai_api import (
        AzureOpenAIConfig,
        AzureOpenAIManager,
        test_api_keys,
        test_vision_api
    )

    print("✅ Azure OpenAI utilities imported successfully")
    print()

    # Test configuration
    print("Testing configuration...")
    config = AzureOpenAIConfig.from_env()

    print(f"Endpoint: {config.gpt4o_endpoint}")
    print(f"API Key: {config.gpt4o_api_key[:20]}..." if config.gpt4o_api_key else "NOT SET")
    print(f"GPT-4o Deployment: {config.gpt4o_deployment}")
    print(f"API Version: {config.gpt4o_api_version}")
    print()

    if not config.validate():
        print("❌ Configuration incomplete!")
        print("   Required env vars:")
        print("   - AZURE_OPENAI_4O_ENDPOINT")
        print("   - AZURE_OPENAI_4O_API_KEY")
        print("   - AZURE_OPENAI_GPT4O_DEPLOYMENT")
        sys.exit(1)

    print("✅ Configuration valid")
    print()

    # Run full test suite
    print("Running API tests...")
    print()
    results = test_api_keys(verbose=True)

    # Test vision if image provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if Path(image_path).exists():
            print()
            test_vision_api(image_path, verbose=True)
        else:
            print(f"⚠️  Image not found: {image_path}")

    # Summary
    print()
    if results.get("chat_completion"):
        if all(results.values()):
            print("✅ ALL TESTS PASSED! Azure OpenAI is fully ready.")
        else:
            print("✅ CORE TESTS PASSED! Azure OpenAI is ready.")
            print("   (Some optional features unavailable)")
        sys.exit(0)
    else:
        print("❌ CRITICAL TESTS FAILED! Chat completion not working.")
        sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("Missing dependencies. Install with:")
    print("  pip install openai python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
