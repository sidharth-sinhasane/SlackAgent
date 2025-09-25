from pymilvus import MilvusClient, DataType, Index

client = MilvusClient("http://localhost:19530")

# Create schema
schema = MilvusClient.create_schema()

schema.add_field(
    field_name="id",
    datatype=DataType.INT64,
    is_primary=True,
    auto_id=True
)

schema.add_field(
    field_name="channel_id",
    datatype=DataType.VARCHAR,
    max_length=100
)

schema.add_field(
    field_name="user_id",
    datatype=DataType.VARCHAR,
    max_length=100
)

schema.add_field(
    field_name="message",
    datatype=DataType.VARCHAR,
    max_length=2000
)

schema.add_field(
    field_name="embedding",
    datatype=DataType.FLOAT_VECTOR,
    dim=384  # OpenAI text-embedding-3-small dimension
)

collection_name = "slack_messages"

# Drop old collection if exists
if client.has_collection(collection_name):
    client.drop_collection(collection_name)
    print(f"Dropped existing collection: {collection_name}")

# Create new collection
client.create_collection(
    collection_name=collection_name,
    schema=schema,
    shards_num=2
)

print(f"Created collection: {collection_name}")