import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import os

# ==========================================
# 1. FIREBASE INITIALIZATION (Dual-Mode)
# ==========================================
if not firebase_admin._apps:
    try:
        # MODE A: Cloud Mode (Looks for the key in Streamlit Secrets)
        if "FIREBASE_JSON" in st.secrets:
            key_dict = json.loads(st.secrets["FIREBASE_JSON"])
            cred = credentials.Certificate(key_dict)
            
        # MODE B: Local Mode (Looks for your secure local file)
        else:
            # It checks both the main folder and the src folder just to be safe
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
    """
    Saves a new transaction record to the Firestore 'transactions' collection.
    """
    try:
        # We add a hidden server timestamp so Firebase can sort them accurately
        transaction_data["timestamp"] = firestore.SERVER_TIMESTAMP
        
        # Add the document to the 'transactions' collection
        db.collection("transactions").add(transaction_data)
        return True
    except Exception as e:
        print(f"🚨 Error saving to Firestore: {e}")
        return False

def load_from_firestore():
    """
    Loads all transactions from Firestore, sorting them so the newest are at the top.
    """
    try:
        # Fetch records ordered by Date (Newest first)
        docs = db.collection("transactions").order_by(
            "Date", direction=firestore.Query.DESCENDING
        ).stream()
        
        records = []
        for doc in docs:
            data = doc.to_dict()
            # Remove the hidden timestamp before sending it to the Streamlit table
            if "timestamp" in data:
                del data["timestamp"]
            records.append(data)
            
        return records
    except Exception as e:
        print(f"🚨 Error loading from Firestore: {e}")
        return []