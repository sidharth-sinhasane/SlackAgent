import logging
from slack_bolt import App

from listner.operations import send_message
from db.milvus_ingest import ingest_data
from schema.data_ingestion_schema import DataIngestionSchema

logger = logging.getLogger(__name__)

def register_handlers(app: App):
    """
    Register all event handlers for the Slack app.
    """
    @app.event("message")
    def handle_message_events(event, say):
        if "subtype" not in event:  # Only handle user messages (ignore bot messages, edits, etc.)
            logger.info(f"Received message: {event['text']} from user {event['user']} in channel {event['channel']}")
            print(f"Received message: {event['text']} from user {event['user']} in channel {event['channel']}")
            object = DataIngestionSchema(
                channel_id= event["channel"],
                user_id= event["user"],
                message= event["text"]
            )            
            ingest_data(object)
            send_message(app, event["channel"], "Hello!")