import psycopg2
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
import json

# Import embeddings from utils
from utils.embedding import EmbeddingGenerator

load_dotenv()

def get_db_connection():
    """Get database connection with parameters"""
    connection_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'vector_db')
    }
    return psycopg2.connect(**connection_params)

def ingest(message_data):
    """
    Ingest a single message with real OpenAI embedding
    
    Args:
        message_data (dict): Dictionary containing:
            - channel_id (str): Channel identifier
            - user_id (str): User identifier  
            - message (str): Message content
            - created_at (str or datetime, optional): Message timestamp
                If not provided, uses current timestamp
                Format: 'YYYY-MM-DD HH:MM:SS' or datetime object
            - handled (bool, optional): Whether message has been handled
            - metadata (dict, optional): Additional metadata as dictionary
            - mention_bot (bool, optional): Whether message mentions the bot
    
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        message = {
            'channel_id': 'general',
            'user_id': 'alice_123',
            'message': 'Hello everyone, how is your day going?',
            'created_at': '2024-01-15 14:30:00',  # Optional
            'handled': False,  # Optional
            'metadata': {'source': 'slack'},  # Optional
            'mention_bot': True  # Optional
        }
        success = ingest(message)
    """
    
    # Validate input data
    required_fields = ['channel_id', 'user_id', 'message']
    for field in required_fields:
        if field not in message_data:
            print(f"Error: Missing required field: {field}")
            return False
        if not message_data[field] or not str(message_data[field]).strip():
            print(f"Error: Empty value for required field: {field}")
            return False
    
    try:
        # Initialize embedding generator
        embedding_generator = EmbeddingGenerator()
        
        # Generate embedding for the message
        print(f"Generating embedding for message: '{message_data['message'][:50]}...'")
        embedding = embedding_generator.get_embedding(message_data['message'])
        
        # Handle created_at timestamp
        created_at = None
        if 'created_at' in message_data and message_data['created_at']:
            if isinstance(message_data['created_at'], str):
                # Parse string timestamp
                try:
                    created_at = datetime.strptime(message_data['created_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        # Try ISO format
                        created_at = datetime.fromisoformat(message_data['created_at'].replace('Z', '+00:00'))
                    except ValueError:
                        print(f"Warning: Invalid created_at format, using current timestamp")
                        created_at = None
            elif isinstance(message_data['created_at'], datetime):
                created_at = message_data['created_at']
            else:
                print(f"Warning: Invalid created_at type, using current timestamp")
        
        # Handle new fields with defaults
        handled = message_data.get('handled', False)
        metadata = message_data.get('metadata', {})
        mention_bot = message_data.get('mention_bot', False)
        
        # Validate metadata is a dictionary
        if not isinstance(metadata, dict):
            print(f"Warning: metadata must be a dictionary, using empty dict")
            metadata = {}
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert message with embedding and new fields
        if created_at:
            insert_query = """
            INSERT INTO messages (channel_id, user_id, message, embedding, created_at, handled, metadata, mention_bot)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """
            cursor.execute(insert_query, (
                str(message_data['channel_id']).strip(),
                str(message_data['user_id']).strip(),
                str(message_data['message']).strip(),
                embedding,
                created_at,
                handled,
                json.dumps(metadata),
                mention_bot
            ))
        else:
            insert_query = """
            INSERT INTO messages (channel_id, user_id, message, embedding, handled, metadata, mention_bot)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
            """
            cursor.execute(insert_query, (
                str(message_data['channel_id']).strip(),
                str(message_data['user_id']).strip(),
                str(message_data['message']).strip(),
                embedding,
                handled,
                json.dumps(metadata),
                mention_bot
            ))
        
        # Get the inserted record details
        result = cursor.fetchone()
        message_id, final_created_at = result
        
        conn.commit()
        
        print(f"Message ingested successfully!")
        print(f"   ID: {message_id}")
        print(f"   Channel: {message_data['channel_id']}")
        print(f"   User: {message_data['user_id']}")
        print(f"   Created: {final_created_at}")
        print(f"   Embedding: {len(embedding)} dimensions")
        print(f"   Handled: {handled}")
        print(f"   Metadata: {metadata}")
        print(f"   Mention Bot: {mention_bot}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error ingesting message: {e}")
        return False

def ingest_batch(messages_list):
    """
    Ingest multiple messages efficiently with batch embedding generation
    
    Args:
        messages_list (list): List of dictionaries, each containing:
            - channel_id (str): Channel identifier
            - user_id (str): User identifier
            - message (str): Message content
            - created_at (str or datetime, optional): Message timestamp
            - handled (bool, optional): Whether message has been handled
            - metadata (dict, optional): Additional metadata as dictionary
            - mention_bot (bool, optional): Whether message mentions the bot
    
    Returns:
        dict: Results with success count and any errors
        
    Example:
        messages = [
            {'channel_id': 'general', 'user_id': 'alice', 'message': 'Hello!', 'created_at': '2024-01-15 10:00:00', 'handled': False},
            {'channel_id': 'tech', 'user_id': 'bob', 'message': 'How does pgvector work?', 'metadata': {'urgent': True}}
        ]
        results = ingest_batch(messages)
    """
    
    if not messages_list:
        print("Error: No messages provided")
        return {'success': 0, 'errors': ['No messages provided']}
    
    # Validate all messages first
    valid_messages = []
    errors = []
    required_fields = ['channel_id', 'user_id', 'message']
    
    for i, msg in enumerate(messages_list):
        # Check for required fields
        missing_fields = [field for field in required_fields if field not in msg or not str(msg[field]).strip()]
        if missing_fields:
            errors.append(f"Message {i+1}: Missing or empty fields: {missing_fields}")
            continue
        
        # Handle created_at validation
        if 'created_at' in msg and msg['created_at']:
            if isinstance(msg['created_at'], str):
                try:
                    datetime.strptime(msg['created_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"Message {i+1}: Invalid created_at format")
                        continue
            elif not isinstance(msg['created_at'], datetime):
                errors.append(f"Message {i+1}: created_at must be string or datetime")
                continue
        
        valid_messages.append(msg)
    
    if not valid_messages:
        print(f"Error: No valid messages to ingest")
        return {'success': 0, 'errors': errors}
    
    try:
        # Initialize embedding generator
        embedding_generator = EmbeddingGenerator()
        
        # Extract messages for batch embedding generation
        messages_text = [msg['message'] for msg in valid_messages]
        
        print(f"Generating embeddings for {len(messages_text)} messages...")
        embeddings = embedding_generator.get_embeddings_batch(messages_text)
        
        if len(embeddings) != len(valid_messages):
            raise Exception(f"Embedding count mismatch: got {len(embeddings)}, expected {len(valid_messages)}")
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert all messages
        success_count = 0
        for i, (msg, embedding) in enumerate(zip(valid_messages, embeddings)):
            try:
                # Handle created_at for this message
                created_at = None
                if 'created_at' in msg and msg['created_at']:
                    if isinstance(msg['created_at'], str):
                        try:
                            created_at = datetime.strptime(msg['created_at'], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            created_at = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
                    elif isinstance(msg['created_at'], datetime):
                        created_at = msg['created_at']
                
                # Handle new fields with defaults
                handled = msg.get('handled', False)
                metadata = msg.get('metadata', {})
                mention_bot = msg.get('mention_bot', False)
                
                # Validate metadata is a dictionary
                if not isinstance(metadata, dict):
                    metadata = {}
                
                # Choose appropriate insert query
                if created_at:
                    insert_query = """
                    INSERT INTO messages (channel_id, user_id, message, embedding, created_at, handled, metadata, mention_bot)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        str(msg['channel_id']).strip(),
                        str(msg['user_id']).strip(),
                        str(msg['message']).strip(),
                        embedding,
                        created_at,
                        handled,
                        json.dumps(metadata),
                        mention_bot
                    ))
                else:
                    insert_query = """
                    INSERT INTO messages (channel_id, user_id, message, embedding, handled, metadata, mention_bot)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        str(msg['channel_id']).strip(),
                        str(msg['user_id']).strip(),
                        str(msg['message']).strip(),
                        embedding,
                        handled,
                        json.dumps(metadata),
                        mention_bot
                    ))
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Message {i+1}: Database insert failed - {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Batch ingest completed!")
        print(f"   Successfully ingested: {success_count}/{len(valid_messages)} messages")
        if errors:
            print(f"   Errors: {len(errors)}")
        
        return {
            'success': success_count,
            'total_valid': len(valid_messages),
            'total_attempted': len(messages_list),
            'errors': errors
        }
        
    except Exception as e:
        print(f"Error: Batch ingest failed: {e}")
        return {'success': 0, 'errors': errors + [str(e)]}

def insert_sample_messages():
    """Insert sample messages with dummy embeddings (original function)"""
    
    connection_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'vector_db')
    }
    
    # Sample data
    sample_messages = [
        {
            'channel_id': 'channel_001',
            'user_id': 'user_123',
            'message': 'Hello, how are you today?',
            'embedding': np.random.rand(1536).tolist()  # Dummy embedding
        },
        {
            'channel_id': 'channel_001',
            'user_id': 'user_456',
            'message': 'I am doing great, thanks for asking!',
            'embedding': np.random.rand(1536).tolist()  # Dummy embedding
        },
        {
            'channel_id': 'channel_002',
            'user_id': 'user_789',
            'message': 'What is the weather like today?',
            'embedding': np.random.rand(1536).tolist()  # Dummy embedding
        }
    ]
    
    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Insert sample data
        insert_query = """
        INSERT INTO messages (channel_id, user_id, message, embedding)
        VALUES (%s, %s, %s, %s)
        """
        
        for msg in sample_messages:
            cursor.execute(insert_query, (
                msg['channel_id'],
                msg['user_id'], 
                msg['message'],
                msg['embedding']
            ))
        
        conn.commit()
        print(f"Inserted {len(sample_messages)} sample messages")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage and testing
if __name__ == "__main__":
    print("Message Ingestion System")
    print("=" * 50)
    
    # Example 1: Single message ingest
    # print("\nTesting single message ingest:")
    # single_message = {
    #     'channel_id': 'general',
    #     'user_id': 'alice_123',
    #     'message': 'I like pizza',
    #     'created_at': '2024-01-15 09:30:00'  # Optional timestamp
    # }
    
    # success = ingest(single_message)
    # print(f"Single ingest result: {'Success' if success else 'Failed'}")
    
    # # Example 2: Batch message ingest
    print("\nTesting batch message ingest:")
    batch_messages = [
        {
            'channel_id': 'general',
            'user_id': 'bob_456',
            'message': 'python is a great language',
            'created_at': '2024-01-15 10:15:00',
            'handled': False,
            'metadata': {'topic': 'programming', 'sentiment': 'positive'},
            'mention_bot': False
        },
        {
            'channel_id': 'general',
            'user_id': 'charlie_789',
            'message': 'python is not that fast but it is easy to learn',
            'created_at': '2024-01-15 10:17:30',
            'handled': True,
            'metadata': {'topic': 'programming', 'response_needed': False}
        },
        {
            'channel_id': 'general',
            'user_id': 'david_101',
            'message': 'java is a great language',
            'mention_bot': True,
            'metadata': {'urgent': True}
            # No created_at - will use current timestamp
        },
        {
            'channel_id': 'general',
            'user_id': 'eve_202',
            'message': 'java is fast',
            'created_at': datetime(2024, 1, 15, 14, 30, 0),  # datetime object
            'handled': False,
            'mention_bot': False
        }
    ]
    
    results = ingest_batch(batch_messages)
    print(f"Batch ingest results:")
    print(f"  Successful: {results['success']}")
    print(f"  Total processed: {results.get('total_valid', 0)}")
    if results.get('errors'):
        print(f"  Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"    - {error}")
    
    print(f"\nIngestion testing completed!")