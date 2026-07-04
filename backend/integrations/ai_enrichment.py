from backend.database.session import get_setting_value
import requests

def enrich_finding(finding_description: str, finding_title: str):
    api_key = get_setting_value("OPENAI_API_KEY")
    if not api_key:
        return None
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Explain this cloud security finding in simple terms and provide a brief remediation summary:\nTitle: {finding_title}\nDescription: {finding_description}"
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful cloud security expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error enriching finding: {e}")
    return None

