# AC-World Video Generation Framework - Makefile

.PHONY: help install test run clean docs

# Default target
help:
	@echo "🎬 AC-World Video Generation Framework"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install     Install dependencies"
	@echo "  make test        Run basic functionality tests"
	@echo "  make run         Run example usage script"
	@echo "  make clean       Remove generated files and cache"
	@echo "  make docs        Show project documentation"
	@echo ""
	@echo "Quick start:"
	@echo "  1. Copy .env.example to .env and add your API keys"
	@echo "  2. make install"
	@echo "  3. make run"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using uv package manager..."; \
		uv pip install -r requirements.txt; \
	else \
		echo "Using pip..."; \
		pip install -r requirements.txt; \
	fi
	@echo "✅ Installation complete!"

# Run basic tests
test:
	@echo "🧪 Running tests..."
	@python3 -c "
import sys; sys.path.insert(0, '.');
try:
    from utils import VideoGenerationManager, SoraVideoGenerator
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
print('✅ All tests passed!')
"

# Run example usage script
run:
	@echo "🚀 Running example usage..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		echo "   Copy .env.example to .env and add your API keys"; \
		exit 1; \
	fi
	@python3 example_usage.py

# Clean generated files
clean:
	@echo "🧹 Cleaning up..."
	@rm -f test_result_*.json
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@find . -name "*.pyc" -delete
	@echo "✅ Cleanup complete!"

# Show documentation
docs:
	@echo "📚 AC-World Video Generation Framework Documentation"
	@echo "==================================================="
	@echo ""
	@echo "📁 Project Structure:"
	@echo "  video_gen/"
	@echo "  ├── README.md           # Project overview and benchmark description"
	@echo "  ├── requirements.txt    # Python dependencies"
	@echo "  ├── .env.example       # Environment variable template"
	@echo "  ├── example_usage.py   # Example usage script"
	@echo "  ├── Makefile           # This file"
	@echo "  └── utils/             # Video generation utilities"
	@echo "      ├── __init__.py    # Package initialization"
	@echo "      ├── unified_interface.py  # Abstract base classes"
	@echo "      ├── sora.py       # OpenAI Sora integration"
	@echo "      ├── runway.py     # Runway ML integration (planned)"
	@echo "      └── stable_diffusion.py  # Stability AI integration (planned)"
	@echo ""
	@echo "🎯 Benchmark Overview:"
	@echo "  - Action-Conditioned World Model testing"
	@echo "  - Temporal planning and scene consistency evaluation"
	@echo "  - Unified interface for multiple video generation providers"
	@echo ""
	@echo "🔧 Quick Setup:"
	@echo "  1. Copy .env.example to .env"
	@echo "  2. Add your API keys to .env"
	@echo "  3. Run: make install && make run"
	@echo ""
	@echo "📖 For more details, see README.md"


