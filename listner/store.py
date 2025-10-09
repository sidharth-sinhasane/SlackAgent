import os
import secrets
from slack_sdk.oauth.installation_store import InstallationStore, Bot, Installation
from slack_sdk.oauth.state_store import OAuthStateStore
from datetime import datetime, timedelta, UTC

class MemoryInstallationStore(InstallationStore):
    def __init__(self):
        self.installations = {}

    def save(self, installation: Installation):
        team_id = installation.team_id
        enterprise_id = installation.enterprise_id or "none"
        key = f"{enterprise_id}-{team_id}"
        self.installations[key] = installation

    def find_bot(self, *, enterprise_id: str | None, team_id: str, is_enterprise_install: bool = False):
        enterprise_id = enterprise_id or "none"
        key = f"{enterprise_id}-{team_id}"
        installation = self.installations.get(key)
        if installation:
            return Bot(
                app_id=installation.app_id,
                enterprise_id=installation.enterprise_id,
                team_id=installation.team_id,
                bot_token=installation.bot_token,
                bot_id=installation.bot_id,
                bot_user_id=installation.bot_user_id,
                bot_scopes=installation.bot_scopes,
                bot_refresh_token=installation.bot_refresh_token,
                bot_token_expires_at=installation.bot_token_expires_at,
                installed_at=installation.installed_at,
            )
        return None

    def find_installation(self, *, enterprise_id: str | None, team_id: str, user_id: str | None = None, is_enterprise_install: bool = False):
        enterprise_id = enterprise_id or "none"
        key = f"{enterprise_id}-{team_id}"
        return self.installations.get(key)
    
    def delete_bot(self, *, enterprise_id: str | None, team_id: str):
        enterprise_id = enterprise_id or "none"
        key = f"{enterprise_id}-{team_id}"
        if key in self.installations:
            del self.installations[key]
    
    def delete_installation(self, *, enterprise_id: str | None, team_id: str, user_id: str | None = None):
        self.delete_bot(enterprise_id=enterprise_id, team_id=team_id)

class MemoryOAuthStateStore(OAuthStateStore):
    def __init__(self):
        self.states = {}

    def issue(self, *args, **kwargs):
        state = secrets.token_urlsafe(32)
        self.states[state] = datetime.now(UTC) + timedelta(minutes=15)
        return state

    def consume(self, state: str):
        if state in self.states:
            del self.states[state]
            return True
        return False

