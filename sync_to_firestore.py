import json
import subprocess
import urllib.request

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def sync():
    token = get_access_token()
    with open("./data/projects_status.json", "r") as f:
        projects = json.load(f)
    
    for project in projects:
        doc_id = project["id"]
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{doc_id}?updateMask.fieldPaths=name&updateMask.fieldPaths=group&updateMask.fieldPaths=progress&updateMask.fieldPaths=status&updateMask.fieldPaths=todos"
        
        # Convert to Firestore REST format
        fields = {
            "name": {"stringValue": project["name"]},
            "group": {"stringValue": project["group"]},
            "progress": {"integerValue": str(project["progress"])},
            "status": {"stringValue": project["status"]},
            "todos": {"arrayValue": {"values": [{"stringValue": t} for t in project["todos"]]}}
        }
        
        data = json.dumps({"fields": fields}).encode("utf-8")
        
        req = urllib.request.Request(url, data=data, method="PATCH")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req) as response:
                print(f"Synced {doc_id}")
        except Exception as e:
            print(f"Failed to sync {doc_id}: {e}")

if __name__ == "__main__":
    sync()
