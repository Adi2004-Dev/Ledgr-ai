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
    /* Main Background */
    .main { background-color: #0e1117; }
    
    /* Metric Card Styling */
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid #3d4156;
    }
    [data-testid="stMetricLabel"] { color: #a1a1aa !important; font-size: 16px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS & KNOWLEDGE BASE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2854/2854537.png", width=70)
    st.title("Ledgr AI Settings")
    
    guru = st.selectbox("🎯 Choose Your Mentor", ["Warren Buffett", "Ramit Sethi", "Saurabh Mukherjea"])
    
    st.divider()
    st.subheader("📚 Guru Knowledge Base")
    st.caption("Upload a financial PDF to train your AI advisor.")
    kb_file = st.file_uploader("Upload PDF", type="pdf")
    
    if kb_file:
        with open("temp.pdf", "wb") as f:
            f.write(kb_file.getbuffer())
        with st.spinner("🧠 Training Agent..."):
            msg = create_knowledge_base("temp.pdf")
            st.success(msg)
        os.remove("temp.pdf")

# --- MAIN DASHBOARD ---
st.title("💰 Ledgr AI: Expense Manager")
st.caption(f"Personalized Advice by: **{guru}** | Monthly Budget Goal: **₹30,000**")

# Metrics Row for "Common People" Utility
m1, m2, m3 = st.columns(3)
total_spent_so_far = 14200  # This could be linked to a database in the future
monthly_budget = 30000

m1.metric("Spent this Month", f"₹{total_spent_so_far}", "₹520 today")
m2.metric("Budget Remaining", f"₹{monthly_budget - total_spent_so_far}")
m3.metric("Savings Status", "On Track", "47%")

# Visual Progress Bar
st.write("### 📈 Monthly Budget Usage")
usage_pct = total_spent_so_far / monthly_budget
st.progress(usage_pct)

if usage_pct > 0.8:
    st.warning(f"⚠️ Warning: You have used {int(usage_pct*100)}% of your budget!")
else:
    st.success(f"✅ Great job! You have used {int(usage_pct*100)}% of your budget. Plenty of room left.")

st.divider()

# --- UPLOAD & ANALYSIS SECTION ---
uploaded_file = st.file_uploader("📸 Upload UPI Screenshot or Receipt", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Process Image
    with open("temp_img.png", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("🔍 AI is reading the receipt..."):
        data = extract_expense_from_image("temp_img.png")
    
    # Layout: Image on Left, Data/Advice on Right
    col_img, col_data = st.columns([1, 1.2])
    
    with col_img:
        st.subheader("Receipt Preview")
        st.image(uploaded_file, use_container_width=True)
    
    with col_data:
        st.subheader("Confirm Transaction")
        
        # Pre-fill inputs with OCR data
        final_amount = st.number_input("Detected Amount (₹)", value=float(data.get('amount', 0)))
        category = st.selectbox("Category", ["Food & Drinks", "Transport", "Shopping", "Investment", "Bills", "Health"])
        note = st.text_input("Note", value="Optional description...")
        
        if st.button(f"✨ Get {guru}'s Advice"):
            with st.spinner("Retrieving strategies from your PDF..."):
                # Combine user data for context
                user_query = f"Amount: {final_amount}, Category: {category}, Note: {note}"
                advice = get_financial_advice(user_query, guru)
                
                st.markdown(f"### 🧔 {guru}'s Insight")
                st.info(advice)
                
                # Show RAG proof
                with st.expander("🔗 Technical Detail: RAG Source Context"):
                    st.write("The advisor is using similarity search to find the most relevant rules from your uploaded PDF to generate this specific advice.")

    os.remove("temp_img.png")
else:
    st.info("👋 **Ready to save?** Upload a screenshot of your latest transaction to get started.")