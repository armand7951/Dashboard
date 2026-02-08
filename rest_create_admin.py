import json
import urllib.request
import subprocess

PROJECT_ID = "dashboard-amen-v2"
DATABASE_ID = "(default)"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def create_admin_user():
    token = get_access_token()
    email = "armand7951@gmail.com"
    password = "000000"
    uid = "admin_amen" # We can't set UID easily via REST without more complex setup, but we can try to create user
    
    # 1. Create User in Auth (REST API)
    # Using the identity toolkit API
    # Note: This needs an API key or Token. We'll use the Bearer token if possible.
    # Actually, simpler to just use the Firestore profile first. 
    # If the user can't login, they can use the "Forgot Password" or I can provide a link.
    # But wait, I'll try the Admin REST API for Auth if available.
    
    print(f"Creating profile for {email} in Firestore...")
    
    # 2. Create Profile in Firestore via REST (Matches the style of sync script)
    doc_id = "armand_admin_v1" # Fixed ID for easier management
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/{DATABASE_ID}/documents/users/{doc_id}"
    
    fields = {
        "name": {"stringValue": "阿門 (Admin)"},
        "company": {"stringValue": "Verdict AI"},
        "email": {"stringValue": email},
        "role": {"stringValue": "admin"}
    }
    
    data = json.dumps({"fields": fields}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            print("Successfully created Admin Profile in Firestore.")
            print("Note: Please manually create this user in Firebase Auth Console with the same email/password.")
    except Exception as e:
        print(f"Error creating profile: {e}")

if __name__ == "__main__":
    create_admin_user()
