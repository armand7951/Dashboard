import json
import subprocess
import urllib.request

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def check_data():
    token = get_access_token()
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/projects"
    
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            if "documents" in data:
                for doc in data["documents"]:
                    name = doc["fields"]["name"]["stringValue"]
                    group = doc["fields"]["group"]["stringValue"]
                    print(f"Project: {name}, Group: [{group}]")
            else:
                print("No documents found in 'projects' collection.")
    except Exception as e:
        print(f"Failed to check data: {e}")

if __name__ == "__main__":
    check_data()
