from backend.database.session import get_setting_value
import requests
from requests.auth import HTTPBasicAuth

def create_jira_ticket(finding):
    jira_url = get_setting_value("JIRA_URL")
    jira_user = get_setting_value("JIRA_USER")
    jira_token = get_setting_value("JIRA_API_TOKEN")
    jira_project_key = get_setting_value("JIRA_PROJECT_KEY", "SEC")
    
    if not all([jira_url, jira_user, jira_token]):
        return
        
    auth = HTTPBasicAuth(jira_user, jira_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    payload = {
        "fields": {
            "project": {"key": jira_project_key},
            "summary": f"[{finding.severity}] {finding.title}",
            "description": f"Service: {finding.service}\nResource: {finding.resource_id}\n\nDescription: {finding.description}\n\nRecommendation: {finding.recommendation}",
            "issuetype": {"name": "Task"}
        }
    }
    
    try:
        url = f"{jira_url.rstrip('/')}/rest/api/2/issue"
        requests.post(url, json=payload, headers=headers, auth=auth, timeout=10)
    except Exception as e:
        print(f"Error creating Jira ticket: {e}")

