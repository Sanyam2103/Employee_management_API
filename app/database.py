from motor.motor_asyncio import AsyncIOMotorClient 
from pymongo import ASCENDING, MongoClient , DESCENDING
import os
from dotenv import load_dotenv

load_dotenv()

client = None
database = None

def connect_to_mongo():
    """Connect to MongoDB and return database instance"""
    global client, database
    
    # Get MongoDB URL from environment variable
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME")
    collection_name = os.getenv("COLLECTION_NAME", "employees")
    print(f"Connecting to MongoDB at: {mongodb_url}")
    print(f"Using database: {database_name}")
    
    # Create MongoDB client
    if not mongodb_url:
        raise ValueError("MONGODB_URL environment variable is not set.")
    if not database_name:
        raise ValueError("DATABASE_NAME environment variable is not set.")
    client = MongoClient(mongodb_url)

    
    # Get database instance
    database = client[database_name]
    
    database[collection_name].create_index(
            [("employee_id", ASCENDING)], unique=True
        )
    database[collection_name].create_index(
        [("department", ASCENDING)], 
        name="department_index"
    )
    
    # Create compound index for department + joining_date queries
    database[collection_name].create_index(
        [("department", ASCENDING), ("joining_date", DESCENDING)], 
        name="dept_join_date_compound"
    )
    
    # Create text index for skill searching
    database[collection_name].create_index(
        [("skills", "text")], 
        name="skills_text_search"
    )
    
    # Create index on name for sorting
    database[collection_name].create_index(
        [("name", ASCENDING)], 
        name="name_sort_index"
    )
        
    print("✅ All indexes created successfully")
        
    print("✅ Connected to MongoDB successfully!")
    return database

def close_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")

def get_database():
    if database is None:
        connect_to_mongo()
    return database

def get_collection():
    """Get employees database[collection_name]"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not established. get_database() returned None.")
    collection_name = os.getenv("COLLECTION_NAME", "employees")
    
    return db[collection_name]