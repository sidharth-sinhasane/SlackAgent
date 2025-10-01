import psycopg2
import os
import sys
from dotenv import load_dotenv
from typing import List, Dict, Optional
import numpy as np
# Import embeddings from utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding import EmbeddingGenerator

load_dotenv()

def get_db_connection():
    """Get database connection with parameters"""
    connection_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '8111'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
        'database': os.getenv('DB_NAME', 'vector_db')
    }
    return psycopg2.connect(**connection_params)

def search(query: str, channel_id: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[str]:
    """
    Search for semantically similar messages in a specific channel
    
    Args:
        query (str): The search query text
        channel_id (str): Channel to search within
        top_k (Optional[int]): Number of top results to return. If None, defaults to 100 or 
                              all results when using threshold
        threshold (Optional[float]): Maximum distance threshold. If provided, only returns 
                                   results with distance < threshold. If None, returns top_k results.
    
    Returns:
        List[str]: List of message strings, ordered by similarity (most similar first)
        
    Example:
        # Get top 5 results
        results = search("how's the weather", "general", top_k=5)
        
        # Get only results with distance < 0.5
        results = search("how's the weather", "general", threshold=0.5)
        
        # Get top 3 results with distance < 0.5
        results = search("how's the weather", "general", top_k=3, threshold=0.5)
        # Returns: ["What's the weather like today?", "Beautiful sunny day!", ...]
    """
    
    # Validate inputs
    if not query or not query.strip():
        print("Query cannot be empty")
        return []
    
    # Set default top_k if not provided
    if top_k is None:
        top_k = 100 if threshold is None else 1000  # Higher limit when using threshold
    
    if top_k <= 0:
        print("top_k must be greater than 0")
        return []
    
    if not channel_id or not channel_id.strip():
        print("channel_id cannot be empty")
        return []
    
    try:
        # Generate embedding for the query
        print(f"Generating embedding for query: '{query[:50]}...'")
        embedding_generator = EmbeddingGenerator()
        print(f"Embedding generator: {embedding_generator}","_"*100)
        query_embedding = embedding_generator.get_embedding(query.strip())
        print(f"Query embedding: {query_embedding}","_"*100)
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        print(f"connection","_"*100)
        
        # Search for similar messages in the specified channel
        if threshold is not None:
            search_query = """
            SELECT id, message, created_at, embedding <=> (%s)::vector AS distance
            FROM messages
            WHERE channel_id = %s AND embedding <=> (%s)::vector < %s
            ORDER BY distance
            LIMIT %s;
            """
            query_params = (query_embedding, channel_id.strip(), query_embedding, threshold, top_k)
        else:
            search_query = """
            SELECT id, message, created_at, embedding <=> (%s)::vector AS distance
            FROM messages
            WHERE channel_id = %s
            ORDER BY distance
            LIMIT %s;
            """
            query_params = (query_embedding, channel_id.strip(), top_k)
        
        print(f"search query","_"*100)

        cursor.execute(search_query, query_params)
        print(f"cursor","_"*100)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        print(f"conn closed","_"*100)
        
        return results
        
    except Exception as e:
        print(f"Search failed: {e}")
        print(f"Search failed: {e}","_"*100)
        return []

def search_messages_with_neighbors(query: str, channel_id: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    results = search(query, channel_id, top_k, threshold)

    unique_messages = {}  # {id: message}

    for result in results:
        msg_id, message, created_at, distance = result
        unique_messages[msg_id] = message

    for result in results:
        msg_id, message, created_at, distance = result

        try:
            cursor.execute("""
                SELECT id, message
                FROM messages
                WHERE channel_id = %s AND created_at > %s 
                ORDER BY created_at ASC
                LIMIT 5
            """, (channel_id, created_at))

            neighbors = cursor.fetchall()
            for row in neighbors:
                neighbor_id, neighbor_message = row
                if neighbor_id not in unique_messages:
                    unique_messages[neighbor_id] = neighbor_message

        except Exception as e:
            print(f"Search failed: {e}")
            continue
    
    try:    
        cursor.execute("""
            SELECT id, message
            FROM messages
            WHERE channel_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (channel_id,))

        last_messages = cursor.fetchall()
        for row in last_messages:
            last_id, last_message = row
            if last_id not in unique_messages:
                unique_messages[last_id] = last_message
        print(f"Last messages: {last_messages}_____________________________________________________")
    except Exception as e:
        print(f"Failed to fetch last messages: {e}")

    cursor.close()
    conn.close()
    
    return list(unique_messages.values())

    
def search_detailed(query: str, channel_id: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[Dict]:
    """
    Search for semantically similar messages with detailed results
    
    Args:
        query (str): The search query text
        channel_id (str): Channel to search within
        top_k (Optional[int]): Number of top results to return. If None, defaults to 100 or 
                              all results when using threshold
        threshold (Optional[float]): Maximum distance threshold. If provided, only returns 
                                   results with distance < threshold. If None, returns top_k results.
    
    Returns:
        List[Dict]: List of dictionaries with detailed message information
        Each dict contains: id, channel_id, user_id, message, created_at, handled, metadata, mention_bot, distance
        
    Example:
        # Get top 3 results with full details
        results = search_detailed("weather today", "general", top_k=3)
        
        # Get only results with distance < 0.4
        results = search_detailed("weather today", "general", threshold=0.4)
        
        # Get top 3 results with distance < 0.4
        results = search_detailed("weather today", "general", top_k=3, threshold=0.4)
        # Returns: [
        #     {
        #         'id': 1, 'channel_id': 'general', 'user_id': 'alice',
        #         'message': 'What\'s the weather like?', 'created_at': '2024-01-15',
        #         'handled': False, 'metadata': {}, 'mention_bot': False, 'distance': 0.123
        #     }, ...
        # ]
    """
    
    # Validate inputs
    if not query or not query.strip():
        print("Query cannot be empty")
        return []
    
    # Set default top_k if not provided
    if top_k is None:
        top_k = 100 if threshold is None else 1000  # Higher limit when using threshold
    
    if top_k <= 0:
        print("top_k must be greater than 0")
        return []
    
    if not channel_id or not channel_id.strip():
        print("channel_id cannot be empty")
        return []
    
    try:
        # Generate embedding for the query
        print(f"Generating embedding for query: '{query[:50]}...'")
        embedding_generator = EmbeddingGenerator()
        query_embedding = embedding_generator.get_embedding(query.strip())
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for similar messages in the specified channel
        if threshold is not None:
            search_query = """
            SELECT id, channel_id, user_id, message, created_at, handled, metadata, mention_bot, embedding <=> (%s)::vector AS distance
            FROM messages
            WHERE channel_id = %s AND embedding <=> (%s)::vector < %s
            ORDER BY distance
            LIMIT %s;
            """
            query_params = (query_embedding, channel_id.strip(), query_embedding, threshold, top_k)
        else:
            search_query = """
            SELECT id, channel_id, user_id, message, created_at, handled, metadata, mention_bot, embedding <=> (%s)::vector AS distance
            FROM messages
            WHERE channel_id = %s
            ORDER BY distance
            LIMIT %s;
            """
            query_params = (query_embedding, channel_id.strip(), top_k)
        
        cursor.execute(search_query, query_params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        detailed_results = []
        for result in results:
            detailed_results.append({
                'id': result[0],
                'channel_id': result[1],
                'user_id': result[2],
                'message': result[3],
                'created_at': result[4],
                'handled': result[5],
                'metadata': result[6] if result[6] else {},
                'mention_bot': result[7],
                'distance': float(result[8])
            })
        
        threshold_msg = f" (threshold < {threshold})" if threshold is not None else ""
        print(f"Found {len(detailed_results)} similar messages in channel '{channel_id}'{threshold_msg}")
        if detailed_results:
            print(f"   Best match distance: {detailed_results[0]['distance']:.4f}")
            print(f"   Worst match distance: {detailed_results[-1]['distance']:.4f}")
            if threshold is not None:
                print(f"   All results below threshold: {threshold}")
        
        cursor.close()
        conn.close()
        
        return detailed_results
        
    except Exception as e:
        print(f"Detailed search failed: {e}")
        return []

def search_all_channels(query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[str]:
    """
    Search for semantically similar messages across all channels
    
    Args:
        query (str): The search query text
        top_k (Optional[int]): Number of top results to return. If None, defaults to 100 or 
                              all results when using threshold
        threshold (Optional[float]): Maximum distance threshold. If provided, only returns 
                                   results with distance < threshold. If None, returns top_k results.
    
    Returns:
        List[str]: List of message strings from all channels, ordered by similarity
        
    Example:
        # Get top 5 results from all channels
        results = search_all_channels("weather today", top_k=5)
        
        # Get only results with distance < 0.3 from all channels
        results = search_all_channels("weather today", threshold=0.3)
        
        # Get top 5 results with distance < 0.3 from all channels
        results = search_all_channels("weather today", top_k=5, threshold=0.3)
    """
    
    # Validate inputs
    if not query or not query.strip():
        print("Query cannot be empty")
        return []
    
    # Set default top_k if not provided
    if top_k is None:
        top_k = 100 if threshold is None else 1000  # Higher limit when using threshold
    
    if top_k <= 0:
        print("top_k must be greater than 0")
        return []
    
    try:
        # Generate embedding for the query
        print(f"Generating embedding for query: '{query[:50]}...'")
        embedding_generator = EmbeddingGenerator()
        query_embedding = embedding_generator.get_embedding(query.strip())
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search across all channels
        if threshold is not None:
            search_query = """
            SELECT channel_id, message, handled, metadata, mention_bot, embedding <=> (%s)::vector AS distance
            FROM messages
            WHERE embedding <=> (%s)::vector < %s
            ORDER BY distance
            LIMIT %s;
            """
            query_params = (query_embedding, query_embedding, threshold, top_k)
        else:
            search_query = """
            SELECT channel_id, message, handled, metadata, mention_bot, embedding <=> (%s)::vector AS distance
            FROM messages
            ORDER BY distance
            LIMIT %s;
            """
            query_params = (query_embedding, top_k)
        
        cursor.execute(search_query, query_params)
        results = cursor.fetchall()
        
        # Extract just the messages
        messages = [result[1] for result in results]
        
        threshold_msg = f" (threshold < {threshold})" if threshold is not None else ""
        print(f"Found {len(messages)} similar messages across all channels{threshold_msg}")
        if results:
            print(f"   Best match distance: {results[0][5]:.4f}")
            print(f"   Results from channels: {set(result[0] for result in results)}")
            print(f"   Handled messages: {sum(1 for result in results if result[2])}")
            print(f"   Bot mentions: {sum(1 for result in results if result[4])}")
            if threshold is not None:
                print(f"   All results below threshold: {threshold}")
        
        cursor.close()
        conn.close()
        
        return messages
        
    except Exception as e:
        print(f"Global search failed: {e}")
        return []

def get_channel_stats(channel_id: str) -> Dict:
    """
    Get statistics for a specific channel
    
    Args:
        channel_id (str): Channel to get stats for
        
    Returns:
        Dict: Statistics including message count, unique users, date range
    """
    
    if not channel_id or not channel_id.strip():
        return {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get channel statistics
        stats_query = """
        SELECT 
            COUNT(*) as total_messages,
            COUNT(DISTINCT user_id) as unique_users,
            MIN(created_at) as earliest_message,
            MAX(created_at) as latest_message,
            COUNT(*) FILTER (WHERE handled = true) as handled_messages,
            COUNT(*) FILTER (WHERE mention_bot = true) as bot_mentions
        FROM messages 
        WHERE channel_id = %s
        """
        
        cursor.execute(stats_query, (channel_id.strip(),))
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            stats = {
                'channel_id': channel_id,
                'total_messages': result[0],
                'unique_users': result[1],
                'earliest_message': result[2],
                'latest_message': result[3],
                'handled_messages': result[4],
                'bot_mentions': result[5]
            }
        else:
            stats = {
                'channel_id': channel_id,
                'total_messages': 0,
                'unique_users': 0,
                'earliest_message': None,
                'latest_message': None,
                'handled_messages': 0,
                'bot_mentions': 0
            }
        
        cursor.close()
        conn.close()
        
        return stats
        
    except Exception as e:
        print(f"Failed to get channel stats: {e}")
        return {}

def list_channels() -> List[str]:
    """
    Get list of all available channels
    
    Returns:
        List[str]: List of channel IDs that have messages
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT DISTINCT channel_id, COUNT(*) as message_count
        FROM messages 
        GROUP BY channel_id 
        ORDER BY message_count DESC
        """)
        
        results = cursor.fetchall()
        channels = [result[0] for result in results]
        
        print(f"Found {len(channels)} channels with messages:")
        for result in results:
            print(f"   • {result[0]}: {result[1]} messages")
        
        cursor.close()
        conn.close()
        
        return channels
        
    except Exception as e:
        print(f"Failed to list channels: {e}")
        return []

def search_with_filters(query: str, top_k: Optional[int] = None, channel_id: str = None, handled: bool = None, mention_bot: bool = None, threshold: Optional[float] = None) -> List[Dict]:
    """
    Search for semantically similar messages with filtering options
    
    Args:
        query (str): The search query text
        top_k (Optional[int]): Number of top results to return. If None, defaults to 100 or 
                              all results when using threshold
        channel_id (str, optional): Channel to search within, if None searches all channels
        handled (bool, optional): Filter by handled status
        mention_bot (bool, optional): Filter by mention_bot status
        threshold (Optional[float]): Maximum distance threshold. If provided, only returns 
                                   results with distance < threshold. If None, returns top_k results.
    
    Returns:
        List[Dict]: List of dictionaries with detailed message information
        Each dict contains: id, channel_id, user_id, message, created_at, handled, metadata, mention_bot, distance
        
    Example:
        # Search for unhandled messages mentioning bot in general channel
        results = search_with_filters("help me", channel_id="general", handled=False, mention_bot=True)
        
        # Search with distance threshold
        results = search_with_filters("help me", threshold=0.4, handled=False)
        
        # Search with top_k and threshold
        results = search_with_filters("help me", top_k=5, threshold=0.4, handled=False)
    """
    
    # Validate inputs
    if not query or not query.strip():
        print("Query cannot be empty")
        return []
    
    # Set default top_k if not provided
    if top_k is None:
        top_k = 100 if threshold is None else 1000  # Higher limit when using threshold
    
    if top_k <= 0:
        print("top_k must be greater than 0")
        return []
    
    try:
        # Generate embedding for the query
        print(f"Generating embedding for query: '{query[:50]}...'")
        embedding_generator = EmbeddingGenerator()
        query_embedding = embedding_generator.get_embedding(query.strip())
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic query with filters
        base_query = """
        SELECT id, channel_id, user_id, message, created_at, handled, metadata, mention_bot, embedding <=> (%s)::vector AS distance
        FROM messages
        WHERE 1=1
        """
        
        params = [query_embedding]
        filters = []
        
        if channel_id:
            filters.append("AND channel_id = %s")
            params.append(channel_id.strip())
        
        if handled is not None:
            filters.append("AND handled = %s")
            params.append(handled)
        
        if mention_bot is not None:
            filters.append("AND mention_bot = %s")
            params.append(mention_bot)
        
        if threshold is not None:
            filters.append("AND embedding <=> (%s)::vector < %s")
            params.append(query_embedding)
            params.append(threshold)
        
        search_query = base_query + " ".join(filters) + """
        ORDER BY distance
        LIMIT %s;
        """
        params.append(top_k)
        
        cursor.execute(search_query, params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        detailed_results = []
        for result in results:
            detailed_results.append({
                'id': result[0],
                'channel_id': result[1],
                'user_id': result[2],
                'message': result[3],
                'created_at': result[4],
                'handled': result[5],
                'metadata': result[6] if result[6] else {},
                'mention_bot': result[7],
                'distance': float(result[8])
            })
        
        filter_desc = []
        if channel_id:
            filter_desc.append(f"channel: {channel_id}")
        if handled is not None:
            filter_desc.append(f"handled: {handled}")
        if mention_bot is not None:
            filter_desc.append(f"mention_bot: {mention_bot}")
        if threshold is not None:
            filter_desc.append(f"threshold < {threshold}")
        
        print(f"Found {len(detailed_results)} similar messages with filters: {', '.join(filter_desc) if filter_desc else 'none'}")
        if detailed_results:
            print(f"   Best match distance: {detailed_results[0]['distance']:.4f}")
            print(f"   Worst match distance: {detailed_results[-1]['distance']:.4f}")
            if threshold is not None:
                print(f"   All results below threshold: {threshold}")
        
        cursor.close()
        conn.close()
        
        return detailed_results
        
    except Exception as e:
        print(f"Filtered search failed: {e}")
        return []

# Example usage and testing
if __name__ == "__main__":
    print("Semantic Search System")
    print("=" * 50)
    
    print("\nAvailable channels:")
    channels = list_channels()
    
    if not channels:
        print("No channels found. Make sure you have inserted some messages first.")
        exit(1)
    
    test_channel = "C09G0HN0EKH"
    
    # Get channel stats
    print(f"\nStats for channel '{test_channel}':")
    stats = get_channel_stats(test_channel)
    if stats:
        print(f"   Total messages: {stats['total_messages']}")
        print(f"   Unique users: {stats['unique_users']}")
        print(f"   Date range: {stats['earliest_message']} to {stats['latest_message']}")
    
    # Test searches
    test_queries = [
        "Agreed. Lets ask the bot to create a ticket."
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}' in channel '{test_channel}'")
        
        # # Simple search
        # results = search(query, test_channel, top_k=10)
        # if results:
        #     print(f"Top {len(results)} results:")
        #     for i, message in enumerate(results, 1):
        #         print(f"   {i}. {message}")
        # else:
        #     print("   No results found")
        
        # Test with threshold (example: only results with distance < 0.8)
        print(f"\nSearching with threshold < 0.8:")
        threshold_results = search_messages_with_neighbors(query=query, channel_id=test_channel, threshold=0.5, top_k=4)
        if threshold_results:
            print(f"Threshold filtered results ({len(threshold_results)}):")
            for i, message in enumerate(threshold_results, 1):
                print(f"   {i}. {message}")
        else:
            print("   No results found within threshold")
        
        print("-" * 40)

    # Test detailed search
    # print(f"\nDetailed search example:")
    # detailed_results = search_detailed("hello", 2, test_channel)
    # if detailed_results:
    #     for i, result in enumerate(detailed_results, 1):
    #         print(f"   {i}. [{result['user_id']}] {result['message']}")
    #         print(f"      Distance: {result['distance']:.4f}, Created: {result['created_at']}")
    
    # # Test global search
    # print(f"\nGlobal search across all channels:")
    # global_results = search_all_channels("good morning", 3)
    # if global_results:
    #     for i, message in enumerate(global_results, 1):
    #         print(f"   {i}. {message}")
    
    # print(f"\nSearch testing completed!")