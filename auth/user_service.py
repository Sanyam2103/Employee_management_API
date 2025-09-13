from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from app.database import get_database
from app.models import UserCreate, User
from .auth_handler import get_password_hash, verify_password
from datetime import datetime
from typing import Optional

def get_user_collection() -> Collection:
    """Get MongoDB users collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not established. get_database() returned None.")
    return db["users"]

def create_user(user_data: UserCreate) -> dict:
    """
    Create a new user account
    
    Args:
        user_data: User registration data
    
    Returns:
        Created user document
    
    Raises:
        Exception: If username/email already exists
    """
    collection = get_user_collection()
    
    # Check if username already exists
    if collection.find_one({"username": user_data.username}):
        raise Exception("Username already exists")
    
    # Check if email already exists
    if collection.find_one({"email": user_data.email}):
        raise Exception("Email already registered")
    
    # Hash password for secure storage
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,  # Store hashed password, never plain text
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert into database
    result = collection.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)
    
    return user_doc

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate user credentials
    
    Args:
        username: Username to authenticate
        password: Plain text password
    
    Returns:
        User document if authentication successful, None otherwise
    """
    collection = get_user_collection()
    
    # Find user by username
    user = collection.find_one({"username": username})
    if not user:
        return None
    
    # Verify password against stored hash
    if not verify_password(password, user["hashed_password"]):
        return None
    
    # Check if user is active
    if not user.get("is_active", True):
        return None
    
    return user

def get_user_by_username(username: str) -> Optional[dict]:
    """
    Get user by username
    
    Args:
        username: Username to lookup
    
    Returns:
        User document or None if not found
    """
    collection = get_user_collection()
    return collection.find_one({"username": username})

def create_default_admin():
    """Create default admin user if none exists"""
    collection = get_user_collection()
    
    # Check if any admin exists
    admin_exists = collection.find_one({"role": "admin"})
    if admin_exists:
        return
    
    # Create default admin
    admin_data = UserCreate(
        username="admin",
        email="admin@company.com",
        password="admin123",  # Change this in production!
        role="admin"
    )
    
    try:
        create_user(admin_data)
        print("✅ Default admin user created: admin/admin123")
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")
