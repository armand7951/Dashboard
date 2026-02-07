import os
import json
import subprocess

FILE_DIR = "/Users/cataholic/.gemini/File"
STATUS_FILE = "/Users/cataholic/.gemini/File/Dashboard/data/projects_status.json"
SYNC_SCRIPT = "/Users/cataholic/.gemini/File/Dashboard/sync_github_to_firestore.py"

def discover():
    # 1. Load existing projects
    with open(STATUS_FILE, "r") as f:
        projects = json.load(f)
    
    existing_ids = {p["id"] for p in projects}
    new_found = False

    # 2. Scan directory
    for item in os.listdir(FILE_DIR):
        item_path = os.path.join(FILE_DIR, item)
        if not os.path.isdir(item_path) or item.startswith('.') or item == 'Dashboard':
            continue
        
        # Create a simple ID from folder name
        project_id = item.lower().replace(" ", "-")
        
        if project_id not in existing_ids:
            print(f"New project discovered: {item}")
            
            # Determine Group
            group = "Gather"
            if item.upper().startswith("DT") or "DEOTENG" in item.upper():
                group = "Deoteng"
            elif item.upper().startswith("V ") or "VERDICT" in item.upper():
                group = "Verdict Ai"
            
            # Add to list
            projects.append({
                "id": project_id,
                "name": item,
                "group": group,
                "progress": 0,
                "status": "New Discovery",
                "todos": ["Initial setup"]
            })
            new_found = True

    if new_found:
        # 3. Save back to local JSON
        with open(STATUS_FILE, "w") as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        
        # 4. Trigger cloud sync
        print("Triggering cloud sync...")
        subprocess.run(["python3", SYNC_SCRIPT])
        
        # 5. Push to GitHub for CI/CD
        os.chdir(os.path.dirname(STATUS_FILE))
        subprocess.run(["git", "add", STATUS_FILE])
        subprocess.run(["git", "commit", "-m", "Auto-discovery: Added new project(s)"])
        subprocess.run(["git", "push", "origin", "main"])
        return True
    
    return False

if __name__ == "__main__":
    if discover():
        print("Discovery and sync complete.")
    else:
        print("No new projects found.")
