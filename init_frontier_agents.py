import json
import subprocess
import urllib.request
import urllib.parse

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def initialize_frontier():
    token = get_access_token()
    
    # Define AI Employees
    agents = [
        {
            "id": "angela-manager",
            "name": "Angela",
            "role": "AI Project Manager / Lead",
            "avatar": "😇",
            "status": "Managing Fleet",
            "load": 20,
            "specialty": "Orchestration & Communication"
        },
        {
            "id": "cody-frontend",
            "name": "Cody",
            "role": "Senior Frontend Engineer",
            "avatar": "🎨",
            "status": "Idle",
            "load": 0,
            "specialty": "React, Tailwind, UI/UX"
        },
        {
            "id": "db-master",
            "name": "Nova",
            "role": "Database Specialist",
            "avatar": "💾",
            "status": "Idle",
            "load": 0,
            "specialty": "Firestore, Postgres, Architecture"
        },
        {
            "id": "bug-hunter",
            "name": "Hunter",
            "role": "QA & Security Engineer",
            "avatar": "🕵️",
            "status": "Monitoring Logs",
            "load": 5,
            "specialty": "TDD, Debugging, Security"
        }
    ]

    for agent in agents:
        doc_id = agent["id"]
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/agents/{doc_id}"
        
        fields = {
            "name": {"stringValue": agent["name"]},
            "role": {"stringValue": agent["role"]},
            "avatar": {"stringValue": agent["avatar"]},
            "status": {"stringValue": agent["status"]},
            "load": {"integerValue": str(agent["load"])},
            "specialty": {"stringValue": agent["specialty"]}
        }
        
        data = json.dumps({"fields": fields}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="PATCH")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        
        try:
            urllib.request.urlopen(req)
            print(f"Hired AI Employee: {agent['name']}")
        except Exception as e:
            print(f"Failed to hire {agent['name']}: {e}")

if __name__ == "__main__":
    initialize_frontier()
