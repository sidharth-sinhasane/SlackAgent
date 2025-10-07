
from temporalio import activity
from db.search import search_messages_with_neighbors
from utils.llm import get_ticket_details
from utils.jira_operations import create_issue,get_all_issues
@activity.defn
def say_hello(metadata: dict) -> dict:
    print("*"*100)
    print(metadata)
    print("*"*100)
    return metadata

@activity.defn
async def query_vector_db(metadata: dict) -> dict:
    print(f"Querying vector DB for: {metadata['query']}")
    results = search_messages_with_neighbors(query=metadata['query'], top_k=metadata['top_k'], channel_id=metadata['channel_id'],threshold= 0.5)
    print("#"*100,"\n")
    print(results)
    print("#"*100,"\n")

    metadata['messages'] = results
    # print(f"Results: {results}")
    return metadata


@activity.defn
def query_jira(metadata: dict) -> dict:
    metadata['existing_tickets'] = get_all_issues()
    print("&"*100)
    print(metadata['existing_tickets'])
    print("&"*100)
    return metadata

@activity.defn
def call_llm_for_ticket_details(metadata: dict) -> dict:
    ticket_details = get_ticket_details(metadata)
    print("$"*100)
    print(ticket_details)
    print("$"*100)
    metadata["ticket_details"] = ticket_details
    return metadata

@activity.defn
def create_jira_ticket(metadata: dict) -> dict:
    create_issue(metadata['ticket_details'])
    return metadata

@activity.defn
def log_workflow_result(metadata: dict) -> dict:
    print("="*100,"\n")
    print("Logging workflow result")
    print(metadata)
    print("="*100,"\n")
    return metadata