"""
Action-Conditioned World Model (AC-World) Benchmark Implementation

This module implements the core benchmark experiments for evaluating
action-conditioned video generation capabilities.
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

from utils import VideoGenerationManager, VideoGenerationResult


@dataclass
class BenchmarkResult:
    """Results from a single benchmark experiment."""

    experiment_id: str
    experiment_type: str
    prompt: str
    expected_output: str
    video_result: VideoGenerationResult
    evaluation_score: float
    evaluation_metrics: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "experiment_id": self.experiment_id,
            "experiment_type": self.experiment_type,
            "prompt": self.prompt,
            "expected_output": self.expected_output,
            "video_result": self.video_result.to_dict(),
            "evaluation_score": self.evaluation_score,
            "evaluation_metrics": self.evaluation_metrics,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark experiments."""

    video_provider: str = "sora"
    evaluation_model: str = "gpt-4"
    max_wait_time: int = 300  # seconds
    evaluation_temperature: float = 0.0
    output_dir: str = "benchmark_results"

    # Experiment-specific settings
    action_inference_tests: int = 5
    goal_conditioned_tests: int = 5
    temporal_memory_tests: int = 3


class ACWorldBenchmark:
    """
    Main benchmark class for Action-Conditioned World Model evaluation.

    This class runs experiments to evaluate how well video generation models
    can understand and generate action-conditioned video sequences.
    """

    def __init__(self, config: BenchmarkConfig = None):
        """Initialize the benchmark with configuration."""
        self.config = config or BenchmarkConfig()
        self.manager = VideoGenerationManager()
        self.results: List[BenchmarkResult] = []

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)

    def setup_providers(self, api_keys: Dict[str, str]):
        """
        Set up video generation providers.

        Args:
            api_keys: Dictionary mapping provider names to API keys
        """
        # Import and register Sora provider
        if "openai" in api_keys:
            from utils.sora import SoraVideoGenerator
            sora_provider = SoraVideoGenerator(api_key=api_keys["openai"])
            self.manager.register_provider("sora", sora_provider)
            self.logger.info("Registered Sora provider")

        # TODO: Add other providers (Runway, Stability AI, etc.)

    def get_action_inference_prompts(self) -> List[Dict[str, str]]:
        """Get prompts for action inference experiments."""
        return [
            {
                "prompt": "A person sitting at a desk, then standing up and walking to the door",
                "expected": "stand up, walk forward"
            },
            {
                "prompt": "Initial: cup on table. Goal: cup on shelf. Show the action sequence.",
                "expected": "pick up cup, raise hand, place on shelf"
            },
            {
                "prompt": "Observation1: ball on ground. Observation2: ball in air.",
                "expected": "throw ball"
            },
            {
                "prompt": "Observation1: car stopped at light. Observation2: car at intersection.",
                "expected": "accelerate, steer forward"
            },
            {
                "prompt": "Observation1: dark room. Observation2: bright room.",
                "expected": "turn on light"
            }
        ]

    def get_goal_conditioned_prompts(self) -> List[Dict[str, str]]:
        """Get prompts for goal-conditioned planning experiments."""
        return [
            {
                "prompt": "Initial state: empty plate. Goal: plate with food.",
                "expected": "pick up food, place on plate"
            },
            {
                "prompt": "Initial state: closed door. Goal: open door.",
                "expected": "walk to door, turn handle, pull door open"
            },
            {
                "prompt": "Initial state: light off. Goal: light on.",
                "expected": "flip light switch"
            },
            {
                "prompt": "Initial state: cup on table. Goal: cup on shelf.",
                "expected": "pick up cup, move to shelf, place cup"
            },
            {
                "prompt": "Initial state: car parked. Goal: car moving.",
                "expected": "start engine, accelerate"
            }
        ]

    async def run_action_inference_experiment(self, experiment_id: str) -> BenchmarkResult:
        """Run a single action inference experiment."""
        prompts = self.get_action_inference_prompts()
        test_case = prompts[int(experiment_id.split('_')[-1]) % len(prompts)]

        self.logger.info(f"Running action inference experiment {experiment_id}")
        self.logger.info(f"Prompt: {test_case['prompt']}")

        try:
            # Generate video
            video_result = self.manager.generate_video(
                provider_name=self.config.video_provider,
                prompt=test_case["prompt"],
                size="1024x1808",
                seconds="8",
                quality="standard"
            )

            # For now, we'll use a simple evaluation based on video generation success
            # In a full implementation, this would involve more sophisticated evaluation
            evaluation_score = 1.0 if video_result.status == "completed" else 0.0

            evaluation_metrics = {
                "generation_success": video_result.status == "completed",
                "generation_time": video_result.created_at.timestamp(),
                "video_id": video_result.id,
            }

            result = BenchmarkResult(
                experiment_id=experiment_id,
                experiment_type="action_inference",
                prompt=test_case["prompt"],
                expected_output=test_case["expected"],
                video_result=video_result,
                evaluation_score=evaluation_score,
                evaluation_metrics=evaluation_metrics,
                timestamp=datetime.now()
            )

            self.results.append(result)
            self.logger.info(f"✅ Action inference experiment {experiment_id} completed")

            return result

        except Exception as e:
            self.logger.error(f"❌ Action inference experiment {experiment_id} failed: {e}")
            # Return a failed result
            failed_result = VideoGenerationResult(
                id=f"failed_{experiment_id}",
                object="video",
                model="failed",
                status="failed",
                progress=0.0,
                created_at=datetime.now(),
                size="0x0",
                seconds="0",
                quality="failed",
                prompt=test_case["prompt"],
                provider="failed",
                error=str(e)
            )

            result = BenchmarkResult(
                experiment_id=experiment_id,
                experiment_type="action_inference",
                prompt=test_case["prompt"],
                expected_output=test_case["expected"],
                video_result=failed_result,
                evaluation_score=0.0,
                evaluation_metrics={"error": str(e)},
                timestamp=datetime.now()
            )

            self.results.append(result)
            return result

    async def run_goal_conditioned_experiment(self, experiment_id: str) -> BenchmarkResult:
        """Run a single goal-conditioned planning experiment."""
        prompts = self.get_goal_conditioned_prompts()
        test_case = prompts[int(experiment_id.split('_')[-1]) % len(prompts)]

        self.logger.info(f"Running goal-conditioned experiment {experiment_id}")
        self.logger.info(f"Prompt: {test_case['prompt']}")

        try:
            # Generate video
            video_result = self.manager.generate_video(
                provider_name=self.config.video_provider,
                prompt=test_case["prompt"],
                size="1024x1808",
                seconds="8",
                quality="standard"
            )

            # Simple evaluation based on generation success
            evaluation_score = 1.0 if video_result.status == "completed" else 0.0

            evaluation_metrics = {
                "generation_success": video_result.status == "completed",
                "generation_time": video_result.created_at.timestamp(),
                "video_id": video_result.id,
            }

            result = BenchmarkResult(
                experiment_id=experiment_id,
                experiment_type="goal_conditioned",
                prompt=test_case["prompt"],
                expected_output=test_case["expected"],
                video_result=video_result,
                evaluation_score=evaluation_score,
                evaluation_metrics=evaluation_metrics,
                timestamp=datetime.now()
            )

            self.results.append(result)
            self.logger.info(f"✅ Goal-conditioned experiment {experiment_id} completed")

            return result

        except Exception as e:
            self.logger.error(f"❌ Goal-conditioned experiment {experiment_id} failed: {e}")
            # Return a failed result
            failed_result = VideoGenerationResult(
                id=f"failed_{experiment_id}",
                object="video",
                model="failed",
                status="failed",
                progress=0.0,
                created_at=datetime.now(),
                size="0x0",
                seconds="0",
                quality="failed",
                prompt=test_case["prompt"],
                provider="failed",
                error=str(e)
            )

            result = BenchmarkResult(
                experiment_id=experiment_id,
                experiment_type="goal_conditioned",
                prompt=test_case["prompt"],
                expected_output=test_case["expected"],
                video_result=failed_result,
                evaluation_score=0.0,
                evaluation_metrics={"error": str(e)},
                timestamp=datetime.now()
            )

            self.results.append(result)
            return result

    async def run_full_benchmark(self, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """
        Run the complete AC-World benchmark.

        Args:
            api_keys: Dictionary mapping provider names to API keys

        Returns:
            Dictionary containing benchmark results and statistics
        """
        self.logger.info("🚀 Starting AC-World benchmark")

        # Setup providers
        self.setup_providers(api_keys)

        # Run action inference experiments
        action_inference_tasks = []
        for i in range(self.config.action_inference_tests):
            experiment_id = f"action_inference_{i}"
            task = self.run_action_inference_experiment(experiment_id)
            action_inference_tasks.append(task)

        # Run goal-conditioned experiments
        goal_conditioned_tasks = []
        for i in range(self.config.goal_conditioned_tests):
            experiment_id = f"goal_conditioned_{i}"
            task = self.run_goal_conditioned_experiment(experiment_id)
            goal_conditioned_tasks.append(task)

        # Execute all experiments concurrently
        all_tasks = action_inference_tasks + goal_conditioned_tasks
        await asyncio.gather(*all_tasks)

        # Calculate statistics
        total_experiments = len(self.results)
        successful_experiments = sum(1 for r in self.results if r.evaluation_score > 0)
        success_rate = successful_experiments / total_experiments if total_experiments > 0 else 0

        avg_score = sum(r.evaluation_score for r in self.results) / total_experiments if total_experiments > 0 else 0

        # Save results
        results_file = os.path.join(self.config.output_dir, "benchmark_results.json")
        with open(results_file, "w") as f:
            json.dump({
                "benchmark_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "config": self.config.__dict__,
                    "total_experiments": total_experiments,
                    "successful_experiments": successful_experiments,
                    "success_rate": success_rate,
                    "average_score": avg_score,
                },
                "results": [result.to_dict() for result in self.results]
            }, f, indent=2)

        self.logger.info("✅ Benchmark completed!")
        self.logger.info(f"   Results saved to: {results_file}")
        self.logger.info(f"   Success rate: {success_rate:.2%} ({successful_experiments}/{total_experiments})")
        self.logger.info(f"   Average score: {avg_score:.3f}")

        return {
            "success_rate": success_rate,
            "average_score": avg_score,
            "total_experiments": total_experiments,
            "successful_experiments": successful_experiments,
            "results_file": results_file,
            "results": self.results
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of benchmark results."""
        if not self.results:
            return {"message": "No results available. Run benchmark first."}

        total = len(self.results)
        successful = sum(1 for r in self.results if r.evaluation_score > 0)
        success_rate = successful / total if total > 0 else 0

        avg_score = sum(r.evaluation_score for r in self.results) / total if total > 0 else 0

        by_type = {}
        for result in self.results:
            exp_type = result.experiment_type
            if exp_type not in by_type:
                by_type[exp_type] = {"count": 0, "successful": 0, "total_score": 0}
            by_type[exp_type]["count"] += 1
            if result.evaluation_score > 0:
                by_type[exp_type]["successful"] += 1
            by_type[exp_type]["total_score"] += result.evaluation_score

        return {
            "summary": {
                "total_experiments": total,
                "successful_experiments": successful,
                "success_rate": success_rate,
                "average_score": avg_score,
            },
            "by_experiment_type": {
                exp_type: {
                    "count": stats["count"],
                    "successful": stats["successful"],
                    "success_rate": stats["successful"] / stats["count"] if stats["count"] > 0 else 0,
                    "average_score": stats["total_score"] / stats["count"] if stats["count"] > 0 else 0,
                }
                for exp_type, stats in by_type.items()
            },
            "results_count": len(self.results)
        }


async def run_quick_benchmark(api_keys: Dict[str, str]) -> Dict[str, Any]:
    """
    Run a quick benchmark with minimal experiments for testing.

    Args:
        api_keys: Dictionary with API keys

    Returns:
        Benchmark results summary
    """
    # Create a minimal config for quick testing
    config = BenchmarkConfig(
        action_inference_tests=2,
        goal_conditioned_tests=2,
        max_wait_time=60
    )

    benchmark = ACWorldBenchmark(config)
    results = await benchmark.run_full_benchmark(api_keys)

    return benchmark.get_summary()


if __name__ == "__main__":
    # Quick test if run directly
    import asyncio

    async def test():
        # This would need actual API keys to work
        api_keys = {
            "openai": os.getenv("OPENAI_API_KEY", "")
        }

        if not api_keys["openai"]:
            print("❌ OPENAI_API_KEY not found. Set it in environment or .env file.")
            return

        summary = await run_quick_benchmark(api_keys)
        print("Benchmark Summary:")
        print(json.dumps(summary, indent=2))

    asyncio.run(test())


