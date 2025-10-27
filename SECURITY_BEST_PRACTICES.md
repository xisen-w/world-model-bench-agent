# Security Best Practices - NEVER PUSH API KEYS TO GITHUB!

## What Went Wrong

**YOU PUSHED `.env` WITH API KEY TO GITHUB** ⚠️

This is why:
1. Your original API key was **revoked automatically** by Google
2. The £18 charge was likely someone using your **exposed public key**
3. GitHub crawlers and bots scan for exposed API keys **within minutes**

## Current Status

✅ New API key added to `.env`
✅ `.env` and `.env.bak` removed from git tracking
✅ Updated `.gitignore` to prevent future leaks

## Critical Actions After Exposing a Key

### 1. Revoke Exposed Key Immediately
- Go to [Google AI Studio](https://aistudio.google.com/)
- Delete the old exposed key: `AIzaSyByX8P1feCnSCPInKZyxJK8DZ3MGy1yI60`
- Create a new key (which you already did!)

### 2. Clean Git History

Even though you removed `.env` from tracking, it's **still in git history**!

**Option A: If you haven't pushed to remote yet**
```bash
# Just commit the removal
git commit -m "chore: remove .env files from tracking"
```

**Option B: If already pushed to GitHub (URGENT)**
```bash
# Use BFG Repo-Cleaner to remove from history
brew install bfg

# Remove .env from ALL commits
bfg --delete-files .env --delete-files .env.bak

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (rewrites history!)
git push --force
```

**Option C: Use git filter-branch (alternative)**
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env .env.bak" \
  --prune-empty --tag-name-filter cat -- --all

git push --force
```

### 3. Check GitHub Secret Scanning

GitHub automatically scans for exposed secrets:
- Check your email for notifications
- Check: https://github.com/[your-username]/[repo-name]/security
- GitHub may have already flagged it

### 4. Verify No Other Secrets

```bash
# Search for other potential secrets in git history
git log --all --full-history --source -S "AIzaSy"
git log --all --full-history --source -S "GEMINI_KEY"
```

## Best Practices Going Forward

### 1. Always Use .gitignore

```gitignore
# Never commit these
.env
.env.*
*.env
*_key.json
*_credentials.json
secrets/
credentials/
```

### 2. Use Environment Variables

**Production**:
```bash
# Set in your deployment platform
export GEMINI_KEY="your_key"
```

**Development**:
```bash
# Load from .env (which is gitignored)
source .env  # or use python-dotenv
```

### 3. Use .env.example Template

Create `.env.example` (safe to commit):
```bash
# .env.example
GEMINI_KEY=your_api_key_here
```

Then users copy it:
```bash
cp .env.example .env
# Then edit .env with real key
```

### 4. Pre-commit Hooks

Install a pre-commit hook to prevent accidental commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -E "\.env$"; then
    echo "ERROR: Attempting to commit .env file!"
    echo "This file contains secrets and should never be committed."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 5. Use Secret Management Tools

For production:
- **Google Secret Manager** (if using GCP)
- **AWS Secrets Manager** (if using AWS)
- **HashiCorp Vault**
- **1Password** / **Bitwarden** for team sharing

## How to Detect Leaked Keys

### GitHub Alerts
- GitHub will email you if they detect exposed secrets
- Check: Settings → Security → Vulnerability alerts

### Scan Manually
```bash
# Use gitleaks to scan for secrets
brew install gitleaks
gitleaks detect --source . --verbose
```

### Check Git History
```bash
# Search for API key patterns
git log -p | grep -E "AIzaSy[A-Za-z0-9_-]{33}"
```

## Cost Protection

To prevent future high charges:

### 1. Set Billing Alerts
- Google Cloud Console → Billing → Budgets & alerts
- Set alert at £5, £10, £15

### 2. Set API Quotas
- Google Cloud Console → APIs & Services → Quotas
- Limit daily requests

### 3. Use API Key Restrictions
- Restrict key to specific APIs only
- Restrict by IP address (if possible)
- Restrict by HTTP referrer (for web apps)

### 4. Rotate Keys Regularly
- Generate new key every 3-6 months
- Revoke old keys immediately after rotation

## What You Should Do RIGHT NOW

1. ✅ **DONE**: New API key in `.env`
2. ✅ **DONE**: Removed `.env` from git tracking
3. ✅ **DONE**: Updated `.gitignore`
4. ⚠️ **TODO**: Revoke old exposed key at Google AI Studio
5. ⚠️ **TODO**: Clean git history if already pushed to GitHub
6. ⚠️ **TODO**: Set up billing alerts in Google Cloud Console
7. ⚠️ **TODO**: Check if repository is public or private on GitHub

## Testing New Key

Let's verify the new key works:
```bash
python test_api_key.py
```

If it works, you're good to go!

## Summary

**The Problem**: Exposed API keys in public repositories are automatically found and abused
**The Solution**: Never commit secrets, always use .gitignore, clean git history
**Prevention**: Pre-commit hooks, secret scanning, regular key rotation

**Remember**: Git history is permanent unless you rewrite it! Even deleted files remain in history.
