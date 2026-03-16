import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_tables():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check all schemas
        result = conn.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """))
        print("Schemas in Neon:")
        for row in result:
            print(f"  {row[0]}")
        
        # Check all tables
        result = conn.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
        """))
        print("\nAll tables:")
        for row in result:
            print(f"  {row[0]}.{row[1]}")

if __name__ == "__main__":
    check_tables()