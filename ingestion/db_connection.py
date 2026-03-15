import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    """Create and return database engine"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in .env file")
    
    engine = create_engine(DATABASE_URL)
    return engine

def test_connection():
    """Test if database connection works"""
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected successfully!")
            print(f"PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()