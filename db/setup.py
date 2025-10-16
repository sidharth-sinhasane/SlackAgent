import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database_and_table():
    """Create database, enable pgvector extension, and create the messages table"""
    
    # Database connection parameters
    connection_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '8111'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'vector_db')
    }
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**connection_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Enable pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("pgvector extension enabled")
        
        # Create the messages table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            channel_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            embedding VECTOR(1536),  -- OpenAI embeddings are 1536 dimensions
            handled BOOLEAN DEFAULT FALSE,
            metadata JSONB DEFAULT '{}',
            mention_bot BOOLEAN DEFAULT FALSE
        );
        """
        
        cursor.execute(create_table_query)
        print("Messages table created successfully")
        
        # Create index on embedding column for better search performance
        index_query = """
        CREATE INDEX IF NOT EXISTS messages_embedding_idx 
        ON messages USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100);
        """
        
        cursor.execute(index_query)
        print("Vector index created for better search performance")
        
        # Create additional indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);")
        print("Additional indexes created")
        
        cursor.close()
        conn.close()
        print("Database setup completed successfully!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def create_thread_table():
    """Create the threads table with embedding support and proper indexing"""
    
    connection_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '8111'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'vector_db')
    }
    
    try:
        conn = psycopg2.connect(**connection_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create the threads table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS threads (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255) NOT NULL,
            message_ids JSONB DEFAULT '[]',
            description TEXT,
            embedding VECTOR(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        print("Threads table created successfully")
        
        # Create vector index on embedding column
        vector_index_query = """
        CREATE INDEX IF NOT EXISTS threads_embedding_idx 
        ON threads USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100);
        """
        
        cursor.execute(vector_index_query)
        print("Vector index created for threads embedding column")
        
        # Create B-tree indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_thread_id ON threads(thread_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_created_at ON threads(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON threads(updated_at);")
        
        # Create GIN index for JSONB message_ids array
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_message_ids ON threads USING GIN (message_ids);")
        
        print("Additional indexes created for threads table")
        
        cursor.close()
        conn.close()
        print("Threads table setup completed successfully!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def delete_thread_table():
    """Delete the threads table and all its data"""
    
    connection_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '8111'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'vector_db')
    }
    
    try:
        conn = psycopg2.connect(**connection_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop the threads table
        drop_table_query = "DROP TABLE IF EXISTS threads CASCADE;"
        
        cursor.execute(drop_table_query)
        print("Threads table deleted successfully")
        
        cursor.close()
        conn.close()
        print("Threads table deletion completed successfully!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    create_database_and_table()
    create_thread_table()