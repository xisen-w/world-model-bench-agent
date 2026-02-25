"""
M3-Agent Style Implementation for Cube World.

This is a reconstruction of the M3-Agent (Multimodal Memory-based Agent)
adapted for the Rubik's Cube Layer Twist Challenge.

Reference: https://arxiv.org/abs/2508.09736
Original Code: https://github.com/bytedance-seed/m3-agent

Key Components Replicated:
1. Dual-process architecture (Memorization + Control)
2. Entity-centric memory graph with episodic/semantic memory
3. Iterative reasoning loop with search tools
4. Multi-round decision making (up to H rounds)

Adaptations for Cube World:
- Uses API-based LLMs (GPT-4o/Claude) instead of local Qwen
- Simplified memory structure (no face/speaker recognition)
- Video transition-based instead of 30-sec clips
"""

import json
import base64
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from abc import abstractmethod
from datetime import datetime

# Try to import optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


# =============================================================================
# Visual Understanding Layer (Optional)
# =============================================================================

class VisualUnderstanding:
    """
    Visual understanding layer for processing video frames.

    This replicates M3-Agent's use of Qwen2.5-Omni for video understanding,
    but uses API-based VLMs (GPT-4o vision, Claude vision) instead.

    IMPORTANCE: HIGH - Agent receives VIDEO/IMAGE input, not text descriptions.
    The agent must visually understand the cube state to make decisions.
    Text descriptions in world JSON are ground truth, not exposed to agent.

    Usage:
        vu = VisualUnderstanding(model="gpt-4o")
        description = vu.describe_video("path/to/video.mov")
        description = vu.describe_frame("path/to/image.png")
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        max_frames: int = 4,
        frame_size: Tuple[int, int] = (512, 512)
    ):
        """
        Initialize visual understanding.

        Args:
            model: VLM to use ("gpt-4o", "claude-3-5-sonnet-20241022")
            max_frames: Maximum frames to extract from video
            frame_size: Resize frames to this size
        """
        self.model = model
        self.max_frames = max_frames
        self.frame_size = frame_size

        # Initialize client
        if "gpt" in model.lower() and HAS_OPENAI:
            self.client = OpenAI()
            self.provider = "openai"
        elif "claude" in model.lower() and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic()
            self.provider = "anthropic"
        else:
            self.client = None
            self.provider = None

    def extract_frames(self, video_path: str) -> List[Any]:  # List[np.ndarray]
        """
        Extract key frames from a video.

        Strategy: first frame, last frame, and evenly spaced middle frames.
        """
        if not HAS_CV2:
            raise ImportError("OpenCV (cv2) required for video processing")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            cap.release()
            return []

        # Determine which frames to extract
        if total_frames <= self.max_frames:
            frame_indices = list(range(total_frames))
        else:
            # First, last, and evenly spaced middle frames
            frame_indices = [0]  # First
            if self.max_frames > 2:
                step = total_frames / (self.max_frames - 1)
                for i in range(1, self.max_frames - 1):
                    frame_indices.append(int(i * step))
            frame_indices.append(total_frames - 1)  # Last

        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Resize
                frame = cv2.resize(frame, self.frame_size)
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)

        cap.release()
        return frames

    def frame_to_base64(self, frame: Any) -> str:  # frame: np.ndarray
        """Convert numpy frame to base64 string."""
        if not HAS_CV2:
            raise ImportError("OpenCV required")

        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return base64.b64encode(buffer).decode('utf-8')

    def image_to_base64(self, image_path: str) -> str:
        """Load image file and convert to base64."""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def describe_frame(
        self,
        image_path: str,
        prompt: str = "Describe what you see in this image. Focus on the Rubik's cube state and any visible rotation or movement."
    ) -> str:
        """
        Describe a single image/frame using VLM.

        Args:
            image_path: Path to image file
            prompt: Custom prompt for description

        Returns:
            Text description of the image
        """
        if self.client is None:
            return f"[No VLM available] Image: {image_path}"

        image_b64 = self.image_to_base64(image_path)

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}",
                                "detail": "low"
                            }
                        }
                    ]
                }],
                max_tokens=300
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            # Determine media type from extension
            ext = Path(image_path).suffix.lower()
            media_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/jpeg')

            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            return response.content[0].text

        return f"[Unknown provider] Image: {image_path}"

    def describe_video(
        self,
        video_path: str,
        prompt: str = None
    ) -> Dict[str, Any]:
        """
        Describe a video by analyzing key frames.

        Following M3-Agent's memorization process:
        - Extract key frames
        - Describe each frame
        - Synthesize into coherent description

        Args:
            video_path: Path to video file
            prompt: Custom prompt (default: cube-specific)

        Returns:
            Dict with frame descriptions and synthesis
        """
        if prompt is None:
            prompt = """Analyze these frames from a Rubik's cube manipulation video.

For each frame, describe:
1. The cube's current state/orientation
2. Any visible rotation or movement
3. Which face/layer appears to be moving

Then provide a synthesis: What action (layer twist) is being performed?
Use standard notation if possible (R, L, U, D for Right, Left, Up, Down face rotations)."""

        # Extract frames
        try:
            frames = self.extract_frames(video_path)
        except Exception as e:
            return {
                "error": str(e),
                "video_path": video_path,
                "synthesis": f"[Could not process video: {e}]"
            }

        if not frames:
            return {
                "error": "No frames extracted",
                "video_path": video_path,
                "synthesis": "[No frames could be extracted from video]"
            }

        if self.client is None:
            return {
                "error": "No VLM client available",
                "video_path": video_path,
                "frame_count": len(frames),
                "synthesis": "[No VLM available for visual analysis]"
            }

        # Convert frames to base64
        frames_b64 = [self.frame_to_base64(f) for f in frames]

        # Build multi-image message
        if self.provider == "openai":
            content = [{"type": "text", "text": prompt}]
            for i, fb64 in enumerate(frames_b64):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{fb64}",
                        "detail": "low"
                    }
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=500
            )
            synthesis = response.choices[0].message.content

        elif self.provider == "anthropic":
            content = []
            for i, fb64 in enumerate(frames_b64):
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": fb64
                    }
                })
            content.append({"type": "text", "text": prompt})

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": content}]
            )
            synthesis = response.content[0].text
        else:
            synthesis = "[Unknown provider]"

        return {
            "video_path": video_path,
            "frame_count": len(frames),
            "synthesis": synthesis
        }

    def compare_frames(
        self,
        frame1_path: str,
        frame2_path: str,
        prompt: str = None
    ) -> str:
        """
        Compare two frames (before/after action).

        Useful for understanding what changed during a transition.
        """
        if prompt is None:
            prompt = """Compare these two images of a Rubik's cube (before and after an action).

Describe:
1. What changed between the images?
2. Which layer/face was rotated?
3. What direction was the rotation (clockwise/counter-clockwise)?

Use standard cube notation if possible (R, L, U, D, R', L', etc.)."""

        if self.client is None:
            return f"[No VLM available] Comparing: {frame1_path} vs {frame2_path}"

        img1_b64 = self.image_to_base64(frame1_path)
        img2_b64 = self.image_to_base64(frame2_path)

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img1_b64}", "detail": "low"}
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img2_b64}", "detail": "low"}
                        }
                    ]
                }],
                max_tokens=400
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            ext1 = Path(frame1_path).suffix.lower()
            ext2 = Path(frame2_path).suffix.lower()
            mt1 = 'image/png' if ext1 == '.png' else 'image/jpeg'
            mt2 = 'image/png' if ext2 == '.png' else 'image/jpeg'

            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": mt1, "data": img1_b64}},
                        {"type": "image", "source": {"type": "base64", "media_type": mt2, "data": img2_b64}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            return response.content[0].text

        return "[Unknown provider]"


# =============================================================================
# Memory Node Structure (following M3-Agent spec)
# =============================================================================

@dataclass
class MemoryNode:
    """
    Memory node following M3-Agent's 6-attribute structure.

    From paper: "Each node contains six attributes: id, type, content,
    embedding, weight, and extra_data"
    """

    id: str
    """Unique identifier for this memory node"""

    type: str  # "text", "image", "video", "episodic", "semantic"
    """Modality type of the content"""

    content: str
    """Raw content (text description, or base64 for media)"""

    embedding: Optional[List[float]] = None
    """Vector representation for similarity retrieval"""

    weight: float = 1.0
    """Confidence score - frequently activated entries get higher weight"""

    extra_data: Dict = field(default_factory=dict)
    """JSON metadata (timestamps, source info, etc.)"""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "embedding": self.embedding,
            "weight": self.weight,
            "extra_data": self.extra_data
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryNode':
        return cls(**data)


@dataclass
class MemoryEdge:
    """Edge connecting memory nodes (temporal, causal, entity relationships)."""

    source_id: str
    target_id: str
    relation: str  # "temporal", "causal", "same_entity", "derived_from"
    weight: float = 1.0
    metadata: Dict = field(default_factory=dict)


# =============================================================================
# Memory Graph (Entity-Centric Structure)
# =============================================================================

class MemoryGraph:
    """
    Entity-centric multimodal memory graph.

    Following M3-Agent: "an entity-centric multimodal graph, where each node
    represents a distinct memory item"

    Features:
    - Episodic memory: Concrete observed events
    - Semantic memory: Abstracted knowledge
    - Weight-based conflict resolution
    - Multimodal search support
    """

    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: List[MemoryEdge] = []
        self.embedding_model = embedding_model
        self._embedding_client = None

        # Separate indices for episodic vs semantic
        self.episodic_ids: List[str] = []
        self.semantic_ids: List[str] = []

        # Entity tracking (cube states in our case)
        self.entity_index: Dict[str, List[str]] = {}  # entity_id -> [node_ids]

    def _get_embedding_client(self):
        """Lazy initialization of embedding client."""
        if self._embedding_client is None and HAS_OPENAI:
            self._embedding_client = OpenAI()
        return self._embedding_client

    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """Compute embedding for text content."""
        client = self._get_embedding_client()
        if client is None:
            return None

        try:
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return None

    def add_episodic_memory(
        self,
        content: str,
        entity_id: Optional[str] = None,
        video_path: Optional[str] = None,
        timestamp: Optional[str] = None,
        **extra_data
    ) -> str:
        """
        Add episodic memory (concrete observed event).

        From paper: "Episodic memory captures what happened - specific events
        with temporal grounding"
        """
        node_id = f"ep_{len(self.episodic_ids):04d}"

        extra = {
            "video_path": video_path,
            "timestamp": timestamp or datetime.now().isoformat(),
            "entity_id": entity_id,
            **extra_data
        }

        node = MemoryNode(
            id=node_id,
            type="episodic",
            content=content,
            embedding=self._compute_embedding(content),
            weight=1.0,
            extra_data=extra
        )

        self.nodes[node_id] = node
        self.episodic_ids.append(node_id)

        # Update entity index
        if entity_id:
            if entity_id not in self.entity_index:
                self.entity_index[entity_id] = []
            self.entity_index[entity_id].append(node_id)

        return node_id

    def add_semantic_memory(
        self,
        content: str,
        derived_from: List[str] = None,
        confidence: float = 1.0,
        **extra_data
    ) -> str:
        """
        Add semantic memory (abstracted knowledge).

        From paper: "Semantic memory captures what I learned - general knowledge
        applicable beyond specific moments"
        """
        node_id = f"sem_{len(self.semantic_ids):04d}"

        extra = {
            "derived_from": derived_from or [],
            "confidence": confidence,
            **extra_data
        }

        node = MemoryNode(
            id=node_id,
            type="semantic",
            content=content,
            embedding=self._compute_embedding(content),
            weight=confidence,
            extra_data=extra
        )

        self.nodes[node_id] = node
        self.semantic_ids.append(node_id)

        # Add derivation edges
        if derived_from:
            for source_id in derived_from:
                self.add_edge(source_id, node_id, "derived_from")

        return node_id

    def add_edge(self, source_id: str, target_id: str, relation: str,
                 weight: float = 1.0, **metadata):
        """Add edge between memory nodes."""
        edge = MemoryEdge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            weight=weight,
            metadata=metadata
        )
        self.edges.append(edge)

    def search_node(
        self,
        query: str,
        top_k: int = 5,
        modality_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant memory nodes.

        Following M3-Agent's search_node tool:
        "Accepts a query and returns the top-k most relevant nodes.
        Supports multimodal queries and modality-specific retrieval."
        """
        query_embedding = self._compute_embedding(query)

        results = []
        for node_id, node in self.nodes.items():
            # Apply modality filter
            if modality_filter and node.type != modality_filter:
                continue

            # Compute similarity score
            if query_embedding and node.embedding:
                similarity = self._cosine_similarity(query_embedding, node.embedding)
            else:
                # Fallback: keyword matching
                similarity = self._keyword_similarity(query, node.content)

            # Apply weight (frequently accessed nodes get priority)
            score = similarity * node.weight

            results.append({
                "node_id": node_id,
                "type": node.type,
                "content": node.content,
                "score": score,
                "weight": node.weight,
                "extra_data": node.extra_data
            })

        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)

        # Increase weight of accessed nodes (activation-based weighting)
        for r in results[:top_k]:
            self.nodes[r["node_id"]].weight += 0.1

        return results[:top_k]

    def search_by_entity(self, entity_id: str) -> List[Dict]:
        """Search all memories related to a specific entity."""
        if entity_id not in self.entity_index:
            return []

        return [
            {
                "node_id": nid,
                "type": self.nodes[nid].type,
                "content": self.nodes[nid].content,
                "extra_data": self.nodes[nid].extra_data
            }
            for nid in self.entity_index[entity_id]
            if nid in self.nodes
        ]

    def search_by_outcome(self, outcome: str) -> List[Dict]:
        """Search memories by outcome (success/failure)."""
        results = []
        for node_id, node in self.nodes.items():
            if node.extra_data.get("outcome") == outcome:
                results.append({
                    "node_id": node_id,
                    "type": node.type,
                    "content": node.content,
                    "extra_data": node.extra_data
                })
        return results

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if HAS_NUMPY:
            a_arr, b_arr = np.array(a), np.array(b)
            return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr) + 1e-8))
        else:
            # Pure Python fallback
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot / (norm_a * norm_b + 1e-8)

    def _keyword_similarity(self, query: str, content: str) -> float:
        """Fallback keyword-based similarity."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        if not query_words:
            return 0.0
        return len(query_words & content_words) / len(query_words)

    def get_statistics(self) -> Dict:
        """Return memory statistics."""
        return {
            "total_nodes": len(self.nodes),
            "episodic_count": len(self.episodic_ids),
            "semantic_count": len(self.semantic_ids),
            "edge_count": len(self.edges),
            "entity_count": len(self.entity_index)
        }

    def save(self, path: str):
        """Save memory graph to file."""
        data = {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [
                {
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "relation": e.relation,
                    "weight": e.weight,
                    "metadata": e.metadata
                }
                for e in self.edges
            ],
            "episodic_ids": self.episodic_ids,
            "semantic_ids": self.semantic_ids,
            "entity_index": self.entity_index
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, path: str):
        """Load memory graph from file."""
        with open(path, 'r') as f:
            data = json.load(f)

        self.nodes = {k: MemoryNode.from_dict(v) for k, v in data["nodes"].items()}
        self.edges = [
            MemoryEdge(**e) for e in data["edges"]
        ]
        self.episodic_ids = data["episodic_ids"]
        self.semantic_ids = data["semantic_ids"]
        self.entity_index = data["entity_index"]


# =============================================================================
# Memorization Process
# =============================================================================

class CubeWorldMemorizer:
    """
    Memorization process for building memory from cube world videos.

    Following M3-Agent's memorization pipeline:
    1. Process video segments (transitions in our case)
    2. Generate episodic memories (what happened)
    3. Extract semantic memories (what was learned)
    4. Build entity-centric graph

    Simplified vs M3-Agent:
    - No face recognition / speaker diarization needed
    - Transitions are our "clips" instead of 30-sec segments
    - Uses API LLM instead of local Qwen2.5-Omni

    Visual Understanding (Optional):
    - Set use_visual=True to analyze actual video content
    - Requires VLM (GPT-4o/Claude) for video frame analysis
    - Default: use pre-defined text descriptions from world JSON
    """

    def __init__(
        self,
        memory_graph: MemoryGraph,
        llm_client=None,
        visual_understanding: Optional['VisualUnderstanding'] = None,
        use_visual: bool = False
    ):
        self.memory = memory_graph
        self.llm_client = llm_client or (OpenAI() if HAS_OPENAI else None)
        self.visual = visual_understanding
        self.use_visual = use_visual and (visual_understanding is not None)

        # Track visual analysis results
        self.visual_analyses: Dict[str, Dict] = {}

    def process_world(self, world_data: Dict) -> None:
        """
        Build memory from a complete world definition.

        Args:
            world_data: Loaded world JSON (states, transitions, etc.)
        """
        # Process all states as entities
        for state in world_data.get("states", []):
            self._process_state(state)

        # Process all transitions as episodic memories
        for transition in world_data.get("transitions", []):
            self._process_transition(transition)

        # Extract semantic knowledge from patterns
        self._extract_semantic_knowledge(world_data)

    def _process_state(self, state: Dict) -> str:
        """Process a state and add to memory."""
        state_id = state["state_id"]
        description = state.get("text_description", "")

        # Determine outcome from metadata
        outcome = state.get("metadata", {}).get("outcome", "intermediate")

        # Add episodic memory for this state observation
        ep_id = self.memory.add_episodic_memory(
            content=f"Observed state {state_id}: {description}",
            entity_id=state_id,
            outcome=outcome,
            state_type=state.get("metadata", {}).get("outcome", "intermediate")
        )

        return ep_id

    def _process_transition(self, transition: Dict) -> str:
        """Process a transition and add episodic memory."""
        start_state = transition["start_state_id"]
        end_state = transition["end_state_id"]
        action_id = transition["action_id"]
        action_desc = transition["action_description"]
        video_path = transition.get("video_path")

        # Determine outcome
        outcome = transition.get("metadata", {}).get("outcome", "intermediate")

        # Optional: Use visual understanding to analyze the video
        visual_description = None
        if self.use_visual and video_path and Path(video_path).exists():
            try:
                analysis = self.visual.describe_video(video_path)
                visual_description = analysis.get("synthesis", "")
                self.visual_analyses[action_id] = analysis
            except Exception as e:
                print(f"Visual analysis failed for {video_path}: {e}")

        # Create episodic memory for the transition
        if visual_description:
            # Use VLM-generated description
            content = (
                f"Action '{action_id}': {action_desc}. "
                f"Visual observation: {visual_description} "
                f"Transitioned from {start_state} to {end_state}."
            )
        else:
            # Use pre-defined description
            content = (
                f"Action '{action_id}': {action_desc}. "
                f"Transitioned from {start_state} to {end_state}."
            )

        if outcome == "success":
            content += " This led to SUCCESS."
        elif outcome == "dead_end":
            content += " This led to a DEAD END."

        ep_id = self.memory.add_episodic_memory(
            content=content,
            entity_id=f"transition_{start_state}_{action_id}",
            video_path=video_path,
            start_state=start_state,
            end_state=end_state,
            action_id=action_id,
            outcome=outcome,
            visual_analysis=visual_description
        )

        return ep_id

    def _extract_semantic_knowledge(self, world_data: Dict) -> None:
        """
        Extract semantic knowledge from episodic memories.

        Following M3-Agent: "Semantic memory captures general knowledge
        extracted from content"
        """
        # Find all successful paths
        success_transitions = [
            t for t in world_data.get("transitions", [])
            if t.get("metadata", {}).get("outcome") == "success"
        ]

        for t in success_transitions:
            self.memory.add_semantic_memory(
                content=f"Taking action '{t['action_id']}' from state {t['start_state_id']} leads to success.",
                derived_from=[],  # Would link to episodic IDs in full implementation
                confidence=1.0,
                knowledge_type="success_path"
            )

        # Find all dead-end transitions
        deadend_transitions = [
            t for t in world_data.get("transitions", [])
            if t.get("metadata", {}).get("outcome") == "dead_end"
        ]

        for t in deadend_transitions:
            self.memory.add_semantic_memory(
                content=f"AVOID: Taking action '{t['action_id']}' from state {t['start_state_id']} leads to dead end.",
                derived_from=[],
                confidence=1.0,
                knowledge_type="dead_end_warning"
            )

        # Extract path patterns
        strategies = world_data.get("metadata", {}).get("success_strategies", [])
        for strategy in strategies:
            self.memory.add_semantic_memory(
                content=f"Strategy '{strategy['name']}': Path {strategy['path']} with {strategy['length']} steps.",
                derived_from=[],
                confidence=0.9,
                knowledge_type="strategy"
            )


# =============================================================================
# Control Process (Algorithm 1 from paper)
# =============================================================================

class M3AgentController:
    """
    Control process implementing M3-Agent's iterative reasoning.

    Following Algorithm 1 from paper:
    1. Initialize with system prompt and user instruction
    2. For each round (up to H rounds):
       - Generate reasoning, action, and argument
       - If action is [Search]: query memory, append results
       - If action is [Answer]: return and terminate
    3. Use multi-turn approach for complex planning

    Differences from original:
    - Uses GPT-4o/Claude instead of Qwen3
    - Simplified action space ([Search], [Answer])
    - Adapted prompts for cube world domain
    """

    def __init__(
        self,
        memory: MemoryGraph,
        model: str = "gpt-4o",
        max_rounds: int = 5,
        temperature: float = 0.7
    ):
        self.memory = memory
        self.model = model
        self.max_rounds = max_rounds
        self.temperature = temperature

        # Initialize LLM client
        if "gpt" in model.lower() and HAS_OPENAI:
            self.client = OpenAI()
            self.provider = "openai"
        elif "claude" in model.lower() and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic()
            self.provider = "anthropic"
        else:
            self.client = None
            self.provider = None

        # Tracking
        self.reasoning_trace: List[Dict] = []
        self.total_searches = 0
        self.total_tokens = 0

    def _build_system_prompt(self) -> str:
        """
        Build system prompt for the control policy.

        Following M3-Agent: System prompt guides the agent's behavior
        and tool usage.
        """
        return """You are an AI agent navigating a Rubik's cube challenge. You can manipulate a 3x3 cube by twisting layers (R, L, U, D moves).

Your goal: Find the correct sequence of layer twists to reach a SUCCESS state while avoiding DEAD ENDs.

You have access to a MEMORY of past observations and learned knowledge. Use it wisely.

AVAILABLE ACTIONS:
1. [Search] <query> - Search your memory for relevant information
   Example: [Search] what happens after R move from s1
   Example: [Search] which actions lead to success
   Example: [Search] dead end paths to avoid

2. [Answer] <action_id> - Choose an action to take
   Example: [Answer] a7_turn_up

STRATEGY:
- First, search memory for relevant experiences
- Look for patterns: what worked before? what failed?
- Avoid known dead-ends
- Then choose your action confidently

You have up to 5 rounds of reasoning. Use [Search] to gather information, then [Answer] to decide."""

    def _build_user_prompt(
        self,
        state_description: str,
        available_actions: List[Dict],
        action_history: List[str],
        search_results: str = ""
    ) -> str:
        """Build the user prompt for current decision."""
        actions_str = "\n".join([
            f"  - {a['action_id']}: {a['description']}"
            for a in available_actions
        ])

        history_str = " → ".join(action_history) if action_history else "None yet"

        prompt = f"""CURRENT SITUATION:
{state_description}

AVAILABLE ACTIONS:
{actions_str}

ACTION HISTORY: {history_str}
"""

        if search_results:
            prompt += f"\nMEMORY SEARCH RESULTS:\n{search_results}\n"

        prompt += "\nWhat do you do? Respond with either [Search] <query> or [Answer] <action_id>."

        return prompt

    def _parse_response(self, response: str) -> Tuple[str, str]:
        """
        Parse LLM response to extract action type and argument.

        Returns:
            Tuple of (action_type, argument)
            action_type: "search" or "answer"
        """
        response = response.strip()

        # Look for [Search] pattern
        if "[Search]" in response or "[search]" in response.lower():
            # Extract query after [Search]
            import re
            match = re.search(r'\[Search\]\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
            if match:
                return "search", match.group(1).strip()
            # Fallback: everything after [Search]
            idx = response.lower().find("[search]")
            return "search", response[idx+8:].strip().split('\n')[0]

        # Look for [Answer] pattern
        if "[Answer]" in response or "[answer]" in response.lower():
            import re
            match = re.search(r'\[Answer\]\s*(\S+)', response, re.IGNORECASE)
            if match:
                return "answer", match.group(1).strip()

        # Fallback: try to find action_id in response
        import re
        action_match = re.search(r'(a\d+_\w+)', response)
        if action_match:
            return "answer", action_match.group(1)

        return "unknown", response

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM and get response."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=1024
            )
            self.total_tokens += response.usage.total_tokens
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text

        else:
            raise RuntimeError("No LLM client available")

    def _execute_search(self, query: str) -> str:
        """
        Execute memory search and format results.

        Implements search_node and search_clip functionality from M3-Agent.
        """
        self.total_searches += 1

        # Search memory nodes
        results = self.memory.search_node(query, top_k=5)

        if not results:
            return "No relevant memories found."

        # Format results
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"{i}. [{r['type']}] {r['content'][:200]}..."
                if len(r['content']) > 200 else
                f"{i}. [{r['type']}] {r['content']}"
            )

        return "\n".join(formatted)

    def select_action(
        self,
        state_description: str,
        available_actions: List[Dict],
        action_history: List[str] = None
    ) -> Dict:
        """
        Main control loop following Algorithm 1.

        Implements M3-Agent's iterative reasoning:
        - Up to H rounds of Search/Answer
        - Multi-turn context accumulation
        - Returns chosen action with reasoning trace
        """
        action_history = action_history or []
        self.reasoning_trace = []

        system_prompt = self._build_system_prompt()
        search_results = ""

        for round_num in range(self.max_rounds):
            # Build prompt with accumulated context
            user_prompt = self._build_user_prompt(
                state_description,
                available_actions,
                action_history,
                search_results
            )

            # Get LLM response
            try:
                response = self._call_llm(system_prompt, user_prompt)
            except Exception as e:
                print(f"LLM error: {e}")
                # Fallback to random
                import random
                action = random.choice(available_actions)
                return {
                    "action_id": action["action_id"],
                    "reasoning_trace": self.reasoning_trace,
                    "error": str(e)
                }

            # Parse response
            action_type, argument = self._parse_response(response)

            # Log reasoning trace
            self.reasoning_trace.append({
                "round": round_num + 1,
                "response": response,
                "action_type": action_type,
                "argument": argument
            })

            if action_type == "search":
                # Execute search and continue
                search_results = self._execute_search(argument)
                search_results = f"Search for '{argument}':\n{search_results}"

            elif action_type == "answer":
                # Validate action exists
                valid_ids = [a["action_id"] for a in available_actions]
                if argument in valid_ids:
                    return {
                        "action_id": argument,
                        "reasoning_trace": self.reasoning_trace,
                        "rounds_used": round_num + 1,
                        "searches_used": self.total_searches
                    }
                else:
                    # Try to find closest match
                    for aid in valid_ids:
                        if argument.lower() in aid.lower() or aid.lower() in argument.lower():
                            return {
                                "action_id": aid,
                                "reasoning_trace": self.reasoning_trace,
                                "rounds_used": round_num + 1,
                                "note": f"Matched '{argument}' to '{aid}'"
                            }

            # Unknown action type, continue

        # Fallback after max rounds
        import random
        action = random.choice(available_actions)
        return {
            "action_id": action["action_id"],
            "reasoning_trace": self.reasoning_trace,
            "fallback": True,
            "note": "Max rounds reached without decision"
        }


# =============================================================================
# Complete M3-Style Agent
# =============================================================================

class M3StyleAgent:
    """
    Complete M3-Agent style implementation for Cube World.

    Combines:
    - MemoryGraph: Entity-centric multimodal memory
    - CubeWorldMemorizer: Builds memory from world data
    - M3AgentController: Iterative reasoning with search
    - VisualUnderstanding (optional): Analyze actual video content

    Usage:
        # Without visual understanding (default, uses text descriptions)
        agent = M3StyleAgent()
        agent.build_memory_from_world("worlds/video_worlds/cube_world.json")

        # With visual understanding (analyzes actual video frames)
        agent = M3StyleAgent(use_visual=True)
        agent.build_memory_from_world("worlds/video_worlds/cube_world.json")

        # Select action
        result = agent.select_action(state_desc, available_actions)
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        max_reasoning_rounds: int = 5,
        embedding_model: str = "text-embedding-3-small",
        use_visual: bool = False,
        visual_model: str = "gpt-4o"
    ):
        """
        Initialize M3-Style Agent.

        Args:
            model: LLM for control/reasoning
            max_reasoning_rounds: Max Search/Answer rounds (H in paper)
            embedding_model: Model for memory embeddings
            use_visual: Whether to use visual understanding (analyzes video frames)
            visual_model: VLM for visual understanding (if use_visual=True)
        """
        # Initialize memory
        self.memory = MemoryGraph(embedding_model=embedding_model)

        # Initialize controller
        self.controller = M3AgentController(
            memory=self.memory,
            model=model,
            max_rounds=max_reasoning_rounds
        )

        # Initialize visual understanding (optional)
        self.use_visual = use_visual
        self.visual = VisualUnderstanding(model=visual_model) if use_visual else None

        # Tracking
        self.action_history: List[str] = []
        self.episode_count = 0
        self.world_loaded = False
        self.visual_analyses: Dict = {}

    def build_memory_from_world(self, world_path: str, verbose: bool = False) -> Dict:
        """
        Build memory graph from world definition.

        Args:
            world_path: Path to world JSON file
            verbose: Print progress during visual analysis

        Returns:
            Memory statistics
        """
        with open(world_path, 'r') as f:
            world_data = json.load(f)

        if verbose and self.use_visual:
            print(f"Building memory with visual understanding enabled...")
            print(f"Processing {len(world_data.get('transitions', []))} transitions...")

        memorizer = CubeWorldMemorizer(
            self.memory,
            visual_understanding=self.visual,
            use_visual=self.use_visual
        )
        memorizer.process_world(world_data)

        # Store visual analyses for inspection
        self.visual_analyses = memorizer.visual_analyses

        self.world_loaded = True

        stats = self.memory.get_statistics()
        if verbose:
            print(f"Memory built: {stats}")
            if self.use_visual:
                print(f"Visual analyses: {len(self.visual_analyses)} transitions analyzed")

        return stats

    def select_action(
        self,
        available_actions: List[Dict],
        state_description: str = None,
        state_image_path: str = None,
        state_video_path: str = None
    ) -> Dict:
        """
        Select action using M3-style reasoning.

        The agent receives VISUAL input (image/video) and action list.
        Text description is optional fallback only.

        Args:
            available_actions: List of available actions (always provided)
            state_description: Text description (optional fallback)
            state_image_path: Path to current state image (preferred)
            state_video_path: Path to video showing transition to current state

        Returns:
            Dict with action_id and reasoning trace
        """
        # Build state understanding from visual input
        visual_description = None

        if self.visual is not None:
            if state_video_path and Path(state_video_path).exists():
                # Analyze the transition video
                analysis = self.visual.describe_video(state_video_path)
                visual_description = analysis.get("synthesis", "")
            elif state_image_path and Path(state_image_path).exists():
                # Analyze the current state image
                visual_description = self.visual.describe_frame(
                    state_image_path,
                    prompt="Describe the current state of the Rubik's cube. What colors are visible on each face? What is the cube's orientation?"
                )

        # Determine what description to use
        if visual_description:
            description_to_use = f"Visual observation: {visual_description}"
        elif state_description:
            description_to_use = state_description
        else:
            description_to_use = "Current state unknown (no visual or text input provided)"

        result = self.controller.select_action(
            state_description=description_to_use,
            available_actions=available_actions,
            action_history=self.action_history
        )

        # Store visual description in result for logging
        result["visual_description"] = visual_description
        result["used_visual"] = visual_description is not None

        # Update history
        self.action_history.append(result["action_id"])

        return result

    def reset_episode(self):
        """Reset for new episode (keeps memory)."""
        self.action_history = []
        self.episode_count += 1
        self.controller.reasoning_trace = []

    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            "memory": self.memory.get_statistics(),
            "episode_count": self.episode_count,
            "total_searches": self.controller.total_searches,
            "total_tokens": self.controller.total_tokens
        }

    def save_memory(self, path: str):
        """Save memory to file."""
        self.memory.save(path)

    def load_memory(self, path: str):
        """Load memory from file."""
        self.memory.load(path)
        self.world_loaded = True


# =============================================================================
# Convenience Functions
# =============================================================================

def create_m3_agent(
    world_path: str,
    model: str = "gpt-4o",
    max_rounds: int = 5
) -> M3StyleAgent:
    """
    Create and initialize an M3-style agent for a world.

    Args:
        world_path: Path to world JSON
        model: LLM model to use
        max_rounds: Maximum reasoning rounds

    Returns:
        Initialized M3StyleAgent
    """
    agent = M3StyleAgent(model=model, max_reasoning_rounds=max_rounds)
    stats = agent.build_memory_from_world(world_path)
    print(f"Memory built: {stats}")
    return agent


if __name__ == "__main__":
    # Quick test
    print("M3-Style Agent for Cube World")
    print("=" * 50)

    # Test memory graph
    memory = MemoryGraph()
    memory.add_episodic_memory(
        content="Observed R move leading from s1 to s2",
        entity_id="s1",
        outcome="intermediate"
    )
    memory.add_semantic_memory(
        content="R R sequence leads to success",
        confidence=1.0
    )

    print(f"Memory stats: {memory.get_statistics()}")

    # Test search
    results = memory.search_node("success", top_k=3)
    print(f"Search results: {len(results)} items")

    print("\nAgent ready for cube world!")
