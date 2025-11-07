# Indoor Plant Watering & Repotting - Egocentric Branching World Rewrite

Complete egocentric, continuous first-person narrative for all states and actions in the branching world.

---

## 🌿 CANONICAL PATH STATES (s0-s8)

### s0 - Initial State
```
You're standing at a table looking down at a small potted plant. The leaves are drooping and slightly wilted - they need help. You reach out and touch the soil - it's completely dry and crumbly. The moisture meter beside the pot confirms it: critically low. Looking around, you see everything you need: a full watering can within arm's reach, a larger empty pot waiting on your right, a bag of fresh potting soil, and a hand trowel.
```

### s1 - After Initial Watering
```
You've just finished watering. Water drips from the drainage holes into the saucer below - good drainage. You watch as the soil darkens with moisture, absorbing the water. The leaves already look slightly more perky. You check the moisture meter again - it's climbing into the healthy range. The plant is responding well, but you know it needs more room to grow.
```

### s2 - Plant Removed, Examining Roots
```
You gently tip the pot and slide the plant out. The root ball comes free in your hands. You turn it slowly, examining the roots from all angles. Some roots look healthy and white, but you notice many are circling around themselves - root bound. A few damaged brown roots catch your eye. You brush away the old, depleted soil with your fingers, letting it fall onto the work surface.
```

### s3 - Roots Trimmed and Prepared
```
You pick up the clean scissors and carefully snip away the damaged brown roots. Now you gently tease apart the tangled, root-bound sections with your fingers, feeling them separate. The healthy white roots are now free to spread. You brush off the last bits of old soil. The plant is ready. Behind you, you've set aside the old pot and discarded soil.
```

### s4 - New Pot Prepared
```
You reach for the larger pot and check the drainage hole at the bottom - clear and open. You pick up the trowel and scoop fresh potting soil from the bag, adding a generous layer to the bottom of the pot. You press it down gently with your palm, creating a stable base. The plant sits beside you, waiting to be positioned.
```

### s5 - Plant Being Positioned
```
You lift the plant carefully with both hands and lower it into the center of the new pot. You adjust it slightly, making sure it's centered and the root ball sits at the right height - just below the rim. Now you scoop more fresh soil around the sides, watching it fill the gaps around the roots. You use your fingers to gently compact the soil as you work your way around.
```

### s6 - Pot Filled with Soil
```
You add the final scoops of soil, filling the pot to the proper level. You press down gently all around the plant, compacting the soil just enough to support the plant but keep it breathable. You check the height - perfect. The top of the root ball is at the right level, leaving about an inch of space at the top for watering. The soil feels slightly moist and rich in your hands.
```

### s7 - Plant Watered in New Pot
```
You pick up the watering can and pour slowly around the base of the plant, watching the water soak in. You continue until you see water beginning to drain from the bottom holes - perfect saturation. You set down the can and lift the saucer, pouring out the excess water. The plant stands upright in its new home, supported by the fresh soil. You notice the leaves already look more vibrant and lifted.
```

### s8 - Completed (Baseline Good Ending)
```
You step back and look at your work. The plant sits healthy and upright in its new, larger home. The fresh moist soil is perfectly compacted, not too tight, not too loose. You touch a leaf gently - it's firm and perky, no longer wilted. The drainage is working well, and the plant is perfectly positioned. You've successfully given it room to grow.
```

---

## 🌱 BRANCHING PATH STATES

### s1_alt_0 - Attempted In-Pot Repotting (Risky/Shortcut Outcome)
```
You've added fresh soil around the edges of the current pot without fully removing the plant. You used a chopstick to loosen some surface roots, but the plant is still cramped in the same container. The new soil sits compacted on top of the old. The leaves show only minimal improvement - they're slightly less wilted, but the root-bound problem persists underneath. You realize this wasn't enough.
```

### s1_alt_1 - Recovery: Proper Root Inspection After Failed Shortcut
```
You've now committed to doing it right. The plant is out of the pot, roots exposed in your hands. You carefully inspect them, turning the root ball. You've trimmed away the dead, brown circling roots with sharp pruning shears - clean cuts. The remaining healthy roots now have space to breathe and grow. The plant is ready for a proper new home.
```

### s4_alt_0 - Hasty Placement (Messy State)
```
You quickly dumped the plant into the new pot without much care. Looking down, you see it's off-center, leaning slightly to one side. The soil is scattered haphazardly around the roots - some gaps remain unfilled, other areas are too loosely packed. There's soil spilled on the rim and work surface. Some roots might be bent or stressed. It's functional, but messy and imperfect.
```

---

## 🎯 SUCCESS ENDING STATES

### s_perfect - Flawless Success (Quality: 1.0)
```
You step back and take in the sight before you. This is perfection. The plant stands proudly in its new pot, centered with absolute precision. The leaves are vibrant green and perky, reaching upward with visible energy. You kneel down to inspect: the soil is evenly moist throughout, perfectly compacted - you can press it gently and it springs back just right. The drainage holes show healthy water flow with no pooling in the saucer. Every root was handled with care during the transition - no damage, no stress. The plant isn't just surviving; it's thriving. This is exactly what plant care should look like.
```

### s_good - Successful with Minor Imperfections (Quality: 0.8)
```
You look at the finished work. The plant is in its new, larger pot and looking healthy - the leaves have good color and are mostly perky. The soil is moist and most excess water has drained away. As you lean in closer, you notice it's positioned slightly off-center, maybe an inch to the left. There's a small amount of soil scattered around the pot rim. You touch a few leaves - they feel good, though perhaps not as vibrant as they could be. A few small roots might have been slightly bent during the transfer. It's a success, definitely better than before, but not quite perfect.
```

### s_acceptable - Adequate Success with Issues (Quality: 0.6)
```
The plant has survived the repotting and is in its new home - that's the important part. But looking at it now, you see several issues. The plant leans noticeably to one side. The soil feels a bit too compacted when you press it - maybe you packed it too hard. There's still water sitting in the drainage tray that hasn't evaporated. The leaves look somewhat dull and show mild stress signals - a slight droop despite the watering. You can see soil spilled around the base. Some of the root ball was clearly disturbed more than ideal. It'll probably be okay, but it's not the quality you were hoping for.
```

---

## ❌ FAILURE ENDING STATES

### f_critical_error - Catastrophic Failure (Quality: 0.0)
```
You stare down at the disaster in front of you. The plant's main stem is snapped - broken cleanly in two, sap oozing from the break. When you tried to force it out of the old pot, the root ball tore apart in your hands. Soil is everywhere - a pile on the table, scattered on the floor. Even the new pot has a crack in it from being knocked over in the chaos. The plant's leaves are wilting rapidly, darkening. You hold the broken pieces, but there's nothing you can do. This plant is beyond saving. The entire operation failed catastrophically.
```

### f_gave_up - Abandoned Mid-Process (Quality: 0.1)
```
The scene in front of you is chaotic and incomplete. The old pot lies on its side, cracked. The plant is partially removed, half the root ball still stuck in the broken pot, the other half exposed to air. Roots are drying out where they're exposed. Soil is spilled everywhere - on the table, the floor, your hands. The new pot sits empty beside you, mocking your abandoned effort. You started the process but couldn't finish. The plant is left in the worst possible state: vulnerable, stressed, and in limbo between its old home and the new one it never reached.
```

---

## 🎬 CANONICAL PATH ACTIONS

### a0 - Initial Watering
```
Pick up the watering can and slowly pour water over the soil, moving in a circular pattern to ensure even coverage. Keep pouring until you see water draining from the bottom holes into the saucer. Set down the can and check the moisture meter - watch it move into the healthy range.
```

### a1 - Remove Plant
```
Place one hand on top of the soil with your fingers gently around the base of the plant. With your other hand, tip the pot and gently squeeze the sides. Slide the plant out carefully, supporting the root ball. Turn it in your hands to examine the roots from all sides, looking for any damage or root-bound areas.
```

### a2 - Trim and Prepare Roots
```
Pick up the clean scissors and identify any brown, mushy, or damaged roots. Snip them off cleanly. Now use your fingers to gently tease apart any roots that are circling around each other, feeling them separate and straighten. Brush away the old soil from the roots, letting it fall away.
```

### a3 - Prepare New Pot
```
Take the larger pot and flip it over briefly to check that the drainage hole is clear. Set it upright. Grab the trowel and scoop fresh potting soil from the bag, adding a 1-2 inch layer to the bottom of the pot. Press it down gently with your palm to create a stable base for the plant.
```

### a4 - Position Plant
```
Lift the prepared plant with both hands, supporting the root ball from below. Lower it into the center of the new pot, adjusting its position until it's centered and the top of the root ball sits slightly below the rim. Begin scooping fresh soil around the sides with the trowel, filling gaps around the roots. Use your fingers to gently press and compact the soil as you go around.
```

### a5 - Fill with Soil
```
Continue adding fresh soil around the plant, working your way up. Fill to about an inch below the pot rim, leaving space for watering. Press down gently all around with your palms, compacting the soil enough to support the plant. Check that the soil level is even and the plant stands upright.
```

### a6 - Final Watering
```
Pick up the watering can and pour water slowly over the new soil, starting near the stem and working outward in circles. Keep pouring until water begins draining from the bottom holes. Set down the can, lift the pot to pour excess water from the saucer underneath. Make sure drainage is working properly.
```

### a7 - Final Observation
```
Step back and observe the plant from all angles. Check that it's standing upright and centered. Touch the soil - it should be moist but not waterlogged. Look at the leaves - they should appear more perky and healthy than before. Confirm the plant has successfully transitioned to its new home and has room to grow.
```

---

## 🔀 BRANCHING PATH ACTIONS

### Risky Action 1: Attempt In-Pot Repotting (from s1)
```
Instead of removing the plant, try to work around it. Grab a chopstick and carefully poke it into the soil along the edges, trying to loosen the root-bound areas without taking the plant out. Sprinkle some fresh soil on top and around the edges where you can reach. Press it down gently, hoping this half-measure will be enough to help the plant without the full repotting effort.
```

### Recovery Action 1: Proper Removal After Failed Shortcut (from s1_alt_0)
```
You realize you need to do this properly. Take a deep breath. Now carefully remove the plant from the pot - tip it, squeeze the sides, and slide it out fully. Hold the root ball in your hands and inspect it closely. Get out the pruning shears and methodically trim away all the dead, circling roots you can see. Make clean cuts. Tease apart the healthy roots gently but thoroughly.
```

### Recovery Action 2: Complete Proper Repotting (from s1_alt_1)
```
Now that the roots are properly prepared, grab the new appropriately-sized pot. Add your base layer of fresh soil. Center the plant carefully in the middle, checking from all angles. Fill around the roots with fresh soil, compacting gently as you go. Water thoroughly, watching it drain completely. Take your time and do it right.
```

### Shortcut Action 1: Skip Full Repotting (from s1)
```
You look at the work ahead and decide to cut corners. Instead of the full repotting process, just sprinkle a small amount of fresh soil on top of the existing soil in the current pot. Smooth it around the base of the plant. Tell yourself you'll do the proper repotting later. For now, just maintain the regular watering schedule and hope the plant manages.
```

### Risky Action 2: Hasty Dump into New Pot (from s4)
```
You're in a hurry. Instead of carefully positioning the plant, just quickly drop it into the new pot - wherever it lands. Grab handfuls of soil and dump them around the roots without much attention to centering or proper compaction. Fill the gaps haphazardly. Don't worry about making it neat. Just get the soil in and hope the plant settles correctly on its own.
```

### Recovery Action 3: Water Despite Messy Placement (from s4_alt_0)
```
Even though the placement isn't ideal and the soil is messy, go ahead and water the plant thoroughly. Pour slowly, watching the water work its way through the loose soil and drain out the bottom. The watering might help settle some of the soil gaps and compact things a bit naturally. Pour out any excess water from the saucer.
```

### Shortcut Action 2: Quick Soil Dump (from s4)
```
Instead of carefully adding soil in stages and compacting as you go, just dump the remaining soil from the bag directly into the pot around the plant. Don't bother with careful compaction or checking soil levels. Just fill the gaps quickly and roughly. Try to get the soil to the right height without much finesse.
```

### Risky Action 3: Skip Observation, Direct Sunlight (from s7)
```
You assume everything is perfect without really checking. Don't bother with the careful observation. Instead, immediately grab the pot and carry it over to the window where direct sunlight streams in. Set it right in the bright sun, thinking this will make the plant grow faster. Walk away to your next task without verifying the plant's condition.
```

### Shortcut Action 3: Quick Glance and Leave (from s7)
```
Give the plant a quick once-over glance. Looks fine from here - it's upright, there's soil, you watered it. That's probably good enough. Don't bother checking the soil moisture closely or examining the leaves. Don't verify the drainage. Just assume it worked out and move on to whatever's next on your to-do list.
```

### Non-action: Continue Watering After Shortcut (from s1_alt_0 - second state)
```
You've tried the shortcut approach and it didn't really work. Now, in frustration or confusion, you decide to just water the plant again on schedule. Pour water over the inadequately repotted plant, giving it a thorough soaking as if that will somehow fix the underlying root-bound problem. The water runs through and drains out, but you're not addressing the real issue.
```

---

## 📊 Usage Guide

### For Video Generation
Each state description is ready to use as a **video generation prompt** with:
- Clear camera perspective (overhead/egocentric)
- Physical action descriptions
- Sensory details (touch, sight, motion)
- Continuous narrative flow

### For Interactive Agents
Each action is written as **executable instructions** with:
- Step-by-step physical movements
- Decision points made explicit
- Observable verification steps
- Hand/body positioning details

### Branching Structure
```
s0 (Initial)
 │
 ├─[a0: Water]─────────────> s1 (Watered)
 │                            ├─[a1: Remove]───> s2 ───> s3 ───> s4 ─┬─> s5 ───> s6 ───> s7 ─┬─> s8 (good)
 │                            │                                      │                      │
 │                            ├─[Risky: In-pot]─> s1_alt_0          │                      ├─[a7]─> s_perfect ✅
 │                            │                    └─[Recover]─> s1_alt_1 ───> s_perfect ✅  │
 │                            │                                                            └─[Risky: Sunlight]─> s_acceptable ✅
 │                            └─[Shortcut: Skip]─> s1_alt_0                                └─[Shortcut: Glance]─> f_critical_error ❌
 │                                                  └─[Water]─> f_critical_error ❌
 │
 └─────────────────────────> s4 (Prepared pot)
                              ├─[a4: Position]──> s5 (normal path)
                              │
                              ├─[Risky: Dump]──> s4_alt_0 ──[Water]──> s_good ✅
                              │
                              └─[Shortcut: Quick Dump]──> f_critical_error ❌
```

---

## 🎯 Key Improvements Over Original

1. **Egocentric View**: Every description uses "you" perspective
2. **Continuous Action**: Present tense, happening right now
3. **Sensory Rich**: Touch (soil texture), sight (water draining), motion (turning the plant)
4. **Physical Details**: Hand positions, body movements, tool handling
5. **Spatial Awareness**: "beside you", "on your right", "in front of you"
6. **Emotional Tone**: Success feels satisfying, failure feels frustrating
7. **Observable States**: What the camera would actually see

---

**File Location**: `worlds/llm_worlds/indoor_plant_watering_repotting_branching_world.json`  
**Total States**: 16 (9 canonical + 3 branching + 4 endings)  
**Total Actions**: 18 (8 canonical + 10 branching variants)  
**Ready for**: Video generation, embodied AI, interactive demos






