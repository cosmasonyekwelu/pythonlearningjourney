
"""
Day 64: Blockchain Fundamentals
Implementation of blockchain core concepts, consensus mechanisms, and cryptographic operations
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import secrets
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Transaction:
    """Representation of a blockchain transaction"""
    sender: str
    receiver: str
    amount: float
    timestamp: float
    signature: Optional[str] = None
    tx_hash: Optional[str] = None
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        transaction_string = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'tx_hash': self.tx_hash
        }

@dataclass
class Block:
    """Representation of a blockchain block"""
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: Optional[str] = None
    difficulty: int = 4
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = (f"{self.index}{self.timestamp}"
                       f"{[tx.to_dict() for tx in self.transactions]}"
                       f"{self.previous_hash}{self.nonce}")
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self) -> None:
        """Mine block using Proof of Work"""
        print(f"Mining block {self.index}...")
        start_time = time.time()
        
        while True:
            self.hash = self.calculate_hash()
            if self.hash[:self.difficulty] == "0" * self.difficulty:
                break
            self.nonce += 1
        
        mining_time = time.time() - start_time
        print(f"Block {self.index} mined in {mining_time:.2f}s with nonce {self.nonce}")
        print(f"Block Hash: {self.hash}")

class Blockchain:
    """Implementation of a simple blockchain"""
    
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.mining_reward = 10.0
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the genesis block"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            difficulty=self.difficulty
        )
        genesis_block.mine_block()
        self.chain.append(genesis_block)
        print("Genesis block created and mined")
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add transaction to pending transactions"""
        # Verify transaction before adding
        if transaction.sender == transaction.receiver:
            raise ValueError("Sender and receiver cannot be the same")
        if transaction.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        transaction.tx_hash = transaction.calculate_hash()
        self.pending_transactions.append(transaction)
        print(f"Transaction added: {transaction.sender} -> {transaction.receiver}: {transaction.amount}")
    
    def mine_pending_transactions(self, mining_reward_address: str) -> None:
        """Mine pending transactions and create new block"""
        if not self.pending_transactions:
            print("No transactions to mine")
            return
        
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )
        
        block.mine_block()
        self.chain.append(block)
        
        # Clear pending transactions and add mining reward
        self.pending_transactions = []
        reward_transaction = Transaction(
            sender="0",
            receiver=mining_reward_address,
            amount=self.mining_reward,
            timestamp=time.time()
        )
        self.pending_transactions.append(reward_transaction)
        
        print(f"Block {block.index} added to chain with {len(block.transactions)} transactions")
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check block hash validity
            if current_block.hash != current_block.calculate_hash():
                print(f"Block {i} hash is invalid")
                return False
            
            # Check chain linkage
            if current_block.previous_hash != previous_block.hash:
                print(f"Block {i} previous hash doesn't match")
                return False
            
            # Check Proof of Work
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                print(f"Block {i} doesn't meet difficulty requirement")
                return False
        
        print("Blockchain is valid")
        return True
    
    def get_balance(self, address: str) -> float:
        """Get balance for an address"""
        balance = 0.0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                if transaction.receiver == address:
                    balance += transaction.amount
        
        # Check pending transactions
        for transaction in self.pending_transactions:
            if transaction.sender == address:
                balance -= transaction.amount
            if transaction.receiver == address:
                balance += transaction.amount
        
        return balance
    
    def display_chain(self) -> None:
        """Display the entire blockchain"""
        print("\n" + "="*80)
        print("BLOCKCHAIN EXPLORER")
        print("="*80)
        
        for block in self.chain:
            print(f"\nBlock {block.index}:")
            print(f"  Timestamp: {datetime.fromtimestamp(block.timestamp)}")
            print(f"  Previous Hash: {block.previous_hash}")
            print(f"  Hash: {block.hash}")
            print(f"  Nonce: {block.nonce}")
            print(f"  Difficulty: {block.difficulty}")
            print(f"  Transactions: {len(block.transactions)}")
            
            for tx in block.transactions:
                print(f"    {tx.sender} -> {tx.receiver}: {tx.amount}")

class CryptographyManager:
    """Manage cryptographic operations for blockchain"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self) -> None:
        """Generate ECDSA key pair"""
        self.private_key = ec.generate_private_key(ec.SECP256K1())
        self.public_key = self.private_key.public_key()
        print("ECDSA key pair generated")
    
    def get_address(self) -> str:
        """Generate Ethereum-style address from public key"""
        if not self.public_key:
            raise ValueError("No public key available")
        
        # Serialize public key
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        
        # Keccak-256 hash (simplified - using SHA3 for demonstration)
        hash_obj = hashes.Hash(hashes.SHA3_256())
        hash_obj.update(public_bytes)
        public_hash = hash_obj.finalize()
        
        # Take last 20 bytes for address
        address = public_hash[-20:].hex()
        return f"0x{address}"
    
    def sign_transaction(self, transaction: Transaction) -> str:
        """Sign a transaction with private key"""
        if not self.private_key:
            raise ValueError("No private key available")
        
        # Create message to sign
        message = f"{transaction.sender}{transaction.receiver}{transaction.amount}{transaction.timestamp}".encode()
        
        # Sign the message
        signature = self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))
        return signature.hex()
    
    def verify_signature(self, transaction: Transaction, signature: str, public_key: ec.EllipticCurvePublicKey) -> bool:
        """Verify transaction signature"""
        try:
            message = f"{transaction.sender}{transaction.receiver}{transaction.amount}{transaction.timestamp}".encode()
            public_key.verify(bytes.fromhex(signature), message, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False

class ConsensusSimulator:
    """Simulate different consensus mechanisms"""
    
    def __init__(self):
        self.stake_holders = {}
    
    def proof_of_work_simulation(self, difficulty: int = 4) -> Dict[str, Any]:
        """Simulate Proof of Work consensus"""
        print(f"\nSimulating Proof of Work (Difficulty: {difficulty})")
        
        start_time = time.time()
        nonce = 0
        target = "0" * difficulty
        
        while True:
            test_hash = hashlib.sha256(f"test_data{nonce}".encode()).hexdigest()
            if test_hash[:difficulty] == target:
                break
            nonce += 1
        
        mining_time = time.time() - start_time
        hashrate = nonce / mining_time if mining_time > 0 else 0
        
        return {
            'nonce': nonce,
            'hash': test_hash,
            'mining_time': mining_time,
            'hashrate': hashrate,
            'difficulty': difficulty
        }
    
    def proof_of_stake_simulation(self, validators: Dict[str, float]) -> str:
        """Simulate Proof of Stake validator selection"""
        print("\nSimulating Proof of Stake Validator Selection")
        
        total_stake = sum(validators.values())
        selection_number = secrets.randbelow(int(total_stake * 100)) / 100
        
        current_sum = 0
        for validator, stake in validators.items():
            current_sum += stake
            if selection_number <= current_sum:
                print(f"Selected validator: {validator} with stake: {stake}")
                return validator
        
        return list(validators.keys())[-1]
    
    def delegated_proof_of_stake_simulation(self, delegates: List[str], votes: Dict[str, int]) -> List[str]:
        """Simulate DPoS delegate election"""
        print("\nSimulating Delegated Proof of Stake Election")
        
        # Sort delegates by votes
        elected_delegates = sorted(delegates, key=lambda x: votes.get(x, 0), reverse=True)[:21]
        
        print("Elected Delegates:")
        for i, delegate in enumerate(elected_delegates, 1):
            print(f"  {i}. {delegate}: {votes.get(delegate, 0)} votes")
        
        return elected_delegates

def main():
    """Main function to demonstrate blockchain fundamentals"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Blockchain Fundamentals')
    parser.add_argument('--simulate_blockchain', action='store_true', help='Run blockchain simulation')
    parser.add_argument('--blocks', type=int, default=5, help='Number of blocks to mine')
    parser.add_argument('--difficulty', type=int, default=4, help='Mining difficulty')
    parser.add_argument('--test_crypto', action='store_true', help='Test cryptographic operations')
    parser.add_argument('--test_consensus', action='store_true', help='Test consensus mechanisms')
    
    args = parser.parse_args()
    
    print("="*80)
    print("BLOCKCHAIN FUNDAMENTALS - DAY 64")
    print("="*80)
    
    if args.simulate_blockchain:
        print("\n1. BLOCKCHAIN SIMULATION")
        print("-" * 40)
        
        # Initialize blockchain
        blockchain = Blockchain(difficulty=args.difficulty)
        crypto_manager = CryptographyManager()
        
        # Generate key pairs for participants
        crypto_manager.generate_key_pair()
        alice_address = crypto_manager.get_address()
        
        crypto_manager.generate_key_pair()
        bob_address = crypto_manager.get_address()
        
        print(f"Alice Address: {alice_address}")
        print(f"Bob Address: {bob_address}")
        
        # Create and mine transactions
        for i in range(args.blocks):
            # Add some transactions
            for j in range(3):
                tx = Transaction(
                    sender=alice_address if j % 2 == 0 else bob_address,
                    receiver=bob_address if j % 2 == 0 else alice_address,
                    amount=(i + j + 1) * 2.5,
                    timestamp=time.time()
                )
                blockchain.add_transaction(tx)
            
            # Mine block
            blockchain.mine_pending_transactions(mining_reward_address=alice_address)
        
        # Display blockchain
        blockchain.display_chain()
        
        # Validate chain
        print(f"\nBlockchain valid: {blockchain.is_chain_valid()}")
        
        # Check balances
        print(f"\nAlice balance: {blockchain.get_balance(alice_address):.2f}")
        print(f"Bob balance: {blockchain.get_balance(bob_address):.2f}")
    
    if args.test_crypto:
        print("\n2. CRYPTOGRAPHIC OPERATIONS")
        print("-" * 40)
        
        crypto_manager = CryptographyManager()
        crypto_manager.generate_key_pair()
        address = crypto_manager.get_address()
        
        print(f"Generated Address: {address}")
        
        # Test transaction signing
        test_tx = Transaction(
            sender=address,
            receiver="0x742d35Cc6634C0532925a3b8D6B6f7f2a1e3a1e1",
            amount=10.0,
            timestamp=time.time()
        )
        
        signature = crypto_manager.sign_transaction(test_tx)
        test_tx.signature = signature
        
        print(f"Transaction signed: {signature[:50]}...")
        
        # Verify signature
        is_valid = crypto_manager.verify_signature(test_tx, signature, crypto_manager.public_key)
        print(f"Signature valid: {is_valid}")
    
    if args.test_consensus:
        print("\n3. CONSENSUS MECHANISM SIMULATION")
        print("-" * 40)
        
        consensus_simulator = ConsensusSimulator()
        
        # Proof of Work simulation
        pow_result = consensus_simulator.proof_of_work_simulation(difficulty=args.difficulty)
        print(f"PoW Result: Nonce={pow_result['nonce']}, "
              f"Time={pow_result['mining_time']:.2f}s, "
              f"Hashrate={pow_result['hashrate']:.0f} H/s")
        
        # Proof of Stake simulation
        validators = {
            "Validator_A": 1000.0,
            "Validator_B": 2500.0,
            "Validator_C": 1500.0,
            "Validator_D": 3000.0
        }
        selected_validator = consensus_simulator.proof_of_stake_simulation(validators)
        
        # Delegated Proof of Stake simulation
        delegates = ["Delegate_1", "Delegate_2", "Delegate_3", "Delegate_4", "Delegate_5"]
        votes = {
            "Delegate_1": 15000,
            "Delegate_2": 22000,
            "Delegate_3": 18000,
            "Delegate_4": 25000,
            "Delegate_5": 12000
        }
        consensus_simulator.delegated_proof_of_stake_simulation(delegates, votes)
    
    print("\n" + "="*80)
    print("Blockchain Fundamentals demonstration completed!")
    print("="*80)

if __name__ == "__main__":
    main()
