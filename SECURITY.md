# Security Best Practices

## 🔐 Protecting Your Credentials

### API Keys & Secrets

**NEVER commit these to git:**
- API keys (OpenRouter, Anthropic, OpenAI, etc.)
- Tenderly access keys
- RPC URLs with embedded keys
- Private keys or mnemonics
- Access tokens

### ✅ Safe Configuration Methods

**Option 1: Environment Variables (Recommended)**
```bash
# In your shell profile (~/.bashrc, ~/.zshrc)
export LLM_API_KEY="sk-..."
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_MODEL="gpt-4"
export TENDERLY_ACCESS_KEY="..."
```

**Option 2: Local Config File (Gitignored)**
```bash
# Create config (already in .gitignore)
~/.ai-crypto-toolkit/config.yaml

# This directory is NEVER committed:
.ai-crypto-toolkit/
config.yaml
*.local.yaml
.env
.env.local
```

**Option 3: .env File (Gitignored)**
```bash
# Create .env in project root (already in .gitignore)
echo "LLM_API_KEY=sk-..." > .env
echo "LLM_API_BASE=https://..." >> .env

# Load with:
export $(cat .env | xargs)
```

### 🚫 What's Already Protected

The `.gitignore` already excludes:
- `.ai-crypto-toolkit/` - Your local database and config
- `config.yaml` - Local configuration
- `*.local.yaml` - Local overrides
- `.env` and `.env.local` - Environment files

### 📝 Example Configs (Safe to Commit)

These files are safe because they use placeholders:
- `config/config.example.yaml` - Template with dummy values
- `README.md` - Examples use placeholders like `YOUR_KEY`
- Documentation - Shows structure, not real keys

### 🔍 How to Check If You Leaked Something

```bash
# Search git history for potential secrets
git log --all --full-history -S "sk-" --source --pretty=format:"%H %s"
git grep -i "api.*key" HEAD | grep -v "api_key:"

# If you find a leak, see "Removing Leaked Secrets" below
```

### 🆘 If You Accidentally Committed a Secret

**Immediate steps:**
1. **Revoke the key immediately** (regenerate on the service)
2. **Don't just delete the file** - it's still in git history!

**To remove from history:**
```bash
# WARNING: This rewrites history - coordinate with team first!

# Option 1: BFG Repo-Cleaner (easiest)
brew install bfg
bfg --replace-text passwords.txt repo.git

# Option 2: git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGER!)
git push origin --force --all
git push origin --force --tags
```

**Better approach: Treat the key as compromised and rotate it.**

### 🎯 Best Practices

1. **Use environment variables for production**
2. **Use local config files for development**
3. **Never hardcode secrets in code**
4. **Always check before committing:**
   ```bash
   git diff --cached | grep -i "sk-\|api.*key\|secret"
   ```
5. **Use git hooks to prevent commits with secrets:**
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   if git diff --cached | grep -E "(sk-|secret|password)" | grep -v "# Example"; then
       echo "⚠️  Potential secret detected! Commit blocked."
       exit 1
   fi
   chmod +x .git/hooks/pre-commit
   ```

### 🔒 Production Security

For production deployments:

**Use secrets managers:**
- AWS Secrets Manager
- HashiCorp Vault
- GitHub Secrets (for CI/CD)
- Kubernetes Secrets
- Doppler

**Example with GitHub Actions:**
```yaml
- name: Run analysis
  env:
    LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
    TENDERLY_KEY: ${{ secrets.TENDERLY_KEY }}
  run: |
    ai-crypto audit contracts/*.sol
```

### 📊 Security Checklist

Before pushing:
- [ ] No API keys in committed files
- [ ] No secrets in environment examples
- [ ] `.gitignore` includes all sensitive patterns
- [ ] Local config files are gitignored
- [ ] Database file (`.ai-crypto-toolkit/`) is gitignored
- [ ] Example configs use placeholders only

### 🤝 Sharing Config Safely

When sharing configurations:

**❌ Don't:**
```yaml
llm:
  api_key: "sk-or-v1-8512b197b2f754d52803..."  # NEVER!
```

**✅ Do:**
```yaml
llm:
  api_key: "your-api-key-here"  # Placeholder
  # Or use environment variable:
  # export LLM_API_KEY="sk-..."
```

### 🔐 API Key Security by Provider

**OpenRouter:**
- Rotate keys regularly
- Monitor usage at https://openrouter.ai/activity
- Set spending limits
- Use separate keys per project

**Local LLMs:**
- No keys needed!
- Use dummy values: `api_key: "dummy-key"`
- Still protect RPC URLs if they have keys

**Tenderly:**
- Protect access keys
- Use project-specific keys
- Enable webhook signatures
- Rotate after team changes

### 📚 Additional Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [git-secrets tool](https://github.com/awslabs/git-secrets)

---

**Remember:** The best way to handle secrets is to never commit them in the first place!

If you're unsure, use environment variables. They're already supported by the toolkit and are the safest option.
