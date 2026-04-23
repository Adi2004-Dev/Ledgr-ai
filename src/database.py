import os
import streamlit as st

# ==========================================
# MAC O.S. FIREBASE BYPASS HACKS
# These two lines stop Apple from freezing the Google connection
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["GRPC_POLL_STRATEGY"] = "poll"
# ==========================================

def get_db():
    # Lazy import prevents crashing on startup
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    if not firebase_admin._apps:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_key = os.path.join(current_dir, 'firebase_key.json')
        
        if os.path.exists(path_to_key):
            cred = credentials.Certificate(path_to_key)
            firebase_admin.initialize_app(cred)
        else:
            st.error("❌ Cannot find firebase_key.json file.")
            return None
            
    return firestore.client()

def load_from_firestore():
    try:
        db = get_db()
        if db:
            # Added a strict timeout to the Firebase call itself
            docs = db.collection("ledger").order_by("Date", direction="DESCENDING").limit(20).get(timeout=3)
            return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Cloud load failed: {e}")
    return []

def save_to_firestore(data):
    try:
        db = get_db()
        if db:
            db.collection("ledger").add(data)
            return True
    except Exception as e:
        print(f"Cloud save failed: {e}")
    return False