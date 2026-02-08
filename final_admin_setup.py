import json
import urllib.request
import subprocess

PROJECT_ID = "dashboard-amen-v2"

def get_access_token():
    return subprocess.check_output(["/Users/cataholic/.gemini/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

def create_auth_user():
    token = get_access_token()
    email = "armand7951@gmail.com"
    password = "000000"
    
    # Firebase Auth Admin REST API: signup New User
    # Actually, projects.accounts.create for Identity Toolkit
    url = f"https://identitytoolkit.googleapis.com/v1/projects/{PROJECT_ID}/accounts"
    
    payload = {
        "email": email,
        "password": password,
        "displayName": "阿門 (Admin)"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.load(resp)
            uid = res_data["localId"]
            print(f"Successfully created Auth User. UID: {uid}")
            return uid
    except Exception as e:
        if "EMAIL_EXISTS" in str(e) or (hasattr(e, 'read') and b"EMAIL_EXISTS" in e.read()):
            print("Auth user already exists.")
            return None
        print(f"Error creating auth user: {e}")
        return None

def update_firestore_with_correct_uid(uid):
    if not uid: return
    token = get_access_token()
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users/{uid}"
    
    fields = {
        "name": {"stringValue": "阿門 (Admin)"},
        "company": {"stringValue": "Verdict AI"},
        "email": {"stringValue": "armand7951@gmail.com"},
        "role": {"stringValue": "admin"}
    }
    
    data = json.dumps({"fields": fields}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Successfully linked Firestore profile to UID: {uid}")
    except Exception as e:
        print(f"Error linking profile: {e}")

if __name__ == "__main__":
    new_uid = create_auth_user()
    update_firestore_with_correct_uid(new_uid)
