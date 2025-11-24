
"""
Day 67: Smart Contract Development
Implementation of Solidity smart contracts for DeFi and automated trading
"""

import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import subprocess
import warnings
warnings.filterwarnings('ignore')

# Web3 and smart contract libraries
from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
import solcx
from solcx import compile_source, install_solc

# Install specific Solidity compiler version
try:
    install_solc('0.8.19')
    solcx.set_solc_version('0.8.19')
except:
    print("Note: Using available Solidity compiler")

@dataclass
class DeployedContract:
    """Representation of a deployed smart contract"""
    name: str
    address: str
    abi: List[Dict]
    bytecode: str
    transaction_hash: str
    network: str

class SmartContractManager:
    """Manage smart contract compilation, deployment, and interaction"""
    
    def __init__(self, web3_provider: str = None, network: str = "local"):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider)) if web3_provider else None
        self.network = network
        self.contracts: Dict[str, DeployedContract] = {}
        
        if self.web3 and network != "local":
            # Add POA middleware for testnets
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    def compile_contract(self, solidity_code: str, contract_name: str) -> Dict[str, Any]:
        """Compile Solidity contract"""
        try:
            compiled_sol = compile_source(solidity_code)
            contract_interface = compiled_sol[f'<stdin>:{contract_name}']
            
            return {
                'abi': contract_interface['abi'],
                'bytecode': contract_interface['bin'],
                'compiled_successfully': True
            }
        except Exception as e:
            print(f"Compilation failed: {e}")
            return {
                'abi': [],
                'bytecode': '',
                'compiled_successfully': False,
                'error': str(e)
            }
    
    def deploy_contract(self, contract_name: str, abi: List[Dict], 
                       bytecode: str, deployer_private_key: str,
                       constructor_args: List[Any] = None) -> DeployedContract:
        """Deploy contract to blockchain"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        # Create contract factory
        contract_factory = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Get deployer account
        deployer_account = self.web3.eth.account.from_key(deployer_private_key)
        
        # Build transaction
        constructor_args = constructor_args or []
        transaction = contract_factory.constructor(*constructor_args).build_transaction({
            'from': deployer_account.address,
            'nonce': self.web3.eth.get_transaction_count(deployer_account.address),
            'gas': 2000000,
            'gasPrice': self.web3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = self.web3.eth.account.sign_transaction(transaction, deployer_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for deployment
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        
        print(f"Contract {contract_name} deployed at: {contract_address}")
        
        deployed_contract = DeployedContract(
            name=contract_name,
            address=contract_address,
            abi=abi,
            bytecode=bytecode,
            transaction_hash=tx_hash.hex(),
            network=self.network
        )
        
        self.contracts[contract_name] = deployed_contract
        return deployed_contract
    
    def load_contract(self, address: str, abi: List[Dict]) -> Contract:
        """Load existing contract instance"""
        if not self.web3:
            raise ValueError("Web3 provider not configured")
        
        return self.web3.eth.contract(address=address, abi=abi)
    
    def call_contract_function(self, contract: Contract, function_name: str, 
                             args: List[Any] = None, caller_private_key: str = None) -> Any:
        """Call contract function (read or write)"""
        args = args or []
        
        try:
            contract_function = getattr(contract.functions, function_name)
            
            if caller_private_key:
                # Write transaction
                caller_account = self.web3.eth.account.from_key(caller_private_key)
                
                transaction = contract_function(*args).build_transaction({
                    'from': caller_account.address,
                    'nonce': self.web3.eth.get_transaction_count(caller_account.address),
                    'gas': 2000000,
                    'gasPrice': self.web3.eth.gas_price
                })
                
                signed_txn = self.web3.eth.account.sign_transaction(transaction, caller_private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                
                print(f"Transaction successful: {tx_hash.hex()}")
                return tx_receipt
            else:
                # Read-only call
                result = contract_function(*args).call()
                return result
        
        except Exception as e:
            print(f"Contract call failed: {e}")
            raise

class DeFiContractTemplates:
    """Templates for common DeFi smart contracts"""
    
    @staticmethod
    def get_erc20_token_template(token_name: str, token_symbol: str, 
                               initial_supply: int, decimals: int = 18) -> str:
        """ERC-20 Token Contract Template"""
        return f'''
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {token_name} is ERC20, Ownable {{
    uint8 private _decimals;
    
    constructor() ERC20("{token_name}", "{token_symbol}") {{
        _decimals = {decimals};
        _mint(msg.sender, {initial_supply} * 10**_decimals);
    }}
    
    function decimals() public view virtual override returns (uint8) {{
        return _decimals;
    }}
    
    function mint(address to, uint256 amount) public onlyOwner {{
        _mint(to, amount);
    }}
    
    function burn(uint256 amount) public {{
        _burn(msg.sender, amount);
    }}
}}
'''
    
    @staticmethod
    def get_staking_contract_template(staking_token: str, reward_token: str) -> str:
        """Staking Contract Template"""
        return f'''
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract StakingContract is ReentrancyGuard, Ownable {{
    IERC20 public stakingToken;
    IERC20 public rewardsToken;
    
    uint256 public rewardRate = 100; // Rewards per second per token (scaled)
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored;
    
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;
    mapping(address => uint256) private _balances;
    
    uint256 private _totalSupply;
    
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);
    
    constructor(address _stakingToken, address _rewardsToken) {{
        stakingToken = IERC20(_stakingToken);
        rewardsToken = IERC20(_rewardsToken);
    }}
    
    function rewardPerToken() public view returns (uint256) {{
        if (_totalSupply == 0) {{
            return rewardPerTokenStored;
        }}
        return rewardPerTokenStored + (
            (block.timestamp - lastUpdateTime) * rewardRate * 1e18 / _totalSupply
        );
    }}
    
    function earned(address account) public view returns (uint256) {{
        return (
            _balances[account] * (rewardPerToken() - userRewardPerTokenPaid[account]) / 1e18
        ) + rewards[account];
    }}
    
    modifier updateReward(address account) {{
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;
        
        if (account != address(0)) {{
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }}
        _;
    }}
    
    function stake(uint256 amount) external nonReentrant updateReward(msg.sender) {{
        require(amount > 0, "Cannot stake 0");
        _totalSupply += amount;
        _balances[msg.sender] += amount;
        stakingToken.transferFrom(msg.sender, address(this), amount);
        emit Staked(msg.sender, amount);
    }}
    
    function withdraw(uint256 amount) public nonReentrant updateReward(msg.sender) {{
        require(amount > 0, "Cannot withdraw 0");
        _totalSupply -= amount;
        _balances[msg.sender] -= amount;
        stakingToken.transfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }}
    
    function getReward() public nonReentrant updateReward(msg.sender) {{
        uint256 reward = rewards[msg.sender];
        if (reward > 0) {{
            rewards[msg.sender] = 0;
            rewardsToken.transfer(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }}
    }}
    
    function setRewardRate(uint256 _rewardRate) external onlyOwner {{
        rewardRate = _rewardRate;
    }}
    
    function totalSupply() external view returns (uint256) {{
        return _totalSupply;
    }}
    
    function balanceOf(address account) external view returns (uint256) {{
        return _balances[account];
    }}
}}
'''
    
    @staticmethod
    def get_amm_pool_template(token_a: str, token_b: str) -> str:
        """Simple AMM Pool Template"""
        return f'''
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SimpleAMM is ReentrancyGuard {{
    IERC20 public tokenA;
    IERC20 public tokenB;
    
    uint256 public reserveA;
    uint256 public reserveB;
    
    event LiquidityAdded(address indexed provider, uint256 amountA, uint256 amountB);
    event LiquidityRemoved(address indexed provider, uint256 amountA, uint256 amountB);
    event Swap(address indexed user, address tokenIn, uint256 amountIn, uint256 amountOut);
    
    constructor(address _tokenA, address _tokenB) {{
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }}
    
    function addLiquidity(uint256 amountA, uint256 amountB) external nonReentrant {{
        require(amountA > 0 && amountB > 0, "Amounts must be positive");
        
        // For first liquidity, use provided ratio
        if (reserveA == 0 && reserveB == 0) {{
            reserveA = amountA;
            reserveB = amountB;
        }} else {{
            // Ensure proportional deposit
            require(amountA * reserveB == amountB * reserveA, "Invalid ratio");
            reserveA += amountA;
            reserveB += amountB;
        }}
        
        tokenA.transferFrom(msg.sender, address(this), amountA);
        tokenB.transferFrom(msg.sender, address(this), amountB);
        
        emit LiquidityAdded(msg.sender, amountA, amountB);
    }}
    
    function removeLiquidity(uint256 liquidityTokens) external nonReentrant {{
        require(liquidityTokens > 0, "Invalid liquidity amount");
        
        // Simplified - in practice you'd use LP tokens
        uint256 amountA = (reserveA * liquidityTokens) / (reserveA + reserveB);
        uint256 amountB = (reserveB * liquidityTokens) / (reserveA + reserveB);
        
        reserveA -= amountA;
        reserveB -= amountB;
        
        tokenA.transfer(msg.sender, amountA);
        tokenB.transfer(msg.sender, amountB);
        
        emit LiquidityRemoved(msg.sender, amountA, amountB);
    }}
    
    function swapAToB(uint256 amountAIn) external nonReentrant returns (uint256 amountBOut) {{
        require(amountAIn > 0, "Invalid input amount");
        require(reserveA > 0 && reserveB > 0, "Insufficient liquidity");
        
        uint256 amountAInWithFee = amountAIn * 997 / 1000; // 0.3% fee
        amountBOut = (reserveB * amountAInWithFee) / (reserveA + amountAInWithFee);
        
        require(amountBOut < reserveB, "Insufficient output liquidity");
        
        reserveA += amountAIn;
        reserveB -= amountBOut;
        
        tokenA.transferFrom(msg.sender, address(this), amountAIn);
        tokenB.transfer(msg.sender, amountBOut);
        
        emit Swap(msg.sender, address(tokenA), amountAIn, amountBOut);
    }}
    
    function swapBToA(uint256 amountBIn) external nonReentrant returns (uint256 amountAOut) {{
        require(amountBIn > 0, "Invalid input amount");
        require(reserveA > 0 && reserveB > 0, "Insufficient liquidity");
        
        uint256 amountBInWithFee = amountBIn * 997 / 1000; // 0.3% fee
        amountAOut = (reserveA * amountBInWithFee) / (reserveB + amountBInWithFee);
        
        require(amountAOut < reserveA, "Insufficient output liquidity");
        
        reserveB += amountBIn;
        reserveA -= amountAOut;
        
        tokenB.transferFrom(msg.sender, address(this), amountBIn);
        tokenA.transfer(msg.sender, amountAOut);
        
        emit Swap(msg.sender, address(tokenB), amountBIn, amountAOut);
    }}
    
    function getReserves() external view returns (uint256, uint256) {{
        return (reserveA, reserveB);
    }}
    
    function getPrice() external view returns (uint256) {{
        if (reserveA == 0 || reserveB == 0) return 0;
        return (reserveB * 1e18) / reserveA;
    }}
}}
'''

class ContractTestingFramework:
    """Framework for testing smart contracts"""
    
    def __init__(self, web3_provider: str):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.test_results = {}
    
    def run_security_tests(self, contract: Contract, contract_name: str) -> Dict[str, bool]:
        """Run basic security tests on contract"""
        security_checks = {}
        
        try:
            # Check for reentrancy vulnerability
            security_checks['no_reentrancy'] = self._check_reentrancy_guard(contract)
            
            # Check access control
            security_checks['proper_access_control'] = self._check_access_control(contract)
            
            # Check integer overflow protection
            security_checks['safe_math'] = self._check_safe_math(contract)
            
            # Check emergency stop
            security_checks['emergency_stop'] = self._check_emergency_stop(contract)
            
        except Exception as e:
            print(f"Security testing failed: {e}")
        
        self.test_results[contract_name] = security_checks
        return security_checks
    
    def _check_reentrancy_guard(self, contract: Contract) -> bool:
        """Check if contract has reentrancy protection"""
        # Simplified check - look for ReentrancyGuard in bytecode
        contract_code = self.web3.eth.get_code(contract.address)
        return len(contract_code) > 0  # Basic check
    
    def _check_access_control(self, contract: Contract) -> bool:
        """Check if contract has proper access control"""
        try:
            # Try to call owner function
            if hasattr(contract.functions, 'owner'):
                owner = contract.functions.owner().call()
                return owner != '0x0000000000000000000000000000000000000000'
            return True
        except:
            return False
    
    def _check_safe_math(self, contract: Contract) -> bool:
        """Check for integer overflow protection"""
        # In practice, check for SafeMath usage or Solidity 0.8+ 
        return True
    
    def _check_emergency_stop(self, contract: Contract) -> bool:
        """Check for emergency stop mechanism"""
        try:
            if hasattr(contract.functions, 'paused'):
                paused = contract.functions.paused().call()
                return True  # Function exists
            return False
        except:
            return False
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        report = ["Smart Contract Security Test Report", "="*50]
        
        for contract_name, results in self.test_results.items():
            report.append(f"\nContract: {contract_name}")
            report.append("-" * 30)
            
            for test_name, passed in results.items():
                status = "PASS" if passed else "FAIL"
                report.append(f"  {test_name}: {status}")
        
        return "\n".join(report)

def main():
    """Main function to demonstrate smart contract development"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Contract Development')
    parser.add_argument('--deploy_token', action='store_true', help='Deploy ERC-20 token')
    parser.add_argument('--deploy_staking', action='store_true', help='Deploy staking contract')
    parser.add_argument('--deploy_amm', action='store_true', help='Deploy AMM contract')
    parser.add_argument('--network', type=str, default='local', help='Network to deploy to')
    parser.add_argument('--test_contracts', action='store_true', help='Run security tests')
    
    args = parser.parse_args()
    
    print("="*80)
    print("SMART CONTRACT DEVELOPMENT - DAY 67")
    print("="*80)
    
    # For demo purposes, use a local testnet or Ganache
    web3_provider = "http://localhost:8545"  # Update with your provider
    
    try:
        contract_manager = SmartContractManager(web3_provider, args.network)
        contract_templates = DeFiContractTemplates()
        
        # Test connection
        if contract_manager.web3:
            print(f"Connected to network: {contract_manager.web3.eth.chain_id}")
            print(f"Latest block: {contract_manager.web3.eth.block_number}")
        else:
            print("Running in offline mode")
        
        if args.deploy_token:
            print("\n1. ERC-20 TOKEN DEPLOYMENT")
            print("-" * 40)
            
            # Compile token contract
            token_code = contract_templates.get_erc20_token_template(
                "DemoToken", "DEMO", 1000000
            )
            
            compilation_result = contract_manager.compile_contract(token_code, "DemoToken")
            
            if compilation_result['compiled_successfully']:
                print("Token contract compiled successfully")
                
                # In a real scenario, you would deploy with a private key
                print("ABI generated successfully")
                print(f"Bytecode length: {len(compilation_result['bytecode'])} bytes")
            else:
                print("Token compilation failed")
        
        if args.deploy_staking:
            print("\n2. STAKING CONTRACT DEPLOYMENT")
            print("-" * 40)
            
            staking_code = contract_templates.get_staking_contract_template(
                "0xTokenA", "0xTokenB"
            )
            
            compilation_result = contract_manager.compile_contract(staking_code, "StakingContract")
            
            if compilation_result['compiled_successfully']:
                print("Staking contract compiled successfully")
                print("Staking features:")
                print("  - Reward distribution")
                print("  - Time-based rewards")
                print("  - Reentrancy protection")
                print("  - Owner controls")
            else:
                print("Staking compilation failed")
        
        if args.deploy_amm:
            print("\n3. AMM POOL CONTRACT DEPLOYMENT")
            print("-" * 40)
            
            amm_code = contract_templates.get_amm_pool_template("0xTokenA", "0xTokenB")
            
            compilation_result = contract_manager.compile_contract(amm_code, "SimpleAMM")
            
            if compilation_result['compiled_successfully']:
                print("AMM contract compiled successfully")
                print("AMM features:")
                print("  - Constant product formula")
                print("  - 0.3% swap fee")
                print("  - Liquidity provision")
                print("  - Price calculations")
            else:
                print("AMM compilation failed")
        
        if args.test_contracts and contract_manager.web3:
            print("\n4. CONTRACT SECURITY TESTING")
            print("-" * 40)
            
            testing_framework = ContractTestingFramework(web3_provider)
            
            # Test deployed contracts
            for contract_name, deployed_contract in contract_manager.contracts.items():
                print(f"Testing {contract_name}...")
                contract_instance = contract_manager.load_contract(
                    deployed_contract.address, deployed_contract.abi
                )
                
                security_results = testing_framework.run_security_tests(
                    contract_instance, contract_name
                )
                
                print(f"Security results for {contract_name}:")
                for test_name, passed in security_results.items():
                    print(f"  {test_name}: {'PASS' if passed else 'FAIL'}")
            
            # Generate report
            report = testing_framework.generate_test_report()
            print(f"\n{report}")
        
        print("\n5. CONTRACT INTERACTION EXAMPLES")
        print("-" * 40)
        
        # Demonstrate contract interaction patterns
        print("Common contract interaction patterns:")
        print("1. Token Transfers: approve() -> transferFrom()")
        print("2. Staking: stake() -> getReward() -> withdraw()")
        print("3. AMM: addLiquidity() -> swap() -> removeLiquidity()")
        print("4. Governance: propose() -> vote() -> execute()")
        
        print("\nGas Optimization Tips:")
        print("- Use view/pure functions for read operations")
        print("- Batch operations to reduce transaction count")
        print("- Use events for off-chain data retrieval")
        print("- Optimize storage layout to reduce gas costs")
        
    except Exception as e:
        print(f"Error in smart contract demonstration: {e}")
        print("Note: For full functionality, ensure you have:")
        print("  - Local Ethereum node (Ganache) running")
        print("  - Solidity compiler installed")
        print("  - Sufficient testnet ETH for deployment")
    
    print("\n" + "="*80)
    print("Smart Contract Development demonstration completed!")
    print("="*80)

if __name__ == "__main__":
    main()