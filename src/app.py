import streamlit as st
import pandas as pd
from datetime import datetime
import warnings

# Hide terminal warnings
warnings.filterwarnings("ignore")

from database import save_to_firestore, load_from_firestore
from advisor import get_financial_advice
from ocr_engine import extract_expense_from_image

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Ledgr AI: Expense Manager", page_icon="💰", layout="wide")

# --- 2. SESSION STATE ---
if 'ledger_records' not in st.session_state:
    st.session_state.ledger_records = []
if 'ocr_amt' not in st.session_state:
    st.session_state.ocr_amt = 0.0
if 'ocr_cat' not in st.session_state:
    st.session_state.ocr_cat = "Other"
# Catch the latest advice so we can display it under the button
if 'latest_advice' not in st.session_state:
    st.session_state.latest_advice = None
if 'latest_mentor' not in st.session_state:
    st.session_state.latest_mentor = None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("📚 Ledgr AI Settings")
    
    st.markdown("🎯 **Choose Your Mentor**")
    ai_mentor = st.selectbox("Mentor", ["Warren Buffett", "Ramit Sethi", "Ankur Warikoo"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("📚 **Guru Knowledge Base**")
    st.caption("Upload a financial PDF to train your AI advisor.")
    kb_pdf = st.file_uploader("Upload PDF", type=['pdf'], help="Limit 200MB per file • PDF")
    
    if kb_pdf:
        st.success(f"{kb_pdf.name} loaded to Knowledge Base!")

    st.divider()
    
    if st.button("🔄 Sync with Firebase", use_container_width=True):
        with st.spinner("Fetching cloud data..."):
            data = load_from_firestore()
            if data:
                st.session_state.ledger_records = data
                st.success("Synced Successfully!")
            else:
                st.warning("Database empty or offline.")

# --- 4. HEADER & METRICS ---
st.title("💰 Ledgr AI: Expense Manager 🔗")

budget_goal = 30000
total_spent = sum(item.get('Amount', 0) for item in st.session_state.ledger_records)
remaining = max(0, budget_goal - total_spent)
percent_used = (total_spent / budget_goal) * 100 if budget_goal > 0 else 0

st.caption(f"Personalized Advice by: **{ai_mentor}** | Monthly Budget Goal: **₹{budget_goal:,.0f}**")

# Metric Cards
c1, c2, c3 = st.columns(3)
c1.metric("Spent this Month", f"₹{total_spent:,.0f}") 
c2.metric("Budget Remaining", f"₹{remaining:,.0f}")

if percent_used <= 80:
    c3.metric("Savings Status", "On Track", f"↑ {percent_used:.0f}%")
else:
    c3.metric("Savings Status", "At Risk", f"↓ {percent_used:.0f}%", delta_color="inverse")

# --- 5. PROGRESS TRACKER ---
st.markdown("### 📈 Monthly Budget Usage")
st.progress(min(percent_used / 100, 1.0))

if percent_used <= 80:
    st.success(f"✅ Great job! You have used {percent_used:.0f}% of your budget. Plenty of room left.")
elif percent_used <= 100:
    st.warning(f"⚠️ Careful! You have used {percent_used:.0f}% of your budget.")
else:
    st.error(f"🚨 You have exceeded your budget by ₹{total_spent - budget_goal:,.0f}!")

st.divider()

# --- 6. LOG TRANSACTION SECTION ---
st.markdown("### 📝 Log a Transaction")
tab_manual, tab_scan = st.tabs(["✍️ Manual Entry", "📸 AI Receipt Scan"])

# --- TAB 1: MANUAL ENTRY ---
with tab_manual:
    with st.form("manual_entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        amt = col1.number_input("Amount (₹)", min_value=0.0, step=100.0)
        cat = col2.selectbox("Category", ["Food", "Bills", "Health", "Shopping", "Transport", "Other"])
        dt = col3.date_input("Date", value=datetime.now())
        
        st.markdown("") 
        ask_ai = st.checkbox(f"🤖 Ask {ai_mentor} for advice on this transaction", value=True)
        
        submit_manual = st.form_submit_button("🚀 Log & Sync to Cloud", use_container_width=True)
        
        if submit_manual:
            if amt > 0:
                advice = "Quick Log (No AI Advice)"
                
                if ask_ai:
                    with st.spinner(f"Getting AI insights from {ai_mentor}..."):
                        advice = get_financial_advice(f"Spent ₹{amt} on {cat}", ai_mentor)
                        st.session_state.latest_advice = advice
                        st.session_state.latest_mentor = ai_mentor
                else:
                    st.session_state.latest_advice = None
                
                new_tx = {"Date": str(dt), "Amount": amt, "Category": cat, "Advice": advice}
                st.session_state.ledger_records.insert(0, new_tx)
                save_to_firestore(new_tx) 
                
                st.balloons()
                st.success("✅ Transaction Logged Successfully!")
                # Removed st.rerun() to fix the double-click bug
            else:
                st.warning("Amount must be greater than 0.")
                
    # ✨ THE NEW ADVICE BOX ✨
    if st.session_state.latest_advice:
        st.info(f"💡 **{st.session_state.latest_mentor} says:** {st.session_state.latest_advice}")

# --- TAB 2: AI SCANNER ---
with tab_scan:
    receipt_file = st.file_uploader("Drag and drop file here", type=['png', 'jpg', 'jpeg'], help="Limit 200MB per file")
    
    col_preview, col_confirm = st.columns(2)
    
    with col_preview:
        st.subheader("Receipt Preview")
        if receipt_file:
            st.image(receipt_file, use_container_width=True)
            if st.button("🔍 Scan with AI"):
                with st.spinner("Extracting..."):
                    res = extract_expense_from_image(receipt_file)
                    st.session_state.ocr_amt = float(res.get('amount', 0))
                    
                    cat = res.get('category', 'Other')
                    valid_cats = ["Food", "Bills", "Health", "Shopping", "Transport", "Other"]
                    st.session_state.ocr_cat = cat if cat in valid_cats else "Other"
                    st.success("Extracted!")
        else:
            st.info("Upload an image above to see preview.")

    with col_confirm:
        st.subheader("Confirm Transaction")
        with st.form("confirm_tx_form", clear_on_submit=True):
            final_amt = st.number_input("Detected Amount (₹)", value=st.session_state.ocr_amt, min_value=0.0)
            valid_categories = ["Food", "Bills", "Health", "Shopping", "Transport", "Other"]
            final_cat = st.selectbox("Category", valid_categories, index=valid_categories.index(st.session_state.ocr_cat))
            final_dt = st.date_input("Date", value=datetime.now())
            
            submit_scan = st.form_submit_button("🚀 Confirm & Sync to Cloud", use_container_width=True)
            
            if submit_scan:
                if final_amt > 0:
                    with st.spinner(f"Getting AI insights from {ai_mentor}..."):
                        advice = get_financial_advice(f"Spent ₹{final_amt} on {final_cat}", ai_mentor)
                        
                        st.session_state.latest_advice = advice
                        st.session_state.latest_mentor = ai_mentor
                        
                        new_tx = {"Date": str(final_dt), "Amount": final_amt, "Category": final_cat, "Advice": advice}
                        st.session_state.ledger_records.insert(0, new_tx)
                        save_to_firestore(new_tx)
                        
                        st.balloons()
                        st.success("✅ Transaction Logged Successfully!")
                        st.session_state.ocr_amt = 0.0
                        st.session_state.ocr_cat = "Other"
                        # Removed st.rerun() to fix the double-click bug
                else:
                    st.warning("Amount must be greater than 0.")
                    
        # ✨ THE NEW ADVICE BOX ✨
        if st.session_state.latest_advice:
            st.info(f"💡 **{st.session_state.latest_mentor} says:** {st.session_state.latest_advice}")

# --- 7. HISTORY TABLE ---
st.divider()
st.subheader("📜 Recent Transactions")

if st.session_state.ledger_records:
    df = pd.DataFrame(st.session_state.ledger_records)
    cols = ["Date", "Category", "Amount", "Advice"]
    st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True)
else:
    st.info("No records yet. Log a new transaction or click 'Sync with Firebase' in the sidebar.")