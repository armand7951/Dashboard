import json
import subprocess
import urllib.request

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def set_agent_activity(project_id, active, logs=[]):
    token = get_access_token()
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{project_id}?updateMask.fieldPaths=agentActive&updateMask.fieldPaths=agentLogs"
    
    fields = {
        "agentActive": {"booleanValue": active},
        "agentLogs": {"arrayValue": {"values": [{"stringValue": log} for log in logs]}}
    }
    
    data = json.dumps({"fields": fields}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Set agent activity for {project_id}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    # Start Simulation for Gather
    set_agent_activity("gather", True, [
        "Lead Agent Angela: 指派子代理人 Alpha...",
        "Agent-Alpha: 正在進入 Gather 工作目錄",
        "Agent-Alpha: 掃描代碼結構中..."
    ])
