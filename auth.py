import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from supabase import create_client, Client
from typing import Optional, Dict, Any

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
JWT_SECRET = os.getenv("JWT_SECRET", "your-jwt-secret")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AuthManager:
    def __init__(self):
        self.supabase = supabase
        
    async def register_user(self, email: str, password: str, user_data: Dict = None) -> Dict:
        """Register a new user"""
        try:
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user in Supabase
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            
            if response.user:
                # Store additional user data
                user_profile = {
                    "id": response.user.id,
                    "email": email,
                    "created_at": datetime.utcnow().isoformat(),
                    "role": "user",
                    "quantum_access": True,
                    "affiliate_access": True,
                    "autonomous_mode": True,
                    **user_data or {}
                }
                
                # Insert into profiles table
                self.supabase.table('profiles').insert(user_profile).execute()
                
                return {
                    "success": True,
                    "user": response.user,
                    "message": "User registered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Registration failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def login_user(self, email: str, password: str) -> Dict:
        """Login user and return JWT token"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Generate JWT token
                token_payload = {
                    "user_id": response.user.id,
                    "email": email,
                    "exp": datetime.utcnow() + timedelta(hours=24)
                }
                
                token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
                
                return {
                    "success": True,
                    "token": token,
                    "user": response.user,
                    "message": "Login successful"
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from database"""
        try:
            response = self.supabase.table('profiles').select('*').eq('id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None

# Global auth manager instance
auth_manager = AuthManager()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get user role from database
            user_id = request.user['user_id']
            user_profile = auth_manager.supabase.table('profiles').select('role').eq('id', user_id).execute()
            
            if not user_profile.data or user_profile.data[0]['role'] != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
