# Contributing to AI Crypto Toolkit

First off, thanks for taking the time to contribute! 🎉

This toolkit gets better when builders share their expertise.

## How to Contribute

### Reporting Bugs

If you find a bug:
1. Check if it's already reported in [Issues](https://github.com/0xSero/ai-crypto-toolkit/issues)
2. If not, open a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, LLM model, OS)
   - Sample contract (if applicable)

### Suggesting Features

Have an idea? Great!
1. Check existing issues first
2. Open a new issue tagged `enhancement`
3. Describe:
   - The use case
   - Why it would be valuable
   - How you envision it working
   - Examples if applicable

### Contributing Code

#### Quick Wins (Good First Contributions)

- Add more security patterns to `llm/prompts.py`
- Improve error messages
- Add more example contracts
- Write tests
- Improve documentation
- Add support for more networks/chains

#### Larger Contributions

- New analyzers (e.g., DeFi-specific, MEV detection)
- Multi-chain support
- Integration with Foundry/Hardhat
- Web UI (optional - CLI first always!)
- Fine-tuning scripts for security models

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-crypto-toolkit.git
cd ai-crypto-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/

# Type check
mypy src/
```

#### Code Style

- Use [Black](https://black.readthedocs.io/) for formatting (line length 100)
- Use [Ruff](https://beta.ruff.rs/) for linting
- Add type hints (we use mypy)
- Write docstrings for public functions
- Keep functions focused and testable

#### Pull Request Process

1. **Fork** the repo
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** if applicable
5. **Run the test suite**: `pytest`
6. **Format your code**: `black src/ && ruff check src/`
7. **Commit** with clear messages:
   ```
   Add support for Optimism network

   - Add Optimism RPC config
   - Update transaction analyzer for L2 specifics
   - Add example L2 transaction
   ```
8. **Push** to your fork
9. **Open a PR** with:
   - Clear description of what you changed
   - Why you changed it
   - How to test it
   - Screenshots if UI-related

### Improving Prompts

Prompts are in `src/ai_crypto_toolkit/llm/prompts.py`.

If you find better prompts:
1. Test them with multiple models (ideally 3+)
2. Compare results with the existing prompts
3. Submit a PR with examples showing improvement

Good prompt contributions:
- More specific vulnerability detection
- Better gas optimization suggestions
- Clearer explanations
- Model-specific optimizations

### Adding Security Patterns

Found a vulnerability pattern that should be detected?

Edit `llm/prompts.py`:
```python
VULNERABILITY_PATTERNS = {
    "your_pattern": {
        "pattern": r"regex_pattern_here",
        "description": "What this detects",
    },
}
```

### Documentation

Documentation improvements are always welcome:
- Fix typos
- Clarify confusing sections
- Add examples
- Improve setup instructions
- Add troubleshooting tips

### Community

- Be respectful and constructive
- Help others in issues and discussions
- Share your findings and improvements
- Give credit where due

## Architecture Overview

```
ai-crypto-toolkit/
├── src/ai_crypto_toolkit/
│   ├── cli.py              # Main CLI (Click commands)
│   ├── config.py           # Configuration handling
│   ├── analyzers/          # Analysis modules
│   │   ├── contract.py     # Contract analysis
│   │   ├── security.py     # Security auditing
│   │   ├── gas.py          # Gas optimization
│   │   └── transaction.py  # Transaction analysis
│   ├── llm/                # LLM integration
│   │   ├── client.py       # API client
│   │   └── prompts.py      # Prompt templates
│   └── utils/              # Utilities
├── examples/               # Example contracts
├── config/                 # Config templates
└── tests/                  # Tests
```

### Key Design Principles

1. **Local First**: Always support local/self-hosted over cloud
2. **CLI First**: Terminal is primary interface, UI optional
3. **Extensible**: Plugin architecture for custom analyzers
4. **Fast**: Async where possible, streaming by default
5. **Practical**: Optimize for real use cases, not demos

## Testing

We value tests but don't let them block useful contributions.

Priority:
1. Core functionality (config, LLM client, CLI)
2. Analysis logic (security patterns, gas detection)
3. Edge cases and error handling

Run tests:
```bash
pytest                    # All tests
pytest tests/test_cli.py  # Specific file
pytest -v                 # Verbose
pytest -k security        # Tests matching pattern
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v0.x.0`
4. Push: `git push origin v0.x.0`
5. Create GitHub release
6. (Optional) Publish to PyPI

## Questions?

- Open a [Discussion](https://github.com/0xSero/ai-crypto-toolkit/discussions)
- DM [@0x_Sero](https://twitter.com/0x_Sero) on X
- Check existing docs and issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thanks for contributing! 🚀

*"If it doesn't compound, pivot quickly and keep the artifact."*
