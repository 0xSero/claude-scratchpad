"""Optimized prompts for smart contract analysis using local LLMs."""

from typing import Any

# System prompts for different analysis types
SYSTEM_PROMPTS = {
    "contract": """You are an expert Solidity developer and smart contract auditor.
Your task is to analyze smart contracts and provide clear, actionable insights.

Focus on:
- Contract purpose and functionality
- Key features and patterns used
- Potential issues or edge cases
- Best practices and recommendations

Be direct and specific. Use code examples when helpful.""",
    "security": """You are a smart contract security expert specializing in vulnerability detection.
Your task is to identify security issues and provide detailed remediation guidance.

Check for:
- Reentrancy vulnerabilities
- Integer overflow/underflow
- Access control issues
- Unchecked external calls
- Delegatecall to untrusted addresses
- tx.origin authentication
- Denial of service vectors
- Front-running risks

For each issue found:
1. Severity (HIGH/MEDIUM/LOW/INFO)
2. Exact location (line numbers)
3. Vulnerable code snippet
4. Explanation of the risk
5. Concrete fix with code example

Be thorough but concise.""",
    "gas": """You are a Solidity optimization expert specializing in gas efficiency.
Your task is to identify gas optimization opportunities and quantify savings.

Look for:
- Inefficient storage access patterns
- Redundant operations
- Suboptimal data types
- Missing caching
- Loop inefficiencies
- Unnecessary external calls

For each optimization:
1. Current inefficient code
2. Optimized version
3. Estimated gas savings
4. Tradeoffs (if any)

Prioritize high-impact optimizations.""",
    "transaction": """You are an expert at analyzing Ethereum transactions.
Your task is to explain what transactions do in plain, non-technical language.

Focus on:
- What action is being performed
- Who is involved (sender, receiver, contracts)
- What value is being transferred or changed
- Why someone might make this transaction
- Any notable details (gas usage, errors, etc.)

Write for someone with basic blockchain knowledge but not deep technical expertise.""",
}


def get_system_prompt(analysis_type: str) -> str:
    """Get system prompt for an analysis type."""
    return SYSTEM_PROMPTS.get(analysis_type, SYSTEM_PROMPTS["contract"])


def get_analysis_prompt(
    analysis_type: str, code: str, context: str | None = None
) -> str:
    """Generate analysis prompt based on type."""
    if analysis_type == "contract":
        return _get_contract_analysis_prompt(code, context)
    elif analysis_type == "security":
        return _get_security_analysis_prompt(code, context)
    elif analysis_type == "gas":
        return _get_gas_analysis_prompt(code, context)
    else:
        return f"Analyze this Solidity code:\n\n```solidity\n{code}\n```"


def _get_contract_analysis_prompt(code: str, context: str | None) -> str:
    """Generate contract analysis prompt."""
    prompt = f"""Analyze this Solidity smart contract:

```solidity
{code}
```

Provide:
1. **Overview**: What does this contract do? What is its main purpose?
2. **Key Features**: What are the important functions and capabilities?
3. **Architecture**: What patterns or standards does it implement?
4. **Potential Issues**: Are there any concerns or edge cases?
5. **Recommendations**: How could this be improved?
"""

    if context:
        prompt += f"\n**Additional Context**: {context}\n"

    return prompt


def _get_security_analysis_prompt(code: str, context: str | None) -> str:
    """Generate security analysis prompt."""
    prompt = f"""Perform a comprehensive security audit of this Solidity contract:

```solidity
{code}
```

For each vulnerability found, provide:
- **Severity**: HIGH/MEDIUM/LOW/INFO
- **Title**: Brief description
- **Location**: Specific line numbers
- **Vulnerable Code**: The problematic code snippet
- **Explanation**: Why this is a security issue
- **Fix**: Concrete code example showing how to fix it
- **References**: Relevant SWC IDs or known attack patterns

Also list any checks that passed.

Be thorough and specific. Include line numbers and code examples.
"""

    if context:
        prompt += f"\n**Additional Context**: {context}\n"

    return prompt


def _get_gas_analysis_prompt(code: str, context: str | None) -> str:
    """Generate gas optimization prompt."""
    prompt = f"""Analyze this Solidity contract for gas optimization opportunities:

```solidity
{code}
```

For each optimization opportunity, provide:
1. **Current Code**: Show the inefficient code with line numbers
2. **Optimized Code**: Show the improved version
3. **Gas Savings**: Estimate gas saved (be specific)
4. **Explanation**: Why this saves gas
5. **Tradeoffs**: Any downsides (if applicable)

Focus on high-impact optimizations first.

Calculate total estimated savings and translate to USD at both 50 gwei and 100 gwei gas prices.
"""

    if context:
        prompt += f"\n**Additional Context**: {context}\n"

    return prompt


def get_transaction_prompt(
    tx_data: dict[str, Any], contract_abi: list[dict[str, Any]] | None = None
) -> str:
    """Generate transaction explanation prompt."""
    prompt = f"""Explain what this Ethereum transaction does:

**Transaction Details**:
- Hash: {tx_data.get('hash', 'N/A')}
- From: {tx_data.get('from', 'N/A')}
- To: {tx_data.get('to', 'N/A')}
- Value: {tx_data.get('value', 0)} wei
- Gas Used: {tx_data.get('gas_used', 'N/A')}
- Block: {tx_data.get('block_number', 'N/A')}
"""

    if input_data := tx_data.get("input"):
        prompt += f"\n**Input Data**:\n```\n{input_data}\n```\n"

    if contract_abi:
        prompt += f"\n**Contract ABI** (for decoding):\n```json\n{contract_abi}\n```\n"

    prompt += """
Explain:
1. What action is this transaction performing?
2. What is the user trying to accomplish?
3. What happens step-by-step?
4. Are there any notable details (high gas, errors, special patterns)?

Use plain language that a non-technical person could understand.
"""

    return prompt


# Quick reference for common vulnerability patterns
VULNERABILITY_PATTERNS = {
    "reentrancy": {
        "pattern": r"\.call\{value:",
        "after_pattern": r"(balance|amount)\s*[-=]",
        "description": "External call before state update (reentrancy risk)",
    },
    "tx_origin": {
        "pattern": r"tx\.origin",
        "description": "Using tx.origin for authentication (phishing risk)",
    },
    "delegatecall": {
        "pattern": r"\.delegatecall\(",
        "description": "Delegatecall to untrusted address (storage corruption risk)",
    },
    "unchecked_call": {
        "pattern": r"\.call\((?!.*require|.*assert|.*revert)",
        "description": "Unchecked return value from external call",
    },
    "overflow": {
        "pattern": r"(\+|-|\*)\s*(?!unchecked)",
        "version": "<0.8.0",
        "description": "Arithmetic without SafeMath (pre-0.8.0)",
    },
}


def get_vulnerability_hints(code: str) -> list[str]:
    """Get hints about potential vulnerabilities based on patterns.

    This provides quick checks before deep AI analysis.
    """
    hints = []

    for vuln_name, vuln_info in VULNERABILITY_PATTERNS.items():
        import re

        if re.search(vuln_info["pattern"], code):
            hints.append(f"Potential {vuln_name}: {vuln_info['description']}")

    return hints
