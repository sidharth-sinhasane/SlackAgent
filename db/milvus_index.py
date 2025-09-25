from pymilvus import MilvusClient

client = MilvusClient("http://localhost:19530")
collection_name = "slack_messages"

# Define index parameters
index_params = client.prepare_index_params()

index_params.add_index(
    field_name="embedding",  # Changed from "Embedding" to "embedding"
    index_type="IVF_FLAT",
    metric_type="COSINE",  # Use COSINE for OpenAI embeddings
    params={"nlist": 128}
)

# Create the index
client.create_index(
    collection_name=collection_name,
    index_params=index_params
)

print(f"Index created successfully on collection: {collection_name}")