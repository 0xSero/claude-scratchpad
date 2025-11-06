# Quick Start Guide

Get up and running with AI Crypto Toolkit in 5 minutes.

## Prerequisites

1. **Local LLM server running** (vLLM, TabbyAPI, LM Studio, etc.)
2. **Python 3.10+**
3. **Git**

## Installation

```bash
# Clone the repo
git clone https://github.com/0xSero/ai-crypto-toolkit.git
cd ai-crypto-toolkit

# Install
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Configuration

### Option 1: Environment Variables (Quickest)

```bash
export LLM_API_BASE="http://localhost:8000/v1"
export LLM_MODEL="Qwen/Qwen2.5-Coder-32B-Instruct"
```

### Option 2: Config File (Recommended)

```bash
# Create default config
ai-crypto init

# Edit ~/.ai-crypto-toolkit/config.yaml
# Update api_base and model to match your setup
```

### Option 3: Use Example Config

```bash
cp config/config.example.yaml ~/.ai-crypto-toolkit/config.yaml
# Edit ~/.ai-crypto-toolkit/config.yaml
```

## Test Your Setup

```bash
# Test LLM connection
ai-crypto test

# Should see: "✓ Connection successful!"
```

## Your First Analysis

```bash
# Analyze a contract
ai-crypto analyze examples/SecureToken.sol

# Audit for security issues
ai-crypto audit examples/VulnerableBank.sol

# Find gas optimizations
ai-crypto optimize examples/VulnerableBank.sol

# Explain a transaction (requires Ethereum RPC)
ai-crypto tx 0x1234... --network ethereum
```

## Common Issues

### "Connection failed"

**Problem**: Can't connect to LLM API

**Solutions**:
1. Check your LLM server is running: `curl http://localhost:8000/v1/models`
2. Verify `api_base` in config matches your server
3. Try a different port (8000, 5000, 1234, 8080 are common)

### "Model not found"

**Problem**: LLM API doesn't recognize model name

**Solutions**:
1. Check available models: `curl http://localhost:8000/v1/models`
2. Update `model` in config to match exactly
3. Some servers use short names like "default" or just the model size

### "Timeout"

**Problem**: LLM taking too long to respond

**Solutions**:
1. Increase timeout in config: `timeout: 600`
2. Use a smaller model or quantization
3. Increase context length limit if model is being cut off

## Local LLM Setup Recommendations

### Best Models for This Toolkit

| Model | Size | Strengths |
|-------|------|-----------|
| Qwen2.5-Coder-32B | 32B | Best overall, great at code analysis |
| DeepSeek-Coder-33B | 33B | Excellent security vulnerability detection |
| CodeLlama-70B | 70B | Good explanations, needs more VRAM |
| Qwen2.5-14B | 14B | Good budget option, fast |

### Server Recommendations

**vLLM** (Recommended for performance)
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-Coder-32B-Instruct \
    --port 8000 \
    --max-model-len 8192
```

**TabbyAPI** (Great for quantized models)
```bash
# See: https://github.com/theroyallab/tabbyAPI
# Good for running Q4/Q6 quantized models efficiently
```

**LM Studio** (Easiest setup)
- Download from lmstudio.ai
- Load any GGUF model
- Start local server (default port 1234)
- Set `api_base: "http://localhost:1234/v1"`

## Your Hardware

With your 4×3090 setup (144GB VRAM total), you can run:
- Qwen2.5-Coder-32B-Instruct at FP16 (full precision) - ~64GB
- DeepSeek-Coder-33B at FP16 - ~66GB
- CodeLlama-70B at Q6 quantization - ~55GB
- Multiple smaller models simultaneously for different tasks

Recommended setup:
```bash
# Use vLLM for best throughput
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
    --tensor-parallel-size 2 \  # Use 2 GPUs
    --port 8000
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [examples/](examples/) for test contracts
- Check [docs/](docs/) for advanced usage
- Customize security checks in config

## Tips for Best Results

1. **Be specific**: Add context with `--context` flag when needed
2. **Iterate**: Run multiple analyses from different angles
3. **Verify**: Always review AI suggestions - they're tools, not oracles
4. **Customize**: Fine-tune prompts in `src/ai_crypto_toolkit/llm/prompts.py` for your use case
5. **Share**: If you find good patterns or prompts, contribute them back!

## Getting Help

- Check [GitHub Issues](https://github.com/0xSero/ai-crypto-toolkit/issues)
- Read the docs in [docs/](docs/)
- Review example contracts in [examples/](examples/)

---

Built with ⚡ by [@0x_Sero](https://twitter.com/0x_Sero)
