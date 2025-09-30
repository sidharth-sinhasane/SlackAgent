
import asyncio
from temporalio.client import Client

# Import the workflow from the previous code
from slack_workflows.workflows.slackagent_workflow import SlackagentWorkflow

async def main(query,channel_id):
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    print("Executing workflow","_"*100)
    metadata = {"name": "sid", "query": query, "top_k": 5, "channel_id": channel_id, "threshold": 0.5}
    result = await client.execute_workflow(SlackagentWorkflow.run,metadata, id="my-workflow-id", task_queue="task_queue_1")

    # print(f"Result: {result}")
    # print("Workflow executed","_"*100)

if __name__ == "__main__":
    asyncio.run(main("create a ticket on for creating socket connection for slack connector","C09G0HN0EKH"))