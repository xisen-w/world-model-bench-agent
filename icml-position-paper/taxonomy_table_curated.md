# Curated Taxonomy Table (State Modality × Action Interface)

This note re-curates a taxonomy table for the paper, using:
- your internal notes in `icml-position-paper/literature_analysis.md`, and
- primary/official sources when available (arXiv/ar5iv, project pages, tech reports, press releases).

The goal is not to rank models, but to justify **what is being treated as state** ($m_S$) and **what counts as an action interface** ($m_A$), because these choices determine which action-conditioned evaluations are well-posed.

---

## Taxonomy Definitions (used in this document)

### State modality ($m_S$): what representation is carried forward as $s_t$?
- **Text/Web**: a natural-language or structured-text state (incl. HTML/DOM summaries for web).
- **Image**: a single visual frame used as the step-to-step state.
- **Video**: a sequence of frames treated as the evolving state.
- **Latent**: a learned compact state used for prediction/planning (e.g., RSSM-like latent dynamics).
- **Spatial/3D**: explicit geometry / multi-view / 3D scene representations (only used when the system explicitly treats 3D structure as state).
- **Structured/Graph**: an explicit symbolic/structured state (graphs, typed fields, metadata) intended to make rollouts diagnosable.

### Action interface ($m_A$): how is an intervention $a_t$ specified?
- **None**: no intervention channel (pure representation learning or unconditional generation).
- **Prompt-only (global)**: prompts condition generation, but there is no stable *stepwise* action semantics for multi-step rollouts.
- **Natural language (stepwise)**: a language command is provided per step, treated as $a_t$ with intended stable semantics.
- **Symbolic (discrete)**: discrete actions/commands (e.g., game buttons, click/type primitives).
- **Motor (continuous)**: continuous control signals (robot/driving control).
- **Pixel/GUI**: low-level UI events (mouse/cursor trajectories, keypress streams) treated as $a_t$.
- **Hybrid**: mixes multiple channels (e.g., language + motor; prompt + motion controls).

---

## Curated Table (taxonomy only; *not* a score table)

| Category | System | Primary reference | $m_S$ | $m_A$ | Notes (1-liner) |
|---|---|---|---:|---:|---|
| Model-Based RL | PlaNet | Hafner et al. “Learning Latent Dynamics for Planning from Pixels” (arXiv:1811.04551) | Latent | Motor | Planning in learned latent dynamics conditioned on actions |
| Model-Based RL | Dreamer | Hafner et al. “Dream to Control: Learning Behaviors by Latent Imagination” (arXiv:1912.01603) | Latent | Motor | Policy learning via imagined rollouts in latent world model |
| Model-Based RL | DreamerV2 | Hafner et al. “Mastering Atari with Discrete World Models” (arXiv:2010.02193) | Latent | Symbolic | Discrete-action games with discrete latent dynamics |
| Model-Based RL | DreamerV3 | Hafner et al. “Mastering Diverse Domains through World Models” (arXiv:2301.04104) | Latent | Motor+Symbolic | Domain-dependent $\mathcal{A}$; still explicit, stepwise actions |
| Model-Based RL | MuZero | Schrittwieser et al. “Mastering Atari, Go, Chess and Shogi …” (arXiv:1911.08265) | Latent | Symbolic | Planning with learned latent model over discrete actions |
| Model-Based RL | DIAMOND | Alonso et al. “Diffusion for World Modeling: Visual Details Matter in Atari” (arXiv:2405.12399) | Video | Symbolic | Diffusion world model conditioned on Atari actions |
| Interactive World Models | Oh et al. (2015) | “Action-Conditional Video Prediction …” (arXiv:1507.08750 / NeurIPS’15) | Video | Symbolic | Next-frame prediction conditioned on game actions |
| Interactive World Models | Genie 1 | Bruce et al. “Genie: Generative Interactive Environments” (arXiv:2402.15391) | Video | Symbolic | Frame-by-frame control via learned discrete latent actions |
| Interactive World Models | Genie 2 | DeepMind blog “Genie 2 …” (2024) | Spatial/3D | Pixel/GUI | Real-time multi-view exploration / navigation in 3D worlds |
| Interactive World Models | Genie 3 | DeepMind blog “Genie 3 …” (2025) | Spatial/3D | Hybrid | Real-time 3D + “promptable events” (UI control + language) |
| Interactive World Models | Oasis | Decart “Oasis: A Universe in a Transformer” (2024 tech report/blog) | Video | Pixel/GUI | Keyboard/mouse-controlled real-time video world |
| Interactive World Models | GameNGen | Valevski et al. “Diffusion Models Are Real-Time Game Engines” (arXiv:2408.14837) | Video | Symbolic | Next-frame generation conditioned on game actions |
| Interactive Video Generation (Streaming) | MotionStream | Shin et al. “MotionStream …” (arXiv:2511.01266) | Video | Hybrid | Real-time video gen w/ interactive motion controls |
| Interactive Video Generation (Streaming) | LongLive | Yang et al. “LongLive …” (arXiv:2509.22622) | Video | Prompt-only (global) | Streaming long video with prompt edits |
| Interactive Video Generation (Streaming) | StreamDiffusionV2 | Feng et al. “StreamDiffusionV2 …” (arXiv:2511.07399) | Video | Hybrid | Streaming system for interactive video generation |
| Interactive Video Generation (Streaming) | CausVid | Yin et al. “From Slow Bidirectional to Fast Autoregressive Video Diffusion Models” (CVPR 2025) | Video | Hybrid | Fast autoregressive video diffusion for streaming |
| Interactive Video Generation (Streaming) | StreamAvatar | Sun et al. “StreamAvatar …” (arXiv:2512.22065) | Video | Hybrid | Real-time streaming human avatars |
| Video Generation (Controlled) | MotionCtrl | Wang et al. “MotionCtrl …” (arXiv:2312.03641) | Video | Hybrid | Motion trajectories/controls guide generation |
| Video Generation (Controlled) | CameraCtrl II | He et al. “CameraCtrl II …” (arXiv:2503.10592) | Video | Hybrid | Camera-motion controls steer video diffusion |
| Video Generation (Controlled) | Image Conductor | Li et al. “Image Conductor …” (arXiv:2406.15339) | Video | Hybrid | Control via image-guided edits |
| Video Generation (Passive) | Sora | OpenAI “Video generation models as world simulators” (2024 tech report) | Video | Prompt-only (global) | Prompt-conditioned video generation (no stepwise $\mathcal{A}$) |
| Video Generation (Passive) | Veo | Google DeepMind “Veo” model page (2024–2025) | Video | Prompt-only (global) | Conditioning controls, but not a stepwise action set |
| Video Generation (Passive) | FreeLong | Lu et al. “FreeLong …” (arXiv:2407.19918) | Video | Prompt-only (global) | Long-video method; no explicit action semantics |
| Video Generation (Passive) | Video-Infinity | Tan et al. “Video-Infinity …” (arXiv:2406.16260) | Video | Prompt-only (global) | Systems scaling for long prompt-based video gen |
| Robotics & Physical AI | RT-2 | Brohan et al. “RT-2 …” (arXiv:2307.15818) | Image | Motor | Vision-language-action policy for robot control |
| Robotics & Physical AI | OpenVLA | Kim et al. “OpenVLA …” (arXiv:2406.09246) | Image | Motor | Open-source VLA mapping vision+language → actions |
| Robotics & Physical AI | V-JEPA 2 | Bardes et al. “V-JEPA 2 …” (arXiv:2506.09985) | Latent/Video | Motor | Video pretraining used to support planning/control |
| Robotics & Physical AI | Cosmos | NVIDIA “Cosmos World Foundation Model Platform …” (arXiv:2501.03575 / 2025) | Video | Hybrid | Generates physics-based futures from prompts + sensor/motion data |
| Autonomous Driving | GAIA-1 | Hu et al. “GAIA-1 …” (arXiv:2309.17080) | Video | Hybrid | Video world model conditioned on actions + text |
| Autonomous Driving | GAIA-2 | Wayve press release “GAIA-2 …” (Mar 26, 2025) | Video | Hybrid | Productized successor: more controllable synthetic driving video |
| Autonomous Driving | DriveDreamer | Wang et al. “DriveDreamer …” (arXiv:2309.09777) | Video | Hybrid | Driving world model with controllable futures |
| Autonomous Driving | DrivingWorld | Hu et al. “DrivingWorld …” (arXiv:2412.19505) | Video | Hybrid | Video world model for driving scene evolution |
| LLM & Web World Models | LLM World Sim | Wang et al. “Can LMs Serve as Text-Based World Simulators?” (ACL 2024) | Text/Web | Symbolic | Predict next text state given action commands |
| LLM & Web World Models | WebDreamer | Gu et al. “Is Your LLM Secretly a World Model …” (arXiv:2411.06559) | Text/Web | Symbolic | Simulates outcomes of web actions (click/type) |
| LLM & Web World Models | Web World Models | Feng et al. “Web World Models” (arXiv:2512.23676) | Text/Web | Hybrid | Structured web “physics” + NL agent layer |
| 3D World Generation | World Labs (Marble) | World Labs site / overview (2024) | Spatial/3D | Continuous/Hybrid | 3D scene generation with editable persistent structure |
| 3D World Generation | Terra | Huang et al. “Terra …” (arXiv:2510.14977) | Spatial/3D | Hybrid | Native 3D world model with point-latent state |
| 3D World Generation | WorldGrow | Li et al. “WorldGrow …” (arXiv:2510.21682) | Spatial/3D | Hybrid | Infinite 3D world generation with growth |
| Language-Action Simulation | PAN | “PAN …” (arXiv:2511.09057) | Video | Natural language (stepwise) | Conditions simulation on per-step NL actions |
| Representation Learning | DINO | Caron et al. “Emerging Properties in SSL ViTs” (ICCV 2021) | Image/Latent | None | State encoder; no action-conditioned rollouts |
| Representation Learning | I-JEPA | Assran et al. “I-JEPA” (CVPR 2023) | Latent | None | Learns predictive representations; no $\mathcal{A}$ |
| Representation Learning | V-JEPA | Bardes et al. “V-JEPA” (arXiv:2404.08471) | Video/Latent | None | Video representation learning; no action interface |
| Reference Environments | Classic games (Mario) | canonical envs | Video | Symbolic | Discrete buttons; clean stepwise action semantics |
| Reference Environments | Minecraft | canonical envs | Spatial/3D | Hybrid | Mix of discrete actions + continuous camera control |
| Reference Environments | Real world | — | Spatial/3D | Hybrid | Full actions; serves as “upper bound” conceptually |
| Proposed | AC-World (ours) | paper formalism | Structured/Graph | Hybrid | Explicit action-conditioned graph with diagnosable transitions |

---

## LaTeX Table (paper-ready, no SC/SD/AR/AF)

```latex
\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\caption{Taxonomy across state modality and action interface. \textbf{Prompt-only} denotes one-shot conditioning without a stable stepwise $\mathcal{A}$. Entries marked \textbf{(policy)} are agents, not environment world models.}
\label{tab:model_taxonomy}
\begin{tabular}{@{}lll|lll@{}}
\toprule
\textbf{Model} & \textbf{State} & \textbf{Action} &
\textbf{Model} & \textbf{State} & \textbf{Action} \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{Model-Based RL}}} &
\multicolumn{3}{l}{\textit{\textbf{Interactive World Models}}} \\
PlaNet \cite{hafner2019planet} & Latent & Motor &
Genie 1 \cite{bruce2024genie} & Video & Symbolic \\
Dreamer \cite{hafner2020dreamer} & Latent & Motor &
Genie 2 \cite{deepmind_genie2} & Spatial/3D & Pixel/GUI \\
DreamerV2 \cite{hafner2021dreamerv2} & Latent & Symbolic &
Genie 3 \cite{deepmind_genie3} & Spatial/3D & Hybrid \\
DreamerV3 \cite{hafner2023dreamerv3} & Latent & Motor/Sym &
Oasis \cite{decart2024oasis} & Video & Pixel/GUI \\
MuZero \cite{schrittwieser2020muzero} & Latent & Symbolic &
GameNGen \cite{valevski2024gamengen} & Video & Symbolic \\
DIAMOND \cite{alonso2024diamond} & Video & Symbolic &
Oh et al.\ \cite{oh2015action} & Video & Symbolic \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{Interactive Video Generation (Streaming)}}} &
\multicolumn{3}{l}{\textit{\textbf{Robotics \& Physical AI}}} \\
MotionStream \cite{shin2025motionstream} & Video & Hybrid &
UniSim \cite{yang2024unisim} & Video & NL \\
LongLive \cite{yang2025longlive} & Video & Prompt-only &
Cosmos \cite{nvidia2025cosmos} & Video & Hybrid \\
StreamDiffusionV2 \cite{feng2025streamdiffusionv2} & Video & Hybrid &
V-JEPA 2 \cite{bardes2025vjepa2} & Latent/Video & Motor \\
CausVid \cite{yin2025causvid} & Video & Hybrid &
RT-2 (policy) \cite{brohan2023rt2} & Image & Motor \\
StreamAvatar \cite{sun2025streamavatar} & Video & Hybrid &
OpenVLA (policy) \cite{kim2024openvla} & Image & Motor \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{Video Generation (Controlled)}}} &
\multicolumn{3}{l}{\textit{\textbf{Autonomous Driving}}} \\
MotionCtrl \cite{wang2023motionctrl} & Video & Hybrid &
GAIA-1 \cite{hu2023gaia1} & Video & Motor+Text \\
CameraCtrl II \cite{he2025cameractrl2} & Video & Hybrid &
GAIA-2 \cite{wayve_gaia} & Video & Motor+Text \\
Image Conductor \cite{li2024imageconductor} & Video & Hybrid &
DriveDreamer \cite{wang2023drivedreamer} & Video & Hybrid \\
& & &
DrivingWorld \cite{hu2024drivingworld} & Video & Hybrid \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{Video Generation (Prompt-only)}}} &
\multicolumn{3}{l}{\textit{\textbf{3D World Generation}}} \\
Sora \cite{openai2024sora} & Video & Prompt-only &
World Labs \cite{worldlabs2024} & Spatial/3D & Hybrid \\
Veo 2/3 \cite{veo2024} & Video & Prompt-only &
Terra \cite{huang2025terra} & Spatial/3D & Hybrid \\
FreeLong \cite{lu2024freelong} & Video & Prompt-only &
WorldGrow \cite{worldgrow2025} & Spatial/3D & Hybrid \\
Video-Infinity \cite{tan2024videoinfinity} & Video & Prompt-only &
& & \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{LLM \& Web-Based World Models}}} &
\multicolumn{3}{l}{\textit{\textbf{Representation Learning}}} \\
LLM World Sim \cite{wang2024llmworldsim} & Text & Symbolic &
I-JEPA \cite{assran2023ijepa} & Latent & None \\
Web World Models \cite{feng2025webworldmodels} & Text/Web & Sym+NL &
V-JEPA \cite{bardes2024vjepa} & Video/Latent & None \\
WebDreamer \cite{gu2024webdreamer} & Text/HTML & Symbolic &
DINO \cite{caron2021dino} & Image/Latent & None \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{History-Conditioned Video}}} &
\multicolumn{3}{l}{\textit{\textbf{Proposed}}} \\
PAN \cite{pan2025worldmodel} & Video & NL &
\textbf{AC-World} & Video+Graph & Hybrid \\
\midrule
\multicolumn{3}{@{}l}{\textit{\textbf{Reference Environments}}} &
\multicolumn{3}{l}{} \\
Classic Games (Mario) & Video & Symbolic & & & \\
Minecraft & Spatial/3D & Hybrid & & & \\
Real World & Spatial/3D & Hybrid & & & \\
\bottomrule
\end{tabular}
\end{table*}
```

## Per-entry Justifications (short reasoning paragraphs)

### PlaNet (arXiv:1811.04551)
PlaNet is **latent-state** because its planning and prediction operate in a learned compact recurrent state-space model rather than directly in pixel space. It is **motor/continuous-action** because its core use case is action-conditioned planning in control tasks, where candidate action sequences are optimized and rolled out through the learned dynamics for decision making.

### Dreamer (arXiv:1912.01603)
Dreamer is **latent-state** because it learns a compact latent dynamics model and performs “imagination” rollouts inside that latent space. It is **motor/continuous-action** because the learned policy chooses actions that are rolled forward through the latent transition model to evaluate long-horizon consequences.

### DreamerV2 (arXiv:2010.02193)
DreamerV2 remains **latent-state**, but explicitly uses **discrete** latent representations. It is **symbolic/discrete-action** in the Atari setting because the environment action set is a finite set of game controls; the world model learns to predict under that discrete $\mathcal{A}$, enabling well-posed inverse/branching diagnostics in that regime.

### DreamerV3 (arXiv:2301.04104)
DreamerV3 is **latent-state** because it remains a world-model-based RL method that improves behavior by imagining futures through a learned dynamics model. Its action interface is **motor+symbolic** because the paper targets a broad suite of domains spanning both continuous and discrete control; the taxonomy point is that the model is trained/evaluated under an explicit per-step $a_t$ rather than one-shot prompting.

### MuZero (arXiv:1911.08265)
MuZero is **latent-state** because it learns an internal model optimized for planning-relevant quantities (rather than reconstructing pixels). It is **symbolic/discrete-action** because it is evaluated in settings with discrete moves (board games, Atari), and planning is performed over that discrete action set, yielding a clear notion of “what action was taken.”

### DIAMOND (arXiv:2405.12399)
DIAMOND is grouped under **video-state** world modeling because it uses diffusion modeling to represent environment dynamics with an emphasis on preserving visual details that matter for RL. It is **symbolic/discrete-action** in Atari because the model is trained to model environment evolution under an explicit discrete $\mathcal{A}$.

### Action-Conditional Video Prediction (Oh et al., arXiv:1507.08750 / NeurIPS 2015)
This work is **video-state** because it directly predicts future frames. It is **symbolic/discrete-action** because the model conditions frame prediction on the Atari control input; the paper’s central claim is that next-state prediction must be action-conditional to be useful for control.

### Genie 1 (arXiv:2402.15391)
Genie 1 is **video-state** because it represents environments as sequences of frames via a video tokenizer and learns dynamics over those tokens. It is **symbolic/discrete-action** because interactivity is achieved through a learned discrete latent action model: the rollout is explicitly conditioned on a per-step action variable even when ground-truth labels are absent.

### Genie 2 (DeepMind blog, 2024)
Genie 2 is categorized as **spatial/3D state** because the advertised interface is multi-view, viewpoint-consistent interaction (i.e., the system is not merely a single-view video clip). Its action interface is **pixel/GUI-like** in our taxonomy because interaction is described in terms of navigation/exploration (camera movement / user control), rather than a fixed symbolic command language.

### Genie 3 (DeepMind blog, 2025)
Genie 3 is again **spatial/3D state** for the same reason (real-time interactive 3D). It is **hybrid-action** because the public descriptions emphasize both real-time interactive control and “promptable world events,” which mix UI-style control with language-conditioned interventions.

### Oasis (Decart, 2024)
Oasis is **video-state** because the “world” is presented as an autoregressively generated stream of frames. It is **pixel/GUI-action** because the system explicitly uses keyboard/mouse user inputs as the control channel that shapes the next frames in real time (i.e., actions are low-level UI events rather than semantic commands).

### GameNGen (arXiv:2408.14837)
GameNGen is **video-state** because the model generates the next frame(s) of gameplay and can be rolled out over long trajectories. It is **symbolic/discrete-action** because the model is trained to generate next frames conditioned on past frames and the game actions, mirroring standard discrete control interfaces in classic games.

### MotionStream (arXiv:2511.01266)
MotionStream is **video-state** because it streams video generation causally in real time. It is **hybrid-action** because it combines (i) a global text prompt with (ii) interactive motion controls (e.g., trajectories/drag/camera control), which are closer to continuous action inputs than pure prompt conditioning.

### LongLive (arXiv:2509.22622)
LongLive is **video-state** because it generates long videos as a temporal stream. Its action interface is best described as **prompt-only (global)** (even though interactive) because the intervention mechanism is prompt switching / edits rather than a stable per-step action set with consistent semantics across states.

### Sora (OpenAI tech report, 2024)
Sora is **video-state** because it is trained as a prompt-conditional video generator. It is **prompt-only (global)** in this taxonomy because control is expressed primarily as conditioning (text and other non-stepwise guidance), without a per-timestep action channel that would define a stable $\mathcal{A}$ for multi-step interactive rollouts.

### Veo (DeepMind model page, 2024–2025)
Veo is **video-state** as a video generator. It is categorized as **prompt-only (global)** because, while the product advertises additional controls (e.g., references, camera directives), these are not presented as a stable stepwise action set comparable to motor/symbolic interfaces used for planning-style evaluation.

### FreeLong (arXiv:2407.19918)
FreeLong is **video-state** by construction: it modifies temporal attention inside video diffusion models to extend short-clip generation to long clips. It is **prompt-only (global)** because it does not introduce an action interface; it is a method to improve long-horizon consistency in prompt-conditioned generation.

### Video-Infinity (arXiv:2406.16260)
Video-Infinity is **video-state** and **prompt-only (global)** for the same reason: it scales long prompt-conditioned video generation via distributed inference, without defining stepwise action semantics.

### RT-2 (arXiv:2307.15818)
RT-2 is **image-state** because it maps robot observations (images) plus language context to actions. Its action interface is **motor** because the outputs correspond to executable robot controls (even if tokenized for modeling convenience), enabling a genuine closed-loop notion of $a_t$.

### OpenVLA (arXiv:2406.09246)
OpenVLA is **image-state** (vision-language input) with a **motor-action** interface because it is a policy intended to output robot control actions for manipulation. The taxonomy distinction versus prompt-only video models is that the action channel is explicit and stepwise.

### V-JEPA 2 (arXiv:2506.09985)
V-JEPA 2 is placed as **latent/video state** because it learns predictive video representations intended to support downstream reasoning and planning. It is categorized as **motor-action** insofar as the headline claim is that these representations enable prediction/planning for embodied control when paired with action inputs; this is closer to an “actionable state model” than to prompt-only generation.

### Cosmos (arXiv:2501.03575 / NVIDIA, 2025)
Cosmos is **video-state** because its core deliverable is a video world foundation model for simulating future visual states. It is **hybrid-action** because the platform is explicitly positioned to condition video generation on multiple inputs (text/image/video prompts plus robot motion/sensor context), rather than a single pure prompt channel.

### GAIA-1 (arXiv:2309.17080)
GAIA-1 is **video-state** because it models the driving world as video sequences. It is **hybrid-action** because controllability is expressed via both ego-vehicle behavior/action inputs and textual conditioning about the scene/behavior, aligning with the “motor+text” interface common in driving stacks.

### GAIA-2 (Wayve press release, Mar 26, 2025)
GAIA-2 is treated as **video-state** because it is positioned as a video-generative world model for driving. It remains **hybrid-action** because the release emphasizes controllable scenario generation (building on GAIA-1’s action+text conditioning), though this entry is based on public product/press descriptions rather than a peer-reviewed paper.

### LLM World Simulators (ACL 2024)
This work is **text/web-state** because states are text game states and evaluation asks the LM to predict next textual states. The action interface is **symbolic** because transitions are defined by explicit action commands (text-game style), giving a clean per-step $a_t$ in a purely textual modality.

### WebDreamer (arXiv:2411.06559)
WebDreamer is **text/web-state** because the “environment” is a web page state (HTML/screenshots/text abstractions). It is **symbolic/discrete-action** because the agent’s interventions are discrete web operations (click/type/etc.), and the method explicitly simulates candidate action outcomes before taking them.

### Web World Models (arXiv:2512.23676)
Web World Models are **text/web-state** because they implement state and transitions in web code and expose structured interfaces. The action interface is **hybrid** because interaction blends structured symbolic operations (the web “physics”) with an NL agent layer that produces higher-level decisions/instructions.

### World Labs (site/overview)
World Labs is categorized as **spatial/3D state** because the product framing centers on generating and editing persistent 3D environments (not just single-view imagery). The action interface is **continuous/hybrid** because interaction with 3D environments generally entails continuous controls (camera/agent movement) plus higher-level editing prompts; treat this row as “company/product” rather than a single paper.

### PAN (arXiv:2511.09057)
PAN is **video-state** because it simulates future world states as video. It is **natural-language (stepwise) action** because the model is explicitly conditioned on per-step language actions (i.e., $a_t$ is a textual command each step), rather than a single global prompt for a whole rollout.

### DINO (ICCV 2021)
DINO is a **state encoder**, not an interactive world simulator: it learns image representations without an action channel. It is placed as **image/latent state** with **no actions** because it can provide $s_t$ encodings for evaluation, but by itself does not define $\mathcal{A}$ or transition semantics.

### I-JEPA (CVPR 2023)
I-JEPA is **latent-state** representation learning: it learns predictive features in representation space, not a full action-conditioned simulator. It is **none-action** because the training objective does not define a per-step intervention channel $\mathcal{A}$.

### V-JEPA (arXiv:2404.08471)
V-JEPA is **video/latent state** representation learning: it predicts masked regions in feature space over time. It is **none-action** because it is trained on passive video without explicit action conditioning, so it does not define an evaluable action interface.

### Reference environments (Mario / Minecraft / real world)
These rows are included to anchor intuition. Mario-like games have **symbolic** button actions with clean stepwise semantics; Minecraft-like sandboxes mix **discrete** actions with continuous camera control (thus **hybrid**); the real world is the “everything is possible” upper bound where both state and action complexity are effectively unbounded.

### AC-World (ours)
AC-World is **structured/graph state** because states and transitions are explicitly represented as action-conditioned graphs (text + metadata), designed so that dynamics errors are diagnosable. Its action interface is **hybrid** because actions are human-readable but also typed/labeled (structured), aiming to keep semantics stable across rollouts.

---

## Known Gaps / TODOs
- If you want to keep a “3D/Spatial” column, we should only assign it when the system’s *state* is explicitly 3D (not merely “the world is 3D”).
- If you want SC/SD/AR/AF scores, we should treat them as **hypotheses** unless tied to an explicit evaluation protocol + evidence.
- If you want every row to be fully “verifiable,” we should add 1–2 evidence bullets per entry (e.g., a quote about action conditioning / interface) and link them to the exact source (paper section, appendix, or official doc).
