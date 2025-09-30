import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)

# Load tokens (raise error if missing)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SOCKET_TOKEN = os.getenv("SOCKET_TOKEN")

if not SLACK_BOT_TOKEN or not SOCKET_TOKEN:
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_APP_TOKEN in .env file")