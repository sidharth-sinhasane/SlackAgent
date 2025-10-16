
import asyncio
from temporalio.client import Client

from slack_workflows.workflows.message_summerizer import MessageSummerizerWorkflow

async def main(query,channel_id):
    client = await Client.connect("localhost:7233")

    metadata = {"name": "sid", "query": query, "top_k": 5, "channel_id": channel_id, "threshold": 0.5}
    result = await client.execute_workflow(MessageSummerizerWorkflow.run,metadata, id="my-workflow-id", task_queue="task_queue_1")

    return result

if __name__ == "__main__":
    asyncio.run(main("create a ticket on for creating socket connection for slack connector","C09G0HN0EKH"))