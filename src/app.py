import streamlit as st
import pandas as pd
from datetime import datetime
from database import save_to_firestore, load_from_firestore, delete_all_firestore_data
from advisor import get_financial_advice
from ocr_engine import extract_expense_from_image # <--- Make sure this is back!

st.set_page_config(page_title="Ledgr AI Pro", page_icon="💰", layout="wide")

# --- FETCH DATA ---
cloud_records = load_from_firestore()
spent_this_month = sum(item['Amount'] for item in cloud_records) if cloud_records else 0.0

# --- SIDEBAR ---
with st.sidebar:
    st.title("💰 Settings")
    budget = st.number_input("Budget Goal (₹)", value=30000)
    guru = st.selectbox("AI Mentor", ["Warren Buffett", "Ramit Sethi"])
    if st.button("🔄 Reset Cloud Data"):
        delete_all_firestore_data()
        st.rerun()

# --- MAIN UI ---
st.title("📊 Ledgr AI Command Center")
st.metric("Spent this Month", f"₹{spent_this_month:,.2f}")
st.progress(min(spent_this_month / budget, 1.0))

tab_add, tab_history = st.tabs(["➕ Add Expense", "📜 Cloud History"])

with tab_add:
    # ADDING THE OCR SECTION BACK HERE:
    method = st.radio("Entry Method", ["Manual", "AI Scan (Upload Receipt)"], horizontal=True)
    
    if method == "AI Scan (Upload Receipt)":
        uploaded_file = st.file_uploader("Upload a receipt image", type=['jpg', 'png', 'jpeg'])
        if uploaded_file is not None:
            if st.button("🔍 Scan with AI"):
                with st.spinner("Extracting data..."):
                    detected = extract_expense_from_image(uploaded_file)
                    # This fills in the manual boxes below automatically
                    st.session_state.temp_amt = detected['amount']
                    st.session_state.temp_cat = detected['category']
    
    st.divider()
    
    # Manual Input Section (Syncs with OCR)
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input("Amount (₹)", min_value=0.0, value=st.session_state.get('temp_amt', 0.0))
    cat = c2.selectbox("Category", ["Food", "Bills", "Health", "Shopping", "Other"], 
                       index=["Food", "Bills", "Health", "Shopping", "Other"].index(st.session_state.get('temp_cat', 'Food')))
    dt = c3.date_input("Date", value=datetime.now())
    
    if st.button("🚀 Log to Cloud"):
        advice = get_financial_advice(f"Spent ₹{amt} on {cat}", guru)
        save_to_firestore({"Date": str(dt), "Amount": amt, "Category": cat, "Advice": advice})
        st.success("Logged!")
        st.rerun()

with tab_history:
    if cloud_records:
        st.dataframe(pd.DataFrame(cloud_records), use_container_width=True)