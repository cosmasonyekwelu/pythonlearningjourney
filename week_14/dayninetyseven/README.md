# Day 97: User Management & Permissions System

## Objective
Implement a robust user management and Role-Based Access Control (RBAC) system for a trading platform.

## Concepts Covered
- **RBAC (Role-Based Access Control)**: Defining roles (Trader, Risk Manager, Admin) and associated permissions.
- **Identity Management**: Authenticating users and managing sessions securely.
- **Permission Enforcement**: Dynamically checking user rights for sensitive actions (trade execution, limit modification).
- **Multi-Tenancy**: Considerations for isolating data and configurations between different users/teams.

## Code Explanation
The `day_ninetyseven.py` script implements an `RBACManager` that manages user roles and provides a centralized way to verify permissions across the platform.

## How to Run
Run the RBAC demonstration:
```bash
python day_ninetyseven.py
```
