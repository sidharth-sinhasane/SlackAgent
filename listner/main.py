import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import Installation

from listner.config import SOCKET_TOKEN, SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, SLACK_SIGNING_SECRET
from listner.handlers import register_handlers
from listner.store import MemoryInstallationStore, MemoryOAuthStateStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

installation_store = MemoryInstallationStore()


# currently written logic to get oauth token from env and store in the installation store
# todo: get the token & team id from db and store in the installation store

oauth_tokens = os.getenv("SLACK_OAUTH_TOKENS", "").strip()
if oauth_tokens:
    for token_entry in oauth_tokens.split(","):
        token_entry = token_entry.strip()
        if ":" in token_entry:
            team_id, oauth_token = token_entry.split(":", 1)
            installation = Installation(
                app_id=os.getenv("SLACK_APP_ID", ""),
                enterprise_id=None,
                team_id=team_id.strip(),
                bot_token=oauth_token.strip(),
                bot_id=os.getenv("SLACK_BOT_ID", ""),
                bot_user_id=os.getenv("SLACK_BOT_USER_ID", ""),
                bot_scopes=["chat:write", "channels:history", "groups:history", "im:history", "mpim:history"],
                user_id=None,
                user_token=None,
                user_scopes=[],
                installed_at=time.time(),
            )
            installation_store.save(installation)
            logger.info(f"Loaded OAuth token for workspace: {team_id.strip()}")

oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=["chat:write", "channels:history", "groups:history", "im:history", "mpim:history"],
    installation_store=installation_store,
    state_store=MemoryOAuthStateStore(),
)

app = App(
    signing_secret=SLACK_SIGNING_SECRET,
    oauth_settings=oauth_settings,
)

register_handlers(app)

if __name__ == "__main__":
    logger.info("Starting Slack Socket Mode handler with OAuth support...")
    handler = SocketModeHandler(app, SOCKET_TOKEN)
    handler.start()