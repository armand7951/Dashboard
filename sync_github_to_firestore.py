import json
import subprocess
import urllib.request
import os

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def get_latest_commit(repo_url):
    if not repo_url or "github.com" not in repo_url:
        return None
    
    # Extract owner/repo from URL
    parts = repo_url.replace(".git", "").split("github.com/")[-1].split("/")
    if len(parts) < 2:
        return None
    
    repo = f"{parts[0]}/{parts[1]}"
    try:
        cmd = ["gh", "api", f"repos/{repo}/commits", "--jq", ".[0] | {message: .commit.message, date: .commit.author.date, author: .commit.author.name}"]
        result = subprocess.check_output(cmd).decode("utf-8").strip()
        return json.loads(result)
    except:
        return None

def sync():
    token = get_access_token()
    
    # Load projects.json for repo URLs
    with open("/Users/cataholic/.gemini/antigravity/projects.json", "r") as f:
        repo_map = json.load(f)

    # Load current status
    with open("./data/projects_status.json", "r") as f:
        projects = json.load(f)
    
    for project in projects:
        doc_id = project["id"]
        repo_url = repo_map.get(project["name"])
        
        # Fetch GitHub info
        commit_info = get_latest_commit(repo_url)
        
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{doc_id}"
        
        fields = {
            "name": {"stringValue": project["name"]},
            "group": {"stringValue": project["group"]},
            "progress": {"integerValue": str(project["progress"])},
            "status": {"stringValue": project["status"]},
            "todos": {"arrayValue": {"values": [{"stringValue": t} for t in project["todos"]]}}
        }
        
        if commit_info:
            fields["lastCommit"] = {"mapValue": {"fields": {
                "message": {"stringValue": commit_info["message"]},
                "date": {"stringValue": commit_info["date"]},
                "author": {"stringValue": commit_info["author"]}
            }}}
        
        data = json.dumps({"fields": fields}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="PATCH")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req) as response:
                print(f"Synced {doc_id} with GitHub info")
        except Exception as e:
            print(f"Failed to sync {doc_id}: {e}")

if __name__ == "__main__":
    sync()
