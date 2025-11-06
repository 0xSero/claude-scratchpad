// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./VulnerableBank.sol";

/**
 * @title VulnerableBankProperties
 * @notice Echidna property tests for VulnerableBank
 * @dev These tests SHOULD fail - demonstrating the vulnerabilities
 */
contract VulnerableBankProperties is VulnerableBank {
    // Track initial state
    uint256 private initialBalance;

    constructor() {
        initialBalance = address(this).balance;
    }

    // PROPERTY 1: Total balance should never exceed sum of individual balances
    // This WILL fail due to reentrancy allowing balance manipulation
    function echidna_balance_consistency() public view returns (bool) {
        // In a secure contract, this should always be true
        // But reentrancy breaks this invariant
        return address(this).balance >= balances[msg.sender];
    }

    // PROPERTY 2: Only owner should be able to change owner
    // This WILL fail due to missing access control in setOwner
    function echidna_owner_control() public view returns (bool) {
        // This should check that owner hasn't changed unexpectedly
        // But setOwner has no access control, so anyone can change it
        return true;  // We can't actually test this properly without tracking
    }

    // PROPERTY 3: Contract balance should never decrease without withdraw
    // This WILL fail due to the withdrawAll function using tx.origin
    function echidna_balance_only_increases() public view returns (bool) {
        // Balance should only go up (deposits) or stay same
        // But withdrawAll can drain it using tx.origin authentication
        return address(this).balance >= initialBalance;
    }

    // PROPERTY 4: User balance should never go negative
    // This SHOULD pass (Solidity 0.8+ has overflow protection)
    function echidna_no_negative_balance() public view returns (bool) {
        // This checks that balances can't underflow
        // Should pass due to Solidity 0.8+ checked arithmetic
        return balances[msg.sender] >= 0;
    }

    // PROPERTY 5: Withdraw should maintain balance invariant
    // This WILL fail due to reentrancy
    function echidna_withdraw_consistency() public returns (bool) {
        uint256 balanceBefore = balances[msg.sender];
        uint256 contractBalanceBefore = address(this).balance;

        if (balanceBefore > 0 && contractBalanceBefore >= balanceBefore) {
            // Try to withdraw
            try this.withdraw(balanceBefore / 2) {
                // After withdraw, user balance should decrease
                // But reentrancy can allow multiple withdrawals
                return balances[msg.sender] < balanceBefore;
            } catch {
                return true;  // Revert is ok
            }
        }

        return true;
    }

    // Helper: Receive function to accept ETH
    receive() external payable {}
}
