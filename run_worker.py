
import asyncio
import concurrent.futures
from temporalio.client import Client
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from slack_activities.activities.slackagent_activities import say_hello, query_vector_db, query_jira, call_llm_for_ticket_details, create_jira_ticket, log_workflow_result
from slack_workflows.workflows.slackagent_workflow import SlackagentWorkflow

async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Run the worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
          client,
          task_queue="task_queue_1",
          workflows=[SlackagentWorkflow],
          activities=[say_hello, query_vector_db, query_jira, call_llm_for_ticket_details, create_jira_ticket, log_workflow_result],
          activity_executor=activity_executor,
        )
        await worker.run()

if __name__ == "__main__":
    asyncio.run(main())