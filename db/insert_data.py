import os
import sys
from dotenv import load_dotenv
from datetime import datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema.models import Base, Message  # noqa: F401
from db.setup import get_database_url, get_session

from utils.embedding import EmbeddingGenerator
load_dotenv()

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
        
        # Create new message object
        new_message = Message(
            channel_id=str(message_data['channel_id']).strip(),
            user_id=str(message_data['user_id']).strip(),
            message=str(message_data['message']).strip(),
            embedding=embedding,
            handled=handled,
            message_metadata=metadata,
            mention_bot=mention_bot
        )
        
        # Insert message with embedding and new fields
        if created_at:
            new_message.created_at = created_at
        
        # Get database session
        session = get_session()
        
        try:
            # Add and commit the new message
            session.add(new_message)
            session.commit()
            
            # Refresh to get the ID and final created_at
            session.refresh(new_message)
            
            print(f"Message ingested successfully!")
            print(f"   ID: {new_message.id}")
            print(f"   Channel: {message_data['channel_id']}")
            print(f"   User: {message_data['user_id']}")
            print(f"   Created: {new_message.created_at}")
            print(f"   Embedding: {len(embedding)} dimensions")
            print(f"   Handled: {handled}")
            print(f"   Metadata: {metadata}")
            print(f"   Mention Bot: {mention_bot}")
            
        finally:
            session.close()
        
        return True
        
    except Exception as e:
        print(f"Error ingesting message: {e}")
        return False

def ingest_batch(messages_list):
    
    if not messages_list:
        print("Error: No messages provided")
        return {'success': 0, 'errors': ['No messages provided']}
    
    success_count = 0
    errors = []
    for i, ele in enumerate(messages_list):
        if ingest(ele):
            success_count += 1
        else:
            errors.append(f"Message {i+1}: Ingest failed")
    
    print(f"Batch ingest completed!")
    print(f"   Successfully ingested: {success_count}/{len(messages_list)} messages")
    if errors:
        print(f"   Errors: {len(errors)}")
    
    return {
        'success': success_count,
        'total_valid': len(messages_list),
        'total_attempted': len(messages_list),
        'errors': errors
    }

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