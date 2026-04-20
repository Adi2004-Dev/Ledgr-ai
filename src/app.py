import streamlit as st
import os
import pandas as pd
import time
from datetime import datetime
from database import save_to_firestore, load_from_firestore, delete_all_firestore_data
from ocr_engine import extract_expense_from_image
from advisor import get_financial_advice

# 1. Page Configuration
st.set_page_config(page_title="Ledgr AI Pro", page_icon="💰", layout="wide")

# 2. UI Styling
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3d4156; }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State
if 'last_detected' not in st.session_state: st.session_state.last_detected = 0.0
if 'current_advice' not in st.session_state: st.session_state.current_advice = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("💰 Ledgr Settings")
    user_budget = st.number_input("🎯 Monthly Budget (₹)", min_value=1000, value=30000, step=1000)
    guru = st.selectbox("🧔 AI Mentor", ["Warren Buffett", "Ramit Sethi", "Saurabh Mukherjea"])
    
    st.divider()
    if st.button("🔄 RESET ALL DATA"):
        if delete_all_firestore_data():
            st.success("Cloud Data Wiped!")
            st.session_state.current_advice = ""
            time.sleep(1)
            st.rerun()

    st.divider()
    st.subheader("🛠️ Debug Tools")
    if st.button("📡 Test Cloud Connection"):
        test_data = {"Date": str(datetime.now().date()), "Amount": 1.0, "Category": "Test", "Method": "Debug", "Advice": "Cloud working!"}
        if save_to_firestore(test_data): st.success("✅ Firebase Live!")
        else: st.error("❌ Connection Failed")

# --- DATA FETCHING ---
cloud_records = load_from_firestore()
spent_this_month = 0.0

if cloud_records:
    df = pd.DataFrame(cloud_records)
    current_month = datetime.now().strftime("%Y-%m")
    # Convert string dates to pandas datetime to filter
    df['Date_dt'] = pd.to_datetime(df['Date'])
    month_df = df[df['Date_dt'].dt.strftime("%Y-%m") == current_month]
    spent_this_month = month_df['Amount'].sum()

# --- MAIN DASHBOARD ---
st.title("📊 Financial Command Center")
m1, m2, m3 = st.columns(3)
m1.metric("Spent this Month", f"₹{spent_this_month:,.2f}")
m2.metric("Remaining", f"₹{max(0.0, user_budget - spent_this_month):,.2f}")
m3.metric("Status", "Good" if spent_this_month < user_budget else "Over Budget")

st.progress(min(spent_this_month / user_budget, 1.0))

if st.session_state.current_advice:
    st.info(f"🧔 **{guru}'s Insight:** {st.session_state.current_advice}")

# --- TABS ---
tab_entry, tab_history = st.tabs(["➕ Add Entry", "📜 Cloud History"])

with tab_entry:
    method = st.radio("Entry Method:", ["AI Smart Scan", "Manual Entry"], horizontal=True)
    
    if method == "Manual Entry":
        c1, c2, c3 = st.columns(3)
        m_amt = c1.number_input("Amount (₹)", min_value=0.0)
        m_cat = c2.selectbox("Category", ["Food", "Transport", "Bills", "Health", "Shopping", "Other"])
        m_dt = c3.date_input("Date", value=datetime.now())
        
        use_ai = st.checkbox("Consult Guru? (Uses Quota)", value=False)
        
        if st.button("➕ Log Expense"):
            if m_amt > 0:
                advice = "Logged manually."
                if use_ai:
                    with st.spinner("Asking Guru..."):
                        advice = get_financial_advice(f"Spent ₹{m_amt} on {m_cat}", guru)
                
                save_to_firestore({"Date": str(m_dt), "Amount": m_amt, "Category": m_cat, "Method": "Manual", "Advice": advice})
                st.session_state.current_advice = advice
                st.rerun()

with tab_history:
    if cloud_records:
        st.subheader("Cloud Records (Live from Firebase)")
        st.dataframe(pd.DataFrame(cloud_records).drop(columns=['Date_dt'], errors='ignore'), use_container_width=True)
    else:
        st.info("No cloud records found.")