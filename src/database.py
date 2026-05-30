import firebase_admin
from firebase_admin import credentials, firestore
import requests
import streamlit as st

# 1. Initialize Firebase Securely from Secrets
if not firebase_admin._apps:
    # Streamlit automatically turns [firebase] into a dictionary!
    key_dict = dict(st.secrets["firebase"])
    
    # Pass the dictionary directly to Firebase
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Database Read/Write Functions
def save_to_firestore(transaction_data, user_id):
    try:
        transaction_data["timestamp"] = firestore.SERVER_TIMESTAMP
        transaction_data["user_id"] = user_id  # 🔒 Securely tag to user
        db.collection("transactions").add(transaction_data)
        return True
    except Exception as e:
        print(f"🚨 Error saving to Firestore: {e}")
        return False

def load_from_firestore(user_id):
    try:
        # 🔒 ONLY fetch documents that belong to this specific user
        docs = db.collection("transactions").where("user_id", "==", user_id).get()
        
        records = []
        for doc in docs:
            data = doc.to_dict()
            if "timestamp" in data:
                del data["timestamp"]
            records.append(data)
            
        records.sort(key=lambda x: str(x.get("Date", "")), reverse=True)
        return records
    except Exception as e:
        print(f"🚨 Error loading from Firestore: {e}")
        return []

# 3. Authentication Functions
def sign_up_with_email_and_password(email, password):
    """Creates a new user in Firebase Auth"""
    try:
        api_key = st.secrets["FIREBASE_WEB_API_KEY"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if "error" in data:
            return False, data["error"]["message"]
        return True, data["localId"] # Returns unique User ID (UID)
    except Exception as e:
        return False, str(e)

def sign_in_with_email_and_password(email, password):
    """Authenticates an existing user"""
    try:
        api_key = st.secrets["FIREBASE_WEB_API_KEY"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if "error" in data:
            return False, data["error"]["message"]
        return True, data["localId"] # Returns unique User ID (UID)
    except Exception as e:
        return False, str(e)