#!/usr/bin/env python3
"""
Egocentric World Generator - Generate worlds with first-person egocentric key-frame descriptions.

This module enhances world generation by:
1. Using first-person "you" perspective throughout
2. Treating each state as a visual "key frame" with rich sensory details
3. Including hand positions, camera angles, and spatial awareness
4. Optimizing for video/image generation
"""

import os
from typing import Optional, Dict, List
from world_model_bench_agent.benchmark_curation import World, State, Action, Transition


class EgocentricWorldGenerator:
    """
    Generates worlds with egocentric, key-frame focused state descriptions.

    Key features:
    - First-person perspective ("you are...", "you see...")
    - Visual key-frame descriptions (camera angle, what's visible)
    - Hand and body position details
    - Sensory information (touch, sight, sound)
    - Present tense, continuous action
    """

    def __init__(self, api_key: Optional[str] = None, output_dir: str = "worlds/llm_worlds"):
        """
        Initialize the egocentric world generator.

        Args:
            api_key: Google AI API key. If None, reads from GEMINI_KEY env var.
            output_dir: Directory to save generated worlds
        """
        self.api_key = api_key or os.getenv("GEMINI_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_KEY not found. Please set it in .env or pass it directly.")

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize Gemini client
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = "gemini-2.0-flash-lite"
        except ImportError:
            raise ImportError("google-genai package not found. Install with: pip install google-genai")

    def generate_egocentric_linear_world(
        self,
        scenario: str,
        initial_state: str,
        goal_state: str,
        num_steps: int = 5,
        camera_perspective: str = "first_person_ego",
        camera_height: str = "1.6m (eye level)",
        context: Optional[str] = None
    ) -> World:
        """
        Generate a linear world with egocentric key-frame descriptions.

        Args:
            scenario: Name of scenario (e.g., "plant_repotting")
            initial_state: Initial state description
            goal_state: Goal state description
            num_steps: Number of intermediate steps
            camera_perspective: Camera view (default: first_person_ego)
            camera_height: Camera height (default: 1.6m eye level)
            context: Additional context

        Returns:
            World with egocentric key-frame state descriptions
        """
        print(f"\n🎥 Generating EGOCENTRIC linear world for: {scenario}")
        print(f"   Camera: {camera_perspective} at {camera_height}")
        print(f"   Steps: {num_steps + 2} total states")

        prompt = self._build_egocentric_linear_prompt(
            scenario=scenario,
            initial_state=initial_state,
            goal_state=goal_state,
            num_steps=num_steps,
            camera_perspective=camera_perspective,
            camera_height=camera_height,
            context=context
        )

        print("📡 Calling Gemini LLM...")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        print("📋 Parsing response...")
        data = self._parse_json_response(response.text)

        print("🏗️  Building World object...")
        world = self._construct_world(scenario, data, "linear_egocentric")

        print(f"✅ Egocentric world created: {len(world.states)} states, {len(world.transitions)} transitions")
        return world

    def _build_egocentric_linear_prompt(
        self,
        scenario: str,
        initial_state: str,
        goal_state: str,
        num_steps: int,
        camera_perspective: str,
        camera_height: str,
        context: Optional[str]
    ) -> str:
        """Build prompt for egocentric key-frame world generation."""

        prompt = f"""You are an EGOCENTRIC WORLD MODEL GENERATOR specialized in creating first-person, visual key-frame descriptions.

🎬 SCENARIO: {scenario}

📹 CAMERA SETUP:
- Perspective: {camera_perspective} (first-person from the actor's eyes)
- Height: {camera_height}
- View: What the person sees looking down/forward at the task

🎯 TASK:
Generate a sequence of {num_steps + 2} states from:
START: {initial_state}
GOAL: {goal_state}
"""

        if context:
            prompt += f"\n📝 CONTEXT: {context}\n"

        prompt += f"""
🔑 KEY-FRAME DESCRIPTION REQUIREMENTS:

Each state must be a VISUAL KEY FRAME that includes:

1. **CAMERA VIEW** (What you see):
   - Position: "You're standing at...", "You lean over...", "You're kneeling..."
   - Visual field: What's in front of you, to your sides, in your hands
   - Perspective: First-person, present tense

2. **HANDS & BODY** (What you're doing):
   - Hand positions: "Your left hand holds...", "You reach out with your right hand..."
   - Body posture: "You bend forward...", "You step back to observe..."
   - Tool usage: "The scissors in your hand...", "You grip the trowel..."

3. **OBJECTS & ENVIRONMENT** (What's visible):
   - Main focus: What you're directly interacting with
   - Nearby items: Tools, materials within reach
   - Spatial layout: "To your right...", "In front of you...", "Beside the pot..."

4. **SENSORY DETAILS** (What you feel/hear):
   - Touch: "The soil feels dry and crumbly", "You feel the roots separate"
   - Visual cues: Colors, textures, changes happening
   - Subtle feedback: Water dripping, soil compacting, leaves perking up

5. **PRESENT CONTINUOUS** (Happening now):
   - Use present tense: "You pour water..." not "You poured..."
   - Active descriptions: "You watch as..." "You notice..." "You feel..."
   - Immediate observations: "The water drains...", "The leaves lift..."

❌ AVOID:
- Third-person: "The plant is watered" ❌
- Past tense: "You watered the plant" ❌
- Passive voice: "Water is poured" ❌
- Abstract statements: "The task is complete" ❌

✅ GOOD EXAMPLES:

State s0:
"You're standing at a wooden table, looking down at a small potted plant directly in front of you. The leaves droop and look wilted - they clearly need help. You reach out and touch the soil with your fingertips - it's completely dry and crumbly, falling away at your touch. To your right, you see a full watering can within arm's reach. Behind the plant sits a larger empty terracotta pot, a bag of dark potting soil, and a hand trowel laid out ready."

State s1:
"You've just finished pouring water from the can. You watch as the last drops fall from the spout and soak into the soil. Water drips steadily from the drainage holes at the bottom into the saucer below - you can hear the soft dripping sound. The soil has darkened significantly, absorbing the moisture. You set down the watering can to your left and notice the leaves already look slightly more perky, beginning to lift. The moisture meter beside the pot now shows a reading in the healthy range."

Action a0:
"Pick up the metal watering can with your right hand. Tilt it over the plant and begin pouring slowly in a circular pattern, watching the water soak into the dry soil. Continue pouring steadily, moving the can around to ensure even coverage, until you see water beginning to drain from the bottom holes into the saucer below. Set the can down and observe the soil darkening with moisture."

📤 OUTPUT FORMAT:

Return ONLY valid JSON with this exact structure:

{{
  "states": [
    {{
      "id": "s0",
      "description": "<Egocentric key-frame description following all requirements above>",
      "progress": 0.0,
      "metadata": {{
        "camera_perspective": "{camera_perspective}",
        "camera_height": "{camera_height}",
        "hands_visible": true,
        "main_focus": "<What you're looking at/interacting with>"
      }}
    }},
    {{
      "id": "s1",
      "description": "<Next key-frame...>",
      "progress": 0.14,
      "metadata": {{
        "camera_perspective": "{camera_perspective}",
        "camera_height": "{camera_height}",
        "hands_visible": true,
        "main_focus": "<Updated focus>"
      }}
    }},
    ... (continue for all {num_steps + 2} states)
  ],
  "actions": [
    {{
      "id": "a0",
      "description": "<Egocentric action description with hand movements and body positioning>",
      "from_state": "s0",
      "to_state": "s1",
      "action_type": "processing",
      "metadata": {{
        "hand_action": true,
        "tool_use": "<tool name if applicable>",
        "both_hands": false
      }}
    }},
    ... (continue for all {num_steps + 1} actions)
  ]
}}

🎬 Remember: Every state is a VISUAL KEY FRAME optimized for image/video generation!

JSON:"""

        return prompt

    def _parse_json_response(self, response_text: str) -> Dict:
        """Extract and parse JSON from LLM response."""
        import json
        import re

        # Try to find JSON block
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response_text

        # Clean markdown formatting if present
        json_str = json_str.replace('```json', '').replace('```', '')

        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            raise

    def _construct_world(self, scenario: str, data: Dict, world_type: str) -> World:
        """Construct World object from parsed JSON data."""
        world = World(
            name=f"{scenario}_{world_type}",
            description=f"Egocentric {world_type} world for {scenario}"
        )

        # Create states
        states_map = {}
        for state_data in data["states"]:
            state = State(
                description=state_data["description"],
                state_id=state_data["id"],
                metadata={
                    "progress": state_data.get("progress", 0.0),
                    **state_data.get("metadata", {})
                }
            )
            states_map[state.state_id] = state

        # Create transitions
        for action_data in data["actions"]:
            action = Action(
                description=action_data["description"],
                action_id=action_data["id"],
                action_type=action_data.get("action_type", "action"),
                metadata=action_data.get("metadata", {})
            )

            start = states_map[action_data["from_state"]]
            end = states_map[action_data["to_state"]]

            world.add_transition(start, action, end)

        # Set initial and goal states
        world.initial_state = states_map["s0"]
        final_state_id = f"s{len(data['states']) - 1}"
        world.add_goal_state(states_map[final_state_id])

        return world

    def save_world(self, world: World, filename: Optional[str] = None) -> str:
        """Save world to JSON file."""
        if filename is None:
            filename = f"{world.name}_world.json"

        filepath = os.path.join(self.output_dir, filename)
        world.save(filepath)
        print(f"💾 Saved world to: {filepath}")
        return filepath


# Convenience function
def generate_egocentric_world(
    scenario: str,
    initial_state: str,
    goal_state: str,
    num_steps: int = 5,
    api_key: Optional[str] = None,
    **kwargs
) -> World:
    """
    Quick helper to generate an egocentric world.

    Example:
        world = generate_egocentric_world(
            scenario="plant_repotting",
            initial_state="Small wilted plant in old pot",
            goal_state="Thriving plant in new larger pot",
            num_steps=6
        )
    """
    generator = EgocentricWorldGenerator(api_key=api_key)
    return generator.generate_egocentric_linear_world(
        scenario=scenario,
        initial_state=initial_state,
        goal_state=goal_state,
        num_steps=num_steps,
        **kwargs
    )
