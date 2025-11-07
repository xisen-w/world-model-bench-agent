#!/usr/bin/env python3
"""Fix image paths in the image world JSON to match actually generated files."""

import json
import os
from pathlib import Path

# Load the image world JSON
image_world_file = "worlds/image_worlds/indoor_plant_watering_repotting_branching_egocentric_image_world.json"
with open(image_world_file) as f:
    image_world = json.load(f)

# Find all actually generated images
image_dir = Path("generated_images/indoor_plant_egocentric_branching")
generated_images = {}

if image_dir.exists():
    for img_file in image_dir.glob("*.png"):
        # Extract state_id from filename (e.g., s0_000.png -> s0)
        state_id = img_file.stem.rsplit('_', 1)[0]
        # Store relative path from root
        generated_images[state_id] = str(img_file)

print(f"Found {len(generated_images)} generated images:")
for state_id, path in sorted(generated_images.items()):
    print(f"  {state_id}: {path}")

# Update image paths in the JSON
updated_count = 0
for state in image_world["states"]:
    state_id = state["state_id"]
    if state_id in generated_images:
        old_path = state.get("image_path", "N/A")
        new_path = generated_images[state_id]
        if old_path != new_path:
            state["image_path"] = new_path
            print(f"\n✓ Updated {state_id}:")
            print(f"    Old: {old_path}")
            print(f"    New: {new_path}")
            updated_count += 1
    else:
        print(f"\n⚠️  No image found for state: {state_id}")

# Save updated JSON
with open(image_world_file, 'w') as f:
    json.dump(image_world, f, indent=2)

print(f"\n✅ Updated {updated_count} image paths")
print(f"💾 Saved to: {image_world_file}")
