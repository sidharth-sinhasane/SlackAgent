# Slack Agent - Multi-Workspace Support

Slack bot with multi-workspace OAuth support. Uses one app-level token (SOCKET_TOKEN) and workspace-specific OAuth tokens.

## Setup

1. Create venv and install requirements
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy `example.env` to `.env` and configure:
- `SOCKET_TOKEN` - App-level token (same for all workspaces)
- `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_SIGNING_SECRET`, `SLACK_APP_ID`
- `SLACK_OAUTH_TOKENS` - Format: `TEAM_ID1:xoxb-token1,TEAM_ID2:xoxb-token2`
- Database and other settings

3. Start pgvector: `docker-compose up -d`

## Running

```bash
python listner/main.py  # Start listener
python run_worker.py    # Start Temporal worker
```

## TODO
- Move OAuth tokens from `.env` to database
- Deploy worker with Eatherion