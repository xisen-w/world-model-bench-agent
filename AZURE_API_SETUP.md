# Azure OpenAI API Setup

✅ **Setup Complete!** Your Azure OpenAI API is configured and working.

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Configuration Loading | ✅ Pass | Loaded from .env |
| Client Initialization | ✅ Pass | Successfully connected |
| Chat Completion (gpt-4o) | ✅ Pass | Main model working |
| Embeddings | ⚠️ Optional | Deployment not found (not critical) |
| Alternative Model (nano) | ✅ Pass | Fast model available |

**Overall**: 4/5 tests passed - **Ready for use!**

---

## Files Created

### 1. `utils/azure_openai_api.py`
Main Azure OpenAI utilities module with:

- **AzureOpenAIConfig**: Configuration management from .env
- **AzureOpenAIManager**: Unified API interface
- **test_api_keys()**: Comprehensive API testing function
- **test_vision_api()**: Vision model testing

### 2. `test_azure_api.py`
Standalone test script that:
- Loads .env manually
- Tests all API endpoints
- Reports detailed results

---

## Usage Examples

### Basic Chat Completion

```python
from utils.azure_openai_api import AzureOpenAIManager

# Initialize manager (auto-loads from .env)
manager = AzureOpenAIManager()

# Chat completion
response = manager.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is a Rubik's cube?"}
    ],
    model="gpt-4o"
)
print(response)
```

### Vision (Image Understanding)

```python
# Analyze an image
description = manager.vision(
    prompt="Describe the Rubik's cube state in this image",
    image_path="generated_images/cube_world_states/s1.png",
    model="gpt-4o"
)
print(description)
```

### Alternative Models

```python
# Use fast/cheap nano model
response = manager.chat(
    messages=[{"role": "user", "content": "Quick question"}],
    model="gpt-4.1-nano"
)

# Embeddings (if deployment exists)
try:
    embedding = manager.embed("some text")
    print(f"Dimension: {len(embedding)}")
except Exception as e:
    print(f"Embeddings not available: {e}")
```

---

## Available Models (from .env)

| Model | Deployment Name | Use Case |
|-------|----------------|----------|
| gpt-4o | `gpt-4o` | Main model (chat + vision) |
| gpt-4.1-nano | `gpt-4.1-nano` | Fast, cheap |
| o1 | `o1` | Reasoning model |
| o4-mini | `o4-mini` | Compact reasoning |

---

## Integration with Agents

### M3StyleAgent with Azure

```python
from world_model_bench_agent.agents import M3StyleAgent
from utils.azure_openai_api import AzureOpenAIManager

# Create agent with Azure backend
agent = M3StyleAgent(
    model="gpt-4o",  # Will use Azure deployment
    use_visual=True,
    visual_model="gpt-4o"
)

# The agent will automatically use Azure OpenAI if configured
agent.build_memory_from_world("worlds/video_worlds/cube_world.json")
```

### NaiveVLMAgent with Azure

```python
from world_model_bench_agent.agents import NaiveVLMAgent

# Simple VLM agent with Azure
agent = NaiveVLMAgent(
    model="gpt-4o",
    memory_size=10
)

result = agent.select_action(
    available_actions=actions,
    state_image_path="current_state.png"
)
```

---

## Testing Commands

### Quick Test
```bash
source venv/bin/activate
python test_azure_api.py
```

### Test with Image
```bash
python test_azure_api.py generated_images/cube_world_states/s1.png
```

### Module-Level Test
```bash
python -m utils.azure_openai_api
```

---

## Environment Variables Used

From `.env` file:

```bash
# Main GPT-4o endpoint
AZURE_OPENAI_4O_ENDPOINT=https://...
AZURE_OPENAI_4O_API_KEY=...
AZURE_OPENAI_GPT4O_DEPLOYMENT=gpt-4o
AZURE_OPENAI_4O_API_VERSION=2025-01-01-preview

# Alternative models
AZURE_OPENAI_NANO_DEPLOYMENT=gpt-4.1-nano
AZURE_OPENAI_O1_DEPLOYMENT=o1
AZURE_OPENAI_O4_MINI_DEPLOYMENT=o4-mini
```

---

## Notes

### Embeddings Not Available
The `text-embedding-3-small` deployment doesn't exist in your Azure account. This is **optional** - agents can work without embeddings using keyword-based similarity fallback.

To add embeddings (optional):
1. Create an embedding deployment in Azure Portal
2. Add to .env: `AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-deployment-name`

### Vision Support
✅ GPT-4o supports vision - can analyze images and videos for the cube world benchmark.

### Cost Optimization
- Use `gpt-4.1-nano` for simple queries (faster, cheaper)
- Use `gpt-4o` for vision and complex reasoning
- Use `o1`/`o4-mini` for reasoning tasks

---

## Troubleshooting

### "Configuration incomplete" error
Check that these env vars are set:
- `AZURE_OPENAI_4O_ENDPOINT`
- `AZURE_OPENAI_4O_API_KEY`
- `AZURE_OPENAI_GPT4O_DEPLOYMENT`

### "DeploymentNotFound" error
The deployment name in .env doesn't match Azure. Check Azure Portal for actual deployment names.

### Import errors
Make sure venv is activated:
```bash
source venv/bin/activate
```

---

## Summary

✅ **Azure OpenAI API is configured and tested**
✅ **Chat completion working** (gpt-4o, gpt-4.1-nano)
✅ **Vision support available**
✅ **Integrated with agent utilities**
⚠️  **Embeddings optional** (deployment not found, using fallback)

**Ready to run agent experiments!**
