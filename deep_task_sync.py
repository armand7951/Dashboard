import os
import json
import urllib.request
import subprocess
import re

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"
BASE_PATH = "/Users/cataholic/.gemini/File"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def parse_markdown_tasks(file_path):
    tasks = []
    if not os.path.exists(file_path):
        return tasks
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex for [ ] and [x]
    lines = content.split('\n')
    for line in lines:
        match = re.search(r'- \[( |x|X)\] (.*)', line)
        if match:
            status = 'done' if match.group(1).lower() == 'x' else 'todo'
            title = match.group(2).strip()
            # Clean up potential markdown formatting in title
            title = re.sub(r'\*\*', '', title)
            tasks.append({
                'title': title,
                'status': status,
                'source': 'File'
            })
    return tasks

def discover_and_sync():
    token = get_access_token()
    projects_dir = BASE_PATH
    
    for item in os.listdir(projects_dir):
        full_path = os.path.join(projects_dir, item)
        if not os.path.isdir(full_path) or item.startswith('.'):
            continue
        
        print(f"Checking project: {item}")
        
        # Look for progress.md in standard locations
        potential_files = [
            os.path.join(full_path, ".agent/memory-bank/progress.md"),
            os.path.join(full_path, "TODO.md"),
            os.path.join(full_path, "progress.md"),
            os.path.join(full_path, ".agent/memory-bank/task.md")
        ]
        
        all_parsed_tasks = []
        for pf in potential_files:
            all_parsed_tasks.extend(parse_markdown_tasks(pf))
        
        if not all_parsed_tasks:
            print(f"  No tasks found for {item}")
            continue

        print(f"  Found {len(all_parsed_tasks)} tasks.")
        
        # Sync to Firestore
        doc_id = item.replace(' ', '_').lower()
        # Handle non-ASCII in URL encoding
        import urllib.parse
        safe_doc_id = urllib.parse.quote(doc_id)
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{safe_doc_id}"
        
        # We need to construct the complex Firestore JSON structure
        task_values = []
        for t in all_parsed_tasks:
            task_values.append({
                "mapValue": {
                    "fields": {
                        "title": {"stringValue": t["title"]},
                        "status": {"stringValue": t["status"]},
                        "source": {"stringValue": t["source"]}
                    }
                }
            })
        
        # Also need basic project info to not wipe it
        # Actually PATCH with updateMask might be safer but REST PATCH is usually an UPSERT.
        # We'll just push the tasks field.
        
        payload = {
            "fields": {
                "tasks": {"arrayValue": {"values": task_values}}
            }
        }
        
        data = json.dumps(payload).encode("utf-8")
        # Use updateMask to only update tasks
        mask_url = f"{url}?updateMask.fieldPaths=tasks"
        req = urllib.request.Request(mask_url, data=data, method="PATCH")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  Successfully synced {item}")
        except Exception as e:
            print(f"  Failed to sync {item}: {e}")

if __name__ == "__main__":
    discover_and_sync()
