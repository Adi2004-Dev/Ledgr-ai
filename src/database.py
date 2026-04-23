import firebase_admin
from firebase_admin import credentials, firestore
import os

# ==========================================
# 1. FIREBASE INITIALIZATION (Local Only)
# ==========================================
if not firebase_admin._apps:
    try:
        # Strictly look for the local file on your Mac
        file_path = "src/firebase_key.json" if os.path.exists("src/firebase_key.json") else "firebase_key.json"
        cred = credentials.Certificate(file_path)
        firebase_admin.initialize_app(cred)
        print("✅ Local Firebase successfully connected.")
    except Exception as e:
        print(f"🚨 Error connecting to Firebase: {e}")

# Connect to the database
db = firestore.client()

# ==========================================
# 2. DATABASE FUNCTIONS
# ==========================================
def save_to_firestore(transaction_data):
    try:
        transaction_data["timestamp"] = firestore.SERVER_TIMESTAMP
        db.collection("transactions").add(transaction_data)
        return True
    except Exception as e:
        print(f"🚨 Error saving to Firestore: {e}")
        return False

def load_from_firestore():
    try:
        # Load directly and sort in Python to prevent infinite loading bugs
        docs = db.collection("transactions").get()
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