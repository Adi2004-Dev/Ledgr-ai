import streamlit as st
import pandas as pd
from datetime import datetime
from database import save_to_firestore, load_from_firestore, delete_all_firestore_data
from advisor import get_financial_advice

# 1. Page Config
st.set_page_config(page_title="Ledgr AI Pro", page_icon="💰", layout="wide")

# 2. Fetch Data
cloud_records = load_from_firestore()
spent_this_month = sum(item['Amount'] for item in cloud_records) if cloud_records else 0.0

# 3. Sidebar
with st.sidebar:
    st.title("💰 Settings")
    budget = st.number_input("Budget Goal (₹)", value=30000)
    guru = st.selectbox("AI Mentor", ["Warren Buffett", "Ramit Sethi"])
    
    if st.button("🔄 Reset Cloud Data"):
        delete_all_firestore_data()
        st.rerun()

# 4. Main UI
st.title("📊 Ledgr AI Command Center")
st.metric("Spent this Month", f"₹{spent_this_month:,.2f}")
st.progress(min(spent_this_month / budget, 1.0))

tab_add, tab_history = st.tabs(["➕ Add Expense", "📜 Cloud History"])

with tab_add:
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input("Amount (₹)", min_value=0.0)
    cat = c2.selectbox("Category", ["Food", "Transport", "Bills", "Health", "Shopping", "Other"])
    dt = c3.date_input("Date", value=datetime.now())
    
    ask_ai = st.checkbox("Get AI Advice?", value=True)
    
    if st.button("🚀 Log to Cloud"):
        if amt > 0:
            with st.spinner("Talking to Cloud..."):
                advice = get_financial_advice(f"Spent ₹{amt} on {cat}", guru) if ask_ai else "Manual entry."
                data = {"Date": str(dt), "Amount": amt, "Category": cat, "Advice": advice}
                if save_to_firestore(data):
                    st.success("Successfully saved to Firebase!")
                    st.rerun()
                else:
                    st.error("Failed to save.")

with tab_history:
    if cloud_records:
        st.dataframe(pd.DataFrame(cloud_records), use_container_width=True)
    else:
        st.info("No cloud history found.")