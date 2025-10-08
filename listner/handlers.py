import logging
from slack_bolt import App
import time
from listner.operations import send_message
from db.insert_data import ingest
from schema.data_ingestion_schema import DataIngestionSchema
import asyncio
from run_workflow import main

logger = logging.getLogger(__name__)

def register_handlers(app: App):
    """
    Register all event handlers for the Slack app.
    """
    @app.event("message")
    def handle_message_events(event, say):
        if "subtype" not in event:  # Only handle user messages (ignore bot messages, edits, etc.)
            logger.info(f"Received message: {event['text']} from user {event['user']} in channel {event['channel']}")


            auth_response = app.client.auth_test()
            bot_id = auth_response['user_id']
            bot_mention = f"<@{bot_id}>"
            if bot_mention in event["text"]:
                is_bot_mention = True
                asyncio.run(main(query=event["text"],channel_id=event["channel"]))
            else:
                is_bot_mention = False
                
            object = {}
            object['channel_id'] = event["channel"]
            object['user_id'] = event["user"]
            object['message'] = event["text"]
            object['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if is_bot_mention:
                object['handled'] = True
            else:
                object['handled'] = False
            object['metadata'] = {}
            object['mention_bot'] = is_bot_mention
            ingest(object)