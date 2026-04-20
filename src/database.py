import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

def get_db():
    if not firebase_admin._apps:
        # Try Cloud Secrets first
        try:
            if "firebase" in st.secrets:
                fb_dict = dict(st.secrets["firebase"])
                # Ensure the private key has correct line breaks
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(fb_dict)
                firebase_admin.initialize_app(cred)
                return firestore.client()
        except Exception:
            pass # Fallback to local file below

        # Local Fallback for Mac
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_key = os.path.join(current_dir, 'firebase_key.json')
        
        if os.path.exists(path_to_key):
            cred = credentials.Certificate(path_to_key)
            firebase_admin.initialize_app(cred)
        else:
            st.error("No credentials found! App cannot connect to database.")
            st.stop()
            
    return firestore.client()

def save_to_firestore(data):
    try:
        db = get_db()
        db.collection("ledger").add(data)
        return True
    except Exception:
        return False

def load_from_firestore():
    try:
        db = get_db()
        docs = db.collection("ledger").order_by("Date", direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
    except Exception:
        return []

def delete_all_firestore_data():
    try:
        db = get_db()
        docs = db.collection("ledger").stream()
        for doc in docs:
            doc.reference.delete()
        return True
    except Exception:
        return False