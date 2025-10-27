# API Key Setup Guide

## Current Status

The Gemini API key in `.env` is currently **INVALID** or **REVOKED**.

## Error Message
```
400 INVALID_ARGUMENT. API Key not found. Please pass a valid API key.
Reason: API_KEY_INVALID
```

## Possible Causes

1. **Key Revoked**: The API key may have been manually revoked in Google AI Studio
2. **Key Expired**: Some API keys have expiration dates
3. **Billing Issues**: The key may be disabled due to billing concerns (related to the £18 charge)
4. **Account Suspended**: The Google Cloud/AI Studio account may be temporarily suspended

## How to Fix

### Option 1: Get a New Google AI Studio API Key (Free Tier)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click on "Get API Key" in the left sidebar
4. Create a new API key or copy an existing valid one
5. Replace the key in `.env`:
   ```bash
   GEMINI_KEY=your_new_api_key_here
   ```

### Option 2: Use Google Cloud Project API Key (Production)

If you want to use a production Google Cloud project with billing:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the "Generative Language API"
4. Go to "APIs & Services" > "Credentials"
5. Create a new API key
6. Restrict the key to "Generative Language API" for security
7. Update `.env` with the new key

### Option 3: Check Your Current Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Go to "API Keys" section
3. Check if your current key is listed and active
4. If it shows as "Revoked" or "Expired", create a new one

## Testing Your New Key

After updating the `.env` file, test it:

```bash
source venv/bin/activate
python test_api_key.py
```

Expected output:
```
API Key loaded: AIzaSy...
Initializing client...
Making test API call to Gemini...
SUCCESS! Response: Hello
```

## Cost Concerns

Based on your earlier concern about the £18 charge:

1. **Our code usage**: The LLM world generator makes approximately 10-20 API calls total for a full test suite
   - Estimated cost: **< $0.01** (less than one penny)

2. **If you're seeing high charges**, it's likely from:
   - Other projects using the same API key
   - Video generation (Veo) which is more expensive
   - Accidental loops or repeated calls
   - API key leakage (someone else using your key)

3. **To prevent future high charges**:
   - Set up billing alerts in Google Cloud Console
   - Use API quotas to limit daily spending
   - Regularly rotate API keys
   - Review API usage in Google Cloud Console

## Quick Summary

**What needs to be done**: Get a new valid Gemini API key from Google AI Studio and update the `.env` file.

**Current blockers**: Cannot test the LLM World Generator until a valid API key is configured.

**Once fixed**: All the code is ready to go - just need the valid key!
