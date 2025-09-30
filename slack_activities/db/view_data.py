import psycopg2
import os
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
import numpy as np

load_dotenv()

class MessageViewer:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'database': os.getenv('DB_NAME', 'vector_db')
        }
    
    def get_connection(self):
        """Get database connection with pgvector support"""
        conn = psycopg2.connect(**self.connection_params)
        register_vector(conn)
        return conn
    
    def view_all_messages(self):
        """View all messages in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, channel_id, user_id, message, created_at 
                FROM messages 
                ORDER BY created_at DESC
            """)
            
            messages = cursor.fetchall()
            
            print("\nAll Messages:")
            print("-" * 80)
            for msg in messages:
                print(f"ID: {msg[0]}")
                print(f"Channel: {msg[1]}")
                print(f"User: {msg[2]}")
                print(f"Message: {msg[3]}")
                print(f"Created: {msg[4]}")
                print("-" * 40)
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
    
    def search_similar_messages(self, query_embedding, limit=5):
        """Search for messages similar to query embedding"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert query embedding to pgvector format
            query_vector = np.array(query_embedding)
            
            cursor.execute("""
                SELECT id, channel_id, user_id, message, created_at,
                       embedding <=> %s AS distance
                FROM messages
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (query_vector, query_vector, limit))
            
            results = cursor.fetchall()
            
            print(f"\nTop {limit} Similar Messages:")
            print("-" * 80)
            for result in results:
                print(f"ID: {result[0]} (Distance: {result[5]:.4f})")
                print(f"Channel: {result[1]}")
                print(f"User: {result[2]}")
                print(f"Message: {result[3]}")
                print(f"Created: {result[4]}")
                print("-" * 40)
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
    
    def get_messages_by_channel(self, channel_id):
        """Get all messages from a specific channel"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, message, created_at 
                FROM messages 
                WHERE channel_id = %s
                ORDER BY created_at DESC
            """, (channel_id,))
            
            messages = cursor.fetchall()
            
            print(f"\nMessages from channel '{channel_id}':")
            print("-" * 80)
            for msg in messages:
                print(f"ID: {msg[0]}")
                print(f"User: {msg[1]}")
                print(f"Message: {msg[2]}")
                print(f"Created: {msg[3]}")
                print("-" * 40)
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
    
    def get_table_stats(self):
        """Get basic statistics about the messages table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_count = cursor.fetchone()[0]
            
            # Get unique channels
            cursor.execute("SELECT COUNT(DISTINCT channel_id) FROM messages")
            unique_channels = cursor.fetchone()[0]
            
            # Get unique users
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM messages")
            unique_users = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM messages")
            date_range = cursor.fetchone()
            
            print("\nDatabase Statistics:")
            print("-" * 40)
            print(f"Total Messages: {total_count}")
            print(f"Unique Channels: {unique_channels}")
            print(f"Unique Users: {unique_users}")
            print(f"Date Range: {date_range[0]} to {date_range[1]}")
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")

def main():
    """Main function to demonstrate viewing capabilities"""
    viewer = MessageViewer()
    
    # Show table statistics
    viewer.get_table_stats()
    
    # View all messages
    viewer.view_all_messages()
    
    # View messages from specific channel
    viewer.get_messages_by_channel('channel_001')
    
    # Example similarity search with dummy embedding
    dummy_query = np.random.rand(1536).tolist()
    viewer.search_similar_messages(dummy_query, limit=3)

if __name__ == "__main__":
    main()