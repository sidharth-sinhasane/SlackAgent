import openai
import os
from dotenv import load_dotenv
from typing import List, Optional
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    A class to generate embeddings using OpenAI's text-embedding models
    """
    
    def __init__(self):
        """Initialize the OpenAI client with API key"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'text-embedding-3-small')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        logger.info(f"EmbeddingGenerator initialized with model: {self.model}")
    
    def get_embedding(self, message: str, max_retries: int = 3) -> List[float]:
        """
        Generate embedding for a single message using OpenAI's text-embedding-3-small
        
        Args:
            message (str): The text message to embed
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            List[float]: The embedding vector (1536 dimensions)
            
        Raises:
            ValueError: If message is empty or None
            Exception: If API call fails after all retries
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty or None")
        
        # Clean the message
        clean_message = message.strip().replace('\n', ' ').replace('\r', ' ')
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating embedding for message (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.embeddings.create(
                    input=clean_message,
                    model=self.model,
                    encoding_format="float"  # Ensures we get float values
                )
                
                # Extract the embedding vector
                embedding = response.data[0].embedding
                
                logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
                return embedding
                
            except openai.RateLimitError as e:
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1, 2, 4 seconds
                logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                
            except openai.APIError as e:
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate embedding after {max_retries} attempts: {e}")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate embedding after {max_retries} attempts: {e}")
                time.sleep(1)
        
        raise Exception(f"Failed to generate embedding after {max_retries} attempts")
    
    def get_embeddings_batch(self, messages: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple messages in batches
        
        Args:
            messages (List[str]): List of messages to embed
            batch_size (int): Number of messages to process in each batch
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not messages:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} messages)")
            
            try:
                # Clean messages in batch
                clean_batch = [msg.strip().replace('\n', ' ').replace('\r', ' ') for msg in batch]
                
                response = self.client.embeddings.create(
                    input=clean_batch,
                    model=self.model,
                    encoding_format="float"
                )
                
                # Extract embeddings from response
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Successfully processed batch with {len(batch_embeddings)} embeddings")
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                # Fall back to individual processing for this batch
                logger.info("Falling back to individual message processing for this batch")
                for msg in batch:
                    try:
                        embedding = self.get_embedding(msg)
                        all_embeddings.append(embedding)
                    except Exception as individual_error:
                        logger.error(f"Failed to process individual message: {individual_error}")
                        # Add a zero vector as placeholder
                        all_embeddings.append([0.0] * 1536)
        
        return all_embeddings
    
    def test_connection(self) -> bool:
        """
        Test the OpenAI API connection with a simple embedding request
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            test_embedding = self.get_embedding("test message")
            logger.info("OpenAI API connection test successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {e}")
            return False


# Convenience functions for easy usage
def get_message_embedding(message: str) -> List[float]:
    """
    Simple function to get embedding for a single message
    
    Args:
        message (str): The message to embed
        
    Returns:
        List[float]: The embedding vector
    """
    generator = EmbeddingGenerator()
    return generator.get_embedding(message)


def get_multiple_embeddings(messages: List[str]) -> List[List[float]]:
    """
    Simple function to get embeddings for multiple messages
    
    Args:
        messages (List[str]): List of messages to embed
        
    Returns:
        List[List[float]]: List of embedding vectors
    """
    generator = EmbeddingGenerator()
    return generator.get_embeddings_batch(messages)


# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize the embedding generator
        generator = EmbeddingGenerator()
        
        # Test the connection
        if not generator.test_connection():
            print("Error: Failed to connect to OpenAI API")
            exit(1)
        
        # Test single message
        test_message = "Hello, how are you today?"
        print(f"\nTesting with message: '{test_message}'")
        
        embedding = generator.get_embedding(test_message)
        print(f"Generated embedding with {len(embedding)} dimensions")
        print(f"First 10 values: {embedding[:10]}")
        
        # Test multiple messages
        test_messages = [
            "Good morning everyone!",
            "How's the weather today?",
            "I love programming with Python",
            "Vector databases are fascinating"
        ]
        
        print(f"\nTesting batch processing with {len(test_messages)} messages")
        embeddings = generator.get_embeddings_batch(test_messages)
        print(f"Generated {len(embeddings)} embeddings")
        
        for i, emb in enumerate(embeddings):
            print(f"Message {i+1}: {len(emb)} dimensions")
        
        # Show similarity between first two messages
        if len(embeddings) >= 2:
            import numpy as np
            
            # Calculate cosine similarity
            emb1 = np.array(embeddings[0])
            emb2 = np.array(embeddings[1])
            
            cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            print(f"\nCosine similarity between first two messages: {cosine_sim:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Added your OpenAI API key to the .env file")
        print("2. Installed required packages: pip install openai python-dotenv")