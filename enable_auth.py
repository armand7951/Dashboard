import json
import urllib.request
import subprocess

PROJECT_ID = "dashboard-amen-v2"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def enable_email_auth():
    token = get_access_token()
    # REST API to update Identity Toolkit config
    # https://cloud.google.com/identity-platform/docs/reference/rest/v2/projects/updateConfig
    url = f"https://identitytoolkit.googleapis.com/v2/projects/{PROJECT_ID}/config?updateMask=signIn"
    
    payload = {
        "signIn": {
            "email": {
                "enabled": True,
                "passwordRequired": True
            }
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            print("Successfully enabled Email/Password Authentication.")
    except Exception as e:
        print(f"Error enabling auth: {e}")

if __name__ == "__main__":
    enable_email_auth()
