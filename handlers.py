import logging
from slack_bolt import App

from operations import send_message

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

            send_message(app, event["channel"], "Hello!")