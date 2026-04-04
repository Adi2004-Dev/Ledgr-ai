import streamlit as st
import os
from ocr_engine import extract_expense_from_image
from advisor import get_financial_advice
from knowledge_base import create_knowledge_base

st.set_page_config(page_title="Ledgr AI", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    guru = st.selectbox("Choose Your Guru", ["Warren Buffett", "Ramit Sethi", "Saurabh Mukherjea"])
    
    st.divider()
    st.subheader("📚 Guru Knowledge Base")
    kb_file = st.file_uploader("Upload Financial PDF", type="pdf")
    
    if kb_file:
        with open("temp.pdf", "wb") as f:
            f.write(kb_file.getbuffer())
        with st.spinner("Training Guru Brain..."):
            msg = create_knowledge_base("temp.pdf")
            st.success(msg)
        os.remove("temp.pdf")

# --- MAIN UI ---
st.title("💰 Ledgr AI: Expense Manager")
uploaded_file = st.file_uploader("Upload UPI Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    with open("temp_img.png", "wb") as f:
        f.write(uploaded_file.getbuffer())
    data = extract_expense_from_image("temp_img.png")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file)
    with col2:
        amount = st.number_input("Detected Amount (₹)", value=float(data['amount']))
        if st.button("Consult Guru"):
            with st.spinner("Analyzing..."):
                advice = get_financial_advice(f"Amount: {amount}", guru)
                st.info(advice)