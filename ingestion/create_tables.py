import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_tables():
    """Read schema.sql and execute it against Neon database"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Read the schema.sql file
        with open("ingestion/schema.sql", "r") as f:
            schema = f.read()
        
        # Execute the schema
        with engine.connect() as connection:
            connection.execute(text(schema))
            connection.commit()
            print("All tables created successfully!")
            print("Schemas created: raw, warehouse, ml")
            print("Tables created:")
            print("  - raw.flights")
            print("  - warehouse.fact_flights")
            print("  - ml.features")
            print("Functions created:")
            print("  - delete_old_flights()")
            
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()