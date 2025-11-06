# AI Crypto Toolkit - Complete Feature List

Comprehensive smart contract analysis powered by **your local LLMs**.

## Core Capabilities

### 1. Smart Contract Analysis (`ai-crypto analyze`)

Deep code understanding with AI:
- Explains contract purpose and architecture
- Identifies design patterns (ERC20, upgradeable, proxy, etc.)
- Maps key functions and their interactions
- Highlights potential edge cases
- Suggests improvements

**Best For**: Understanding new codebases, onboarding developers, documentation

### 2. Security Auditing (`ai-crypto audit`)

Multi-layer vulnerability detection:

**Quick Pattern Checks** (Instant)
- Reentrancy risks (external calls before state updates)
- tx.origin authentication
- Unchecked delegatecall
- Missing return value checks
- Unsafe arithmetic (pre-0.8.0)

**Deep AI Analysis** (Using your LLM)
- Context-aware vulnerability detection
- Severity classification (HIGH/MEDIUM/LOW/INFO)
- Exact line numbers and code snippets
- Exploitation scenarios
- Concrete fixes with code examples
- SWC references

**Best For**: Pre-deployment security review, competitive audits, learning secure patterns

### 3. Transaction Analysis (`ai-crypto tx`)

Decode and explain on-chain activity:
- Fetches transaction data from any EVM chain
- Decodes calldata and internal calls
- Explains intent in plain English
- Identifies contract interactions
- Calculates effective prices and gas costs
- Detects MEV and sandwich attacks

**Best For**: Investigating suspicious transactions, debugging failed txs, understanding protocols

### 4. Gas Optimization (`ai-crypto optimize`)

Find and quantify savings:
- Storage optimization opportunities
- Loop efficiency improvements
- Function visibility optimizations
- Data location recommendations (calldata vs memory)
- Arithmetic optimization patterns
- Packing and caching strategies

**Calculates**: Gas saved, USD cost at different gas prices, percentage improvements

**Best For**: Pre-deployment optimization, cost reduction for high-volume contracts

### 5. AI-Powered Fuzzing (`ai-crypto fuzz`) 🆕

Combines automated testing with AI analysis:

**Integrations**:
- **Echidna**: Property-based fuzzing for Solidity
- **Foundry**: Fuzz testing framework

**What It Does**:
1. Runs fuzzer (Echidna/Foundry) on your contract
2. Collects failures and counterexamples
3. Uses AI to analyze root causes
4. Explains vulnerabilities in plain English
5. Suggests concrete fixes
6. Recommends better invariants

**Best For**: Finding edge cases, testing invariants, catching logic bugs

### 6. Property Test Generation (`ai-crypto gentest`) 🆕

Auto-generate comprehensive test suites:

**Generates Tests For**:
- Balance invariants
- Access control rules
- State consistency checks
- Mathematical properties
- Edge cases and boundaries

**Supports**:
- Echidna property format
- Foundry fuzz test format

**Best For**: Starting test suites, improving coverage, learning property-based testing

## Configuration & Setup

### Supported LLM Backends

Works with any OpenAI-compatible API:

| Backend | Setup Difficulty | Performance | Quantization Support |
|---------|------------------|-------------|---------------------|
| **vLLM** | Medium | Excellent | Limited |
| **TabbyAPI** | Medium | Good | Excellent |
| **LM Studio** | Easy | Good | Good |
| **llama.cpp** | Easy | Fair | Excellent |
| **Text Generation WebUI** | Easy | Fair | Excellent |

### Recommended Models

| Use Case | Model | Size | Why |
|----------|-------|------|-----|
| Best Overall | Qwen2.5-Coder-32B | 32B | Top code understanding + security |
| Security Focus | DeepSeek-Coder-33B | 33B | Excellent vulnerability detection |
| Budget Option | Qwen2.5-14B | 14B | Fast, good quality |
| Maximum Quality | CodeLlama-70B | 70B | Best explanations (needs more VRAM) |

### Hardware Requirements

**Minimum** (for 14B models):
- 24GB VRAM (single 3090/4090)
- 32GB RAM
- 100GB storage

**Recommended** (for 32B models):
- 48GB+ VRAM (2x3090, 2x4090)
- 64GB RAM
- 200GB storage

**Your Setup** (4x3090 = 96GB VRAM):
- Perfect for 32B models at full precision
- Can run 70B models with quantization
- Can run multiple models simultaneously

## Output Formats

All commands support:
- **Terminal**: Rich formatted output with colors and tables
- **Streaming**: Real-time responses for long analyses
- **Markdown**: Copy-paste ready for documentation
- **JSON**: (Coming soon) Machine-readable output

## Configuration Options

### LLM Settings

```yaml
llm:
  api_base: "http://localhost:8000/v1"
  model: "Qwen/Qwen2.5-Coder-32B-Instruct"
  temperature: 0.1          # Lower = more deterministic
  max_tokens: 4000          # Increase for large contracts
  timeout: 300              # Seconds before timeout
  stream: true              # Real-time output
```

### Security Settings

```yaml
security:
  check_reentrancy: true
  check_overflow: true
  check_access_control: true
  check_delegatecall: true
  check_tx_origin: true
  check_unchecked_calls: true
  custom_patterns: []       # Your regex patterns
```

### Ethereum Settings

```yaml
ethereum:
  rpc_url: "http://localhost:8545"
  # Or: "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
  timeout: 30
```

## Advanced Usage

### Chaining Commands

```bash
# Full analysis pipeline
ai-crypto analyze contract.sol
ai-crypto audit contract.sol --severity high
ai-crypto optimize contract.sol
ai-crypto fuzz contract.sol --tool echidna
```

### Custom Context

```bash
# Add context for better analysis
ai-crypto analyze contract.sol --context "This is a staking contract for an NFT project"

# Specific security focus
ai-crypto audit contract.sol --context "Focus on MEV risks and sandwich attacks"
```

### Batch Processing

```bash
# Analyze multiple contracts
for contract in contracts/*.sol; do
    ai-crypto audit "$contract" --severity high > "reports/$(basename $contract .sol).md"
done
```

### Output Redirection

```bash
# Save to files
ai-crypto analyze contract.sol > analysis.md
ai-crypto audit contract.sol 2>&1 | tee audit-log.txt
```

## Extending the Toolkit

### Custom Security Patterns

Add regex patterns for domain-specific checks:

```yaml
security:
  custom_patterns:
    - 'flashLoan\([^)]*\).*transfer'  # Flash loan + transfer pattern
    - 'selfdestruct\('                 # Selfdestruct usage
```

### Custom Prompts

Edit `src/ai_crypto_toolkit/llm/prompts.py`:

```python
SYSTEM_PROMPTS["defi"] = """You are a DeFi security expert.
Focus on MEV, oracle manipulation, and economic attacks."""
```

### Plugin Architecture (Coming Soon)

```python
# ~/.ai-crypto-toolkit/plugins/mev_detector.py
from ai_crypto_toolkit.analyzers import Analyzer

class MEVDetector(Analyzer):
    def analyze(self, contract):
        # Your custom analysis
        pass
```

## Performance Tips

### Speed Up Analysis

1. **Use streaming**: Set `stream: true` for faster perceived response
2. **Reduce temperature**: `temperature: 0.0` for fastest inference
3. **Quantization**: Use Q4 or Q6 quantized models for 2-3x speedup
4. **Batch API calls**: Analyze multiple contracts in parallel
5. **Use vLLM**: Fastest inference server for production use

### Optimize VRAM Usage

```bash
# Multiple GPUs with tensor parallelism
vllm serve model --tensor-parallel-size 2

# Smaller context window (if contracts are small)
vllm serve model --max-model-len 4096
```

## Comparison with Other Tools

| Tool | Static Analysis | Dynamic Testing | AI Analysis | Local |
|------|----------------|-----------------|-------------|-------|
| **AI Crypto Toolkit** | ✅ | ✅ (via fuzzing) | ✅ | ✅ |
| Slither | ✅ | ❌ | ❌ | ✅ |
| Mythril | ✅ | ✅ (symbolic) | ❌ | ✅ |
| Echidna | ❌ | ✅ | ❌ | ✅ |
| OpenZeppelin Defender | ✅ | ❌ | ❌ | ❌ |
| Trail of Bits Review | ✅ | ✅ | ✅ | ❌ (manual) |

**Unique Advantages**:
- Only tool combining fuzzing + AI analysis
- Fully local (no data leaves your machine)
- Generates property tests automatically
- Explains findings in plain English
- Extensible and hackable

## Use Cases

### 1. Independent Audit Preparation
Run comprehensive analysis before paying for professional audit:
```bash
ai-crypto audit contract.sol > pre-audit.md
ai-crypto fuzz contract.sol --tool echidna > fuzzing-results.md
```

### 2. Code Review Assistance
Understand unfamiliar codebases quickly:
```bash
ai-crypto analyze complex-protocol.sol --context "DeFi lending protocol"
```

### 3. Competitive Auditing
Speed up bug hunting in contests:
```bash
ai-crypto audit --severity high target.sol
```

### 4. Learning Resource
Study security patterns and best practices:
```bash
ai-crypto audit examples/VulnerableBank.sol  # See what's wrong
ai-crypto audit examples/SecureToken.sol      # See what's right
```

### 5. CI/CD Integration
Automated security checks in your pipeline:
```bash
# .github/workflows/security.yml
- name: AI Security Audit
  run: ai-crypto audit contracts/*.sol --severity high
```

## Limitations & Best Practices

### Known Limitations

1. **AI is not deterministic**: Different runs may give slightly different results
2. **Context window**: Very large contracts may need to be split
3. **No formal verification**: AI analysis complements but doesn't replace formal methods
4. **Local model quality**: Results depend on your model choice

### Best Practices

1. **Always verify**: Review AI suggestions before implementing
2. **Use multiple tools**: Combine with Slither, Mythril, manual review
3. **Iterate**: Run analysis multiple times from different angles
4. **Add context**: Help the AI with relevant information
5. **Test generated code**: Always test AI-generated fixes and tests
6. **Keep models updated**: Newer models often perform better

## Roadmap

### Coming Soon
- [ ] Multi-chain support (Arbitrum, Optimism, Polygon, etc.)
- [ ] Contract diffing (compare versions)
- [ ] Historical vulnerability database
- [ ] JSON output format
- [ ] VS Code extension
- [ ] Automated fix application (with confirmation)

### Future Plans
- [ ] Web UI (optional, CLI-first always)
- [ ] Integration with Foundry/Hardhat
- [ ] Fine-tuned models for security
- [ ] Collaborative analysis (multi-agent)
- [ ] Real-time monitoring mode

## Getting Help

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Configuration**: See [config/config.example.yaml](config/config.example.yaml)
- **Examples**: See [examples/](examples/)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/0xSero/ai-crypto-toolkit/issues)

---

Built with ⚡ by [@0x_Sero](https://twitter.com/0x_Sero)

*"Your hardware. Your models. Your rules."*
