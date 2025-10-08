
from temporalio import activity
from db.search import search_messages_with_neighbors
from utils.llm import get_ticket_details
from utils.jira_operations import create_issue,get_all_issues
from pprint import pprint
@activity.defn
def say_hello(metadata: dict) -> dict:
    return metadata

@activity.defn
async def query_vector_db(metadata: dict) -> dict:
    print(f"Querying vector DB for: {metadata['query']}")
    results = search_messages_with_neighbors(query=metadata['query'], top_k=metadata['top_k'], channel_id=metadata['channel_id'],threshold= 0.5)

    metadata['messages'] = results
    return metadata


@activity.defn
def query_jira(metadata: dict) -> dict:
    metadata['existing_tickets'] = get_all_issues()
    return metadata

@activity.defn
def call_llm_for_ticket_details(metadata: dict) -> dict:
    ticket_details = get_ticket_details(metadata)
    metadata["ticket_details"] = ticket_details
    return metadata

@activity.defn
def create_jira_ticket(metadata: dict) -> dict:
    if metadata['ticket_details']['should_create_ticket']==True:
        create_issue(metadata['ticket_details'])
    return metadata

@activity.defn
def log_workflow_result(metadata: dict) -> dict:
    print("="*100,"\n")
    print("Logging workflow result")
    pprint(metadata)
    print("="*100,"\n")
    return metadata