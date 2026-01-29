# Day 64: Blockchain Fundamentals

**Date:** November 24, 2025

## Learning Objective
To understand the core components of a blockchain, including blocks, hashing, Proof of Work (PoW), and transaction management.

## Concepts Covered
- **Block Structure**: Linking blocks using cryptographic hashes to ensure data integrity.
- **Proof of Work (PoW)**: Implementing a "nonce" based mining algorithm with adjustable difficulty.
- **Consensus Mechanisms**: Simulating PoW, Proof of Stake (PoS), and Delegated PoS (DPoS).
- **Asymmetric Cryptography**: Using Elliptic Curve Digital Signature Algorithm (ECDSA) for secure transaction signing.
- **Wallet Addresses**: Generating public/private key pairs and Ethereum-style addresses.

## Code Explanation
The `day_sixtyfour.py` script implements a complete blockchain prototype:
- **`Block` Class**: Handles the mining process by finding a hash that starts with a specific number of zeros.
- **`Blockchain` Class**: Manages the chain, pending transactions, and verifies the validity of the entire history.
- **`CryptographyManager`**: Uses the `cryptography` library to sign transactions, ensuring only the owner of a private key can spend their funds.
- **`ConsensusSimulator`**: Provides mathematical models for how different blockchains reach agreement.

## How to Run
1. Install requirements: `pip install cryptography`
2. Run the simulation:
```bash
python week_10/daysixtyfour/day_sixtyfour.py --simulate_blockchain --difficulty 4
```

## Reflection
A blockchain is essentially a distributed, append-only database secured by math. Understanding how hashes link blocks together is fundamental to seeing why it's so difficult to tamper with historical data.
