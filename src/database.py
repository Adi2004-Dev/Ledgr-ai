import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

# Setup paths for local use
current_dir = os.path.dirname(os.path.abspath(__file__))
path_to_key = os.path.join(current_dir, 'firebase_key.json')

def get_db():
    """Ensures Firebase is initialized correctly for both Local and Cloud"""
    if not firebase_admin._apps:
        # 1. Check if running on Streamlit Cloud (using Secrets)
        if "firebase" in st.secrets:
            fb_secrets = dict(st.secrets["firebase"])
            # Firebase requires the private key to have correct line breaks
            fb_secrets["private_key"] = fb_secrets["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_secrets)
            firebase_admin.initialize_app(cred)
        
        # 2. Fallback to local file for your MacBook
        elif os.path.exists(path_to_key):
            cred = credentials.Certificate(path_to_key)
            firebase_admin.initialize_app(cred)
        
        else:
            st.error("No Firebase credentials found! Please check Streamlit Secrets or provide firebase_key.json.")
            st.stop()
            
    return firestore.client()

def save_to_firestore(data):
    """Saves a single transaction dictionary to the cloud"""
    try:
        db = get_db()
        db.collection("ledger").add(data)
        return True
    except Exception as e:
        print(f"Firestore Save Error: {e}")
        return False

def load_from_firestore():
    """Fetches all transactions, newest first"""
    try:
        db = get_db()
        docs = db.collection("ledger").order_by("Date", direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Firestore Load Error: {e}")
        return []

def delete_all_firestore_data():
    """Wipes the cloud database for a fresh start"""
    try:
        db = get_db()
        docs = db.collection("ledger").stream()
        for doc in docs:
            doc.reference.delete()
        return True
    except Exception as e:
        print(f"Firestore Delete Error: {e}")
        return False