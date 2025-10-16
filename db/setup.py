import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema.models import Base, Message  # Import Message model for table creation

load_dotenv()

def get_database_url():
    """Get database URL from environment variables"""
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '8111')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'password')
    database = os.getenv('DB_NAME', 'vector_db')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def create_database_and_table():
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        session.commit()
        
        Base.metadata.create_all(engine)
        session.close()
        
    except Exception as e:
        print(f"Error creating database and table: {e}")

def get_session():
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    create_database_and_table()