import logging
from slack_bolt import App
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

def send_message(app: App, channel: str, text: str):
    try:
        response = app.client.chat_postMessage(channel=channel, text=text)
        logger.info(f"Message sent to channel {channel}: {text}")
        return response
    except SlackApiError as e:
        logger.error(f"Error sending message: {e.response['error']}")
        raise

def get_channel_history(app: App, channel: str, limit: int = 10):
    """Retrieve recent message history from a channel."""
    try:
        response = app.client.conversations_history(channel=channel, limit=limit)
        return response["messages"]
    except SlackApiError as e:
        logger.error(f"Error fetching history: {e.response['error']}")
        raise

def invite_user_to_channel(app: App, channel: str, user_id: str):
    """Invite a user to a channel."""
    try:
        response = app.client.conversations_invite(channel=channel, users=user_id)
        return response
    except SlackApiError as e:
        logger.error(f"Error inviting user: {e.response['error']}")
        raise