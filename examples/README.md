# Example Contracts

This directory contains example Solidity contracts for testing the AI Crypto Toolkit.

## VulnerableBank.sol

An **intentionally vulnerable** contract demonstrating common security issues:
- Reentrancy vulnerability
- Missing access control
- tx.origin authentication
- Unchecked external calls
- Gas-inefficient patterns

**Use for testing:**
```bash
# Security audit (should find multiple HIGH severity issues)
ai-crypto audit examples/VulnerableBank.sol

# Gas optimization (should find several opportunities)
ai-crypto optimize examples/VulnerableBank.sol
```

## SecureToken.sol

A well-written ERC20 token implementation with:
- Standard ERC20 functionality
- Owner-controlled minting with max supply
- Pausable transfers
- Burning capability
- Good event coverage
- Proper access control

**Use for testing:**
```bash
# Contract analysis (should explain features clearly)
ai-crypto analyze examples/SecureToken.sol

# Security audit (should pass most checks, might suggest improvements)
ai-crypto audit examples/SecureToken.sol

# Gas optimization (should find minor optimizations)
ai-crypto optimize examples/SecureToken.sol
```

## Testing Your Setup

After installing and configuring the toolkit:

1. **Test connection:**
   ```bash
   ai-crypto test
   ```

2. **Analyze the vulnerable contract:**
   ```bash
   ai-crypto audit examples/VulnerableBank.sol
   ```
   Expected: Multiple HIGH severity findings (reentrancy, access control, etc.)

3. **Analyze the secure token:**
   ```bash
   ai-crypto analyze examples/SecureToken.sol
   ```
   Expected: Clear explanation of ERC20 features and patterns

4. **Check gas optimizations:**
   ```bash
   ai-crypto optimize examples/VulnerableBank.sol
   ```
   Expected: Suggestions for loop caching, comparison operators, etc.

## Creating Your Own Test Contracts

The AI works best when analyzing:
- Complete, compilable contracts
- Real-world patterns and use cases
- Contracts with clear business logic
- Code with context (comments help!)

Avoid:
- Code snippets without context
- Pseudo-code or incomplete logic
- Contracts with many external dependencies (unless you provide context)
