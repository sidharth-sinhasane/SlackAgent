from pymilvus import MilvusClient

client = MilvusClient("http://localhost:19530")
collection_name = "slack_messages"
description = client.describe_collection(collection_name)
print(description)