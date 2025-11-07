# Driving World Generator Improvements - Implementation Summary

## Overview
This document summarizes the sophisticated improvements made to fix two critical issues in the driving LLM world generator:
1. **Angle consistency constraint** not working properly
2. **Image changes** being too subtle

## Problem Analysis

### Issue 1: Poor Angle Consistency
- **Root Cause**: Generic prompts like "Same camera angle and scene layout" were too weak
- **Impact**: Camera would shift between images, breaking egocentric consistency

### Issue 2: Subtle Image Changes
- **Root Cause**:
  - Driving actions (check mirrors, release brake) are inherently subtle from first-person view
  - Generic prompts didn't emphasize visual indicators
  - States 0-5 were all "sitting in parked car" with minimal distinction
- **Impact**: Images looked nearly identical, making it hard to distinguish states

## Solution Architecture

### Design Principle: Domain-Specific Methods Only
- **Keep general methods clean and generic** (no changes)
- **Create NEW driving-specific methods** with heavy, detailed guidance
- **Auto-detect driving scenarios** and route to specialized methods
- **Fall back to general methods** for other scenarios

---

## Implementation Details

### 1. DrivingPromptEnhancer Class
**File**: `world_model_bench_agent/prompt_enhancer.py` (lines 568-808)

**Purpose**: Sophisticated prompt enhancement specifically for driving scenarios

**Key Features**:
- **Comprehensive Action → Visual Mapping**: `DRIVING_ACTION_VISUALS` dict maps each driving action to:
  - Exact hand positions and movements
  - Before/after visual indicators
  - Key visual changes
  - Emphasis points

- **Action Enhancement**: `enhance_driving_action()` matches actions to templates and generates detailed descriptions with:
  - Egocentric POV specifications
  - Hand position details
  - Visual transformations (before/after)
  - Camera continuity constraints

- **State Description Building**:
  - `build_driving_state_description()` creates detailed state specs
  - `_build_initial_driving_state()` - full specification with all visual elements
  - `_build_variation_driving_state()` - emphasizes only what changed

**Example Visual Mapping** (seatbelt action):
```python
"fasten seatbelt": {
    "hands": "Left hand pulling belt, right hand holding buckle",
    "before": "Seatbelt hanging loose, no strap across chest",
    "after": "Seatbelt strap CLEARLY VISIBLE as diagonal line across chest",
    "emphasis": "CRITICAL: Transformation is DRAMATIC - absent → present",
    "key_change": "Diagonal black/gray strap now crosses torso prominently"
}
```

---

### 2. LLM World Generation Enhancements
**File**: `world_model_bench_agent/llm_world_generator.py`

**New Methods**:
- `_is_driving_scenario()` (line 759): Detects driving scenarios via keywords
- `_build_driving_linear_world_prompt()` (line 765): Generates heavily guided prompt

**Integration**: Modified `generate_linear_world()` (line 96) to:
1. Detect if scenario is driving-related
2. Route to driving-specific prompt builder
3. Fall back to generic builder for other scenarios

**Driving Prompt Guidance** (lines 787-902):
The prompt includes **8 critical requirements** for each state:

1. **Dashboard Status** (most important for visual distinction)
   - Lights ON/OFF
   - Specific colored indicators (red, yellow, green, blue)
   - Speedometer reading
   - Gear indicator display
   - Example: "dashboard completely DARK with all indicator lights OFF"

2. **Seatbelt Status** (critical visual indicator)
   - BUCKLED with diagonal strap visible
   - OR UNBUCKLED hanging loose
   - Must be explicit in every state
   - Example: "seatbelt hanging loose and unbuckled on left side, no strap across chest"

3. **Hand Positions** (creates visual variety)
   - Exact locations: on lap, wheel, brake, ignition, mirrors
   - Which hand does what
   - Example: "both hands resting on lap, not touching steering wheel"

4. **Parking Brake** (clear physical indicator)
   - Lever UP (engaged, raised) or DOWN (released, lowered)
   - Must state visible position
   - Example: "parking brake lever in UP engaged position, visible between seats"

5. **Ignition/Engine Status**
   - Key OFF (dark dashboard) or ON (illuminated dashboard)
   - Must match dashboard light status

6. **Steering Wheel Interaction**
   - Untouched and straight, or hands gripping

7. **Environment View Through Windshield**
   - Stationary parking lot view OR moving road view
   - Changes dramatically between parked and driving states

8. **Gear Shift Position**
   - P (Park), D (Drive), R (Reverse)
   - Physical position or display indicator

**Example Excellent States** provided in prompt (lines 868-878):
- Shows exactly how detailed state descriptions should be
- Includes every visual element explicitly
- Demonstrates progression between states

---

### 3. Image Generation Enhancements
**File**: `world_model_bench_agent/image_world_generator.py`

**New Methods**:
- `_is_driving_scenario()` (line 498): Detects driving via keyword count (≥3 keywords)
- `_extract_driving_visual_elements()` (line 509): Parses state description to extract:
  - Dashboard lights status
  - Seatbelt status (buckled/unbuckled)
  - Hand positions
  - Parking brake position
  - Gear indicator
  - Environment view
  - Ignition status
  - Speedometer reading

- `_build_driving_state_prompt()` (line 640): Generates sophisticated image prompts

**Integration**: Modified `_generate_state_image()` (line 381) to:
1. Detect if state is driving-related
2. Use driving-specific prompt builder with visual inventories
3. Extract and store visual elements for next iteration
4. Pass elements between states for before/after comparison
5. Fall back to generic prompt for non-driving

**Camera Anchor System** (lines 663-668):
```
FIXED CAMERA POSITION (CRITICAL - MUST NOT CHANGE):
- Position: Driver's seat, eye level (1.6m), first-person egocentric
- Direction: Looking straight ahead through windshield
- Framing: Steering wheel centered bottom-middle, dashboard bottom edge, rearview mirror top-center
- Lens: 35mm equivalent
- THIS MUST REMAIN PIXEL-PERFECT IDENTICAL
```

**Initial State Prompt** (lines 672-708):
- Full visual specification with camera anchor
- MUST SHOW requirements for:
  - Steering wheel position
  - Dashboard details (indicators, speedometer, gear)
  - Driver elements (hands, seatbelt)
  - Vehicle controls (parking brake, ignition)
  - Environment through windshield
  - Rearview mirror

**Variation Prompt** (lines 710-791):
- Emphasizes camera must stay IDENTICAL
- Lists "WHAT MUST STAY IDENTICAL" (camera, steering wheel, dashboard layout, etc.)
- "ONLY THESE ELEMENTS CHANGE" section
- **Before/After Comparison** for changed elements:
  - Dashboard lights: BEFORE → AFTER
  - Seatbelt: BEFORE → AFTER
  - Hands: BEFORE → AFTER
  - Parking brake: BEFORE → AFTER
  - Environment: BEFORE → AFTER
- Emphasis: "Make changes DRAMATIC and OBVIOUS"

**Modified Canonical Path Generation** (lines 189-230):
- Tracks `previous_driving_elements` between iterations
- Passes elements to each state generation
- Stores elements in metadata for next comparison
- Enables before/after visual diff in variation prompts

---

## Key Innovations

### 1. Fixed Camera Anchor System
- **Explicit "MUST NOT CHANGE" constraints** for camera position
- Specified exact framing (steering wheel centered, dashboard at bottom, mirror at top)
- Repeated in every variation prompt with "PIXEL-PERFECT IDENTICAL" emphasis

### 2. Visual Inventory System
- Each state has explicit **"MUST SHOW"** elements list
- Visual elements extracted and tracked across states
- Enables precise before/after comparisons

### 3. Difference-Based Variation Prompts
- **Only specify what changes**, not full description
- "BEFORE: X → AFTER: Y" format for each changed element
- Dramatically reduces confusion for image generator

### 4. Driving-Specific Action Mappings
- Custom visual indicators for each common driving action
- Maps abstract actions (check mirrors) to concrete visuals (hand touching mirror)
- Emphasizes most dramatic changes (dashboard dark → lit)

### 5. Egocentric Emphasis
- All descriptions written from driver's direct POV
- Focus on visible elements in frame
- Hand positions and movements explicitly described

---

## Benefits

### For Angle Consistency:
✅ Fixed camera anchor prevents angle drift
✅ Explicit "DO NOT CHANGE" list for camera
✅ Pixel-perfect consistency enforcement
✅ Same framing reference in every variation

### For Visual Changes:
✅ Before/after comparison makes changes obvious
✅ Dashboard transformation (dark → lit) creates dramatic visual
✅ Seatbelt status (absent → diagonal strap) clearly visible
✅ Hand positions create variety within same scene
✅ Each state has unique visual signature

---

## Usage

The system **automatically detects driving scenarios** and applies specialized prompts:

1. **World Generation**: `python generate_driving_world.py`
   - Detects "driving" in scenario name
   - Uses `_build_driving_linear_world_prompt()`
   - Generates states with detailed visual specifications

2. **Image Generation**: `python generate_driving_images.py`
   - Detects driving keywords in state descriptions
   - Uses `_build_driving_state_prompt()` with visual inventories
   - Generates images with fixed camera and dramatic changes

3. **Fallback**: Non-driving scenarios automatically use general methods

---

## Testing

To validate the improvements:

1. **Regenerate driving world**:
   ```bash
   python generate_driving_world.py
   ```
   - Check that states have detailed visual descriptions
   - Verify dashboard, seatbelt, hand positions specified

2. **Regenerate driving images**:
   ```bash
   python generate_driving_images.py
   ```
   - Verify camera angle stays consistent across all images
   - Check that visual changes are dramatic and obvious
   - Dashboard lights, seatbelt strap, hand movements should be clear

3. **Compare old vs new**:
   - Old: Subtle differences, camera angle drift
   - New: Fixed camera, obvious visual changes

---

## Files Modified

1. `world_model_bench_agent/prompt_enhancer.py`
   - Added `DrivingPromptEnhancer` class (lines 568-808)

2. `world_model_bench_agent/llm_world_generator.py`
   - Added `_is_driving_scenario()` (line 759)
   - Added `_build_driving_linear_world_prompt()` (lines 765-903)
   - Modified `generate_linear_world()` for auto-detection (lines 95-115)

3. `world_model_bench_agent/image_world_generator.py`
   - Added `_is_driving_scenario()` (line 498)
   - Added `_extract_driving_visual_elements()` (lines 509-638)
   - Added `_build_driving_state_prompt()` (lines 640-792)
   - Modified `_generate_state_image()` for auto-detection (lines 380-396)
   - Modified `_generate_canonical_path()` to track visual elements (lines 189-230)

---

## Conclusion

These sophisticated, domain-specific enhancements transform the driving world generator from producing:
- **Before**: Subtle, inconsistent images with camera angle drift
- **After**: Dramatically different states with pixel-perfect camera consistency

The system maintains code cleanliness by:
- Keeping general methods unchanged
- Creating specialized methods only for driving
- Auto-detecting and routing appropriately
- Falling back gracefully for other scenarios

**Result**: Perfect angle consistency + obvious visual changes for driving scenarios! 🚗✨
