import streamlit as st
import os
from ocr_engine import extract_expense_from_image
from advisor import get_financial_advice
from knowledge_base import create_knowledge_base

# 1. Page Configuration
st.set_page_config(page_title="Ledgr AI | Personal Finance Coach", page_icon="💰", layout="wide")

# 2. Dark Mode Professional CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid #3d4156;
    }
    [data-testid="stMetricLabel"] { color: #a1a1aa !important; font-size: 16px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialize Persistent Data (Session State)
if 'total_spent' not in st.session_state:
    st.session_state.total_spent = 14200  # Starting base spend
if 'last_detected' not in st.session_state:
    st.session_state.last_detected = 0

monthly_budget = 30000

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2854/2854537.png", width=70)
    st.title("Ledgr AI Settings")
    guru = st.selectbox("🎯 Choose Your Mentor", ["Warren Buffett", "Ramit Sethi", "Saurabh Mukherjea"])
    
    st.divider()
    st.subheader("📚 Guru Knowledge Base")
    kb_file = st.file_uploader("Upload PDF", type="pdf")
    
    if kb_file:
        with open("temp.pdf", "wb") as f:
            f.write(kb_file.getbuffer())
        with st.spinner("🧠 Training Agent..."):
            msg = create_knowledge_base("temp.pdf")
            st.success(msg)
        os.remove("temp.pdf")
    
    if st.button("Reset Monthly Spend"):
        st.session_state.total_spent = 0
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("💰 Ledgr AI: Expense Manager")
st.caption(f"Personalized Advice by: **{guru}** | Monthly Budget Goal: **₹30,000**")

# Section 1: Dynamic Metrics & Progress Bar
display_total = st.session_state.total_spent + st.session_state.last_detected

m1, m2, m3 = st.columns(3)
m1.metric("Total Spent", f"₹{display_total}", f"+₹{st.session_state.last_detected}" if st.session_state.last_detected > 0 else None)
m2.metric("Remaining", f"₹{max(0, monthly_budget - display_total)}")
m3.metric("Goal Status", "On Track" if display_total < monthly_budget else "Limit Reached")

st.write("### 📈 Monthly Budget Usage")
usage_pct = min(display_total / monthly_budget, 1.0)
st.progress(usage_pct)

if usage_pct > 0.85:
    st.warning(f"🚨 Warning: You've exhausted {int(usage_pct*100)}% of your budget!")
else:
    st.success(f"✅ Budget usage is at {int(usage_pct*100)}%.")

st.divider()

# Section 2: Upload & Analysis
uploaded_file = st.file_uploader("📸 Upload UPI Screenshot or Receipt", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # We only process if it's a new file upload
    with open("temp_img.png", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("🔍 AI is reading receipt..."):
        # This calls your ocr_engine.py
        data = extract_expense_from_image("temp_img.png")
        st.session_state.last_detected = float(data.get('amount', 0))
    
    col_img, col_data = st.columns([1, 1.2])
    
    with col_img:
        st.subheader("Receipt Preview")
        st.image(uploaded_file, use_container_width=True)
    
    with col_data:
        st.subheader("Confirm Details")
        # Pre-fill inputs with OCR data
        final_amount = st.number_input("Amount (₹)", value=float(st.session_state.last_detected))
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Investment", "Bills"])
        
        if st.button(f"✨ Get {guru}'s Advice"):
            # Update the permanent total when the user confirms with advice
            st.session_state.total_spent += final_amount
            st.session_state.last_detected = 0 # reset for next upload
            
            with st.spinner("Searching Knowledge Base..."):
                user_query = f"Amount: {final_amount}, Category: {category}"
                advice = get_financial_advice(user_query, guru)
                
                st.markdown(f"### 🧔 {guru}'s Insight")
                st.info(advice)
                
                with st.expander("🔗 RAG Source Context"):
                    st.write("Retrieved specific spending rules from the uploaded PDF to verify this transaction against your long-term goals.")
            
            # Auto-refresh to update the top Spend Bar
            st.rerun()

    os.remove("temp_img.png")
else:
    st.info("👋 Upload a screenshot to see your budget progress update live!")

st.divider()
st.caption("Ledgr AI | Your Personal Finance Coach | Powered by Google Gemini & LangChain")