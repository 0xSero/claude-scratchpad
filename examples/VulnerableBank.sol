// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableBank
 * @notice INTENTIONALLY VULNERABLE - For testing security analysis
 * @dev This contract contains multiple security issues for demonstration
 */
contract VulnerableBank {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // VULNERABILITY: Missing access control
    function setOwner(address newOwner) public {
        owner = newOwner;
    }

    // Deposit function
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABILITY: Reentrancy attack
    // State is updated AFTER external call
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // External call before state update!
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // State update happens after external call
        balances[msg.sender] -= amount;
    }

    // VULNERABILITY: tx.origin authentication
    function withdrawAll() public {
        require(tx.origin == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }

    // VULNERABILITY: Unchecked return value
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        balances[msg.sender] -= amount;
        balances[to] += amount;

        // Unchecked external call
        to.call{value: amount}("");
    }

    // Gas-inefficient function for testing optimization
    function inefficientLoop(uint256[] memory data) public {
        for (uint256 i = 0; i < data.length; i++) {
            // Array length is checked every iteration
            balances[msg.sender] += data[i];
        }
    }

    // Another gas-inefficient pattern
    function checkBalance(uint256 amount) public view returns (bool) {
        if (balances[msg.sender] > 0) {  // Should use != 0
            return balances[msg.sender] >= amount;
        }
        return false;
    }

    // Get contract balance
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
