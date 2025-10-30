# Day 38: Encryption & Cryptography

This module provides comprehensive cryptographic operations including symmetric/asymmetric encryption, hashing, digital signatures, and key derivation.

## Features Implemented

### 1. Symmetric Encryption (AES)

- **AES-256-CBC** mode encryption and decryption
- Random key and IV generation
- Proper padding handling
- Secure key management

### 2. Asymmetric Encryption (RSA)

- **RSA-2048** key pair generation
- OAEP padding for secure encryption
- Public key encryption, private key decryption
- Key serialization capabilities

### 3. Digital Signatures

- **RSA-PSS** with SHA-256 for signing
- Signature verification
- Data integrity assurance
- Non-repudiation support

### 4. Hashing Algorithms

- **SHA-256** for general hashing
- **bcrypt** for password hashing
- Salt generation and management
- Secure password verification

### 5. Key Derivation

- **PBKDF2** with SHA-256
- Configurable iteration count (100,000 recommended)
- Salt generation and storage
- Secure key derivation from passwords

## Classes and Methods

### CryptoManager Class

#### Symmetric Encryption

- `generate_aes_key()`: Generate random AES keys
- `generate_iv()`: Create initialization vectors
- `aes_encrypt()`: Encrypt data with AES
- `aes_decrypt()`: Decrypt AES-encrypted data

#### Asymmetric Encryption

- `generate_rsa_keypair()`: Create RSA key pairs
- `rsa_encrypt()`: Encrypt with public key
- `rsa_decrypt()`: Decrypt with private key

#### Digital Signatures

- `sign_data()`: Create digital signatures
- `verify_signature()`: Verify signature authenticity

#### Hashing

- `sha256_hash()`: Generate SHA-256 hashes
- `bcrypt_hash_password()`: Secure password hashing
- `bcrypt_verify_password()`: Password verification

#### Key Derivation

- `derive_key_from_password()`: Derive keys from passwords using PBKDF2

### SecureMessage Class

- End-to-end encrypted messaging
- Combined symmetric and asymmetric encryption
- Digital signatures for authentication
- Secure message packaging

## Security Best Practices

### 1. Key Management

- Generate cryptographically secure random keys
- Use appropriate key sizes (AES-256, RSA-2048+)
- Never hardcode keys in source code
- Implement proper key storage and rotation

### 2. Encryption Practices

- Always use authenticated encryption when possible
- Generate new IV for each encryption operation
- Use appropriate padding schemes
- Combine symmetric and asymmetric encryption efficiently

### 3. Password Security

- Use bcrypt for password hashing
- Implement proper salt generation
- Use high iteration counts for key derivation
- Never store plaintext passwords

### 4. Cryptographic Protocols

- Implement proper digital signatures for data integrity
- Use established standards and libraries
- Avoid custom cryptographic algorithms
- Regular security audits and updates

## Usage Examples

```python
# Initialize crypto manager
crypto = CryptoManager()

# Encrypt data with AES
key = crypto.generate_aes_key()
iv = crypto.generate_iv()
ciphertext = crypto.aes_encrypt(b"secret data", key, iv)

# Hash passwords
hashed_pw = crypto.bcrypt_hash_password("user_password")

# Create digital signatures
signature = crypto.sign_data(b"important data", private_key)
```
