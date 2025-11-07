#!/usr/bin/env python3
"""
Vision Experiment - Test Image Variation with Fixed Camera Anchor

This script loads an existing image and generates a variation using
the same sophisticated prompting techniques as the driving world generator.

Usage:
    python vision_experiment.py
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
    print("ERROR: GEMINI_KEY not found in .env")
    sys.exit(1)

# Import Veo
import google.genai as genai
from utils.veo import VeoVideoGenerator

print("=" * 80)
print("VISION EXPERIMENT - Image Variation with Fixed Camera Anchor")
print("=" * 80)

# Initialize Veo client
print("\nInitializing Veo client...")
client = genai.Client(api_key=api_key)
veo = VeoVideoGenerator(
    api_key=api_key,
    client=client,
    acknowledged_paid_feature=True
)

# Load a base image from the recently generated driving images
base_image_path = "/Users/wangxiang/Desktop/my_workspace/memory/world_model_bench_agent/4181761840618_.pic.jpg"

if not os.path.exists(base_image_path):
    print(f"\n❌ Error: Base image not found at {base_image_path}")
    print("Please run generate_driving_images.py first to create the base images.")
    sys.exit(1)

print(f"\n📸 Loading base image: {base_image_path}")
base_image = Image.open(base_image_path)
print(f"   Image size: {base_image.size}")
print(f"   Image mode: {base_image.mode}")

# Define a sophisticated variation prompt with fixed camera anchor
variation_prompt = """

Initial State (Reference) 



This image captures a close-up view of a work desk with a computer monitor and various items, likely in an office or study environment.

🖥️ The Setup and Central Focus

The central and most dominant object is a large, black computer monitor with a relatively thin bezel. It is resting on its stand in the center of the wooden desk. The screen is off or blank (black). A white board covered in handwriting and mathematical/logical notation forms the background directly behind the monitor. The monitor appears to be a modern flat-panel display.

💻 Desk Objects

The wooden desk surface, which is a light-medium brown or orange-wood tone, holds several objects:

Left Side:

A black, wired computer mouse is positioned near the left edge.

To the right of the mouse is a thick, dark-colored book (likely black or dark blue/green) stacked with a smaller, dark booklet or another volume underneath it. The cover of the lower book has some visible white text, perhaps related to technical or engineering subjects (e.g., "ABAQUS User Manual" is partially legible on the spine of one book).

A USB cable or similar cord is loosely coiled near the book.

A green-labeled can, possibly for a beverage like "Gin & Tonic" (partial text visible), is tucked against the wall/whiteboard on the far left.

Right Side:

A white plate holds the remains of a snack, likely a slice of cake, crumble, or muffin. The remaining piece shows a crumbly top and a yellow-brown interior.

A fork and a knife, both silver-colored, are resting on the plate, indicating the snack was recently consumed.

To the right of the plate, there are various small, dark objects and cables, including a dark piece of electronic equipment (possibly a remote or small device) and tangled black wires trailing toward the back of the desk.

🔠 Background and Implications

The whiteboard background is filled with technical-looking notes, equations, and diagrams written in blue and black markers. This strongly implies that the user of this desk is involved in technical, scientific, or complex problem-solving work, perhaps in software engineering, mathematics, or physics.

Visible notations include bracketed terms like [B, E], equations such as $XW = P$, and some numerical values and percentages (e.g., "30%").

The writing suggests a focus on logic, data structures, or formal systems.

The overall scene conveys a moment of a work break, with the snack plate suggesting a recent pause in activity. The dark, technical books and the complex notes on the whiteboard reinforce the idea of a demanding intellectual task being undertaken.

📊 Object Count Summary

Here is a count of the distinct, recognizable objects in the image:

Computer Monitor: 1

Monitor Stand/Base: 1

Wired Mouse: 1

Thick Book: 1

Lower Book/Manual: 1

Canned Beverage: 1

White Snack Plate: 1

Fork: 1

Knife: 1

Remaining Snack Piece: 1

Small Electronic Device/Remote: 1

USB/Charging Cable (left): 1

Assortment of Cables/Wires (right): 1 (or more, but appearing as a cluster)



What we want to generate: 

Inferred States and Stated Changes

CategoryOriginal State (Infer)New State (Change)PerspectiveClose-up, fixed, third-person view of a desk scene.Ego-centric, first-person (POV), looking down at the plate and hand/fork.Action/FocusA static scene; the snack is finished, and the cutlery is resting on the plate.A dynamic action; the user's hand is the primary subject, picking up the fork from the plate/desk.Cutlery PositionFork and knife are resting on the plate, signaling the end of the break.The fork is in the hand, ready to engage with the remaining cake, signaling the continuation or start of the break/snack.Emotional StateSuggests a break is over or winding down; a moment of pause.Suggests a moment of anticipation or immediate action; the break is starting or resuming.Prompt Variation: Ego-centric Action

Generate an image from an ego-centric (first-person) point of view. The scene is a close-up of a wooden desk featuring a white plate with a partially eaten piece of cake. The main focus is the user's hand (specifically the fingers and lower palm) reaching down and picking up the silver fork from the edge of the plate, preparing to take the next bite of the cake. The background should be slightly blurred to draw attention to the action but still show the original elements: a blurred, dark computer monitor, a sliver of the technical whiteboard notes, and the dark books on the left. The lighting should be soft, highlighting the texture of the wooden desk and the metallic sheen of the fork. Focus on the moment just as the fingers grip the handle of the fork.

"""



print("\n" + "=" * 80)
print("GENERATING VARIATION IMAGE")
print("=" * 80)

print("\nPrompt preview (first 500 chars):")
print("-" * 80)
print(variation_prompt[:500])
print("...")
print("-" * 80)

print(f"\n🎨 Generating variation image...")
print("   This may take 30-60 seconds...")

try:
    variation_image = veo.generate_image_variation(
        prompt=variation_prompt,
        base_image=base_image,
        aspect_ratio="16:9"
    )

    # Save the variation
    output_path = "tests/test1.png"
    variation_image.save(output_path)

    # Reload to check properties (Veo's Image object doesn't have size/mode)
    saved_image = Image.open(output_path)

    print(f"\n✅ SUCCESS! Variation generated and saved!")
    print(f"   Output: {output_path}")
    print(f"   Image size: {saved_image.size}")
    print(f"   Image mode: {saved_image.mode}")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

    print("\nGenerated files:")
    print(f"  📸 Base image:      {base_image_path}")
    print(f"  🎨 Variation image: {output_path}")

    print("\n🔍 Next steps:")
    print("  1. Compare the two images side-by-side")
    print("  2. Check if camera angle is identical")
    print("  3. Verify that seatbelt change is dramatic and visible")
    print("  4. Confirm steering wheel, dashboard, mirrors stayed in same position")

    print("\n💡 What to look for:")
    print("  ✓ Camera angle: Should be pixel-perfect identical")
    print("  ✓ Seatbelt: Should show diagonal strap across chest (was absent before)")
    print("  ✓ Hands: Should show motion (was resting on lap before)")
    print("  ✓ Dashboard: Should remain dark and unchanged")
    print("  ✓ Steering wheel: Should be in exact same position")

except Exception as e:
    print(f"\n❌ Error generating variation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)


# ============================================================================
# MULTI-STEP INTELLIGENT IMAGE VARIATION ALGORITHM
# ============================================================================

def generate_intelligent_variation(
    base_image_path: str,
    action_description: str,
    output_path: str,
    veo_client,
    gemini_client
):
    """
    Sophisticated multi-step algorithm for image variation:

    Algorithm:
    1. Image → Text Description (Comprehensive scene understanding)
    2. Text Description → Prompt Variation (LLM generates target state)
    3. Scene Reasoning (LLM infers action implications)
    4. Image Generation (Original image + Initial state + Final state + Action)

    Args:
        base_image_path: Path to the base image
        action_description: Desired action (e.g., "user picking up fork")
        output_path: Where to save the variation
        veo_client: VeoVideoGenerator instance
        gemini_client: Gemini client for text generation

    Returns:
        dict with all intermediate outputs
    """

    print("\n" + "=" * 80)
    print("INTELLIGENT VARIATION ALGORITHM - MULTI-STEP PROCESS")
    print("=" * 80)

    # Load base image
    print(f"\n📸 Step 1: Loading base image...")
    base_image = Image.open(base_image_path)
    print(f"   Loaded: {base_image_path}")
    print(f"   Size: {base_image.size}")

    # ========================================================================
    # STEP 1: IMAGE → TEXT DESCRIPTION (Comprehensive)
    # ========================================================================

    print(f"\n🔍 Step 2: Generating comprehensive scene description...")
    print("   Using Gemini vision model to understand the scene...")

    description_prompt = """Please describe this image in great detail.

Include:
1. The entire setup and composition
2. The implications of relevant tasks visible in the scene
3. The camera view and perspective
4. The different number of objects present related to the scene
5. Spatial relationships between objects
6. Lighting and atmosphere
7. Any text or symbols visible
8. The likely context or activity

Be comprehensive and systematic. This description will be used to generate a variation of the image."""

    # Use Gemini vision API to describe the image
    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[description_prompt, base_image]
    )

    initial_description = response.text

    print(f"   ✅ Description generated ({len(initial_description)} characters)")
    print(f"\n   Preview (first 300 chars):")
    print("   " + "-" * 76)
    print("   " + initial_description[:300].replace("\n", "\n   ") + "...")
    print("   " + "-" * 76)

    # ========================================================================
    # STEP 2: TEXT DESCRIPTION → PROMPT VARIATION (LLM generates target)
    # ========================================================================

    print(f"\n🎯 Step 3: Generating variation prompt...")
    print(f"   Action to incorporate: '{action_description}'")

    variation_generation_prompt = f"""Given this comprehensive description of an image:

{initial_description}

Generate a detailed prompt variation that describes the SAME scene but with this change:

ACTION: {action_description}

Requirements:
1. Keep the same base scene, camera angle, and all existing objects
2. Only modify what's necessary for the action
3. Describe what changes from the initial state to enable this action
4. Be specific about hand positions, object interactions, and perspective shifts if needed
5. Maintain all other elements identical

Output format:
INITIAL STATE: [Description of relevant elements in initial state]
ACTION: [What specifically happens]
FINAL STATE: [Description of the scene after the action]

Generate the variation prompt now:"""

    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=variation_generation_prompt
    )

    variation_description = response.text

    print(f"   ✅ Variation prompt generated ({len(variation_description)} characters)")
    print(f"\n   Preview (first 300 chars):")
    print("   " + "-" * 76)
    print("   " + variation_description[:300].replace("\n", "\n   ") + "...")
    print("   " + "-" * 76)

    # ========================================================================
    # STEP 3: SCENE REASONING (LLM infers action implications)
    # ========================================================================

    print(f"\n🧠 Step 4: Scene reasoning and action inference...")

    reasoning_prompt = f"""Given:
- Initial scene: {initial_description[:500]}...
- Desired action: {action_description}
- Variation description: {variation_description[:500]}...

Analyze and infer:
1. What are the physical implications of this action?
2. What objects must be visible or reachable?
3. What hand/body movements are required?
4. What stays fixed (camera, background, other objects)?
5. What are potential visual cues that make this action obvious?

Provide a brief analysis (3-5 bullet points):"""

    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=reasoning_prompt
    )

    scene_reasoning = response.text

    print(f"   ✅ Scene reasoning complete")
    print(f"\n   Key insights:")
    print("   " + "-" * 76)
    for line in scene_reasoning.split('\n')[:5]:
        if line.strip():
            print("   " + line)
    print("   " + "-" * 76)

    # ========================================================================
    # STEP 4: IMAGE GENERATION (Sophisticated prompt with all context)
    # ========================================================================

    print(f"\n🎨 Step 5: Generating variation image with full context...")
    print("   This may take 30-60 seconds...")

    # Build comprehensive generation prompt
    final_generation_prompt = f"""FIXED CAMERA POSITION (CRITICAL - MUST NOT CHANGE).

CRITICAL: Generate variation of previous image with IDENTICAL camera angle and framing.

===== INITIAL STATE (Reference) =====

{initial_description}

===== DESIRED CHANGE =====

{variation_description}

===== SCENE REASONING =====

{scene_reasoning}

===== GENERATION INSTRUCTIONS =====

1. KEEP IDENTICAL:
   - Camera position and angle
   - All background elements
   - Lighting conditions
   - All objects not involved in the action
   - Overall scene composition

2. CHANGE ONLY:
   - Elements directly involved in: {action_description}
   - Make these changes DRAMATIC and CLEARLY VISIBLE

3. REALISM:
   - Natural hand/body positions
   - Realistic physics and object interactions
   - Maintain scene continuity

Generate the variation image now."""

    # Generate the image variation
    variation_image = veo_client.generate_image_variation(
        prompt=final_generation_prompt,
        base_image=base_image,
        aspect_ratio="16:9"
    )

    # Save variation
    variation_image.save(output_path)
    saved_image = Image.open(output_path)

    print(f"   ✅ Variation image generated!")
    print(f"   Output: {output_path}")
    print(f"   Size: {saved_image.size}")

    # ========================================================================
    # RESULTS
    # ========================================================================

    print("\n" + "=" * 80)
    print("INTELLIGENT VARIATION COMPLETE")
    print("=" * 80)

    print("\n📊 Algorithm Steps Completed:")
    print("   ✅ 1. Image → Text Description (Comprehensive)")
    print("   ✅ 2. Text Description → Prompt Variation")
    print("   ✅ 3. Scene Reasoning (Action Inference)")
    print("   ✅ 4. Image Generation (With Full Context)")

    print("\n📁 Generated Files:")
    print(f"   📸 Base:      {base_image_path}")
    print(f"   🎨 Variation: {output_path}")

    # Return all intermediate outputs
    return {
        "base_image_path": base_image_path,
        "output_path": output_path,
        "initial_description": initial_description,
        "variation_description": variation_description,
        "scene_reasoning": scene_reasoning,
        "final_prompt": final_generation_prompt,
        "success": True
    }


# ============================================================================
# MAIN EXECUTION - Run the intelligent algorithm
# ============================================================================

print("\n\n" + "=" * 80)
print("RUNNING INTELLIGENT VARIATION ALGORITHM")
print("=" * 80)

try:
    result = generate_intelligent_variation(
        base_image_path=base_image_path,
        action_description="the egocentric user picking up the fork to cut the small cake",
        output_path="tests/intelligent_variation.png",
        veo_client=veo,
        gemini_client=client
    )

    print("\n" + "=" * 80)
    print("✅ SUCCESS! All steps completed!")
    print("=" * 80)

    print("\n💡 Compare the results:")
    print(f"   Base:               {result['base_image_path']}")
    print(f"   Intelligent Output: {result['output_path']}")

    print("\n🔬 Intermediate Artifacts Available:")
    print(f"   - Initial description:   {len(result['initial_description'])} chars")
    print(f"   - Variation description: {len(result['variation_description'])} chars")
    print(f"   - Scene reasoning:       {len(result['scene_reasoning'])} chars")
    print(f"   - Final prompt:          {len(result['final_prompt'])} chars")

except Exception as e:
    print(f"\n❌ Error in intelligent variation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
