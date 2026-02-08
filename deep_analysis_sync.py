import os
import json
import urllib.request
import subprocess
import re
import urllib.parse

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"
BASE_PATH = "/Users/cataholic/.gemini/File"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def analyze_project(project_path):
    project_name = os.path.basename(project_path)
    analysis = {
        "current_status": "Unknown",
        "next_actions": []
    }
    
    # Try to find memory bank files
    mb_path = os.path.join(project_path, ".agent/memory-bank")
    progress_file = os.path.join(mb_path, "progress.md")
    product_file = os.path.join(mb_path, "productContext.md")
    
    if not os.path.exists(progress_file):
        # Fallback to root files
        progress_file = os.path.join(project_path, "TODO.md")
        if not os.path.exists(progress_file):
            progress_file = os.path.join(project_path, "progress.md")

    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find phase
            phase_match = re.search(r'\*\*Phase\*\*:\s*(.*)', content)
            if phase_match:
                analysis["current_status"] = phase_match.group(1).strip()
            
            # Find open tasks
            lines = content.split('\n')
            for line in lines:
                if '- [ ]' in line:
                    task_text = line.replace('- [ ]', '').strip()
                    # Clean markdown
                    task_text = re.sub(r'\*\*', '', task_text)
                    if task_text:
                        analysis["next_actions"].append({
                            "title": task_text,
                            "status": "todo",
                            "source": "Analysis"
                        })
    
    # If no tasks found, infer from phase
    if not analysis["next_actions"]:
        if "Initial" in analysis["current_status"]:
            analysis["next_actions"].append({"title": "Setup basic project structure", "status": "todo", "source": "AI-Suggestion"})
        elif "Refinement" in analysis["current_status"]:
            analysis["next_actions"].append({"title": "UI/UX Polishing and Bug Fixing", "status": "todo", "source": "AI-Suggestion"})
            
    return analysis

def deep_analyze_and_sync():
    token = get_access_token()
    projects = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d)) and not d.startswith('.')]
    
    report = {}
    
    for proj in projects:
        path = os.path.join(BASE_PATH, proj)
        print(f"Analyzing {proj}...")
        analysis = analyze_project(path)
        report[proj] = analysis
        
        # Build tasks for Firestore
        task_values = []
        for t in analysis["next_actions"]:
            task_values.append({
                "mapValue": {
                    "fields": {
                        "title": {"stringValue": t["title"]},
                        "status": {"stringValue": t["status"]},
                        "source": {"stringValue": t["source"]}
                    }
                }
            })
            
        if not task_values: continue
            
        doc_id = proj.replace(' ', '_').lower()
        safe_doc_id = urllib.parse.quote(doc_id)
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects/{safe_doc_id}?updateMask.fieldPaths=tasks"
        
        payload = {"fields": {"tasks": {"arrayValue": {"values": task_values}}}}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="PATCH")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  Successfully synced {proj}")
        except Exception as e:
            print(f"  Failed to sync {proj}: {e}")
            
    return report

if __name__ == "__main__":
    report = deep_analyze_and_sync()
    # Print summary for the user
    print("\n--- Project Analysis Summary ---")
    for proj, data in report.items():
        print(f"[{proj}] Status: {data['current_status']}")
        for t in data['next_actions'][:2]:
            print(f"  -> Next: {t['title']}")
