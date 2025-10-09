import os
import requests
import webbrowser
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
import threading

load_dotenv()

app = FastAPI()

# Store OAuth token
oauth_token = None

def get_slack_oauth_token(code: str) -> str:
    client_id = os.getenv("SLACK_CLIENT_ID")
    client_secret = os.getenv("SLACK_CLIENT_SECRET")
    redirect_uri = os.getenv("SLACK_REDIRECT_URI00", "https://redirectmeto.com/http://localhost:8000/callback")

    if not client_id or not client_secret:
        raise ValueError("SLACK_CLIENT_ID and SLACK_CLIENT_SECRET required in .env")

    response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
    )

    data = response.json()
    if not data.get("ok"):
        raise ValueError(f"Slack OAuth failed: {data.get('error')}")
    
    return data["access_token"]

@app.get("/callback")
async def callback(request: Request):
    global oauth_token
    code = request.query_params.get("code")
    print(f"________________________________________________________")
    print(f"Code: {code}")
    if not code:
        return {"error": "No code received"}
    try:
        oauth_token = get_slack_oauth_token(code)
        return {"message": "OAuth successful! You can close this tab."}
    except Exception as e:
        return {"error": str(e)}

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def perform_slack_oauth():
    global oauth_token
    redirect_uri = os.getenv("SLACK_REDIRECT_URI99", "https://redirectmeto.com/http://localhost:8000/callback")
    client_id = os.getenv("SLACK_CLIENT_ID")
    scopes = "chat:write,users:read"  # adjust as needed

    auth_url = f"https://slack.com/oauth/v2/authorize?client_id={client_id}&scope={scopes}&redirect_uri={redirect_uri}"
    webbrowser.open(auth_url)

    # Start FastAPI in a separate thread
    server_thread = threading.Thread(target=start_fastapi, daemon=True)
    server_thread.start()

    # Wait for the token
    while oauth_token is None:
        pass

    return oauth_token

if __name__ == "__main__":
    token = perform_slack_oauth()
    print("Slack OAuth Token:", token)
