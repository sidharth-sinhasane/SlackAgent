import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listner.config import SLACK_BOT_TOKEN, SOCKET_TOKEN
from listner.handlers import register_handlers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Bolt app
app = App(token=SLACK_BOT_TOKEN)

# Register event handlers
register_handlers(app)

if __name__ == "__main__":
    logger.info("Starting Slack Socket Mode handler...")
    handler = SocketModeHandler(app, SOCKET_TOKEN)
    handler.start()  # This blocks and runs indefinitely