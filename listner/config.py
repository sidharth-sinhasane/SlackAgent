import os
from dotenv import load_dotenv

load_dotenv(override=True)

SOCKET_TOKEN = os.getenv("SOCKET_TOKEN")
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

if not SOCKET_TOKEN:
    raise ValueError("Missing SOCKET_TOKEN in .env file")

if not SLACK_CLIENT_ID or not SLACK_CLIENT_SECRET:
    raise ValueError("Missing SLACK_CLIENT_ID or SLACK_CLIENT_SECRET in .env file")