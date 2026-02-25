# Literature Analysis: World Models and Action-Centric Benchmarking

This document provides a comprehensive analysis of literature related to world models, their evaluation, and the action-centric benchmarking framework proposed in the position paper.

---

## Table of Contents

1. [Paper Overview and Central Thesis](#paper-overview-and-central-thesis)
2. [Taxonomy Framework](#taxonomy-framework)
3. [Literature Analysis by Category](#literature-analysis-by-category)
   - [A. Foundational World Models (Model-Based RL)](#a-foundational-world-models-model-based-rl)
   - [B. Video Prediction and Generative World Models](#b-video-prediction-and-generative-world-models)
   - [C. Self-Supervised Representation Learning](#c-self-supervised-representation-learning)
   - [D. Embodied AI and Robotics Benchmarks](#d-embodied-ai-and-robotics-benchmarks)
   - [E. Evaluation Metrics and Frameworks](#e-evaluation-metrics-and-frameworks)
   - [F. Agent Benchmarks and Tool Use](#f-agent-benchmarks-and-tool-use)
   - [G. Vision-Language Models](#g-vision-language-models)
   - [H. Long-Form Video Generation](#h-long-form-video-generation)
   - [I. World Model Theory and Surveys](#i-world-model-theory-and-surveys)
4. [Extended Literature: Additional World Model Papers](#extended-literature-additional-world-model-papers)
5. [Taxonomy Mapping Table](#taxonomy-mapping-table)

---

## Paper Overview and Central Thesis

The position paper argues that world models should be benchmarked for **action-state consistency**, not just visual/perceptual quality. The key contributions are:

1. **State-Action Taxonomy**: Organizing world models by state modality (text/image/video) and action interface (none/pixel/motor/symbolic/hybrid)
2. **Metric Quad**: Four evaluation dimensions:
   - **State Consistency (SC)**: Does the world hold together over time?
   - **State Degrees of Freedom (SD)**: How rich/diverse is the reachable world?
   - **Action Rationality (AR_inv)**: Are transitions causally interpretable?
   - **Action Degrees of Freedom (AF)**: How many distinct futures can actions induce?
3. **AC-World Construction**: Explicit action-conditioned graphs as benchmark environments

---

## Taxonomy Framework

### State Modality ($m_S$)
| Modality | Description | Examples |
|----------|-------------|----------|
| Text | Language-based state descriptions | LLM world models, text adventures |
| Image | Single-frame visual states | Image generators, static scenes |
| Video | Temporal visual sequences | Video generators, simulators |
| Latent | Learned representation space | Dreamer, PlaNet |
| 3D/Spatial | Explicit 3D structure | World Labs, NeRF-based models |

### Action Interface ($m_A$)
| Interface | Description | Examples |
|-----------|-------------|----------|
| None | Prompt-only, no explicit actions | Sora, Stable Diffusion |
| Pixel | Low-level pixel/mouse control | Genie |
| Motor | Continuous control signals | Robotics controllers |
| Symbolic | Discrete structured commands | Game actions, API calls |
| Hybrid | Mix of high and low-level | AC-World |

---

## Literature Analysis by Category

### A. Foundational World Models (Model-Based RL)

#### 1. PlaNet (Hafner et al., 2019)
**Citation**: `hafner2019planet`
- **Title**: Learning Latent Dynamics for Planning from Pixels
- **Venue**: ICML 2019

**Summary**: PlaNet learns a latent dynamics model from high-dimensional image observations and uses it for planning via the cross-entropy method. It represents one of the first successful applications of learned world models for continuous control from pixels.

**Relationship to Paper**:
- **State Modality**: Latent (learned from video)
- **Action Interface**: Motor (continuous control)
- **Metric Profile**: High SC (trained for prediction accuracy), Medium SD (task-specific), High AR (deterministic actions), Medium AF (continuous action space)
- **Relevance**: Foundational example of action-conditioned world modeling. PlaNet explicitly conditions predictions on actions, making it directly relevant to the paper's thesis. However, it lacks explicit state-action graphs and is evaluated primarily on task success rather than action consistency.

---

#### 2. Dreamer (Hafner et al., 2020)
**Citation**: `hafner2020dreamer`
- **Title**: Dream to Control: Learning Behaviors by Latent Imagination
- **Venue**: ICLR 2020

**Summary**: Dreamer extends PlaNet by learning behaviors entirely within the learned world model ("imagination"), using actor-critic methods in latent space rather than planning.

**Relationship to Paper**:
- **State Modality**: Latent
- **Action Interface**: Motor/Symbolic (task-dependent)
- **Metric Profile**: Similar to PlaNet but with learned policies
- **Relevance**: Demonstrates the utility of world models for policy learning. The "dreaming" paradigm aligns with the paper's vision of world models as simulators for agent development. Evaluated on task reward rather than action-state consistency.

---

#### 3. DreamerV2 (Hafner et al., 2021)
**Citation**: `hafner2021dreamerv2`
- **Title**: Mastering Atari with Discrete World Models
- **Venue**: ICLR 2021

**Summary**: DreamerV2 introduces discrete latent representations using categorical distributions, achieving human-level performance on Atari games using world model learning.

**Relationship to Paper**:
- **State Modality**: Latent (discrete)
- **Action Interface**: Symbolic (discrete game actions)
- **Metric Profile**: High SC (Atari games are deterministic), Finite SD (game states), High AR (discrete actions), Finite AF (fixed action set)
- **Relevance**: Key baseline for discrete action spaces. The paper's "Classic Platformer (Mario)" category directly relates to DreamerV2's domain. Demonstrates that world models can achieve strong performance in structured environments.

---

#### 4. Action-Conditional Video Prediction (Oh et al., 2015)
**Citation**: `oh2015action`
- **Title**: Action-Conditional Video Prediction using Deep Networks in Atari Games
- **Venue**: NeurIPS 2015

**Summary**: One of the earliest works on action-conditioned video prediction, predicting future frames in Atari games conditioned on agent actions.

**Relationship to Paper**:
- **State Modality**: Video (pixel-level)
- **Action Interface**: Symbolic (discrete)
- **Metric Profile**: Medium SC (early architecture), Finite SD, High AR (explicit conditioning)
- **Relevance**: Pioneering work that establishes the action-conditioned prediction paradigm central to the paper's thesis. Demonstrates that conditioning on actions is essential for controllable world models.

---

### B. Video Prediction and Generative World Models

#### 5. VastDreamer (Wu et al., 2023)
**Citation**: `wu2023vastdreamer`
- **Title**: VastDreamer: Universal World Models for 3D Video Generation
- **Venue**: arXiv 2023

**Summary**: VastDreamer extends world modeling to 3D video generation, aiming for universal world simulation across diverse scenes.

**Relationship to Paper**:
- **State Modality**: 3D/Video
- **Action Interface**: Likely None/Prompt
- **Metric Profile**: High SC, High SD, Low AR (no explicit action interface), Low AF
- **Relevance**: Represents the "cinematic world model" category that the paper argues is insufficient. High visual quality but limited action-grounded controllability.

---

#### 6. WorldWalk (Wang et al., 2023)
**Citation**: `wang2023worldwalk`
- **Title**: WorldWalk: World Models as World Simulators
- **Venue**: arXiv 2023

**Summary**: Proposes treating world models explicitly as world simulators, bridging the gap between generation and simulation.

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: Variable
- **Relevance**: Philosophically aligned with the paper's view of world models as actionable simulators rather than passive generators.

---

### C. Self-Supervised Representation Learning

#### 7. DINO (Caron et al., 2021)
**Citation**: `caron2021dino`
- **Title**: Emerging Properties in Self-Supervised Vision Transformers
- **Venue**: ICCV 2021

**Summary**: DINO demonstrates that self-supervised vision transformers learn semantically meaningful features that emerge without explicit supervision.

**Relationship to Paper**:
- **Role**: Perceptual encoder for evaluation metrics
- **Relevance**: The paper uses DINO (alongside CLIP) as $\phi(\cdot)$ for embedding states in the metric computations. DINO features provide semantic similarity measures for clustering states and computing consistency scores.

---

#### 8. CLIP (Radford et al., 2021)
**Citation**: `radford2021clip`
- **Title**: Learning Transferable Visual Models From Natural Language Supervision
- **Venue**: ICML 2021

**Summary**: CLIP learns visual representations aligned with natural language through contrastive learning on image-text pairs.

**Relationship to Paper**:
- **Role**: Perceptual encoder for evaluation; potential bridge between text and visual modalities
- **Relevance**: Used as $\phi(\cdot)$ for computing state embeddings. Enables cross-modal evaluation and could support hybrid text-visual world models.

---

#### 9. LeCun's Path Towards Autonomous Intelligence (2022)
**Citation**: `lecun2022path`
- **Title**: A Path Towards Autonomous Machine Intelligence (Version 0.9)
- **Venue**: Technical Report 2022

**Summary**: LeCun's influential position paper proposing the Joint-Embedding Predictive Architecture (JEPA) as a path toward human-like intelligence, emphasizing world models and prediction in representation space.

**Relationship to Paper**:
- **Relevance**: Foundational theoretical work that motivates prediction in representation space rather than pixel space. The JEPA framework directly inspires I-JEPA and V-JEPA. The paper's metric quad can be seen as operationalizing aspects of LeCun's vision for evaluating world models.

---

#### 10. I-JEPA (Assran et al., 2023)
**Citation**: `assran2023ijepa`
- **Title**: Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture
- **Venue**: CVPR 2023

**Summary**: I-JEPA applies the JEPA framework to images, predicting representations of masked regions rather than reconstructing pixels.

**Relationship to Paper**:
- **State Modality**: Latent (image-derived)
- **Action Interface**: None (passive prediction)
- **Relevance**: Represents the representation-learning substrate that could underpin visual world models. Does not include actions but provides strong state representations.

---

#### 11. V-JEPA (Bardes et al., 2024)
**Citation**: `bardes2024vjepa`
- **Title**: Revisiting Feature Prediction for Learning Visual Representations from Video
- **Venue**: arXiv 2024

**Summary**: V-JEPA extends JEPA to video, learning temporal representations by predicting masked video regions in representation space.

**Relationship to Paper**:
- **State Modality**: Video/Latent
- **Action Interface**: None
- **Metric Profile**: High SC (designed for temporal coherence), Medium SD, N/A for action metrics
- **Relevance**: Strong video representations but no action interface. Illustrates the gap between representation learning and action-conditioned world modeling that the paper addresses.

---

#### 12. VideoMAE (Tong et al., 2022)
**Citation**: `tong2022videomae`
- **Title**: VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training
- **Venue**: NeurIPS 2022

**Summary**: Applies masked autoencoding to video, demonstrating data-efficient self-supervised pre-training for video understanding.

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: None
- **Relevance**: Provides video representations that could be used for state encoding. Like V-JEPA, focuses on passive prediction without action conditioning.

---

### D. Embodied AI and Robotics Benchmarks

#### 13. D4RL (Fu et al., 2021)
**Citation**: `fu2021d4rl`
- **Title**: D4RL: Datasets for Deep Data-Driven Reinforcement Learning
- **Venue**: NeurIPS 2021

**Summary**: D4RL provides offline RL datasets across diverse domains (locomotion, navigation, manipulation) for benchmarking data-driven RL methods.

**Relationship to Paper**:
- **State Modality**: Varies (state vectors, images)
- **Action Interface**: Motor (continuous control)
- **Limitation**: Evaluates downstream control performance, not world model quality directly
- **Relevance**: The paper notes that such benchmarks "conflate the agent, exploration, reward design, and the environment itself" and don't provide explicit ground-truth state graphs for diagnosing world model dynamics.

---

#### 14. Meta-World (Yu et al., 2020)
**Citation**: `yu2020metaworld`
- **Title**: Meta-World: A Benchmark and Evaluation for Multi-Task and Meta Reinforcement Learning
- **Venue**: CoRL 2020

**Summary**: Meta-World provides 50 distinct robotic manipulation tasks for evaluating multi-task and meta-learning algorithms.

**Relationship to Paper**:
- **State Modality**: State vectors / Images
- **Action Interface**: Motor
- **Limitation**: Task success metrics, not action-state consistency
- **Relevance**: Rich action space but evaluation focuses on task completion rather than whether the world model correctly predicts action-conditioned transitions.

---

#### 15. BEHAVIOR (Li et al., 2022)
**Citation**: `li2022behavior`
- **Title**: BEHAVIOR: Benchmark for Everyday Household Activities in Virtual, Interactive, and Ecological Environments
- **Venue**: CVPR 2022

**Summary**: BEHAVIOR provides realistic household activity benchmarks in simulated environments with complex object interactions.

**Relationship to Paper**:
- **State Modality**: 3D/Video
- **Action Interface**: Symbolic/Motor (hybrid)
- **Relevance**: Complex action spaces and state transitions, but lacks explicit ground-truth transition graphs. Could benefit from AC-World-style evaluation.

---

#### 16. RLBench (James et al., 2020)
**Citation**: `james2020rlbench`
- **Title**: RLBench: The Robot Learning Benchmark & Learning Environment
- **Venue**: IEEE RA-L 2020

**Summary**: RLBench provides 100 robot manipulation tasks with realistic simulation and demonstration data.

**Relationship to Paper**:
- **State Modality**: Image/Video
- **Action Interface**: Motor (end-effector control)
- **Relevance**: Rich manipulation environment but evaluates policy success, not world model action consistency.

---

#### 17. ALFRED (Shridhar et al., 2020)
**Citation**: `shridhar2020alfred`
- **Title**: ALFRED: A Benchmark for Interpreting Grounded Instructions
- **Venue**: CVPR 2020

**Summary**: ALFRED requires agents to follow natural language instructions in simulated household environments.

**Relationship to Paper**:
- **State Modality**: Image/Video
- **Action Interface**: Symbolic (high-level actions) + NL instructions
- **Relevance**: Combines language and visual grounding with action execution. Closer to the paper's hybrid action interface but still lacks explicit state-action graph structure.

---

#### 18. Habitat (Savva et al., 2019)
**Citation**: `savva2019habitat`
- **Title**: Habitat: A Platform for Embodied AI Research
- **Venue**: ICCV 2019

**Summary**: Habitat provides a simulation platform for training embodied agents in photorealistic 3D environments.

**Relationship to Paper**:
- **State Modality**: 3D/Video
- **Action Interface**: Motor (navigation) + Symbolic
- **Relevance**: Platform for embodied AI but evaluation focuses on navigation success. The paper's benchmark could be instantiated within Habitat for action-consistency evaluation.

---

#### 19. Ego4D (Grauman et al., 2022)
**Citation**: `grauman2022ego4d`
- **Title**: Ego4D: Human-Centric Video Understanding at Scale
- **Venue**: CVPR 2022

**Summary**: Ego4D provides massive egocentric video data with annotations for understanding human activities from first-person perspective.

**Relationship to Paper**:
- **State Modality**: Video (egocentric)
- **Action Interface**: Implicit (observed actions, not agent-controlled)
- **Relevance**: Rich egocentric video data aligns with the paper's egocentric state descriptions. However, Ego4D evaluates understanding, not generation or control. Could provide data for training egocentric world models.

---

#### 20. Something-Something (Goyal et al., 2017)
**Citation**: `goyal2017something`
- **Title**: The "Something Something" Video Dataset for Learning and Evaluating Visual Common Sense
- **Venue**: ICCV 2017

**Summary**: A dataset of videos showing humans performing physical interactions with objects, designed to test understanding of physical common sense.

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: Implicit (observed human actions)
- **Relevance**: Tests physical reasoning and action understanding. Could inform action rationality evaluation ($AR_{inv}$) by providing examples of interpretable physical actions.

---

### E. Evaluation Metrics and Frameworks

#### 21. LPIPS (Zhang et al., 2018)
**Citation**: `zhang2018lpips`
- **Title**: The Unreasonable Effectiveness of Deep Features as a Perceptual Metric
- **Venue**: CVPR 2018

**Summary**: LPIPS uses deep features for perceptual similarity, better matching human judgments than pixel-based metrics.

**Relationship to Paper**:
- **Role**: Component of State Consistency metric ($SC$)
- **Relevance**: Used for measuring perceptual stability between consecutive frames (flow-warped LPIPS). Essential for operationalizing visual consistency.

---

#### 22. FVD - Fréchet Video Distance (Unterthiner et al., 2019)
**Citation**: `unterthiner2019fvd`
- **Title**: Towards Accurate Generative Models of Video: A New Metric and Challenges
- **Venue**: arXiv 2019 / ICML Workshops

**Summary**: FVD extends Fréchet Inception Distance to video, measuring distributional similarity of generated videos to real videos.

**Relationship to Paper**:
- **Role**: Component of State Consistency metric ($SC$)
- **Relevance**: Used as the temporal/distributional component of $SC_{temp}$. Measures whether generated rollouts match the statistical properties of real videos.

---

#### 23. VBench (Du et al., 2023)
**Citation**: `du2023vbench`
- **Title**: VBench: Comprehensive Benchmark Suite for Video Generative Models
- **Venue**: arXiv 2023

**Summary**: VBench provides a comprehensive evaluation suite for video generation covering multiple quality dimensions.

**Relationship to Paper**:
- **Relevance**: VBench evaluates video quality but under "passive rollouts" - it tests fidelity and coherence but not action-conditioned transitions. The paper argues this is incomplete for world models: VBench-style metrics should be combined with action-centric evaluation.

---

#### 24. Evaluating World Models in Generative Models (Vafa et al., 2024)
**Citation**: `vafa2024evaluating`
- **Title**: Evaluating the World Model Implicit in a Generative Model
- **Venue**: arXiv 2024

**Summary**: Proposes methods for probing whether generative models implicitly contain coherent world models, revealing failures not visible to standard metrics.

**Relationship to Paper**:
- **Relevance**: Directly aligned with the paper's thesis. Vafa et al. provide diagnostics for world model coherence; the paper's benchmark complements this by providing explicit state-action structure for systematic evaluation.

---

### F. Agent Benchmarks and Tool Use

#### 25. AgentBench (Liu et al., 2023)
**Citation**: `liu2023agentbench`
- **Title**: AgentBench: Evaluating LLMs as General-Purpose Agents
- **Venue**: arXiv 2023

**Summary**: AgentBench evaluates LLMs as agents across diverse environments including web, games, and coding.

**Relationship to Paper**:
- **State Modality**: Text (primarily)
- **Action Interface**: Symbolic (API calls, commands)
- **Limitation**: Tests agent competence, not world model quality
- **Relevance**: Evaluates whether agents can act effectively but doesn't isolate world model accuracy. The paper's teacher-forced evaluation mode addresses this by separating model fidelity from policy competence.

---

#### 26. ToolBench (Xu et al., 2023)
**Citation**: `xu2023toolbench`
- **Title**: ToolBench: A Large-Scale Dataset for Training and Evaluating Tool-Using Agents
- **Venue**: arXiv 2023

**Summary**: ToolBench provides training and evaluation data for agents that use external tools via API calls.

**Relationship to Paper**:
- **State Modality**: Text
- **Action Interface**: Symbolic (tool calls)
- **Relevance**: Tests tool use ability but lacks grounded environment dynamics. Could benefit from world model evaluation to test whether agents correctly predict tool effects.

---

#### 27. WebArena (Zhou et al., 2023)
**Citation**: `zhou2023webarena`
- **Title**: WebArena: A Realistic Web Environment for Building Autonomous Agents
- **Venue**: arXiv 2023

**Summary**: WebArena provides a realistic web environment for evaluating autonomous web agents.

**Relationship to Paper**:
- **State Modality**: Mixed (visual + text)
- **Action Interface**: Symbolic (web interactions)
- **Relevance**: Rich interactive environment but evaluation focuses on task success. The explicit state transitions in web interactions could be formalized using AC-World structure.

---

### G. Vision-Language Models

#### 28. GPT-4V Survey (Liu et al., 2023)
**Citation**: `liu2023gpt4v`
- **Title**: A Survey on GPT-4V(ision)
- **Venue**: arXiv 2023

**Summary**: Surveys the capabilities and applications of GPT-4V, the multimodal version of GPT-4.

**Relationship to Paper**:
- **Relevance**: GPT-4V could serve as the inverse dynamics judge ($\Psi$) for computing Action Rationality ($AR_{inv}$). Strong VLMs can infer actions from before/after visual pairs.

---

#### 29. LLaVA-NeXT (Li et al., 2024)
**Citation**: `li2024llava`
- **Title**: LLaVA-NeXT: A Stronger Vision-Language Model with High-Resolution Capabilities
- **Venue**: arXiv 2024

**Summary**: LLaVA-NeXT extends LLaVA with higher resolution image understanding.

**Relationship to Paper**:
- **Relevance**: Another candidate for the inverse dynamics judge. Open-source VLMs like LLaVA could provide reproducible evaluation of action rationality.

---

### H. Long-Form Video Generation

#### 30. FreeLong (Lu et al., 2024)
**Citation**: `lu2024freelong`
- **Title**: FreeLong: Training-Free Long Video Generation with SpectralBlend Temporal Attention
- **Venue**: arXiv 2024

**Summary**: FreeLong enables long video generation without additional training through spectral blending in temporal attention.

**Relationship to Paper**:
- **State Modality**: Video (long-form)
- **Action Interface**: None (prompt-only)
- **Relevance**: Addresses temporal coherence for long videos (high SC) but lacks action interface. Represents progress in passive video generation that the paper argues is insufficient for world models.

---

#### 31. Video-Infinity (Tan et al., 2024)
**Citation**: `tan2024videoinfinity`
- **Title**: Video-Infinity: Distributed Long Video Generation
- **Venue**: arXiv 2024

**Summary**: Video-Infinity enables arbitrarily long video generation through distributed computation.

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: None
- **Relevance**: Like FreeLong, focuses on extending video length while maintaining coherence. Important for world models that need long rollouts, but action conditioning is not addressed.

---

### I. World Model Theory and Surveys

#### 32. Survey of World Models (Ke et al., 2023)
**Citation**: `ke2023reviewworldmodel`
- **Title**: A Survey of World Models
- **Venue**: arXiv 2023

**Summary**: Comprehensive survey covering the landscape of world model research across domains.

**Relationship to Paper**:
- **Relevance**: Provides background and context for world model research. The paper's taxonomy and metric quad can be seen as a contribution to this survey landscape, providing a specific evaluation framework.

---

## Extended Literature: Additional World Model Papers

This section expands the literature analysis with additional world model papers discovered through comprehensive research, organized by the state-action taxonomy.

---

### J. Large-Scale Video Generation Models (State: Video, Action: None/Prompt)

These models achieve high visual quality but lack explicit action interfaces, representing the "cinematic world model" paradigm.

#### 33. Sora (OpenAI, 2024-2025)
- **Title**: Video Generation Models as World Simulators
- **Source**: [OpenAI Technical Report](https://openai.com/index/video-generation-models-as-world-simulators/)
- **Release**: February 2024 (preview), December 2024 (public), September 2025 (Sora 2)

**Summary**: Sora is OpenAI's text-to-video model capable of generating up to one minute of high-fidelity video. OpenAI explicitly frames Sora as a step toward "general purpose simulators of the physical world." The model uses a diffusion transformer architecture operating on spacetime patches of video latent codes.

**Technical Details**:
- Uses visual patches (analogous to text tokens in LLMs)
- Trained jointly on videos and images of variable durations, resolutions, and aspect ratios
- Sora 2 (2025) features internal world modeling for maintaining continuity across shots

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: None (prompt-only)
- **Metric Profile**: High SC (trained for coherence), High SD (diverse generation), Low AR_inv (no causal action interface), 0 AF (no action control)
- **Relevance**: Exemplifies the gap the paper identifies—high cinematic quality but no action-grounded controllability. OpenAI's framing as a "world simulator" motivates the paper's argument that simulation requires action interfaces.

---

#### 34. Veo (Google DeepMind, 2024-2025)
- **Title**: Veo Video Generation Model
- **Source**: [Google DeepMind](https://deepmind.google/models/veo/)
- **Releases**: May 2024 (Veo 1), December 2024 (Veo 2), May 2025 (Veo 3), October 2025 (Veo 3.1)

**Summary**: Veo is Google's text-to-video model emphasizing cinematography understanding—genres, lenses, camera moves, lighting—aiming for coherent motion, plausible physics, and scene consistency. Veo 3 adds native audio generation.

**Technical Details**:
- Uses 3D Convolutional Layers within a U-Net architecture
- Processes spatiotemporal data across channels, time, height, and width simultaneously
- Veo 2 supports 4K resolution with improved physics understanding

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: None (prompt-only)
- **Metric Profile**: High SC, High SD, Low AR_inv, 0 AF
- **Relevance**: Like Sora, demonstrates state-of-the-art passive video generation. The paper's experiments use Veo 3.0 as a baseline and as a rendering backbone for AC-World instantiation.

---

### K. Interactive World Models (State: Video, Action: Pixel/Symbolic)

These models provide explicit action interfaces, enabling real-time interaction.

#### 35. Genie 1/2/3 (Google DeepMind, 2024-2025)
- **Title**: Generative Interactive Environments / Large-Scale Foundation World Model
- **Source**: [DeepMind Blog](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)
- **Paper**: [arXiv:2402.15391](https://arxiv.org/abs/2402.15391)
- **Releases**: February 2024 (Genie 1), December 2024 (Genie 2), 2025 (Genie 3)

**Summary**: The Genie series represents DeepMind's foundation world models for interactive environment generation. Key innovations include:
- **Genie 1** (11B parameters): Trained on internet videos to learn latent actions without ground-truth labels
- **Genie 2**: Generates consistent 3D worlds from single images, supporting diverse viewpoints for 10-60 seconds
- **Genie 3**: Real-time generation at 24fps, 720p, with "promptable world events" for dynamic modification

**Technical Architecture** (Genie 1):
- Spatiotemporal video tokenizer
- Autoregressive dynamics model
- Latent action model (learns action space from observation changes)

**Relationship to Paper**:
- **State Modality**: Video (2D/3D)
- **Action Interface**: Pixel (keyboard/mouse style control)
- **Metric Profile**: Medium SC (improving across versions), Medium SD, Medium AR_inv (latent actions may be ambiguous), Medium AF
- **Relevance**: Closest existing work to the paper's vision of interactive world models. Genie's latent action model is innovative but may lack the causal interpretability the paper emphasizes. Included as a baseline in experiments.

---

#### 36. Oasis (Decart + Etched, 2024)
- **Title**: Oasis: A Universe in a Transformer
- **Source**: [Decart AI](https://decart.ai/publications/oasis-interactive-ai-video-game-model)
- **Release**: October 31, 2024

**Summary**: Oasis is the first real-time AI world model, generating a playable Minecraft-like environment entirely through neural network inference. It runs at 20fps using next-frame prediction based on keyboard/mouse inputs.

**Technical Details**:
- Trained on millions of hours of Minecraft gameplay footage
- End-to-end transformer architecture
- No traditional game engine—physics, rules, and graphics all generated by the model
- 500M parameter model available for local execution

**Limitations**:
- No persistent memory (3-second context window)
- "Dream-like" appearance with unpredictable scenery changes
- No sound

**Relationship to Paper**:
- **State Modality**: Video (3D-like)
- **Action Interface**: Pixel (keyboard/mouse)
- **Metric Profile**: Medium SC (drift issues), Medium SD, Medium AR_inv, Medium AF
- **Relevance**: Demonstrates feasibility of neural game engines. The memory limitations illustrate challenges in maintaining long-horizon consistency—a key concern for the paper's State Consistency metric.

---

#### 37. GameNGen (Google, 2024)
- **Title**: Diffusion Models Are Real-Time Game Engines
- **Source**: [arXiv:2408.14837](https://arxiv.org/abs/2408.14837)
- **Release**: August 2024 (NeurIPS 2024)

**Summary**: GameNGen demonstrates that diffusion models can function as real-time game engines, achieving 20fps DOOM simulation on a single TPU. Human raters cannot reliably distinguish generated gameplay from actual game footage.

**Technical Details**:
- Based on Stable Diffusion v1.4, modified for action conditioning
- Two-phase training: (1) RL agent plays game, (2) diffusion model trained on recorded frames+actions
- PSNR of 29.4 (comparable to lossy JPEG)
- Extended to Counter-Strike: Global Offensive with 381M parameters

**Relationship to Paper**:
- **State Modality**: Video (2D game)
- **Action Interface**: Symbolic (game controls)
- **Metric Profile**: High SC (within 3-second context), Finite SD (game-specific), High AR_inv (discrete actions), Finite AF
- **Relevance**: Strong example of action-conditioned world modeling in constrained domains. The paper's framework could evaluate GameNGen's action consistency more rigorously.

---

### L. Model-Based Reinforcement Learning World Models

#### 38. DIAMOND (Alonso et al., 2024)
- **Title**: Diffusion for World Modeling: Visual Details Matter in Atari
- **Source**: [arXiv:2405.12399](https://arxiv.org/abs/2405.12399)
- **Venue**: NeurIPS 2024 Spotlight

**Summary**: DIAMOND (DIffusion As a Model Of eNvironment Dreams) uses diffusion models for world modeling in RL, achieving 1.46 mean human-normalized score on Atari 100k—surpassing DreamerV3 (1.097), STORM (1.266), and IRIS (1.046).

**Technical Innovation**:
- First use of diffusion models as world models for online RL
- EDM formulation for long-horizon stability
- Preserves visual details lost by discrete latent approaches

**Relationship to Paper**:
- **State Modality**: Video (pixel-level)
- **Action Interface**: Symbolic (discrete game actions)
- **Metric Profile**: High SC, Finite SD, High AR_inv (explicit action conditioning), Finite AF
- **Relevance**: Advances state-of-the-art in action-conditioned world models for RL. Demonstrates that visual fidelity matters for world modeling—aligning with the paper's emphasis on state representation quality.

---

#### 39. MuZero (DeepMind, 2019-2021)
- **Title**: Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model
- **Source**: [arXiv:1911.08265](https://arxiv.org/abs/1911.08265)
- **Venue**: Nature 2020

**Summary**: MuZero learns a world model that predicts task-relevant quantities (reward, policy, value) rather than full state reconstructions. Combines AlphaZero's tree search with learned dynamics, achieving superhuman performance without knowing environment rules.

**Key Innovation**:
- Implicit world model focused on decision-relevant predictions
- Does not reconstruct observations—learns abstract transition dynamics
- Variants: EfficientZero (more sample-efficient), Equivariant MuZero (symmetry-aware)

**Relationship to Paper**:
- **State Modality**: Latent (abstract)
- **Action Interface**: Symbolic (discrete)
- **Metric Profile**: High SC (for task-relevant predictions), Variable SD, High AR_inv (explicit actions), Finite AF
- **Relevance**: Represents an alternative philosophy—world models need not reconstruct observations. The paper's framework could extend to evaluate abstract world models via inverse dynamics on predicted representations.

---

#### 40. DreamerV3 (Hafner et al., 2023)
- **Title**: Mastering Diverse Domains through World Models
- **Source**: [arXiv:2301.04104](https://arxiv.org/abs/2301.04104)

**Summary**: DreamerV3 extends the Dreamer line to work across diverse domains with fixed hyperparameters, from Atari to 3D environments to real robotics.

**Relationship to Paper**:
- **State Modality**: Latent
- **Action Interface**: Motor/Symbolic (domain-dependent)
- **Metric Profile**: High SC, Variable SD, High AR_inv, Variable AF
- **Relevance**: Strong general-purpose baseline for model-based RL. The paper mentions it as a benchmark in the RL world model category.

---

### M. Autonomous Driving World Models

#### 41. GAIA-1/2 (Wayve, 2023-2024)
- **Title**: GAIA-1: A Generative World Model for Autonomous Driving
- **Source**: [arXiv:2309.17080](https://arxiv.org/abs/2309.17080)
- **Release**: September 2023 (GAIA-1), 2024 (GAIA-2)

**Summary**: GAIA-1 is the first generative world model specifically designed for autonomous driving. It leverages video, text, and action inputs to generate realistic driving scenarios with fine-grained control over ego-vehicle behavior.

**Technical Details**:
- 9 billion parameters trained on 4,700 hours of UK driving data
- Casts world modeling as unsupervised sequence modeling with discrete tokens
- Emergent properties: scene dynamics understanding, contextual awareness, geometry comprehension

**GAIA-2 Improvements**:
- Enhanced controllability and geographic diversity (UK, US, Germany)
- Systematic generation of rare/high-risk scenarios (cut-ins, emergency maneuvers)

**Relationship to Paper**:
- **State Modality**: Video (driving scenes)
- **Action Interface**: Motor (vehicle control) + Text (scene specification)
- **Metric Profile**: High SC, High SD (diverse scenarios), Medium AR_inv (continuous control), Medium AF
- **Relevance**: Demonstrates domain-specific world models with explicit action conditioning. Wayve's approach to generating rare scenarios aligns with the paper's vision of world models for agent testing.

---

### N. Robotics World Models and VLAs

#### 42. RT-2 (Google DeepMind, 2023)
- **Title**: RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control
- **Source**: [arXiv:2307.15818](https://arxiv.org/abs/2307.15818)
- **Release**: July 2023

**Summary**: RT-2 is a Vision-Language-Action (VLA) model that unifies perception, reasoning, and control for robotic manipulation. It co-fine-tunes vision-language models (PaLI-X, PaLM-E) on both web data and robot trajectories.

**Key Capabilities**:
- Outputs discretized robot actions as text tokens
- Improved generalization: 32% → 62% on unseen scenarios
- Chain-of-thought reasoning for multi-stage tasks

**Related Developments**:
- OpenVLA (Stanford, 2024): Open-source 7B VLA trained on Open X-Embodiment
- SARA-RT: More efficient RT variants

**Relationship to Paper**:
- **State Modality**: Image/Video
- **Action Interface**: Motor (end-effector control as tokens)
- **Metric Profile**: Variable SC, Medium SD, High AR_inv (explicit action tokens), Medium AF
- **Relevance**: VLAs embed world models implicitly. The paper's inverse dynamics evaluation could probe whether VLAs correctly predict action effects.

---

#### 43. UniSim (Yang et al., 2024)
- **Title**: Learning Interactive Real-World Simulators
- **Source**: [arXiv:2310.06114](https://arxiv.org/abs/2310.06114)
- **Venue**: ICLR 2024 Outstanding Paper

**Summary**: UniSim is a visual universal simulator that takes an image and a natural-language action (e.g., "move forward," "open the drawer") and generates a video showing the action's execution.

**Technical Details**:
- Video U-Net architecture with interleaved temporal/spatial attention
- Trained on diverse datasets: images, robotics data, navigation data
- Unified action-in-video-out interface

**Applications**:
- Training high-level vision-language planners
- Training low-level RL policies with zero-shot real-world transfer
- Simulating rare/dangerous events (e.g., car crashes)

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: Symbolic/NL (natural language actions)
- **Metric Profile**: High SC, Medium SD, High AR_inv (explicit NL conditioning), Medium AF
- **Relevance**: Directly aligned with the paper's vision of action-conditioned world models. UniSim's NL action interface is similar to AC-World's hybrid approach.

---

#### 44. Cosmos (NVIDIA, 2025)
- **Title**: Cosmos World Foundation Model Platform for Physical AI
- **Source**: [NVIDIA Research](https://research.nvidia.com/publication/2025-01_cosmos-world-foundation-model-platform-physical-ai)
- **Release**: January 2025 (CES), March 2025 (GTC major update)

**Summary**: Cosmos is NVIDIA's platform of world foundation models for physical AI (robotics, autonomous vehicles). The models generate physics-aware videos predicting future states.

**Technical Details**:
- Trained on 9,000 trillion tokens from 20 million hours of real-world data
- Model tiers: Nano (real-time), Super (baseline), Ultra (maximum quality)
- Cosmos Reason: Chain-of-thought reasoning for predicting interaction outcomes

**Industry Adoption**:
- 1X (humanoid robot NEO Gamma), Figure AI, Skild AI, Uber, XPENG, Waabi
- 2 million+ downloads

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: Motor/Sensor data
- **Metric Profile**: High SC, High SD, High AR_inv (physics-aware), High AF
- **Relevance**: Represents the industry trend toward foundation world models for robotics. The paper's benchmark could standardize evaluation across such platforms.

---

### O. 3D World Generation

#### 45. World Labs Marble (Fei-Fei Li et al., 2024-2025)
- **Title**: Spatial Intelligence for 3D World Generation
- **Source**: [World Labs](https://www.worldlabs.ai/)
- **Release**: September 2024 (founding), November 2025 (Marble commercial launch)

**Summary**: World Labs, founded by AI pioneer Fei-Fei Li, develops 3D world generation with spatial intelligence. Their Marble platform generates interactive, explorable 3D environments from text, images, video, or panoramas.

**Technical Details**:
- Outputs: Gaussian splats, meshes, videos
- VR-compatible (Vision Pro, Quest 3)
- Persistent 3D structure with editing capabilities

**Target Applications**:
- VFX studios and game developers
- Industrial simulation and robotics
- Digital twins

**Relationship to Paper**:
- **State Modality**: 3D/Video
- **Action Interface**: Continuous (spatial manipulation)
- **Metric Profile**: High SC, Finite SD, High AR_inv (explicit spatial control), Finite AF
- **Relevance**: Represents the 3D world model paradigm. The paper includes World Labs as a baseline in the taxonomy table.

---

### P. LLM-Based and Web-Based World Models (State: Text/Web, Action: Symbolic)

These models use language models as world simulators, operating on textual or structured web state representations rather than visual observations.

#### 46. LLM World Simulators (Mitchell et al., 2024)
- **Title**: Can Language Models Serve as Text-Based World Simulators?
- **Source**: [arXiv:2406.06485](https://arxiv.org/abs/2406.06485)
- **Venue**: ACL 2024

**Summary**: Investigates whether LLMs can serve as world simulators for text games. Introduces ByteSized32-State-Prediction benchmark with text game state transitions.

**Key Findings**:
- GPT-4 is an "unreliable world simulator without further innovations"
- Consistency varies by domain: >90% in structured worlds (SciWorld), <80% in combinatorial spaces (WebShop)

**Relationship to Paper**:
- **State Modality**: Text
- **Action Interface**: Symbolic (text commands)
- **Metric Profile**: Medium SC (consistency varies), Variable SD, Medium AR_inv, Medium AF
- **Relevance**: Directly tests action-state consistency in text domain. The paper's "Text IF / LLM World" category maps to this work.

---

#### 47. From Word to World (2025)
- **Title**: From Word to World: Can Large Language Models be Implicit Text-based World Models?
- **Source**: [arXiv:2512.18832](https://arxiv.org/abs/2512.18832)

**Summary**: Proposes a three-level framework for evaluating LLM-based world models: (1) fidelity and consistency, (2) scalability and robustness, (3) agent utility.

**Key Findings**:
- Sufficiently trained world models maintain coherent latent state
- Performance scales predictably with data and model size
- Long-horizon coherence remains challenging in large state spaces

**Relationship to Paper**:
- **Relevance**: Provides evaluation framework complementary to the paper's metric quad, specifically for text-based world models.

---

#### 48. Web World Models (Mengdi Wang et al., Princeton, 2025)
- **Title**: Web World Models
- **Source**: [arXiv:2512.23676](https://arxiv.org/abs/2512.23676)
- **Project Page**: [Princeton AI2 Lab](https://princeton-ai2-lab.github.io/Web-World-Models/)
- **Release**: December 2025

**Summary**: Web World Models (WWM) propose a hybrid architectural paradigm that decouples environmental state into two layers: a deterministic "Physics" layer defined by standard web code (TypeScript/JSON), and a probabilistic "Imagination" layer synthesized by LLMs. This middle ground combines the reliability of conventional web frameworks with the generativity of neural world models.

**Technical Architecture**:
- **Physics Layer**: Web code (TypeScript/JSON) ensures logical consistency, state persistence, and deterministic rules
- **Imagination Layer**: LLMs generate context, narratives, and high-level decisions on top of the structured latent state
- Hybrid approach: code governs structure while LLMs provide narrative and creativity

**Implementations & Demos**:
- Geographic coordinate expansion into rich places and stories
- Procedural galaxies where code governs structure and LLMs provide narrative
- "Falling sand" simulator with LLM-hallucinated chemical reactions (Gemini)
- Deck-builder with real-time AI-generated cards via "Wish" mechanic
- Interactive 3D solar system with view-dependent AI narration

**Key Innovation**:
The WWM paradigm addresses the fundamental tension between:
- **Fixed web frameworks**: Reliable but limited creativity
- **Fully generative models**: Creative but lack controllability and engineering practicality

**Relationship to Paper**:
- **State Modality**: Text/Structured (web code + JSON)
- **Action Interface**: Symbolic (web interactions) + NL (LLM prompts)
- **Metric Profile**: High SC (code ensures consistency), Variable SD (depends on LLM), High AR_inv (explicit code-defined transitions), Medium AF
- **Relevance**: Represents a novel hybrid paradigm for world models that bridges structured programming with generative AI. The explicit code-based "physics" layer aligns with AC-World's emphasis on explicit, verifiable state-action structure.

---

#### 49. WebDreamer (OSU NLP Group, 2024)
- **Title**: Is Your LLM Secretly a World Model of the Internet? Model-Based Planning for Web Agents
- **Source**: [arXiv:2411.06559](https://arxiv.org/abs/2411.06559)
- **GitHub**: [OSU-NLP-Group/WebDreamer](https://github.com/OSU-NLP-Group/WebDreamer)
- **Venue**: TMLR 2025

**Summary**: WebDreamer is a model-based planning framework that uses LLMs as world models for web navigation. Before committing to any action, the agent "dreams" by using the LLM to simulate the outcome of each candidate action, expressed as natural language descriptions of state changes.

**Core Methodology**:
- **"Dreaming" Process**: LLM imagines outcomes for each candidate action (e.g., "what would happen if I click this button?")
- **Natural Language Simulation**: Outcomes expressed as descriptions of how state would change
- **Value-Based Selection**: Imagined outcomes evaluated based on progress toward task objective
- **Trained World Model**: Dreamer-7B performs comparably to GPT-4o

**Performance**:
- 33.3% relative improvement over Reactive agents on VWA dataset
- 13.1% improvement on Mind2Web-live dataset
- 4-5x more efficient than tree search while remaining competitive
- Effective on real-world websites (not just sandboxes)

**Key Insight**: LLMs trained on web data implicitly contain a world model of the internet—they can predict how web pages change in response to actions.

**Relationship to Paper**:
- **State Modality**: Text/HTML (web page representations)
- **Action Interface**: Symbolic (web actions: click, type, scroll)
- **Metric Profile**: Medium SC (LLM limitations), Medium SD, High AR_inv (explicit action simulation), Medium AF
- **Relevance**: Demonstrates that LLMs can serve as implicit world models for structured environments. The "simulation before action" paradigm aligns with the paper's emphasis on action-conditioned prediction. WebDreamer's evaluation of action outcomes relates to the paper's Action Rationality metric.

---

#### 50. Multi-Agent LLM Simulations and Social Simulacra

**Overview**: A growing body of work uses LLMs as world models for multi-agent social simulations, replacing hard-coded agent programs with LLM-driven prompts.

**Key Examples**:
- **Generative Agents (Stanford, 2023)**: LLM-powered agents in sandbox environments with memory and reflection
- **AgentSims**: LLM agents in interactive social environments
- **Swarm Intelligence with LLMs**: Ant colony foraging and bird flocking simulated with GPT-4o via NetLogo integration

**Technical Approach**:
- LLM agents adaptively react to environments without predefined explicit instructions
- Integration with simulation platforms (NetLogo, custom sandboxes)
- Memory and retrieval augmentation for long-horizon coherence

**Limitations**:
- Hallucination and distributional drift over long rollouts
- Static pretraining limits adaptation to novel dynamics
- Computational cost for many-agent simulations

**Solutions**:
- Retrieval-Augmented World Models (R-WoM): Inject up-to-date knowledge at each step
- Hybrid code+LLM approaches (like Web World Models)

**Relationship to Paper**:
- **State Modality**: Text (social state descriptions)
- **Action Interface**: Symbolic/NL (agent decisions)
- **Relevance**: Extends world modeling to social/multi-agent domains. The paper's framework could be adapted to evaluate social simulacra for action consistency and state coherence.

---

### Q. History-Conditioned Video Simulation

#### 51. PAN (MBZUAI, 2025)
- **Title**: PAN: A World Model for General, Interactable, and Long-Horizon World Simulation
- **Source**: [arXiv:2511.09057](https://arxiv.org/abs/2511.09057)
- **Release**: November 2025

**Summary**: PAN is a general, interactable world model for long-horizon simulation, predicting future states through video conditioned on history and natural language actions.

**Architecture**:
- Generative Latent Prediction (GLP): LLM backbone + video diffusion decoder
- Built on Qwen2.5-VL-7B-Instruct
- Causal Swin-DPM for smooth long-horizon transitions

**Training**:
- Uses VLM for dense video captioning to create action labels automatically
- Trained on large-scale video-action pairs across domains

**Performance**:
- State-of-the-art among open-source systems
- Best scores for transition smoothness and simulation consistency

**Relationship to Paper**:
- **State Modality**: Video
- **Action Interface**: Symbolic/NL (natural language actions)
- **Metric Profile**: High SC (Causal Swin-DPM design), High SD, High AR_inv (NL conditioning), Medium AF
- **Relevance**: PAN is explicitly mentioned as a baseline in the paper. Its NL action interface and long-horizon focus align with AC-World's design goals.

---

### R. Recent Surveys and Theoretical Work

#### 52. ACM Computing Surveys: Understanding World or Predicting Future? (2025)
- **Title**: Understanding World or Predicting Future? A Comprehensive Survey of World Models
- **Source**: [ACM CSUR](https://dl.acm.org/doi/10.1145/3746449), [arXiv:2411.14499](https://arxiv.org/abs/2411.14499)

**Summary**: Comprehensive survey categorizing world models by two functions: (1) understanding present state, (2) predicting future dynamics. Covers games, autonomous driving, robotics, and social simulacra.

**Relevance**: Provides taxonomic context for the paper's contribution. The paper's state-action taxonomy offers a complementary organizational framework focused on evaluation.

---

#### 53. A Comprehensive Survey on World Models for Embodied AI (2025)
- **Source**: [arXiv:2510.16732](https://arxiv.org/html/2510.16732v1)

**Summary**: Proposes a three-axis taxonomy:
1. **Functionality**: Decision-Coupled vs. General-Purpose
2. **Temporal Modeling**: Sequential Simulation vs. Global Difference Prediction
3. **Spatial Representation**: Global Latent, Token Sequence, Spatial Grid, Decomposed Rendering

**Relevance**: Offers alternative taxonomic axes. The paper's state-action taxonomy is simpler and more directly tied to evaluation.

---

#### 54. V-JEPA 2 (Meta, 2025)
- **Title**: V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning
- **Source**: arXiv 2025

**Summary**: V-JEPA 2 demonstrates that web-scale video pretraining plus minimal robot data yields an actionable world model.

**Relevance**: Bridges passive representation learning with action-grounded control—directly addressing the gap the paper identifies.

---

## Taxonomy Mapping Table

### Comprehensive Model Comparison

| Model/Paper | State Modality | Action Interface | SC | SD | AR_inv | AF | Category | Year |
|-------------|---------------|------------------|----|----|--------|----|----|------|
| **Model-Based RL** ||||||||
| PlaNet | Latent | Motor | H | M | H | M | Foundational MBRL | 2019 |
| Dreamer | Latent | Motor | H | M | H | M | Imagination-based | 2020 |
| DreamerV2 | Latent (discrete) | Symbolic | H | F | H | F | Atari mastery | 2021 |
| DreamerV3 | Latent | Motor/Symbolic | H | V | H | V | General-purpose | 2023 |
| MuZero | Latent (abstract) | Symbolic | H | V | H | F | Planning-focused | 2020 |
| DIAMOND | Video | Symbolic | H | F | H | F | Diffusion MBRL | 2024 |
| **Video Generation (Passive)** ||||||||
| Sora | Video | None | H | H | L | 0 | Text-to-video | 2024 |
| Sora 2 | Video | None | H | H | L | 0 | Enhanced coherence | 2025 |
| Veo 2/3 | Video | None | H | H | L | 0 | Cinematography | 2024-25 |
| VastDreamer | 3D/Video | None | H | H | L | 0 | 3D video gen | 2023 |
| FreeLong | Video | None | H | H | L | 0 | Long-form | 2024 |
| Video-Infinity | Video | None | H | H | L | 0 | Distributed gen | 2024 |
| **Interactive World Models** ||||||||
| Genie 1 | Video | Pixel | M | M | M | M | Latent actions | 2024 |
| Genie 2 | 3D/Video | Pixel | H | M | M | M | 3D worlds | 2024 |
| Genie 3 | 3D/Video | Pixel+NL | H | H | M | M | Real-time | 2025 |
| Oasis | Video | Pixel | M | M | M | M | Neural Minecraft | 2024 |
| GameNGen | Video | Symbolic | H | F | H | F | Neural DOOM | 2024 |
| **Autonomous Driving** ||||||||
| GAIA-1 | Video | Motor+Text | H | H | M | M | Driving simulator | 2023 |
| GAIA-2 | Video | Motor+Text | H | H | M | M | Multi-region | 2024 |
| **Robotics** ||||||||
| UniSim | Video | NL | H | M | H | M | Universal sim | 2024 |
| RT-2 | Image | Motor (tokens) | V | M | H | M | VLA | 2023 |
| Cosmos | Video | Motor/Sensor | H | H | H | H | Physical AI | 2025 |
| **3D World Generation** ||||||||
| World Labs Marble | 3D/Video | Continuous | H | F | H | F | Spatial AI | 2024-25 |
| **LLM-Based & Web-Based** ||||||||
| LLM World Sim | Text | Symbolic | M | V | M | M | Text games | 2024 |
| Web World Models | Text/Web | Symbolic+NL | H | V | H | M | Hybrid code+LLM | 2025 |
| WebDreamer | Text/HTML | Symbolic | M | M | H | M | Web navigation | 2024 |
| Social Simulacra | Text | NL | M | M | M | M | Multi-agent | 2023+ |
| **History-Conditioned** ||||||||
| PAN | Video | NL | H | H | H | M | Long-horizon | 2025 |
| Oh et al. 2015 | Video | Symbolic | M | F | H | F | Pioneer work | 2015 |
| **Representation Learning** ||||||||
| I-JEPA | Latent | None | H | M | - | - | Image JEPA | 2023 |
| V-JEPA | Video/Latent | None | H | M | - | - | Video JEPA | 2024 |
| V-JEPA 2 | Video/Latent | Motor | H | M | H | M | Actionable | 2025 |
| VideoMAE | Video | None | M | M | - | - | Masked AE | 2022 |
| DINO | Image/Latent | None | H | M | - | - | Self-supervised | 2021 |
| **Reference Environments** ||||||||
| Mario/Games | 2D Video | Symbolic | H | F | H | F | Classic games | - |
| Minecraft | 3D Block | Hybrid | M | I | H | H | Sandbox | - |
| Real World | Physical | All | H | I | H | I | Upper bound | - |
| **Proposed** ||||||||
| **AC-World (ours)** | Video+Graph | Hybrid | H | H | H | H | Action-centric | 2026 |

**Legend**:
- H=High, M=Medium, L=Low, F=Finite, I=Infinite, V=Variable, -=Not applicable, 0=Zero
- NL=Natural Language

---

## Summary of Gaps in Existing Literature

### 1. Evaluation Gap
Most benchmarks evaluate task success (downstream) rather than world model fidelity (intrinsic):
- **D4RL, Meta-World, RLBench**: Measure policy performance, not dynamics accuracy
- **AgentBench, WebArena**: Test agent competence, conflating world model and policy
- **VBench, FVD**: Measure perceptual quality under passive rollouts, not action consistency

### 2. Action Gap
A clear dichotomy exists between visual quality and action controllability:
- **High Visual Quality, No Actions**: Sora, Veo, VastDreamer, FreeLong
- **Action Interfaces, Limited Visual Quality**: Dreamer variants (latent), early Genie (lower resolution)
- **Emerging Bridge**: GameNGen, Oasis, Genie 2/3, PAN begin to address both

### 3. Structure Gap
No existing benchmark provides explicit ground-truth state-action graphs:
- Embodied benchmarks use implicit transitions (simulators)
- Video benchmarks lack action structure entirely
- Game environments have implicit rules, not explicit transition graphs

### 4. Metrics Gap
- **Visual Metrics**: LPIPS, FVD, PSNR measure perceptual quality
- **RL Metrics**: Episode return, success rate measure policy performance
- **Missing**: Standardized action rationality metrics, inverse dynamics evaluation

### 5. Taxonomy Gap
- Multiple competing taxonomies exist (functionality, temporal, spatial)
- No unified framework connects state modality + action interface + evaluation metrics
- Difficult to compare across paradigms (e.g., Sora vs. Dreamer vs. RT-2)

### How the Paper Addresses These Gaps

| Gap | Paper's Solution |
|-----|------------------|
| Evaluation | Teacher-forced mode separates model fidelity from policy competence |
| Action | AC-World provides explicit action-conditioned graph structure |
| Structure | Ground-truth state-action graphs with multiple modality groundings |
| Metrics | Metric quad: SC, SD, AR_inv, AF across all modalities |
| Taxonomy | State modality × Action interface matrix with per-cell evaluation |

---

## Research Trends and Observations

### Trend 1: Convergence Toward Interactive World Models (2024-2025)
The field is rapidly moving from passive video generation toward interactive world modeling:
- **2024**: Genie 1/2, GameNGen, Oasis demonstrate feasibility
- **2025**: Genie 3 (real-time), Cosmos (physics-aware), V-JEPA 2 (actionable representations)

### Trend 2: Natural Language as Action Interface
Multiple recent models use NL for action conditioning:
- UniSim, PAN, GAIA use text descriptions as actions
- Enables rich, interpretable action specification
- Aligns with AC-World's hybrid approach

### Trend 3: Foundation Models for Physical AI
Industry investment in world models for robotics/AV:
- NVIDIA Cosmos (2M+ downloads)
- Wayve GAIA-1/2 (deployed in vehicles)
- World Labs (VFX, robotics, digital twins)

### Trend 4: Diffusion Models as World Models
Shift from autoregressive/latent approaches to diffusion:
- DIAMOND (MBRL), GameNGen (games), PAN (general)
- Better visual quality, more stable long-horizon generation

### Trend 5: Scaling Laws Apply to World Models
Evidence that world model quality scales with data/compute:
- GAIA-1 scaling experiments
- Cosmos training on 20M hours of data
- LLM world model consistency improves with model size

---

## Recommended Citations for Position Paper

### Essential (Core Related Work)
```bibtex
@article{hafner2020dreamer,
@article{hafner2023dreamerv3,
@inproceedings{genie2024,
@article{sora2024,
@inproceedings{unisim2024,
@article{pan2025,
@article{cosmos2025,
@article{vafa2024evaluating,
@article{webworldmodels2025,  % Mengdi Wang, Princeton - hybrid code+LLM world models
@article{webdreamer2024,      % LLM as web world model
```

### Strongly Recommended (Benchmarks & Metrics)
```bibtex
@article{vbench2023,
@article{zhang2018lpips,
@article{unterthiner2019fvd,
@article{fu2021d4rl,
```

### Foundational (Theoretical Background)
```bibtex
@article{lecun2022path,
@article{muzero2020,
```

---

## Sources and References

### Surveys
- [ACM CSUR World Models Survey](https://dl.acm.org/doi/10.1145/3746449)
- [Embodied AI World Models Survey](https://arxiv.org/html/2510.16732v1)
- [Autonomous Driving World Models Survey](https://arxiv.org/pdf/2501.11260)

### Project Pages
- [Genie 2](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)
- [Genie 3](https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/)
- [UniSim](https://universal-simulator.github.io/)
- [Oasis](https://oasis-model.github.io/)
- [GameNGen](https://gamengen.github.io/)
- [DIAMOND](https://diamond-wm.github.io/)
- [PAN](https://panworld.ai/)
- [World Labs](https://www.worldlabs.ai/)
- [NVIDIA Cosmos](https://www.nvidia.com/en-us/ai/cosmos/)
- [Wayve GAIA](https://wayve.ai/science/gaia/)
- [Web World Models (Princeton)](https://princeton-ai2-lab.github.io/Web-World-Models/)
- [WebDreamer (OSU)](https://github.com/OSU-NLP-Group/WebDreamer)

### Company Announcements
- [OpenAI Sora](https://openai.com/index/sora/)
- [Google Veo](https://deepmind.google/models/veo/)

---

*Document generated for ICML 2026 position paper on Action-Centric World Model Benchmarking*
*Last updated: January 2026*
*Total papers analyzed: 54+*
