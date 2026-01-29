"""
Day 97: User Management & Role-Based Access Control (RBAC)
Implements a simple RBAC system for a trading platform.
"""

from enum import Enum
from typing import Dict, List, Set

class Permission(Enum):
    VIEW_PORTFOLIO = "view_portfolio"
    EXECUTE_TRADE = "execute_trade"
    MANAGE_RISK = "manage_risk"
    ADMIN_ACCESS = "admin_access"

class Role(Enum):
    VIEWER = [Permission.VIEW_PORTFOLIO]
    TRADER = [Permission.VIEW_PORTFOLIO, Permission.EXECUTE_TRADE]
    RISK_MANAGER = [Permission.VIEW_PORTFOLIO, Permission.MANAGE_RISK]
    ADMIN = [p for p in Permission]

class RBACManager:
    """Manages users, roles, and permissions."""

    def __init__(self):
        self.users: Dict[str, Role] = {}

    def add_user(self, username: str, role: Role):
        self.users[username] = role
        print(f"User '{username}' added with role '{role.name}'")

    def check_permission(self, username: str, permission: Permission) -> bool:
        """Check if a user has a specific permission."""
        role = self.users.get(username)
        if not role:
            return False
        return permission in role.value

def demonstrate_rbac():
    rbac = RBACManager()

    rbac.add_user("alice", Role.TRADER)
    rbac.add_user("bob", Role.VIEWER)

    print("\nPermission Checks:")

    # Alice can trade
    can_alice_trade = rbac.check_permission("alice", Permission.EXECUTE_TRADE)
    print(f"Can Alice execute trade? {'YES ✓' if can_alice_trade else 'NO ✗'}")

    # Bob cannot trade
    can_bob_trade = rbac.check_permission("bob", Permission.EXECUTE_TRADE)
    print(f"Can Bob execute trade? {'YES ✓' if can_bob_trade else 'NO ✗'}")

    # Admin check
    rbac.add_user("charlie", Role.ADMIN)
    can_charlie_manage_risk = rbac.check_permission("charlie", Permission.MANAGE_RISK)
    print(f"Can Admin Charlie manage risk? {'YES ✓' if can_charlie_manage_risk else 'NO ✗'}")

if __name__ == "__main__":
    demonstrate_rbac()
