# Day 38: Encryption & Cryptography

**Date:** October 29, 2025

## Learning Objective
To master the usage of modern cryptographic primitives in Python, including symmetric/asymmetric encryption, hashing, and digital signatures.

## Concepts Covered
- **Symmetric Encryption (AES)**: Using the same key for both encryption and decryption (fast, good for bulk data).
- **Asymmetric Encryption (RSA)**: Using public/private key pairs for secure key exchange.
- **Hashing (SHA-256, bcrypt)**: Creating "fingerprints" of data and securely storing passwords.
- **Digital Signatures**: Proving the authenticity and integrity of a message using RSA.
- **Key Derivation (PBKDF2)**: Generating strong cryptographic keys from user passwords.

## Code Explanation
The `day_thirtyeight.py` script provides a `CryptoManager` class that wraps the `cryptography` library:
- **`aes_encrypt()`**: Implements AES-256 in CBC mode with manual padding management.
- **`rsa_encrypt()`**: Demonstrates using a public key to encrypt a session key.
- **`bcrypt_hash_password()`**: Uses the industry-standard bcrypt algorithm to salt and hash passwords.
- **`SecureMessage`**: A class that simulates a "secure handshake" where a message is encrypted with AES, the AES key is encrypted with RSA, and the whole package is digitally signed.

## How to Run
1. Install requirements: `pip install cryptography bcrypt`
2. Run the cryptographic tests:
```bash
python week_06/daythirtyeight/day_thirtyeight.py
```

## Reflection
Cryptography is the "math of secrets." The most important takeaway is to never roll your own crypto—always use proven libraries like `cryptography` and algorithms like AES and bcrypt to protect user data.
