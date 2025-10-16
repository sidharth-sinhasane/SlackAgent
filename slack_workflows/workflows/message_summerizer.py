
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from slack_activities.activities.slackagent_activities import say_hello

@workflow.defn
class MessageSummerizerWorkflow:
    @workflow.run
    async def run(self, metadata: dict) -> dict:
        metadata = await workflow.execute_activity(
            say_hello, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )
        return metadata