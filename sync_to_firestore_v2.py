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
    
    # First, let's list and delete all existing docs to ensure no orphans
    list_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects"
    req_list = urllib.request.Request(list_url, method="GET")
    req_list.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req_list) as resp:
            data = json.load(resp)
            if "documents" in data:
                for doc in data["documents"]:
                    doc_path = doc["name"]
                    del_url = f"https://firestore.googleapis.com/v1/{doc_path}"
                    req_del = urllib.request.Request(del_url, method="DELETE")
                    req_del.add_header("Authorization", f"Bearer {token}")
                    urllib.request.urlopen(req_del)
                    print(f"Deleted old doc: {doc_path.split('/')[-1]}")
    except Exception as e:
        print(f"Cleanup failed (maybe empty): {e}")

    # Now upload the fresh data
    for project in projects:
        doc_id = project["id"]
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{doc_id}"
        
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
                print(f"Synced {doc_id} with group {project['group']}")
        except Exception as e:
            print(f"Failed to sync {doc_id}: {e}")

if __name__ == "__main__":
    sync()
