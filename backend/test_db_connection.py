"""
Test script to verify database connection
This can be run locally to test your Supabase connection string
"""
import os
from sqlalchemy import create_engine
from config import Config

def test_db_connection():
    try:
        # Get database URL from environment or config
        database_url = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
        
        print(f"Testing connection to: {database_url}")
        
        # Create engine and test connection
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("Database connection successful!")
            print(f"Connection result: {result.fetchone()}")
            return True
            
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("\nConnection test passed! Your database configuration is correct.")
    else:
        print("\nConnection test failed! Please check your database configuration.")