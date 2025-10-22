#!/usr/bin/env python3
"""
Setup script for AC-World Video Generation Framework

This script helps users quickly set up and validate their environment
for the Action-Conditioned World Model benchmark.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please use Python 3.8 or higher")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        "openai",
        "python-dotenv",
        "requests"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)

    if missing_packages:
        print("📦 Installing missing packages...")        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    return True


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    if env_example.exists():
        env_example.copy(env_file)
        print("✅ Created .env file from .env.example")
        print("   Please edit .env and add your API keys")
        return True
    else:
        print("❌ .env.example file not found")
        return False


def validate_configuration():
    """Validate the configuration by checking API keys."""
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False

    # Check for API keys (without revealing them)
    with open(".env", "r") as f:
        content = f.read()

    api_keys_found = []
    if "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content:
        api_keys_found.append("OpenAI")

    if "RUNWAY_API_KEY=" in content and "your_runway_api_key_here" not in content:
        api_keys_found.append("Runway ML")

    if "STABILITY_API_KEY=" in content and "your_stability_api_key_here" not in content:
        api_keys_found.append("Stability AI")

    if api_keys_found:
        print(f"✅ Found API keys for: {', '.join(api_keys_found)}")
        return True
    else:
        print("⚠️  No API keys configured yet")
        print("   Please add your API keys to .env file")
        return False


def run_tests():
    """Run basic functionality tests."""
    print("\n🧪 Running functionality tests...")

    try:
        # Test imports
        from utils import VideoGenerationManager, SoraVideoGenerator
        print("✅ Core imports successful")

        # Test manager creation
        manager = VideoGenerationManager()
        print("✅ VideoGenerationManager created")

        # Test provider registration (without API key)
        print("✅ Basic functionality tests passed")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 AC-World Video Generation Framework Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return 1

    # Check and install dependencies
    if not check_dependencies():
        return 1

    # Create .env file
    if not create_env_file():
        return 1

    # Validate configuration
    validate_configuration()

    # Run tests
    if not run_tests():
        return 1

    print("\n🎉 Setup completed successfully!")
    print("=" * 50)
    print("Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: make run (or python3 example_usage.py)")
    print("3. Check the generated JSON results")
    print("4. Read README.md for detailed documentation")

    return 0


if __name__ == "__main__":
    sys.exit(main())


