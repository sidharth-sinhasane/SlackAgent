import os
from pymilvus import MilvusClient
from openai import OpenAI
from schema.data_ingestion_schema import DataIngestionSchema, IngestedDataSchema
import logging

milvus_client = MilvusClient("http://localhost:19530")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

collection_name = "slack_messages"

def ingest_data(data: DataIngestionSchema):
    logger.info(f"Ingesting data")
    try:
        response = openai_client.embeddings.create(
            input=data.message,
            model="text-embedding-3-small",
            dimensions=384  # Added to match schema dim
        )
    except Exception as e:
        logger.error(f"Error ingesting data: {e}")
        raise

    output_data = IngestedDataSchema(
        channel_id=data.channel_id,
        user_id=data.user_id,
        message=data.message,
        embedding=response.data[0].embedding
    )
    logger.info(f"Data embedded successfully")

    try:
        milvus_client.insert(collection_name, output_data.model_dump())
    except Exception as e:
        logger.error(f"Error inserting data into Milvus: {e}")
        raise

    logger.info(f"Data inserted into Milvus successfully")
    return output_data


if __name__ == "__main__":

# Example data
    data = [
        {
            "channel_id": "C0123456789",
            "user_id": "U0123456789",
            "message": "Hello, world!"
        },
        {
            "channel_id": "C0123456789",
            "user_id": "U0123456789",
            "message": "i like pizza!"
        },
        {
            "channel_id": "C0123456789",
            "user_id": "U0123456789",
            "message": "i live in pune!"
        }
    ]
    for item in data:
        ingest_data(item)