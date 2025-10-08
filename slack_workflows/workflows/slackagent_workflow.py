
from datetime import timedelta
from temporalio import workflow

# Import our activity, passing it through the sandbox
with workflow.unsafe.imports_passed_through():
    from slack_activities.activities.slackagent_activities import say_hello, query_vector_db, query_jira, call_llm_for_ticket_details, create_jira_ticket, log_workflow_result

@workflow.defn
class SlackagentWorkflow:
    @workflow.run
    async def run(self, metadata: dict) -> dict:
        # Execute activities in sequence
        
        
        # 1. Say hello
        metadata = await workflow.execute_activity(
            say_hello, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )
        
        # 2. Query vector database
        metadata = await workflow.execute_activity(
            query_vector_db, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )
        
        # 3. Query Jira
        metadata = await workflow.execute_activity(
            query_jira, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )
        
        # 4. Call LLM for ticket details
        metadata = await workflow.execute_activity(
            call_llm_for_ticket_details, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )

        # 5. Create Jira ticket
        metadata = await workflow.execute_activity(
            create_jira_ticket, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )
        
        # 6. Log workflow result
        metadata = await workflow.execute_activity(
            log_workflow_result, metadata, schedule_to_close_timeout=timedelta(seconds=10), task_queue="task_queue_1"
        )
        
        return metadata