import json
import subprocess
import urllib.request
import urllib.parse

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def initialize_all_v2():
    token = get_access_token()
    with open("./data/projects_status.json", "r") as f:
        projects = json.load(f)
    
    for project in projects:
        doc_id = project["id"]
        encoded_id = urllib.parse.quote(doc_id)
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{encoded_id}?updateMask.fieldPaths=agentActive&updateMask.fieldPaths=agentLogs"
        
        logs = ["System: Agent Command Center Initialized"]
        active = False
        
        if doc_id == "gather":
            active = True
            logs = [
                "Agent-Alpha: Scan Complete",
                "Status: Phase 4 (Payment Integration)",
                "Structure: Next.js Monorepo detected"
            ]
        
        fields = {
            "agentActive": {"booleanValue": active},
            "agentLogs": {"arrayValue": {"values": [{"stringValue": log} for log in logs]}}
        }
        
        data = json.dumps({"fields": fields}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="PATCH")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        
        try:
            urllib.request.urlopen(req)
            print(f"Initialized V2 fields for {doc_id}")
        except Exception as e:
            print(f"Failed {doc_id}: {e}")

if __name__ == "__main__":
    initialize_all_v2()
