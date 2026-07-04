from backend.database.session import get_setting_value
import requests

def notify_slack(finding):
    webhook_url = get_setting_value("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
        
    payload = {
        "text": f"*New {finding.severity} Finding Detected!*",
        "attachments": [
            {
                "color": "#ff0000" if finding.severity == "CRITICAL" else "#ffa500",
                "title": finding.title,
                "fields": [
                    {"title": "Service", "value": finding.service, "short": True},
                    {"title": "Resource", "value": finding.resource_id, "short": False},
                    {"title": "Description", "value": finding.description, "short": False},
                    {"title": "Recommendation", "value": finding.recommendation, "short": False}
                ]
            }
        ]
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Slack notification: {e}")

