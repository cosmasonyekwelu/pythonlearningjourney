"""
Day 38: Encryption & Cryptography
This module demonstrates various encryption techniques and cryptographic operations:
- Symmetric encryption (AES)
- Asymmetric encryption (RSA)
- Hashing algorithms (SHA-256, bcrypt)
- Digital signatures
- Key derivation (PBKDF2)
"""

import os
import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import bcrypt
import secrets


class CryptoManager:
    """Comprehensive cryptography manager for various operations"""

    def __init__(self):
        self.backend = default_backend()

    # Symmetric Encryption (AES)
    def generate_aes_key(self, key_size=32):
        """Generate a random AES key (256-bit by default)"""
        return os.urandom(key_size)

    def generate_iv(self):
        """Generate a random initialization vector for AES"""
        return os.urandom(16)

    def aes_encrypt(self, plaintext, key, iv):
        """Encrypt data using AES in CBC mode"""
        if len(key) not in [16, 24, 32]:
            raise ValueError("Key must be 16, 24, or 32 bytes long")

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=self.backend)
        encryptor = cipher.encryptor()

        # Pad data to be multiple of block size
        pad_length = 16 - (len(plaintext) % 16)
        padded_data = plaintext + bytes([pad_length] * pad_length)

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext

    def aes_decrypt(self, ciphertext, key, iv):
        """Decrypt data using AES in CBC mode"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                        backend=self.backend)
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        pad_length = padded_plaintext[-1]
        if pad_length > 16:
            raise ValueError("Invalid padding")

        return padded_plaintext[:-pad_length]

    # Asymmetric Encryption (RSA)
    def generate_rsa_keypair(self, key_size=2048):
        """Generate RSA public/private key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        return private_key, public_key

    def rsa_encrypt(self, plaintext, public_key):
        """Encrypt data using RSA public key"""
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def rsa_decrypt(self, ciphertext, private_key):
        """Decrypt data using RSA private key"""
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    # Digital Signatures
    def sign_data(self, data, private_key):
        """Create digital signature for data"""
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, data, signature, public_key):
        """Verify digital signature"""
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    # Hashing Functions
    def sha256_hash(self, data):
        """Generate SHA-256 hash"""
        digest = hashes.Hash(hashes.SHA256(), backend=self.backend)
        digest.update(data)
        return digest.finalize()

    def bcrypt_hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    def bcrypt_verify_password(self, password, hashed):
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    # Key Derivation
    def derive_key_from_password(self, password, salt=None, key_length=32):
        """Derive cryptographic key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(password.encode('utf-8'))
        return key, salt

    # Utility functions
    def bytes_to_base64(self, data):
        """Convert bytes to base64 string"""
        return base64.b64encode(data).decode('utf-8')

    def base64_to_bytes(self, data):
        """Convert base64 string to bytes"""
        return base64.b64decode(data.encode('utf-8'))


def demonstrate_crypto_operations():
    """Demonstrate various cryptographic operations"""
    crypto = CryptoManager()

    print("=== Cryptographic Operations Demo ===\n")

    # 1. Symmetric Encryption Demo
    print("1. Symmetric Encryption (AES-256-CBC)")
    aes_key = crypto.generate_aes_key()
    iv = crypto.generate_iv()
    plaintext = b"Secret message for symmetric encryption"

    ciphertext = crypto.aes_encrypt(plaintext, aes_key, iv)
    decrypted = crypto.aes_decrypt(ciphertext, aes_key, iv)

    print(f"Original: {plaintext}")
    print(f"Encrypted: {crypto.bytes_to_base64(ciphertext)}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {plaintext == decrypted}\n")

    # 2. Asymmetric Encryption Demo
    print("2. Asymmetric Encryption (RSA-2048)")
    private_key, public_key = crypto.generate_rsa_keypair()
    message = b"Secret message for asymmetric encryption"

    encrypted_msg = crypto.rsa_encrypt(message, public_key)
    decrypted_msg = crypto.rsa_decrypt(encrypted_msg, private_key)

    print(f"Original: {message}")
    print(f"Decrypted: {decrypted_msg}")
    print(f"Match: {message == decrypted_msg}\n")

    # 3. Digital Signatures Demo
    print("3. Digital Signatures")
    data_to_sign = b"Important data that needs verification"
    signature = crypto.sign_data(data_to_sign, private_key)
    is_valid = crypto.verify_signature(data_to_sign, signature, public_key)

    print(f"Data: {data_to_sign}")
    print(f"Signature: {crypto.bytes_to_base64(signature)}")
    print(f"Signature Valid: {is_valid}\n")

    # 4. Password Hashing Demo
    print("4. Password Hashing (bcrypt)")
    password = "MySecurePassword123!"
    hashed_password = crypto.bcrypt_hash_password(password)
    password_correct = crypto.bcrypt_verify_password(password, hashed_password)
    password_wrong = crypto.bcrypt_verify_password(
        "WrongPassword", hashed_password)

    print(f"Password: {password}")
    print(f"Hashed: {hashed_password.decode('utf-8')}")
    print(f"Correct password verification: {password_correct}")
    print(f"Wrong password verification: {password_wrong}\n")

    # 5. Key Derivation Demo
    print("5. Key Derivation (PBKDF2)")
    user_password = "UserPassword123"
    derived_key, salt = crypto.derive_key_from_password(user_password)

    print(f"Password: {user_password}")
    print(f"Derived Key: {crypto.bytes_to_base64(derived_key)}")
    print(f"Salt: {crypto.bytes_to_base64(salt)}\n")

    # 6. Hash Demo
    print("6. SHA-256 Hashing")
    data = b"Data to hash"
    hash_result = crypto.sha256_hash(data)
    print(f"Data: {data}")
    print(f"SHA-256 Hash: {crypto.bytes_to_base64(hash_result)}")


class SecureMessage:
    """Class for secure message encryption and signing"""

    def __init__(self, crypto_manager):
        self.crypto = crypto_manager
        self.private_key, self.public_key = crypto_manager.generate_rsa_keypair()

    def encrypt_and_sign_message(self, message, recipient_public_key):
        """Encrypt message and add digital signature"""
        # Generate session key for symmetric encryption
        session_key = self.crypto.generate_aes_key()
        iv = self.crypto.generate_iv()

        # Encrypt message with session key
        encrypted_message = self.crypto.aes_encrypt(
            message.encode('utf-8'), session_key, iv)

        # Encrypt session key with recipient's public key
        encrypted_session_key = self.crypto.rsa_encrypt(
            session_key, recipient_public_key)

        # Sign the encrypted message
        signature = self.crypto.sign_data(encrypted_message, self.private_key)

        return {
            'encrypted_message': self.crypto.bytes_to_base64(encrypted_message),
            'encrypted_session_key': self.crypto.bytes_to_base64(encrypted_session_key),
            'iv': self.crypto.bytes_to_base64(iv),
            'signature': self.crypto.bytes_to_base64(signature)
        }

    def decrypt_and_verify_message(self, encrypted_package, sender_public_key):
        """Decrypt message and verify signature"""
        # Convert from base64
        encrypted_message = self.crypto.base64_to_bytes(
            encrypted_package['encrypted_message'])
        encrypted_session_key = self.crypto.base64_to_bytes(
            encrypted_package['encrypted_session_key'])
        iv = self.crypto.base64_to_bytes(encrypted_package['iv'])
        signature = self.crypto.base64_to_bytes(encrypted_package['signature'])

        # Verify signature
        if not self.crypto.verify_signature(encrypted_message, signature, sender_public_key):
            raise ValueError(
                "Invalid signature - message may have been tampered with")

        # Decrypt session key
        session_key = self.crypto.rsa_decrypt(
            encrypted_session_key, self.private_key)

        # Decrypt message
        decrypted_message = self.crypto.aes_decrypt(
            encrypted_message, session_key, iv)

        return decrypted_message.decode('utf-8')


if __name__ == '__main__':
    # Run the demonstration
    demonstrate_crypto_operations()

    print("\n=== Secure Message Exchange Demo ===")
    crypto = CryptoManager()

    # Create two users
    alice = SecureMessage(crypto)
    bob = SecureMessage(crypto)

    # Alice sends encrypted message to Bob
    message = "Hello Bob, this is a secret message from Alice!"
    encrypted_package = alice.encrypt_and_sign_message(message, bob.public_key)

    print(f"Original message: {message}")
    print(f"Encrypted package keys: {list(encrypted_package.keys())}")

    # Bob decrypts and verifies the message
    try:
        decrypted_message = bob.decrypt_and_verify_message(
            encrypted_package, alice.public_key)
        print(f"Decrypted message: {decrypted_message}")
    except ValueError as e:
        print(f"Verification failed: {e}")
