# Enhanced Paper Organization (ICML Position Paper)

Purpose: Updated, concrete outline that merges (a) the current architecture in
`paper_structure.md`, (b) legacy details in `example_paper.tex`, and (c) the
action-graph construction and grounding pipeline implemented in this repo.

Guiding constraints:
- Keep the position-paper tone (manifesto + conceptual clarity).
- Make Section 3 very concrete (action-graph proposal and grounding pipeline).
- Keep Section 4 to exactly one minimal experiment, aligned with existing code.

---

## Section 0 - Introduction (manifesto, 1 to 1.5 pages)

Goal: Start the debate and state the thesis plainly.

Key beats:
- Why now: explosion of video and multimodal "world models" (Sora, Veo, Genie,
  PAN, World Labs Marble, Cosmos, GAIA). The field equates visual realism with
  world-model quality.
- Core failure: passive realism is not interactive correctness. Prompt-only
  rollouts hide causal incoherence and action ambiguity.
- Thesis (explicit): world models must be evaluated and constructed around
  action-state consistency, not only perceptual fidelity.
- What this paper does (high level, no tech yet):
  - Defines a state-modality x action-interface taxonomy.
  - Argues for action-centric evaluation via a metric quad.
  - Shows an explicit action-graph construction that makes the principle
    operational.
- Why it matters: agents, planning, simulation, safety, comparability.

Suggested citation anchors:
- Sora, Veo, Genie/Oasis/GameNGen (visual realism, passive or limited action).
- Dreamer / PlaNet (action-conditioned but latent).
- VBench / FVD / LPIPS (evaluation bias toward perceptual fidelity).

Possible figure:
- "Perceptual fidelity vs action controllability" scatterplot with exemplar
  systems (Sora, Dreamer, Genie, Minecraft, etc.).

---

## Section 1 - A Taxonomy for World Models (reframing the field)

Goal: Give the community a shared language so comparisons are well-posed.

Core structure (from legacy + literature analysis):
- State modality axis: text, image, video, latent, 3D/spatial.
- Action interface axis: none (prompt-only), pixel, motor/continuous, symbolic,
  hybrid.
- Table 1: taxonomy mapping with representative systems per cell.

Concrete items to include:
- Explicit definition of "state modality" and "action interface".
- Why "Sora-like" and "Dreamer-like" models are incomparable without this split.
- Immediate consequence: cinematic models can rank high on perceptual metrics
  yet be unusable for agents.

Recommended citations by slot:
- Foundational: PlaNet, Dreamer, DreamerV2/V3.
- Passive video: Sora, Veo, VastDreamer, FreeLong, Video-Infinity.
- Interactive: Genie 1/2/3, Oasis, GameNGen, PAN.
- 3D/Spatial: World Labs Marble.
- Robotics / driving: RT-2, UniSim, GAIA-1/2, Cosmos.
- Agent benchmarks: D4RL, Meta-World, RLBench, ALFRED, Habitat, AgentBench,
  WebArena.

Deliverables:
- Taxonomy table (updated from legacy Table 1).
- One paragraph clarifying apples-to-apples evaluation within each cell.

---

## Section 2 - Why Action-State Consistency Is the Missing Axis

Goal: Justify the evaluation lens; show what current benchmarks miss.

Key arguments (from legacy + literature analysis):
- What is measured today: visual fidelity and short-horizon smoothness
  (LPIPS, FVD, VBench), downstream task success (D4RL, RLBench, Habitat).
- What is not measured: causal legibility, counterfactual correctness, branching
  control, inverse dynamics.
- Action-state consistency as a diagnostic:
  - Can we infer the action from the transition? (inverse dynamics)
  - Do distinct actions induce distinct futures? (branching control)

Legacy detail to carry over:
- Metric quad (2x2): State Consistency (SC), State DoF (SD),
  Action Rationality AR_inv (inverse dynamics), Action DoF (AF).
- Brief definitions of each metric, without heavy math.

Suggested figure or table:
- The metric quad (clean, 2x2 grid) with one-line definitions.

Optional short inset (kept tight):
- "Why prompt-as-action is insufficient" (argue that prompts are not a
  controllable action interface with stable semantics).

---

## Section 3 - From Principle to Practice: An Action-Centric Construction

Goal: Provide a concrete existence proof (not a SOTA claim). This is the core
section that should be clear and operational.

### 3.1 Design requirements implied by the thesis
- Explicit action interface (symbolic or hybrid), not implicit prompt-only.
- Explicit state representations (text + metadata), not opaque latent-only.
- Graph-structured transitions so branching is inspectable and evaluable.
- Multi-ending outcomes (graded success and failures) to reflect real tasks.

### 3.2 Action-conditioned world graphs (AC-World)
Grounded in the implementation in `world_model_bench_agent/benchmark_curation.py`.

Key elements to describe:
- World is a directed multigraph: states, actions, transitions.
- Each Transition is (state_t, action_t) -> state_{t+1}.
- World includes initial state, goal states, and final states.
- Graph diagnostics enabled by code:
  - Decision points: `get_decision_points()` for multi-action states.
  - Branching factor: `get_branching_factor()`.
  - Canonical path: `get_canonical_path()`.
  - Successful vs failed paths: `get_successful_paths()` / `get_failed_paths()`.
- States and actions are human-readable with metadata
  (progress, quality, tools, risk, etc.).

### 3.3 World families (linear, branching, multi-ending)
Backed by curated examples in `benchmark_curation.py` and LLM generation in
`llm_world_generator.py`.

What to say:
- Linear worlds: single canonical path (procedural tasks).
- Branching worlds: decision points with alternative strategies.
- Multi-ending worlds: multiple success qualities and explicit failures.
- LLM generator flow (code-backed):
  - `generate_linear_world()` produces a canonical path.
  - `expand_to_branching_world()` adds alternative actions and endings.
  - Endings include quality metadata (perfect/good/acceptable/failure).

Example tasks (already present in repo):
- IKEA desk assembly (branching + multi-ending).
- Apple eating (small branching world, 8 states, 7 transitions).
- Plant repotting (egocentric branching world).

### 3.4 Grounding pipeline: text -> image -> video
Grounded in `image_world_generator.py`, `video_world_generator.py`,
and the pipeline docs.

Concrete details to include:
- Image world generation:
  - Initial state generated from scratch with full prompt.
  - Subsequent states generated via image variation (reference image) to
    preserve camera angle and scene identity.
  - Two strategies: `canonical_path` (cheap) and `full_world` (BFS over graph).
- Video world generation:
  - First-frame + last-frame interpolation with action prompt.
  - Two strategies: `canonical_only` or `all_transitions`.
- JSON schema tracks parent-state and parent-action for each node.
- Explicitly mention "same graph, multiple modalities": text nodes, egocentric
  descriptions, images, videos are all grounded to the same transition graph.

Optional practical note (one sentence):
- Cost and feasibility: text world is cheap, images moderate, videos expensive
  but feasible for small worlds (from pipeline docs).

Suggested figures:
- Figure A: action-conditioned world graph (nodes/edges + branching).
- Figure B: pipeline diagram (text world -> image world -> video world).
- Figure C (optional): "same state, two actions, two distinct outcomes".

---

## Section 4 - Evidence: What Breaks Without Action-Centricity

Requirement: ONE minimal experiment only, aligned with existing code.

### Minimal experiment: Action-Inference Diagnostic on a Small AC-World

Setup (all assets already in repo):
- World: `worlds/llm_worlds/apple_eating_branching_world.json`
  (8 states, 7 transitions, 3 distinct success paths).
- Optional grounding (if visuals needed): `ImageWorldGenerator` with
  `strategy="full_world"`; existing output in
  `worlds/image_worlds/apple_eating_branching_image_world.json`.

Procedure (minimal):
- For each transition, infer the action from (state_t, state_{t+1}).
- Use `StateActionGenerator.infer_action()` on textual states (fastest, no
  additional tooling), then match to the ground-truth action label in the graph.
- Report top-1 accuracy as a proxy for AR_inv on this tiny world.

What it demonstrates:
- With an explicit action graph, action inference is well-posed and measurable.
- Prompt-only rollouts do not define a stable candidate action set, so AR_inv is
  ill-posed or collapses to "free-form prompt matching".

Deliverables in the paper:
- One small table: action inference accuracy on the 7 transitions.
- One qualitative figure: two alternative branches from the same state
  (cut vs bite), showing distinct outcomes.

No additional experiments beyond this single diagnostic.

---

## Section 5 - Implications for the Field

Focus points (from paper_structure + literature trends):
- Agent benchmarking: evaluations should separate model dynamics from policy.
- World models as testbeds: action graphs enable reproducible, shared tasks.
- Co-evolution of policy and model: explicit action interfaces make failures
  diagnosable (bad action vs bad dynamics).
- JEPA-style representation learning is necessary but insufficient without
  action grounding.
- Visual realism will plateau without interaction grounding.

---

## Section 6 - Alternative Views and Counterarguments

Keep short and direct:
- "Prompts are actions" -> prompt semantics are unstable, not a fixed interface.
- "Agents can learn around it" -> still obscures the model's dynamics quality.
- "Realism correlates with usefulness" -> correlation is not evaluability.
- "Physical consistency as priority" vs action as the priority 

---

## Section 7 - Conclusion (short and strong)

Restate:
- The evaluation axis is incomplete without action-state consistency.
- A simple, explicit action-graph construction makes the principle operational.
- Progress in world models should be measured by reliable response to
  intervention, not just realism.

Closing line (echo paper_structure):
"Measure progress not by how real the world looks, but by how reliably it
responds to intervention."
