
from temporalio import activity
from db.search import search
from utils.llm import get_ticket_details

@activity.defn
def say_hello(metadata: dict) -> dict:
    print("*"*100)
    print(metadata)
    print("*"*100)
    return metadata

@activity.defn
async def query_vector_db(metadata: dict) -> dict:
    print(f"Querying vector DB for: {metadata['query']}")
    results = search(query=metadata['query'], top_k=metadata['top_k'], channel_id=metadata['channel_id'],threshold= 0.5)
    print("#"*100,"\n")
    print(results)
    print("#"*100,"\n")

    metadata['messages'] = results
    # print(f"Results: {results}")
    return metadata


@activity.defn
def query_jira(metadata: dict) -> dict:
    metadata['existing_tickets'] = []
    return metadata

@activity.defn
def call_llm_for_ticket_details(metadata: dict) -> dict:
    # print("*"*100)
    # print(metadata)
    # print("*"*100)
    ticket_details = get_ticket_details(metadata)
    metadata["ticket_details"] = ticket_details
    return metadata

@activity.defn
def create_jira_ticket(metadata: dict) -> dict:
    return metadata

@activity.defn
def log_workflow_result(metadata: dict) -> dict:
    print("="*100,"\n")
    print("Logging workflow result")
    print(metadata)
    print("="*100,"\n")
    return metadata