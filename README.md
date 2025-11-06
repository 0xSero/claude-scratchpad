# AI Crypto Toolkit

A powerful CLI toolkit for analyzing smart contracts, auditing security, and understanding blockchain transactions using **your local LLM setup**. Built for developers who value independence and want AI assistance without corporate dependencies.

## Why This Exists

After the great "unlimited plan" rug-pull of 2024, this toolkit gives you full control. Use your own hardware, your own models, your own rules.

## Features

🔍 **Smart Contract Analysis**
- Explain contract logic in plain English
- Identify potential issues and edge cases
- Understand complex inheritance and delegate calls

🛡️ **Security Auditing**
- Scan for common vulnerabilities (reentrancy, overflow, etc.)
- Custom vulnerability patterns
- AI-powered threat analysis using your local models

💰 **Transaction Analysis**
- Decode complex transaction calldata
- Explain what a transaction actually does
- Trace internal calls and state changes

⚡ **Gas Optimization**
- Identify expensive operations
- Suggest optimization patterns
- Compare before/after estimates

🔬 **AI-Powered Fuzzing** (NEW!)
- Integrates with Echidna and Foundry fuzzers
- AI analyzes fuzzing failures and suggests fixes
- Auto-generate property tests from contract analysis
- Explain vulnerabilities found by fuzzers in plain English

🤖 **Local AI First**
- Works with any OpenAI-compatible API (vLLM, TabbyAPI, LM Studio, etc.)
- Optimized prompts for code analysis
- Streaming support for real-time feedback
- No external dependencies - your models, your data

## Quick Start

```bash
# Install
pip install -e .

# Configure (point to your local LLM)
export LLM_API_BASE="http://localhost:8000/v1"
export LLM_MODEL="your-model-name"

# Analyze a contract
ai-crypto analyze contract.sol

# Audit for vulnerabilities
ai-crypto audit contract.sol --severity high

# Explain a transaction
ai-crypto tx 0x1234...5678 --network ethereum

# Get gas optimization suggestions
ai-crypto optimize contract.sol

# Run AI-powered fuzzing
ai-crypto fuzz contract.sol --tool echidna

# Generate property tests with AI
ai-crypto gentest contract.sol --tool foundry -o test/Properties.t.sol
```

## Installation

```bash
# Clone
git clone https://github.com/0xSero/ai-crypto-toolkit.git
cd ai-crypto-toolkit

# Install with all dependencies
pip install -e ".[dev]"

# Or just core dependencies
pip install -e .
```

## Configuration

Create `~/.ai-crypto-toolkit/config.yaml`:

```yaml
llm:
  api_base: "http://localhost:8000/v1"
  model: "Qwen/Qwen2.5-Coder-32B-Instruct"
  temperature: 0.1
  max_tokens: 4000
  timeout: 300

ethereum:
  rpc_url: "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"

security:
  check_reentrancy: true
  check_overflow: true
  check_access_control: true
  check_delegatecall: true
  custom_patterns: []
```

## Usage Examples

### Analyze a Contract

```bash
ai-crypto analyze contracts/MyToken.sol
```

Output:
```
📝 Contract Analysis: MyToken.sol

🎯 Overview:
This is an ERC20 token implementation with the following features:
- Standard transfer/approve/transferFrom functionality
- Minting capability (owner only)
- Burning capability (any holder)
- 18 decimal places

⚠️  Potential Issues:
1. Centralization risk: Owner can mint unlimited tokens
2. No maximum supply cap
3. Missing pause functionality for emergency situations

🔧 Suggestions:
- Consider adding a max supply limit
- Implement pausable pattern for emergency stops
- Add events for mint/burn operations
```

### Security Audit

```bash
ai-crypto audit contracts/DeFiProtocol.sol --verbose
```

Output:
```
🛡️  Security Audit: DeFiProtocol.sol

❌ HIGH: Reentrancy Vulnerability (Line 45)
   The function `withdraw()` updates state after external call.

   Vulnerable Code:
   ```solidity
   function withdraw(uint amount) public {
       require(balances[msg.sender] >= amount);
       (bool success, ) = msg.sender.call{value: amount}("");
       require(success);
       balances[msg.sender] -= amount; // State change after external call!
   }
   ```

   Fix: Use checks-effects-interactions pattern
   ```solidity
   function withdraw(uint amount) public {
       require(balances[msg.sender] >= amount);
       balances[msg.sender] -= amount; // Update state first
       (bool success, ) = msg.sender.call{value: amount}("");
       require(success);
   }
   ```

⚠️  MEDIUM: Unchecked Return Value (Line 78)
   ERC20 transfer return value not checked.

✓  INFO: 15 checks passed
```

### Transaction Analysis

```bash
ai-crypto tx 0xa1b2c3... --network ethereum --explain
```

Output:
```
🔍 Transaction Analysis

Hash: 0xa1b2c3...
Block: 18234567
From: 0xabcd...
To: 0x1234... (Uniswap V3 Router)

📊 What This Transaction Does:

This transaction swaps 1 ETH for USDC using Uniswap V3:

1. Wraps 1 ETH → WETH
2. Approves Uniswap router for WETH
3. Executes swap: WETH → USDC
4. Uses 0.3% fee pool
5. Minimum output: 1,850 USDC (3% slippage tolerance)

Actual Output: 1,891.23 USDC
Gas Used: 184,392 (0.0023 ETH)
Effective Price: $1,891.23 per ETH
```

### Gas Optimization

```bash
ai-crypto optimize contract.sol --compare
```

Output:
```
⚡ Gas Optimization Report

📈 Found 8 optimization opportunities

1. Use `!= 0` instead of `> 0` for unsigned integers
   Line 34: if (balance > 0) → if (balance != 0)
   Savings: ~6 gas per check

2. Cache array length in loops
   Line 89-92:
   Before:
   ```solidity
   for (uint i = 0; i < users.length; i++) {
       // ...
   }
   ```
   After:
   ```solidity
   uint len = users.length;
   for (uint i = 0; i < len; i++) {
       // ...
   }
   ```
   Savings: ~97 gas per iteration

3. Use `calldata` instead of `memory` for read-only arrays
   Line 45: function process(uint[] memory data)
   → function process(uint[] calldata data)
   Savings: ~1,200 gas for 10-element array

💰 Total Estimated Savings: ~15,400 gas per typical transaction
   At 50 gwei: ~$0.77 per tx
   At 100 gwei: ~$1.54 per tx
```

### AI-Powered Fuzzing

```bash
ai-crypto fuzz examples/VulnerableBank.sol --tool echidna
```

Output:
```
🔬 AI-Powered Fuzzing: VulnerableBank.sol

Running Echidna fuzzer...

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Metric            ┃ Value              ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Contract          │ VulnerableBank.sol │
│ Properties Tested │ 5                  │
│ Passed            │ 2                  │
│ Failed            │ 3                  │
│ Success Rate      │ 40.0%              │
│ Duration          │ 45.2s              │
└───────────────────┴────────────────────┘

🔬 AI Analysis of Fuzzing Results:

### Failure 1: echidna_balance_consistency

**What Went Wrong**: The property checking that contract balance >= user balance failed
after a sequence of deposits and withdraws.

**Root Cause**: Reentrancy vulnerability in the `withdraw()` function. The function
sends ETH before updating the user's balance, allowing a malicious contract to
call withdraw() again before the balance is updated.

**Security Implications**: HIGH SEVERITY - This is a critical reentrancy vulnerability
that allows attackers to drain the contract of all funds.

**Fix**:
```solidity
function withdraw(uint256 amount) public {
    require(balances[msg.sender] >= amount, "Insufficient balance");

    // Update state BEFORE external call (Checks-Effects-Interactions)
    balances[msg.sender] -= amount;

    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

**Better Properties**: Add explicit reentrancy guards and test with:
```solidity
function echidna_no_reentrancy() public returns (bool) {
    // Test that balance can only decrease once per transaction
}
```

[... more failures analyzed ...]
```

### Generate Property Tests

```bash
ai-crypto gentest examples/SecureToken.sol --tool foundry -o test/TokenProperties.t.sol
```

Output:
```
Generated Foundry Property Tests

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/SecureToken.sol";

contract TokenPropertiesTest is Test {
    SecureToken public token;

    function setUp() public {
        token = new SecureToken("Test", "TST", 18, 1000e18, 10000e18);
    }

    // Property 1: Total supply never exceeds max supply
    function testFuzz_TotalSupplyNeverExceedsMax(uint256 mintAmount) public {
        vm.assume(mintAmount > 0 && mintAmount < type(uint128).max);

        uint256 currentSupply = token.totalSupply();
        uint256 maxSupply = token.maxSupply();

        if (currentSupply + mintAmount <= maxSupply) {
            token.mint(address(this), mintAmount);
        }

        assertLe(token.totalSupply(), maxSupply, "Supply exceeded max");
    }

    // Property 2: Transfers maintain total supply
    function testFuzz_TransferMaintainsTotalSupply(
        address to,
        uint256 amount
    ) public {
        vm.assume(to != address(0) && amount > 0);

        uint256 supplyBefore = token.totalSupply();

        if (token.balanceOf(address(this)) >= amount) {
            token.transfer(to, amount);
        }

        assertEq(token.totalSupply(), supplyBefore, "Supply changed");
    }

    // ... 8 more properties generated ...
}

✓ Tests saved to: test/TokenProperties.t.sol
```

## Architecture

```
ai-crypto-toolkit/
├── src/ai_crypto_toolkit/
│   ├── cli.py              # Main CLI interface
│   ├── analyzers/
│   │   ├── contract.py     # Contract analysis
│   │   ├── security.py     # Security auditing
│   │   ├── transaction.py  # Transaction decoding
│   │   ├── gas.py          # Gas optimization
│   │   └── fuzzing.py      # AI-powered fuzzing
│   ├── llm/
│   │   ├── client.py       # LLM API client
│   │   └── prompts.py      # Optimized prompts
│   └── utils/
│       ├── solidity.py     # Solidity parsing
│       └── ethereum.py     # Web3 utilities
├── config/
│   └── config.example.yaml
├── examples/
│   └── vulnerable_contract.sol
└── docs/
    ├── PROMPTS.md          # Prompt engineering guide
    └── EXTENDING.md        # Plugin development
```

## Works With Your Stack

Tested with:
- ✅ vLLM (recommended for throughput)
- ✅ TabbyAPI (great for quantized models)
- ✅ LM Studio (easiest setup)
- ✅ llama.cpp server
- ✅ Any OpenAI-compatible API

Recommended models:
- **Qwen2.5-Coder-32B**: Best overall for code analysis
- **DeepSeek-Coder-33B**: Strong at vulnerability detection
- **CodeLlama-70B**: Good for explanations
- **Your own fine-tuned models**: Full control!

## Why Local AI?

1. **No rate limits** - Run as many analyses as you need
2. **Privacy** - Your contracts stay on your hardware
3. **Customization** - Fine-tune on your own vuln dataset
4. **Cost** - $15 for 55 hours of GPU time > $20/month rug-pulls
5. **Independence** - No corporate dependencies

## Extending

Add custom vulnerability patterns:

```python
# ~/.ai-crypto-toolkit/plugins/my_checks.py

from ai_crypto_toolkit.analyzers.security import SecurityCheck

class CustomFlashLoanCheck(SecurityCheck):
    name = "flash_loan_attack"
    severity = "high"

    def check(self, contract_ast):
        # Your custom logic
        pass
```

Register in config:
```yaml
security:
  custom_checks:
    - ~/.ai-crypto-toolkit/plugins/my_checks.py
```

## Roadmap

- [ ] Multi-chain support (L2s, Solana, etc.)
- [ ] Contract diffing (compare versions)
- [ ] Historical vulnerability database
- [ ] Fine-tuning scripts for security models
- [ ] Web UI (optional, CLI-first always)
- [ ] Integration with Foundry/Hardhat
- [ ] Automated fix suggestions
- [ ] Batch processing for large codebases

## Philosophy

This tool embodies:
- **Independence**: Your hardware, your models, your control
- **Practicality**: Ship working tools, iterate based on usage
- **Clarity**: Straight answers, no hedging
- **Leverage**: Compound your expertise with AI

Built for builders who value freedom and want AI that works for them, not the other way around.

## Contributing

PRs welcome! This tool gets better when builders contribute their expertise.

See `CONTRIBUTING.md` for guidelines.

## License

MIT - Build whatever you want with it.

---

Built with ⚡ by [@0x_Sero](https://twitter.com/0x_Sero)

*"If it doesn't compound, pivot quickly and keep the artifact."*
