# Slackagent Temporal Workflow

This directory contains a simple Temporal workflow implementation with activities, worker, and client.

## Components

### 1. Activities (`slack_activities/activities/slackagent_activities.py`)
- `greeting_activity`: Creates personalized greeting messages
- `process_message_activity`: Processes text messages with optional uppercase conversion

### 2. Workflow (`slack_workflows/workflows/slackagent_workflow.py`)
- `SlackagentWorkflow`: Orchestrates the execution of activities
- Supports signals and queries for workflow state management
- Includes retry policies and timeout configurations

### 3. Worker (`run_worker.py`)
- Connects to Temporal server and registers activities/workflows
- Listens for workflow executions on the task queue

### 4. Client (`run_workflow.py`)
- Starts workflow executions
- Demonstrates querying workflow state
- Shows workflow results

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Temporal Server** (if not already running):
   ```bash
   # Using Temporal CLI
   temporal server start-dev
   
   # Or using Docker
   docker run --rm -p 7233:7233 temporalio/auto-setup:1.20
   ```

## Usage

### 1. Start the Worker
In one terminal, run the worker to listen for workflow tasks:

```bash
cd /Users/sidharth.sinhasane/Downloads/starforge-main/calfus/slackagent
python run_worker.py
```

### 2. Execute the Workflow
In another terminal, run the client to execute a workflow:

```bash
cd /Users/sidharth.sinhasane/Downloads/starforge-main/calfus/slackagent
python run_workflow.py
```

## Environment Variables

You can configure the following environment variables:

- `TEMPORAL_ADDRESS`: Temporal server address (default: `localhost:7233`)
- `TEMPORAL_NAMESPACE`: Temporal namespace (default: `default`)
- `TASK_QUEUE`: Task queue name (default: `slackagent-task-queue`)

Example:
```bash
export TEMPORAL_ADDRESS="localhost:7233"
export TEMPORAL_NAMESPACE="my-namespace"
export TASK_QUEUE="my-task-queue"
```

## Workflow Execution Flow

1. **Greeting Phase**: Executes `greeting_activity` to create a personalized greeting
2. **Processing Phase**: Executes `process_message_activity` to process a text message
3. **Result**: Returns a dictionary containing all results and metadata

## Advanced Features

- **Queries**: Check workflow status and progress during execution
- **Signals**: Send signals to update workflow state
- **Retry Policies**: Automatic retry on activity failures
- **Timeouts**: Configurable execution timeouts

## Sample Output

When you run the workflow, you should see output similar to:

```
INFO:__main__:Starting workflow with ID: slackagent-workflow-12345
INFO:__main__:Workflow args: {'user_name': 'John Doe', 'custom_message': 'Hello', 'text_to_process': 'Welcome to Temporal workflows!', 'uppercase': False}
INFO:__main__:Workflow started successfully!
INFO:__main__:Waiting for workflow to complete...
INFO:__main__:Workflow completed successfully!
INFO:__main__:Workflow result: {'user_name': 'John Doe', 'greeting': 'Hello, John Doe! Welcome to the Slackagent workflow!', 'processed_message': 'Processed: Welcome to Temporal workflows!', 'status': 'success', 'workflow_id': 'slackagent-workflow-12345'}
```
