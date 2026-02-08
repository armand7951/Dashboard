import firebase_admin
from firebase_admin import credentials, auth, firestore
import getpass

def create_dashboard_user():
    # Use the local service account if available, or initialize with project ID
    # Since I'm running in your environment, I'll assume the default credentials work 
    # or you have the JSON file. 
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': 'dashboard-amen-v2',
        })

    db = firestore.client()

    print("--- Dashboard User Creator ---")
    email = input("Enter Email: ")
    password = getpass.getpass("Enter Password: ")
    name = input("Enter Full Name: ")
    company = input("Enter Company Name: ")

    try:
        # 1. Create User in Auth
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        
        # 2. Create Profile in Firestore
        db.collection('users').document(user.uid).set({
            'name': name,
            'company': company,
            'email': email,
            'role': 'user',
            'createdAt': firestore.SERVER_TIMESTAMP
        })

        print(f"\n✅ Success! User {name} created with ID: {user.uid}")
        print(f"They can now log in at https://dashboard-amen-v2.web.app")

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    create_dashboard_user()
