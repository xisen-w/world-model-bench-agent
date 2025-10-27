#!/usr/bin/env python3
"""Quick test to verify LLM world generator works."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

print("Testing LLM World Generator...")
print(f"API key loaded: {bool(os.getenv('GEMINI_KEY'))}")

from world_model_bench_agent.llm_world_generator import LLMWorldGenerator

# Test initialization
print("\n1. Initializing generator...")
generator = LLMWorldGenerator()
print("   SUCCESS: Generator initialized")

# Test linear world generation with minimal scenario
print("\n2. Generating simple linear world...")
linear_world = generator.generate_linear_world(
    scenario="making_tea",
    initial_description="Empty cup on table with tea bag and kettle",
    goal_description="Cup filled with hot tea, ready to drink",
    num_steps=3,
    context="Simple tea making"
)

print(f"   SUCCESS: Generated world with {len(linear_world.states)} states")
print(f"   Initial state: {linear_world.initial_state.description}")
print(f"   Goal state: {linear_world.goal_states[0].description if linear_world.goal_states else 'None'}")

# Show the path
print("\n3. Linear path:")
for i, transition in enumerate(linear_world.transitions, 1):
    print(f"   {i}. {transition.action.description}")
    print(f"      -> {transition.end_state.description[:60]}...")

print("\n4. Saving world...")
linear_world.save("test_tea_world.json")
print("   SUCCESS: Saved to test_tea_world.json")

print("\nAll basic tests passed!")
