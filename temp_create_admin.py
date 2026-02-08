import firebase_admin
from firebase_admin import credentials, auth, firestore

def create_specific_admin():
    if not firebase_admin._apps:
        # Use project ID for ADC
        firebase_admin.initialize_app(options={'projectId': 'dashboard-amen-v2'})

    db = firestore.client()
    
    email = "armand7951@gmail.com"
    password = "000000"
    name = "阿門 (Admin)"
    company = "Verdict AI"

    try:
        # Check if user exists
        try:
            user = auth.get_user_by_email(email)
            print(f"User already exists with UID: {user.uid}")
        except auth.UserNotFoundError:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            print(f"User created with UID: {user.uid}")
        
        # Upsert Profile
        db.collection('users').document(user.uid).set({
            'name': name,
            'company': company,
            'email': email,
            'role': 'admin',
            'createdAt': firestore.SERVER_TIMESTAMP
        }, merge=True)

        print(f"Profile updated for {name}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_specific_admin()
