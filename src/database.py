import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os

# ==========================================
# 1. FIREBASE INITIALIZATION (Dual-Mode)
# ==========================================
if not firebase_admin._apps:
    try:
        # MODE A: Cloud Mode (Using Streamlit Native Secrets format)
        if "firebase" in st.secrets:
            # This directly converts the secrets block into a dictionary. No JSON parsing needed!
            key_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(key_dict)
            
        # MODE B: Local Mode (Looks for your secure local file)
        else:
            file_path = "src/firebase_key.json" if os.path.exists("src/firebase_key.json") else "firebase_key.json"
            cred = credentials.Certificate(file_path)
            
        firebase_admin.initialize_app(cred)
        print("✅ Firebase successfully connected.")
        
    except Exception as e:
        print(f"🚨 Error connecting to Firebase: {e}")

# Connect to the Firestore database
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
        # 1. Grab raw data directly using .get() to avoid index hangs
        docs = db.collection("transactions").get()
        
        records = []
        for doc in docs:
            data = doc.to_dict()
            if "timestamp" in data:
                del data["timestamp"]
            records.append(data)
            
        # 2. Sort the dates manually in Python so it loads instantly
        records.sort(key=lambda x: x.get("Date", ""), reverse=True)
        return records
        
    except Exception as e:
        print(f"🚨 Error loading from Firestore: {e}")
        return []