"""
Prompt Enhancement System for Video World Generation.

This module provides sophisticated prompt supplementation to generate
high-quality, physically realistic, cinematically styled videos with
proper continuity constraints.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class CinematicStyle:
    """Cinematic styling parameters for video generation."""
    duration: str = "4.0 s"
    shutter: str = "180°"
    film_emulation: str = "digital capture emulating 65 mm photochemical contrast"
    grain: str = "fine, tight grain"
    halation: str = "gentle halation on metallic speculars"

    lens_focal: str = "35 mm / 65 mm spherical primes"
    aperture: str = "T2.8–T4"
    filtration: str = "Black Pro-Mist 1/8 for bloom on overhead practical; light CPL"

    # Color grading
    highlights: str = "clean tungsten practical with soft amber lift"
    mids: str = "neutral porcelain whites; natural waxy sheen on objects"
    shadows: str = "cool-teal bias in falloff; blacks lifted slightly to preserve texture"

    # Lighting setup
    key_light: str = "overhead pendant (3000 K) as practical"
    fill_light: str = "4×4 white bounce camera right at surface level"
    negative_fill: str = "black foamcore camera left to preserve edge contrast"
    atmosphere: str = "none (clarity preferred)"


class PromptEnhancer:
    """
    Enhances prompts for video generation with rich cinematic details,
    egocentric POV, physical realism, and continuity constraints.
    """

    def __init__(self, style: Optional[CinematicStyle] = None):
        self.style = style or CinematicStyle()

    def enhance_action_description(
        self,
        action: str,
        context: str = "domestic kitchen"
    ) -> str:
        """
        Enhance a simple action description with egocentric POV and physical details.

        Args:
            action: Simple action like "Cut the apple in half with a knife"
            context: Scene context (kitchen, living room, etc.)

        Returns:
            Enhanced action with POV, body mechanics, and physics
        """
        # Extract key verbs and objects
        action_lower = action.lower()

        # Determine action category
        if any(verb in action_lower for verb in ["cut", "slice", "chop", "dice"]):
            return self._enhance_cutting_action(action, context)
        elif any(verb in action_lower for verb in ["eat", "bite", "consume"]):
            return self._enhance_eating_action(action, context)
        elif any(verb in action_lower for verb in ["pick", "grab", "lift", "take", "remove"]):
            return self._enhance_picking_action(action, context)
        elif any(verb in action_lower for verb in ["place", "put", "set", "drop"]):
            return self._enhance_placing_action(action, context)
        elif any(verb in action_lower for verb in ["pour", "fill"]):
            return self._enhance_pouring_action(action, context)
        elif any(verb in action_lower for verb in ["open", "close"]):
            return self._enhance_opening_action(action, context)
        else:
            # Generic enhancement
            return self._enhance_generic_action(action, context)

    def _enhance_cutting_action(self, action: str, context: str) -> str:
        """Enhance cutting/slicing actions with egocentric detail."""
        return f"""**{action}**

**Egocentric POV:**
First-person view from above the cutting surface. Both hands visible in frame:
- **Dominant hand** (right): grips knife handle firmly, knuckles forward, wrist relaxed
- **Off hand** (left): stabilizes object with fingertips, thumb arced over top, keeping clear of blade path

**Physical Motion:**
Natural cutting sequence:
1. Position off-hand to stabilize object (visible finger placement)
2. Raise knife blade 2-3 inches above surface
3. Execute controlled downward slice with slight rocking motion
4. Blade passes through object with clean separation
5. Gentle scrape sound as knife contacts cutting board
6. Slight pressure release, fingers adjust object position

**Continuity:**
- Maintain consistent hand position and skin tone throughout
- Object remains stationary except when deliberately moved
- Cutting board stays fixed; no sliding
- Crumbs/debris accumulate naturally at cut site
- Blade shows appropriate moisture/residue after contact"""

    def _enhance_eating_action(self, action: str, context: str) -> str:
        """Enhance eating actions with first-person perspective."""
        return f"""**{action}**

**Egocentric POV:**
First-person view from eater's perspective. Camera positioned at eye level, looking down ~30° angle:
- **Hand(s) visible** entering from bottom of frame
- **Chest/torso partially visible** in bottom third (clothing texture, natural posture)
- Object approaches camera as hand brings it toward mouth

**Physical Motion:**
Natural eating sequence:
1. Hand reaches for food item (visible forearm, fingers curl around object)
2. Lift motion - smooth arc from surface toward face
3. Object approaches upper frame edge (implies mouth position)
4. Brief pause at top of arc (bite moment - implied, not shown)
5. Hand retreats with remaining portion OR sets down empty
6. Possible visible chewing motion if jaw/lower face partially visible

**Continuity:**
- Consistent hand/arm appearance and clothing
- Food item shows progressive reduction (bites taken)
- Natural progression: whole → partially eaten → cores/remains
- Crumbs or residue may fall naturally
- Lighting remains consistent as object moves through space"""

    def _enhance_picking_action(self, action: str, context: str) -> str:
        """Enhance picking/grabbing actions."""
        return f"""**{action}**

**Egocentric POV:**
First-person view from actor's perspective:
- **Hand enters frame** from lower right or bottom
- **Approach trajectory** visible - fingers open, reaching toward object
- **Surface level** camera angle showing hand and object at same plane

**Physical Motion:**
Natural grasping sequence:
1. Hand approaches with fingers slightly spread
2. Fingers curl around object (wrap contact points visible)
3. Gentle grip tightening (slight finger flex, knuckle definition)
4. Vertical lift begins - object separates from surface
5. Slight acceleration upward, maintaining grip
6. Object rises 6-12 inches above surface before stabilizing

**Continuity:**
- Object identity maintained (same label, color, texture)
- No sudden teleportation - smooth continuous motion
- Contact sound: slight scrape/tap as object lifts from surface
- Surface remains undisturbed except where object was
- Consistent lighting as object moves through space"""

    def _enhance_placing_action(self, action: str, context: str) -> str:
        """Enhance placing/setting down actions."""
        return f"""**{action}**

**Egocentric POV:**
First-person view showing hand lowering object toward destination:
- **Hand visible** gripping object from top or side
- **Destination surface** visible in frame (table, counter, plate)
- **Depth perception** maintained through parallax of hand/surface

**Physical Motion:**
Natural placement sequence:
1. Hand holding object moves into upper frame
2. Controlled descent toward target surface
3. Object orientation adjusts for stable landing (if needed)
4. Gentle deceleration as object nears surface
5. Contact moment - slight tap/click sound
6. Fingers release grip, withdraw smoothly
7. Object settles into stable position

**Continuity:**
- Object remains same throughout (no substitution)
- Placement is deliberate, not dropped
- Surface undisturbed except for new object
- No bouncing, sliding, or unnatural physics
- Lighting consistent between source and destination"""

    def _enhance_pouring_action(self, action: str, context: str) -> str:
        """Enhance pouring/liquid transfer actions."""
        return f"""**{action}**

**Egocentric POV:**
First-person view from above the receiving vessel:
- **Pouring hand** visible gripping container/bottle
- **Receiving vessel** centered in frame, opening clearly visible
- **Liquid stream** trajectory visible throughout pour

**Physical Motion:**
Natural pouring sequence:
1. Lift container with dominant hand (visible grip, tilting begins)
2. Position spout/opening above receiving vessel (12-18 inches)
3. Gradual tilt increase - liquid begins to flow
4. Steady stream maintained (gravity-natural arc)
5. Visual/audio cues: liquid splashing, filling sound, rising level
6. Tilt back to vertical, flow ceases cleanly
7. Container lowered and set down

**Continuity:**
- Liquid behaves with realistic physics (gravity, viscosity)
- Receiving vessel fills progressively, level rises
- No sudden appearance of full volume
- Possible splashing/foam if poured quickly
- Container weight shifts as liquid transfers (subtle hand adjustment)"""

    def _enhance_opening_action(self, action: str, context: str) -> str:
        """Enhance opening/closing actions (doors, containers, etc.)."""
        return f"""**{action}**

**Egocentric POV:**
First-person view approaching the object to be opened:
- **Hand reaches forward** into frame toward handle/latch
- **Object** (door, fridge, container) dominates frame
- **Depth changes** as object opens and reveals interior

**Physical Motion:**
Natural opening sequence:
1. Hand approaches handle/grip point (fingers visible reaching)
2. Grip established (wrap around handle, knuckles flex)
3. Pull/twist motion begins (wrist rotation or arm retraction)
4. Object begins to open - hinge/pivot visible
5. Interior revealed progressively (lighting changes as it opens)
6. Full open position reached, hand releases or steadies
7. Brief hold showing interior contents/view

**Continuity:**
- Smooth mechanical motion (hinges, latches work naturally)
- Interior lighting changes realistically (dark → lit)
- No instant transitions - progressive reveal
- Handle/grip stays in contact until fully open
- Environmental sounds: latch click, hinge creak, air pressure change"""

    def _enhance_generic_action(self, action: str, context: str) -> str:
        """Generic enhancement for actions not matching specific categories."""
        return f"""**{action}**

**Egocentric POV:**
First-person view from actor's perspective:
- Hands/arms visible when interacting with objects
- Camera at natural eye level (~5-6 feet) looking forward or down
- Partial torso visible in lower frame if relevant

**Physical Motion:**
Natural human motion:
- Deliberate, smooth movements (no sudden jerks)
- Realistic hand-object interaction
- Weight and balance considerations visible
- Sequential steps, not instant transitions

**Continuity:**
- Consistent object identity throughout
- Realistic physics (gravity, friction, momentum)
- Appropriate sounds for actions
- Lighting stays consistent unless explicitly changing environments"""

    def build_initial_state_description(
        self,
        state_description: str,
        objects: List[str],
        location: str = "kitchen countertop"
    ) -> str:
        """
        Build detailed initial state description with cinematic framing.

        Args:
            state_description: Basic state description
            objects: List of key objects in the scene
            location: Scene location

        Returns:
            Enhanced state description with camera, lighting, and composition details
        """
        return f"""# Initial State (Frame-Accurate Description)

**Scene:** {location}, {self.style.key_light}

{state_description}

**Key Objects:** {', '.join(objects)}

**Camera & Framing:**
- **View:** Egocentric first-person POV
- **Angle:** Eye level or slightly downward (~20-30°) toward surface
- **Lens:** {self.style.lens_focal} at {self.style.aperture}
- **Depth of Field:** Shallow, focus on primary objects; background softly out of focus
- **Composition:** Objects arranged naturally; no hands in contact yet

**Lighting:**
- **Key:** {self.style.key_light}
- **Fill:** {self.style.fill_light}
- **Environment:** {self.style.atmosphere}
- **Color:** {self.style.highlights}; midtones {self.style.mids}; shadows {self.style.shadows}

**Physical State:**
- All objects at rest, stable positions
- No motion blur, sharp detail on hero objects
- Natural shadows indicating light source direction
- Surface clean/appropriate for scene (cutting board texture, etc.)

**Format & Quality:**
- {self.style.duration}; {self.style.shutter}
- {self.style.film_emulation}
- {self.style.grain}; {self.style.halation}"""

    def build_final_state_description(
        self,
        state_description: str,
        changes: List[str],
        location: str = "kitchen countertop"
    ) -> str:
        """
        Build detailed final state description showing results of action.

        Args:
            state_description: Basic final state description
            changes: List of changes from initial state
            location: Scene location

        Returns:
            Enhanced final state with verification details
        """
        return f"""# Final State (Frame-Accurate Description)

**Scene:** {location} (post-action)

{state_description}

**Changes from Initial State:**
{chr(10).join(f'- {change}' for change in changes)}

**Camera & Framing:**
- **View:** Same egocentric POV as initial state
- **Continuity:** Same lens, angle, and framing maintained
- **Focus:** Adjusted if object depth changed, but smoothly

**Physical Verification:**
- All moved objects show new stable positions
- No objects floating or defying physics
- Appropriate interaction marks (moisture, crumbs, residue)
- Tools/utensils returned to rest position
- Hands have cleared frame (unless frozen in final pose)

**Lighting:**
- Consistent with initial state unless action changed environment
- New object positions create new shadow patterns
- No sudden lighting jumps or color shifts

**Quality Markers:**
- Clean final frame composition
- Hero objects in focus and well-lit
- Natural resting state after motion
- Appropriate sound: final contact, settling, silence"""

    def build_continuity_constraints(
        self,
        objects: List[str],
        physics_notes: Optional[List[str]] = None
    ) -> str:
        """
        Build continuity and constraint specifications.

        Args:
            objects: Key objects that must maintain identity
            physics_notes: Special physics considerations

        Returns:
            Detailed continuity requirements
        """
        physics_notes = physics_notes or [
            "Gravity operates normally",
            "No object teleportation",
            "Realistic momentum and friction"
        ]

        return f"""# Continuity & Constraints

**Object Identity:**
{chr(10).join(f'- **{obj}:** Exact same instance maintained (same label, color, texture, wear)' for obj in objects)}

**Physical Laws:**
{chr(10).join(f'- {note}' for note in physics_notes)}

**Temporal Continuity:**
- No instant transitions or jumps
- Smooth motion sequences (grasp → lift → move → place)
- Realistic action duration (not sped up or slowed down unnaturally)
- Hand/arm motion follows natural human kinematics

**Camera Rules:**
- Egocentric POV maintained throughout
- No sudden camera cuts or angle changes
- Focus shifts smoothly if object depth changes
- Frame keeps primary action visible

**Environmental Stability:**
- Lighting remains consistent unless action changes it (e.g., opening fridge)
- Background objects remain static unless deliberately moved
- Surfaces don't shift or warp
- Ambient sounds appropriate to action

**Prohibition List:**
- No objects appearing/disappearing outside action
- No physics violations (floating, passing through solid objects)
- No sudden lighting/color jumps
- No visible artifacts or glitches
- No loss of object detail/texture"""

    def build_success_criteria(
        self,
        action_steps: List[str],
        final_verification: List[str]
    ) -> str:
        """
        Build frame-by-frame success criteria for verification.

        Args:
            action_steps: Step-by-step breakdown of action
            final_verification: Final state verification points

        Returns:
            Timestamped success criteria
        """
        return f"""# Success Criteria

**Action Sequence Verification:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(action_steps))}

**Frame Requirements:**
1. **First frame (0.0s):** Matches initial state description exactly
2. **Mid-sequence:** Shows continuous action with visible intermediate steps
3. **Final frame ({self.style.duration}):** Matches final state description exactly

**Physical Verification:**
{chr(10).join(f'- {criteria}' for criteria in final_verification)}

**Quality Gates:**
- No visible glitches, artifacts, or impossible physics
- Smooth motion throughout (no stuttering or jumps)
- Audio-visual sync (sounds match visible actions)
- Proper egocentric perspective maintained
- All hero objects maintain identity and detail"""

    def enhance_full_transition(
        self,
        initial_state: str,
        action: str,
        final_state: str,
        objects: List[str],
        location: str = "kitchen countertop",
        context: Optional[str] = None
    ) -> str:
        """
        Create a complete, fully enhanced transition prompt.

        Args:
            initial_state: Basic initial state description
            action: Simple action description
            final_state: Basic final state description
            objects: Key objects in scene
            location: Scene location
            context: Additional context

        Returns:
            Comprehensive prompt with all enhancements
        """
        # Enhance action
        enhanced_action = self.enhance_action_description(action, location)

        # Build initial state
        initial_full = self.build_initial_state_description(
            initial_state,
            objects,
            location
        )

        # Detect changes for final state
        changes = [
            f"Action '{action}' has been completed",
            "Object positions updated",
            "Appropriate residue/traces left by action"
        ]

        # Build final state
        final_full = self.build_final_state_description(
            final_state,
            changes,
            location
        )

        # Build continuity constraints
        continuity = self.build_continuity_constraints(objects)

        # Build success criteria
        # Extract action steps (simplified - can be made more sophisticated)
        action_steps = [
            "Hand(s) enter frame and approach object",
            f"Execute action: {action}",
            "Complete action and hands withdraw",
            "Final state achieved and stable"
        ]

        verification = [
            "All objects in expected positions",
            "No physics violations observed",
            "Egocentric perspective maintained"
        ]

        success = self.build_success_criteria(action_steps, verification)

        # Assemble complete prompt
        full_prompt = f"""{initial_full}

{enhanced_action}

{final_full}

{continuity}

{success}"""

        return full_prompt


# Convenience function for quick enhancement
def enhance_video_prompt(
    initial_state: str,
    action: str,
    final_state: str,
    objects: List[str],
    location: str = "kitchen countertop",
    style: Optional[CinematicStyle] = None
) -> str:
    """
    Quick function to enhance a video transition prompt.

    Args:
        initial_state: Initial state description
        action: Action description
        final_state: Final state description
        objects: List of key objects
        location: Scene location
        style: Optional custom cinematic style

    Returns:
        Fully enhanced prompt
    """
    enhancer = PromptEnhancer(style)
    return enhancer.enhance_full_transition(
        initial_state=initial_state,
        action=action,
        final_state=final_state,
        objects=objects,
        location=location
    )
