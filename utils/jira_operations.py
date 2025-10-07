import os
import requests
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
global_cloud_id = None

def get_cloud_id():
    """Get Jira cloud ID from accessible-resources endpoint."""
    oauth_token = os.getenv('JIRA_OAUTH_TOKEN')

    if not oauth_token:
        raise ValueError("JIRA_OAUTH_TOKEN environment variable is required")
    
    url = "https://api.atlassian.com/oauth/token/accessible-resources"
    headers = {"Authorization": f"Bearer {oauth_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        global global_cloud_id
        global_cloud_id = data[0]['id']
        return global_cloud_id
    except requests.RequestException as e:
        logger.error(f"Failed to get Jira cloud ID: {e}")
        return global_cloud_id


def get_all_issues():
    """Get all issues from Jira."""
    oauth_token = os.getenv('JIRA_OAUTH_TOKEN')
    cloud_id = get_cloud_id()
    project_key = os.getenv("JIRA_PROJECT_KEY")
    if not oauth_token:
        raise ValueError("JIRA_OAUTH_TOKEN environment variable is required")
    
    if not cloud_id:
        raise ValueError("Global cloud ID is required")
    
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search/jql"
    headers = {
        "Authorization": f"Bearer {oauth_token}", 
        "Accept": "application/json"
    }
    
    params = {
        "jql": f"project = {project_key} AND statusCategory != Done AND created >= -7d ORDER BY created DESC",  # Last 7 days (1 week)
        "maxResults": 50,  # Increase limit
        "startAt": 0,
        "fields": "summary,status"  # Get both summary and status
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Format the response as requested: [{"summary":"...", "status":"..."}]
        formatted_issues = []
        for issue in data.get('issues', []):
            fields = issue.get('fields', {})
            formatted_issue = {
                "summary": fields.get('summary', ''),
                "status": fields.get('status', {}).get('name', '') if fields.get('status') else ''
            }
            formatted_issues.append(formatted_issue)
        
        return formatted_issues
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        logger.error(f"Response text: {response.text}")
        raise


def create_issue(ticket_data):
    """Create a Jira issue from TicketDetailsSchema data."""
    oauth_token = os.getenv("JIRA_OAUTH_TOKEN")
    cloud_id = get_cloud_id()
    project_key= os.getenv("JIRA_PROJECT_KEY")

    
    #  print(oauth_token, cloud_id, project_key)
    # if not oauth_token or not cloud_id:
    #     raise ValueError("JIRA_OAUTH_TOKEN and cloud_id are required")
    
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Map TicketDetailsSchema to Jira API format
    jira_payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": ticket_data.get("ticket_title", ""),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": ticket_data.get("ticket_description", "")}]}]
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": ticket_data.get("ticket_priority", "Medium")}
        }
    }
    
    # Add assignee if provided (need accountId format)
    if ticket_data.get("ticket_assignee"):
        jira_payload["fields"]["assignee"] = {"displayName": ticket_data["ticket_assignee"]}
    
    try:
        if ticket_data.get("should_create_ticket"):
            response = requests.post(url, headers=headers, json=jira_payload)
            response.raise_for_status()
            return response.json()
        else:
            return "Ticket not created"
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to create issue: {e}")
        logger.error(f"Response text: {response.text}")
        raise
# Example usage:


#print(get_cloud_id())
print(get_all_issues())
#print(create_issue({'ticket_id': '', 'ticket_title': 'Build WebSocket Connection with Slack Server', 'ticket_description': 'Create a WebSocket connection to the Slack server to enhance real-time communication and interactions.', 'ticket_status': 'Open', 'ticket_priority': 'High', 'ticket_assignee': 'Unassigned', 'should_create_ticket': True}))