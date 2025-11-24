
"""
Day 66: Wallet Integration & Management
Implementation of secure cryptocurrency wallet management with HD wallets, multi-sig, and transaction management
"""

import os
import json
import secrets
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import hmac
import base58
import warnings
warnings.filterwarnings('ignore')

# Cryptography libraries
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from eth_account import Account
from eth_account.messages import encode_defunct
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Bitcoin and HD wallet libraries
try:
    from bitcoinlib.wallets import Wallet as BTCWallet
    from bitcoinlib.mnemonic import Mnemonic
    from bitcoinlib.keys import Key
except ImportError:
    print("bitcoinlib not available, Bitcoin features disabled")

@dataclass
class Wallet:
    """Base wallet class"""
    name: str
    address: str
    public_key: str
    private_key: Optional[str] = None
    balance: float = 0.0
    network: str = "ethereum"
    derivation_path: str = "m/44'/60'/0'/0/0"

@dataclass
class Transaction:
    """Transaction representation"""
    from_address: str
    to_address: str
    amount: float
    gas_limit: int
    gas_price: int
    nonce: int
    data: str = "0x"
    value: int = 0
    chain_id: int = 1

class HDWalletManager:
    """Hierarchical Deterministic Wallet Manager"""
    
    def __init__(self, storage_path: str = "./wallets"):
        self.storage_path = storage_path
        self.wallets: Dict[str, Wallet] = {}
        self.master_seed = None
        os.makedirs(storage_path, exist_ok=True)
    
    def generate_mnemonic(self, strength: int = 128) -> str:
        """Generate BIP-39 mnemonic phrase"""
        # Strength: 128 -> 12 words, 256 -> 24 words
        if strength not in [128, 160, 192, 224, 256]:
            raise ValueError("Strength should be one of: 128, 160, 192, 224, 256")
        
        # Generate random entropy
        entropy = secrets.token_bytes(strength // 8)
        
        # Calculate checksum
        entropy_hash = hashlib.sha256(entropy).digest()
        checksum_bits = bin(entropy_hash[0])[2:].zfill(8)[:strength // 32]
        
        # Combine entropy and checksum
        entropy_bits = ''.join([bin(byte)[2:].zfill(8) for byte in entropy])
        combined_bits = entropy_bits + checksum_bits
        
        # Convert to mnemonic words (simplified - in practice use wordlist)
        wordlist = self._get_bip39_wordlist()
        mnemonic_words = []
        
        for i in range(0, len(combined_bits), 11):
            index = int(combined_bits[i:i+11], 2)
            mnemonic_words.append(wordlist[index])
        
        return ' '.join(mnemonic_words)
    
    def _get_bip39_wordlist(self) -> List[str]:
        """Get BIP-39 English wordlist (first 100 words for demo)"""
        # In practice, use the full 2048 word list
        sample_words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
            "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
            # ... full list would be here
        ]
        return sample_words * 20  # Extend for demo
    
    def create_hd_wallet(self, name: str, mnemonic: str, passphrase: str = "", 
                        network: str = "ethereum") -> Wallet:
        """Create HD wallet from mnemonic"""
        # Generate seed from mnemonic
        seed = self._mnemonic_to_seed(mnemonic, passphrase)
        
        # Generate master key
        master_key = self._derive_master_key(seed)
        
        # Derive account keys based on network
        if network == "ethereum":
            private_key, public_key, address = self._derive_ethereum_key(master_key)
        elif network == "bitcoin":
            private_key, public_key, address = self._derive_bitcoin_key(master_key)
        else:
            raise ValueError(f"Unsupported network: {network}")
        
        wallet = Wallet(
            name=name,
            address=address,
            public_key=public_key,
            private_key=private_key,
            network=network
        )
        
        self.wallets[name] = wallet
        self._save_wallet(wallet)
        
        print(f"Created HD wallet '{name}' with address: {address}")
        return wallet
    
    def _mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """Convert mnemonic to seed using PBKDF2"""
        # Normalize mnemonic and passphrase
        mnemonic_normalized = mnemonic.lower().strip()
        passphrase_normalized = "mnemonic" + passphrase
        
        # Use PBKDF2 to derive seed
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=64,
            salt=mnemonic_normalized.encode('utf-8'),
            iterations=2048,
        )
        seed = kdf.derive(passphrase_normalized.encode('utf-8'))
        return seed
    
    def _derive_master_key(self, seed: bytes) -> bytes:
        """Derive master key from seed using HMAC-SHA512"""
        # Simplified implementation
        hmac_result = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        return hmac_result
    
    def _derive_ethereum_key(self, master_key: bytes) -> Tuple[str, str, str]:
        """Derive Ethereum key pair from master key"""
        # Simplified derivation - in practice use proper BIP32/44
        private_key_bytes = hashlib.sha256(master_key).digest()
        private_key_hex = private_key_bytes.hex()
        
        # Create Ethereum account
        account = Account.from_key(private_key_hex)
        
        return private_key_hex, account.key, account.address
    
    def _derive_bitcoin_key(self, master_key: bytes) -> Tuple[str, str, str]:
        """Derive Bitcoin key pair from master key"""
        # Simplified implementation
        private_key_bytes = hashlib.sha256(master_key + b"bitcoin").digest()
        private_key_hex = private_key_bytes.hex()
        
        # Generate Bitcoin address (simplified)
        public_key_hash = hashlib.sha256(private_key_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(public_key_hash)
        public_key_hash_160 = ripemd160.digest()
        
        # Add network byte and checksum
        network_byte = b'\x00'  # Mainnet
        payload = network_byte + public_key_hash_160
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        bitcoin_address_bytes = payload + checksum
        bitcoin_address = base58.b58encode(bitcoin_address_bytes).decode()
        
        return private_key_hex, private_key_hex, bitcoin_address
    
    def _save_wallet(self, wallet: Wallet) -> None:
        """Save wallet to encrypted storage"""
        wallet_data = {
            'name': wallet.name,
            'address': wallet.address,
            'public_key': wallet.public_key,
            'network': wallet.network,
            'derivation_path': wallet.derivation_path,
            'created_at': datetime.now().isoformat()
        }
        
        # Don't save private key to disk in this implementation
        # In production, use secure encrypted storage
        
        file_path = os.path.join(self.storage_path, f"{wallet.name}.json")
        with open(file_path, 'w') as f:
            json.dump(wallet_data, f, indent=2)
    
    def load_wallet(self, name: str) -> Optional[Wallet]:
        """Load wallet from storage"""
        file_path = os.path.join(self.storage_path, f"{name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                wallet_data = json.load(f)
            
            wallet = Wallet(
                name=wallet_data['name'],
                address=wallet_data['address'],
                public_key=wallet_data['public_key'],
                network=wallet_data['network'],
                derivation_path=wallet_data['derivation_path']
            )
            
            self.wallets[name] = wallet
            return wallet
        
        return None

class TransactionManager:
    """Manage cryptocurrency transactions"""
    
    def __init__(self, web3_provider: str = None):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider)) if web3_provider else None
        self.pending_transactions = {}
    
    def create_eth_transaction(self, from_wallet: Wallet, to_address: str, 
                             amount: float, gas_limit: int = 21000, 
                             gas_price: int = None) -> Transaction:
        """Create Ethereum transaction"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        # Get current gas price if not provided
        if gas_price is None:
            gas_price = self.web3.eth.gas_price
        
        # Get nonce
        nonce = self.web3.eth.get_transaction_count(from_wallet.address)
        
        # Convert amount to wei
        value_wei = self.web3.to_wei(amount, 'ether')
        
        transaction = Transaction(
            from_address=from_wallet.address,
            to_address=to_address,
            amount=amount,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            value=value_wei,
            chain_id=1  # Mainnet
        )
        
        return transaction
    
    def sign_transaction(self, transaction: Transaction, private_key: str) -> str:
        """Sign transaction with private key"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        # Prepare transaction dict
        tx_dict = {
            'nonce': transaction.nonce,
            'gasPrice': transaction.gas_price,
            'gas': transaction.gas_limit,
            'to': transaction.to_address,
            'value': transaction.value,
            'data': transaction.data,
            'chainId': transaction.chain_id
        }
        
        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(tx_dict, private_key)
        return signed_tx.rawTransaction.hex()
    
    def send_transaction(self, signed_transaction: str) -> str:
        """Send signed transaction to network"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        try:
            tx_hash = self.web3.eth.send_raw_transaction(signed_transaction)
            tx_hash_hex = tx_hash.hex()
            
            self.pending_transactions[tx_hash_hex] = {
                'status': 'pending',
                'submitted_at': datetime.now()
            }
            
            print(f"Transaction sent: {tx_hash_hex}")
            return tx_hash_hex
        
        except Exception as e:
            print(f"Failed to send transaction: {e}")
            raise
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status and receipt"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        try:
            # Check if transaction is mined
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                return {
                    'status': 'confirmed',
                    'block_number': receipt.blockNumber,
                    'gas_used': receipt.gasUsed,
                    'confirmations': self.web3.eth.block_number - receipt.blockNumber
                }
            
            # Check if transaction is pending
            tx = self.web3.eth.get_transaction(tx_hash)
            if tx:
                return {'status': 'pending'}
            
            return {'status': 'not_found'}
        
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def estimate_gas(self, transaction: Transaction) -> int:
        """Estimate gas required for transaction"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        tx_dict = {
            'from': transaction.from_address,
            'to': transaction.to_address,
            'value': transaction.value,
            'data': transaction.data
        }
        
        return self.web3.eth.estimate_gas(tx_dict)

class MultiSigWallet:
    """Multi-signature wallet implementation"""
    
    def __init__(self, owners: List[str], required_signatures: int):
        self.owners = owners
        self.required_signatures = required_signatures
        self.pending_transactions = {}
        self.transaction_approvals = {}
    
    def create_transaction(self, transaction: Transaction, creator: str) -> str:
        """Create new multi-sig transaction"""
        if creator not in self.owners:
            raise ValueError("Creator must be one of the owners")
        
        tx_id = hashlib.sha256(
            f"{transaction.from_address}{transaction.to_address}{transaction.amount}{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        self.pending_transactions[tx_id] = {
            'transaction': transaction,
            'creator': creator,
            'created_at': datetime.now(),
            'approvals': [],
            'rejections': []
        }
        
        self.transaction_approvals[tx_id] = {}
        
        print(f"Created multi-sig transaction {tx_id}")
        return tx_id
    
    def approve_transaction(self, tx_id: str, owner: str, signature: str) -> bool:
        """Approve multi-sig transaction"""
        if owner not in self.owners:
            raise ValueError("Not an owner of this wallet")
        
        if tx_id not in self.pending_transactions:
            raise ValueError("Transaction not found")
        
        # Store approval
        self.transaction_approvals[tx_id][owner] = {
            'signature': signature,
            'timestamp': datetime.now()
        }
        
        self.pending_transactions[tx_id]['approvals'].append(owner)
        
        print(f"Owner {owner} approved transaction {tx_id}")
        
        # Check if we have enough approvals
        if len(self.pending_transactions[tx_id]['approvals']) >= self.required_signatures:
            print(f"Transaction {tx_id} has sufficient approvals")
            return True
        
        return False
    
    def get_transaction_status(self, tx_id: str) -> Dict[str, Any]:
        """Get multi-sig transaction status"""
        if tx_id not in self.pending_transactions:
            return {'status': 'not_found'}
        
        tx_data = self.pending_transactions[tx_id]
        approvals_count = len(tx_data['approvals'])
        
        status = {
            'transaction': tx_data['transaction'],
            'creator': tx_data['creator'],
            'created_at': tx_data['created_at'],
            'approvals': tx_data['approvals'],
            'approvals_count': approvals_count,
            'required_signatures': self.required_signatures,
            'can_execute': approvals_count >= self.required_signatures
        }
        
        return status

class WalletSecurityManager:
    """Manage wallet security and monitoring"""
    
    def __init__(self):
        self.security_events = []
        self.whitelisted_addresses = set()
        self.spending_limits = {}
    
    def add_whitelisted_address(self, address: str) -> None:
        """Add address to whitelist"""
        self.whitelisted_addresses.add(address.lower())
        self.log_security_event("WHITELIST_ADD", f"Added {address} to whitelist")
    
    def set_spending_limit(self, wallet_address: str, daily_limit: float) -> None:
        """Set daily spending limit for wallet"""
        self.spending_limits[wallet_address.lower()] = {
            'daily_limit': daily_limit,
            'daily_spent': 0.0,
            'last_reset': datetime.now().date()
        }
        self.log_security_event("SPENDING_LIMIT_SET", 
                              f"Set ${daily_limit} daily limit for {wallet_address}")
    
    def check_transaction_security(self, transaction: Transaction) -> Dict[str, Any]:
        """Check transaction against security rules"""
        security_check = {
            'allowed': True,
            'warnings': [],
            'block_reasons': []
        }
        
        # Check whitelist
        if (self.whitelisted_addresses and 
            transaction.to_address.lower() not in self.whitelisted_addresses):
            security_check['warnings'].append("Recipient not in whitelist")
        
        # Check spending limits
        wallet_key = transaction.from_address.lower()
        if wallet_key in self.spending_limits:
            limit_data = self.spending_limits[wallet_key]
            
            # Reset daily spent if new day
            if datetime.now().date() > limit_data['last_reset']:
                limit_data['daily_spent'] = 0.0
                limit_data['last_reset'] = datetime.now().date()
            
            # Check if transaction exceeds limit
            new_daily_total = limit_data['daily_spent'] + transaction.amount
            if new_daily_total > limit_data['daily_limit']:
                security_check['block_reasons'].append(
                    f"Daily spending limit exceeded: ${new_daily_total:.2f} > ${limit_data['daily_limit']:.2f}"
                )
                security_check['allowed'] = False
        
        # Log security check
        if not security_check['allowed']:
            self.log_security_event("TX_BLOCKED", 
                                  f"Blocked transaction from {transaction.from_address} to {transaction.to_address}")
        elif security_check['warnings']:
            self.log_security_event("TX_WARNING", 
                                  f"Warning for transaction: {', '.join(security_check['warnings'])}")
        
        return security_check
    
    def log_security_event(self, event_type: str, description: str) -> None:
        """Log security event"""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'description': description
        }
        self.security_events.append(event)
        print(f"SECURITY: {event_type} - {description}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        recent_events = [e for e in self.security_events 
                        if (datetime.now() - e['timestamp']).days < 7]
        
        return {
            'total_events_7d': len(recent_events),
            'blocked_transactions': len([e for e in recent_events if e['type'] == 'TX_BLOCKED']),
            'whitelisted_addresses': len(self.whitelisted_addresses),
            'active_spending_limits': len(self.spending_limits),
            'recent_events': recent_events[-10:]  # Last 10 events
        }

def main():
    """Main function to demonstrate wallet management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Wallet Integration & Management')
    parser.add_argument('--create_wallet', action='store_true', help='Create new HD wallet')
    parser.add_argument('--wallet_name', type=str, default='my_wallet', help='Wallet name')
    parser.add_argument('--network', type=str, default='ethereum', choices=['ethereum', 'bitcoin'])
    parser.add_argument('--multi_sig', action='store_true', help='Demonstrate multi-sig wallet')
    parser.add_argument('--security', action='store_true', help='Test security features')
    
    args = parser.parse_args()
    
    print("="*80)
    print("WALLET INTEGRATION & MANAGEMENT - DAY 66")
    print("="*80)
    
    # Initialize wallet manager
    wallet_manager = HDWalletManager()
    security_manager = WalletSecurityManager()
    
    if args.create_wallet:
        print("\n1. HD WALLET CREATION")
        print("-" * 40)
        
        # Generate mnemonic
        mnemonic = wallet_manager.generate_mnemonic(strength=128)
        print(f"Generated Mnemonic: {mnemonic}")
        print("⚠️  Keep this mnemonic secure! It can recover all wallet funds.")
        
        # Create wallet
        wallet = wallet_manager.create_hd_wallet(
            name=args.wallet_name,
            mnemonic=mnemonic,
            network=args.network
        )
        
        print(f"Wallet Address: {wallet.address}")
        print(f"Public Key: {wallet.public_key[:50]}...")
        print(f"Network: {wallet.network}")
    
    if args.multi_sig:
        print("\n2. MULTI-SIGNATURE WALLET")
        print("-" * 40)
        
        # Create owners
        owners = []
        for i in range(3):
            mnemonic = wallet_manager.generate_mnemonic()
            wallet = wallet_manager.create_hd_wallet(
                name=f"owner_{i+1}",
                mnemonic=mnemonic,
                network='ethereum'
            )
            owners.append(wallet.address)
        
        # Create multi-sig wallet
        multi_sig = MultiSigWallet(owners=owners, required_signatures=2)
        
        print(f"Multi-sig Wallet Created:")
        print(f"  Owners: {len(owners)}")
        print(f"  Required Signatures: {multi_sig.required_signatures}")
        for i, owner in enumerate(owners, 1):
            print(f"  Owner {i}: {owner}")
        
        # Simulate multi-sig transaction
        print("\nSimulating multi-sig transaction...")
        test_tx = Transaction(
            from_address=owners[0],
            to_address="0x742d35Cc6634C0532925a3b8D6B6f7f2a1e3a1e1",
            amount=1.0,
            gas_limit=21000,
            gas_price=30000000000,
            nonce=1
        )
        
        tx_id = multi_sig.create_transaction(test_tx, owners[0])
        
        # Approve by multiple owners
        for i in range(2):
            multi_sig.approve_transaction(tx_id, owners[i], f"signature_{i}")
        
        # Check status
        status = multi_sig.get_transaction_status(tx_id)
        print(f"Transaction Status: {status['can_execute']}")
        print(f"Approvals: {status['approvals_count']}/{status['required_signatures']}")
    
    if args.security:
        print("\n3. WALLET SECURITY FEATURES")
        print("-" * 40)
        
        # Create test wallet
        mnemonic = wallet_manager.generate_mnemonic()
        wallet = wallet_manager.create_hd_wallet(
            name="security_test",
            mnemonic=mnemonic,
            network='ethereum'
        )
        
        # Set up security rules
        security_manager.add_whitelisted_address("0x742d35Cc6634C0532925a3b8D6B6f7f2a1e3a1e1")
        security_manager.set_spending_limit(wallet.address, daily_limit=1000.0)
        
        # Test transactions
        test_transactions = [
            Transaction(
                from_address=wallet.address,
                to_address="0x742d35Cc6634C0532925a3b8D6B6f7f2a1e3a1e1",  # Whitelisted
                amount=500.0,
                gas_limit=21000,
                gas_price=30000000000,
                nonce=1
            ),
            Transaction(
                from_address=wallet.address,
                to_address="0x1234567890123456789012345678901234567890",  # Not whitelisted
                amount=100.0,
                gas_limit=21000,
                gas_price=30000000000,
                nonce=2
            ),
            Transaction(
                from_address=wallet.address,
                to_address="0x742d35Cc6634C0532925a3b8D6B6f7f2a1e3a1e1",  # Whitelisted but over limit
                amount=600.0,
                gas_limit=21000,
                gas_price=30000000000,
                nonce=3
            )
        ]
        
        for i, tx in enumerate(test_transactions, 1):
            print(f"\nTransaction {i} Security Check:")
            security_check = security_manager.check_transaction_security(tx)
            print(f"  Allowed: {security_check['allowed']}")
            if security_check['warnings']:
                print(f"  Warnings: {', '.join(security_check['warnings'])}")
            if security_check['block_reasons']:
                print(f"  Block Reasons: {', '.join(security_check['block_reasons'])}")
        
        # Generate security report
        report = security_manager.get_security_report()
        print(f"\nSecurity Report:")
        print(f"  Total Events (7d): {report['total_events_7d']}")
        print(f"  Blocked Transactions: {report['blocked_transactions']}")
        print(f"  Whitelisted Addresses: {report['whitelisted_addresses']}")
        print(f"  Active Spending Limits: {report['active_spending_limits']}")
    
    print("\n4. WALLET RECOVERY DEMONSTRATION")
    print("-" * 40)
    
    # Demonstrate wallet recovery from mnemonic
    test_mnemonic = wallet_manager.generate_mnemonic()
    original_wallet = wallet_manager.create_hd_wallet(
        name="recover_test",
        mnemonic=test_mnemonic,
        network='ethereum'
    )
    
    print(f"Original Wallet Address: {original_wallet.address}")
    
    # Simulate recovery (create new wallet manager instance)
    recovery_manager = HDWalletManager(storage_path="./recovery_wallets")
    recovered_wallet = recovery_manager.create_hd_wallet(
        name="recovered_wallet",
        mnemonic=test_mnemonic,
        network='ethereum'
    )
    
    print(f"Recovered Wallet Address: {recovered_wallet.address}")
    print(f"Recovery Successful: {original_wallet.address == recovered_wallet.address}")
    
    print("\n" + "="*80)
    print("Wallet Integration & Management demonstration completed!")
    print("="*80)

if __name__ == "__main__":
    main()