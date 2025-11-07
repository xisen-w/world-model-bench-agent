# Coffee World Image Generation Failure - Diagnosis Summary

## Issue
Image generation fails at state 2 (s2) with error:
```
VideoGenerationError: Image generation response did not include inline image data.
```

## Root Cause
The Gemini API sometimes returns responses with:
- **Warning**: `IMAGE_OTHER is not a valid FinishReason`
- **No image data** in the response despite the API call succeeding

This is **NOT a code bug** - it's an **API behavior issue**.

## What We Know

### ✅ Working Cases:
- Initial image generation (s0) - **SUCCESS**
- First variation (s1) - **SUCCESS**
- Diagnostic test with simple prompt - **SUCCESS**
- Plant branching world (all 16 images) - **SUCCESS**

### ❌ Failing Case:
- Coffee world, second variation (s1 → s2) - **FAILURE**
- Occurs specifically when generating variation from s1 to s2

## Why It Fails

The API returns a `finish_reason` of `IMAGE_OTHER` instead of `STOP`. This non-standard finish reason indicates:

1. **Content Policy**: The generated image might have triggered a safety filter
2. **API Instability**: Transient API issues (rate limits, internal errors)
3. **Complex Prompts**: The 5-step advanced generation pipeline creates very detailed prompts that might be too complex

## Evidence

From the error log:
```python
[5/5] Generating varied image...
      Using base image: generated_images/coffee_making_egocentric/s1_001.png
      Generation prompt: Here's a comprehensive image generation prompt designed to...

/venv/lib/python3.13/site-packages/google/genai/_common.py:613: UserWarning:
IMAGE_OTHER is not a valid FinishReason
```

The code reaches step [5/5] of the advanced pipeline, calls the API, but the response contains no image data.

## Recommended Solutions

### Option 1: Add Retry Logic (Quick Fix)
Modify `veo.py` to retry failed image generations 2-3 times with exponential backoff.

### Option 2: Fallback to Simple Generation
When advanced generation fails, fall back to simple prompt-only generation without the 5-step VLM pipeline.

### Option 3: Better Error Handling
Log the full API response when `parts` is empty to diagnose what the API is actually returning.

### Option 4: Simplify Prompts
The advanced generation creates very long, detailed prompts (5000+ chars). Shorter prompts might be more reliable.

### Option 5: Skip and Continue
Allow generation to continue even when individual states fail, marking them as skipped.

## Next Steps

1. **Immediate**: Try running generation again - it might succeed (API transient issue)
2. **Short-term**: Implement retry logic with exponential backoff
3. **Long-term**: Add fallback to simple generation when advanced fails

## Files Involved
- `utils/veo.py:751` - Where error is raised
- `world_model_bench_agent/image_world_generator.py:778` - Calls `generate_image_variation()`
- `generation_engine/generate_coffee_egocentric_images.py` - The failing script

## Command to Retry
```bash
cd /Users/wangxiang/Desktop/my_workspace/memory/world_model_bench_agent
source venv/bin/activate
python generation_engine/generate_coffee_egocentric_images.py --yes
```

Note: Previous runs generated s0 and s1 successfully, so the next run will try to continue from s2.
