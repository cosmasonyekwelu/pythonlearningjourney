"""
Day 39: Authentication Protocols
This module demonstrates various authentication protocols and methods:
- JWT (JSON Web Tokens)
- OAuth 2.0 client implementation
- Session-based authentication
- API key authentication
- Multi-factor authentication (MFA)
"""

import os
import time
import json
import base64
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import bcrypt


class JWTAuthManager:
    """JWT Authentication Manager for token-based auth"""

    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self,
                            user_id: str,
                            username: str,
                            roles: list,
                            expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        payload = {
            'sub': user_id,
            'username': username,
            'roles': roles,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=30)

        payload = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """Generate new access token using refresh token"""
        payload = self.verify_token(refresh_token)

        if payload.get('type') != 'refresh':
            raise ValueError("Invalid refresh token")

        # In real application, fetch user data from database
        user_id = payload['sub']
        new_access_token = self.create_access_token(
            user_id=user_id,
            username="user",  # Fetch from DB
            roles=["user"]    # Fetch from DB
        )

        return {
            'access_token': new_access_token,
            'refresh_token': refresh_token  # Refresh token rotation optional
        }


class SessionAuthManager:
    """Session-based authentication manager"""

    def __init__(self):
        self.sessions = {}  # In production, use Redis or database
        self.session_timeout = timedelta(hours=1)

    def create_session(self, user_id: str, user_data: Dict) -> str:
        """Create new session and return session ID"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'user_id': user_id,
            'user_data': user_data,
            'created_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow()
        }

        self.sessions[session_id] = session_data
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data and update last accessed time"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check if session has expired
        if datetime.utcnow() - session['last_accessed'] > self.session_timeout:
            self.delete_session(session_id)
            return None

        # Update last accessed time
        session['last_accessed'] = datetime.utcnow()
        return session

    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session['last_accessed'] > self.session_timeout
        ]

        for session_id in expired_sessions:
            self.delete_session(session_id)


class APIKeyAuthManager:
    """API Key authentication manager"""

    def __init__(self):
        self.api_keys = {}  # In production, use database
        self.key_prefix = "sk_"  # Secret key prefix

    def generate_api_key(self, user_id: str, permissions: list, description: str = "") -> str:
        """Generate new API key"""
        # Generate random key material
        key_material = secrets.token_bytes(32)

        # Create the full API key
        api_key = self.key_prefix + \
            base64.urlsafe_b64encode(key_material).decode('utf-8')

        # Store key hash (never store the actual key)
        key_hash = self._hash_api_key(api_key)

        self.api_keys[key_hash] = {
            'user_id': user_id,
            'permissions': permissions,
            'description': description,
            'created_at': datetime.utcnow(),
            'last_used': None,
            'is_active': True
        }

        return api_key  # Return only once - cannot be retrieved again

    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return user data"""
        if not api_key.startswith(self.key_prefix):
            return None

        key_hash = self._hash_api_key(api_key)

        if key_hash not in self.api_keys:
            return None

        key_data = self.api_keys[key_hash]

        if not key_data['is_active']:
            return None

        # Update last used timestamp
        key_data['last_used'] = datetime.utcnow()

        return {
            'user_id': key_data['user_id'],
            'permissions': key_data['permissions']
        }

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        key_hash = self._hash_api_key(api_key)

        if key_hash in self.api_keys:
            self.api_keys[key_hash]['is_active'] = False
            return True

        return False

    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


class MFAManager:
    """Multi-Factor Authentication Manager"""

    def __init__(self):
        self.totp_secrets = {}  # In production, use secure database

    def generate_totp_secret(self, user_id: str) -> str:
        """Generate TOTP secret for a user"""
        secret = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
        self.totp_secrets[user_id] = secret
        return secret

    def verify_totp_code(self, user_id: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code (simplified implementation)"""
        if user_id not in self.totp_secrets:
            return False

        # In production, use proper TOTP library like pyotp
        # This is a simplified demonstration
        secret = self.totp_secrets[user_id]
        current_time = int(time.time())

        # Generate codes for current and adjacent time windows
        for i in range(-window, window + 1):
            expected_code = self._generate_simple_totp(
                secret, current_time + i * 30)
            if hmac.compare_digest(str(code), str(expected_code)):
                return True

        return False

    def _generate_simple_totp(self, secret: str, timestamp: int) -> int:
        """Simple TOTP generation (for demonstration only)"""
        time_window = timestamp // 30
        message = time_window.to_bytes(8, byteorder='big')

        key = base64.b32decode(secret)
        hmac_result = hmac.new(key, message, hashlib.sha1).digest()

        offset = hmac_result[-1] & 0xf
        code = ((hmac_result[offset] & 0x7f) << 24 |
                (hmac_result[offset + 1] & 0xff) << 16 |
                (hmac_result[offset + 2] & 0xff) << 8 |
                (hmac_result[offset + 3] & 0xff))

        return code % 1000000


class OAuthClient:
    """Simple OAuth 2.0 client implementation"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_codes = {}  # In production, use proper storage

    def get_authorization_url(self, state: str, scope: str = "read") -> str:
        """Generate authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'state': state
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://oauth-provider.com/authorize?{query_string}"

    def handle_authorization_callback(self, code: str, state: str) -> bool:
        """Handle authorization callback and store auth code"""
        # Verify state parameter to prevent CSRF
        if not self._verify_state(state):
            return False

        self.auth_codes[state] = code
        return True

    def exchange_code_for_token(self, state: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        if state not in self.auth_codes:
            return None

        # In real implementation, make HTTP request to token endpoint
        # This is a simplified demonstration
        auth_code = self.auth_codes[state]

        # Simulate token response
        return {
            'access_token': f"oat_{secrets.token_urlsafe(24)}",
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': f"ort_{secrets.token_urlsafe(24)}",
            'scope': 'read'
        }

    def _verify_state(self, state: str) -> bool:
        """Verify state parameter (implementation depends on state storage)"""
        return True  # Simplified


class AuthenticationService:
    """Comprehensive authentication service combining multiple methods"""

    def __init__(self):
        self.jwt_manager = JWTAuthManager(
            secret_key=os.getenv('JWT_SECRET', 'fallback-secret-key'))
        self.session_manager = SessionAuthManager()
        self.api_key_manager = APIKeyAuthManager()
        self.mfa_manager = MFAManager()
        self.users = {}  # In production, use database

    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register new user"""
        if username in self.users:
            return False

        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        self.users[username] = {
            'password_hash': password_hash,
            'email': email,
            'user_id': secrets.token_urlsafe(16),
            'roles': ['user'],
            'mfa_enabled': False,
            'mfa_secret': None
        }

        return True

    def authenticate_password(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with password"""
        if username not in self.users:
            return None

        user = self.users[username]

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return None

        return {
            'user_id': user['user_id'],
            'username': username,
            'roles': user['roles'],
            'mfa_required': user['mfa_enabled']
        }

    def enable_mfa(self, username: str) -> str:
        """Enable MFA for user and return secret"""
        if username not in self.users:
            raise ValueError("User not found")

        secret = self.mfa_manager.generate_totp_secret(username)
        self.users[username]['mfa_enabled'] = True
        self.users[username]['mfa_secret'] = secret

        return secret

    def verify_mfa(self, username: str, code: str) -> bool:
        """Verify MFA code"""
        return self.mfa_manager.verify_totp_code(username, code)


def demonstrate_authentication():
    """Demonstrate various authentication methods"""
    print("=== Authentication Protocols Demo ===\n")

    auth_service = AuthenticationService()

    # 1. User Registration and Password Auth
    print("1. User Registration and Password Authentication")
    auth_service.register_user(
        "alice", "SecurePassword123!", "alice@example.com")

    auth_result = auth_service.authenticate_password(
        "alice", "SecurePassword123!")
    print(f"Authentication successful: {auth_result is not None}")
    if auth_result:
        print(f"User ID: {auth_result['user_id']}")
        print(f"MFA Required: {auth_result['mfa_required']}\n")

    # 2. JWT Tokens
    print("2. JWT Token Authentication")
    jwt_manager = auth_service.jwt_manager

    access_token = jwt_manager.create_access_token(
        user_id="user123",
        username="alice",
        roles=["user", "admin"],
        expires_delta=timedelta(hours=1)
    )

    refresh_token = jwt_manager.create_refresh_token("user123")

    print(f"Access Token: {access_token[:50]}...")
    print(f"Refresh Token: {refresh_token[:50]}...")

    # Verify token
    try:
        payload = jwt_manager.verify_token(access_token)
        print(
            f"Token verified. User: {payload['username']}, Roles: {payload['roles']}\n")
    except ValueError as e:
        print(f"Token verification failed: {e}\n")

    # 3. Session Authentication
    print("3. Session-based Authentication")
    session_id = auth_service.session_manager.create_session(
        "user123",
        {"username": "alice", "roles": ["user"]}
    )

    session_data = auth_service.session_manager.get_session(session_id)
    print(f"Session created: {session_id[:20]}...")
    print(f"Session user: {session_data['user_data']['username']}\n")

    # 4. API Key Authentication
    print("4. API Key Authentication")
    api_key_manager = auth_service.api_key_manager

    api_key = api_key_manager.generate_api_key(
        user_id="user123",
        permissions=["read", "write"],
        description="Test API Key"
    )

    print(f"Generated API Key: {api_key[:30]}...")

    # Validate API key
    key_validation = api_key_manager.validate_api_key(api_key)
    print(f"API Key valid: {key_validation is not None}")
    if key_validation:
        print(
            f"User ID: {key_validation['user_id']}, Permissions: {key_validation['permissions']}\n")

    # 5. Multi-Factor Authentication
    print("5. Multi-Factor Authentication")
    mfa_secret = auth_service.enable_mfa("alice")
    print(f"MFA Secret: {mfa_secret}")

    # In real scenario, user would provide code from authenticator app
    # For demo, we'll skip actual verification
    print("MFA enabled for user 'alice'\n")

    # 6. OAuth 2.0 Client
    print("6. OAuth 2.0 Client")
    oauth_client = OAuthClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="https://app.com/callback"
    )

    auth_url = oauth_client.get_authorization_url(state="random_state_123")
    print(f"Authorization URL: {auth_url[:80]}...\n")


class SecureAPIAuthenticator:
    """Secure API authenticator combining multiple methods"""

    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service

    def authenticate_request(self, request_headers: Dict, request_method: str) -> Dict:
        """Authenticate API request using multiple methods"""
        auth_result = {
            'authenticated': False,
            'user_id': None,
            'username': None,
            'roles': [],
            'auth_method': None,
            'permissions': []
        }

        # Try JWT Bearer token first
        auth_header = request_headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = self.auth_service.jwt_manager.verify_token(token)
                auth_result.update({
                    'authenticated': True,
                    'user_id': payload['sub'],
                    'username': payload['username'],
                    'roles': payload['roles'],
                    'auth_method': 'jwt'
                })
                return auth_result
            except ValueError:
                pass

        # Try API Key
        api_key = request_headers.get('X-API-Key')
        if api_key:
            key_data = self.auth_service.api_key_manager.validate_api_key(
                api_key)
            if key_data:
                auth_result.update({
                    'authenticated': True,
                    'user_id': key_data['user_id'],
                    'roles': ['api_user'],
                    'auth_method': 'api_key',
                    'permissions': key_data['permissions']
                })
                return auth_result

        # Try Session
        session_id = request_headers.get('X-Session-ID')
        if session_id:
            session_data = self.auth_service.session_manager.get_session(
                session_id)
            if session_data:
                auth_result.update({
                    'authenticated': True,
                    'user_id': session_data['user_id'],
                    'username': session_data['user_data']['username'],
                    'roles': session_data['user_data']['roles'],
                    'auth_method': 'session'
                })
                return auth_result

        return auth_result


if __name__ == '__main__':
    demonstrate_authentication()

    print("=== Secure API Authentication Demo ===")
    auth_service = AuthenticationService()
    authenticator = SecureAPIAuthenticator(auth_service)

    # Test different authentication methods
    test_cases = [
        {
            'name': 'JWT Authentication',
            'headers': {
                'Authorization': 'Bearer ' + auth_service.jwt_manager.create_access_token(
                    'test_user', 'testuser', ['user']
                )
            }
        },
        {
            'name': 'API Key Authentication',
            'headers': {
                'X-API-Key': auth_service.api_key_manager.generate_api_key('test_user', ['read'])
            }
        },
        {
            'name': 'Invalid Authentication',
            'headers': {
                'Authorization': 'Bearer invalid_token'
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        result = authenticator.authenticate_request(
            test_case['headers'], 'GET')
        print(f"  Authenticated: {result['authenticated']}")
        if result['authenticated']:
            print(f"  Method: {result['auth_method']}")
            print(f"  User: {result.get('username', 'N/A')}")
            print(f"  Roles: {result['roles']}")
