import streamlit as st
from ocr_engine import extract_expense_from_image
from advisor import get_financial_advice

st.set_page_config(page_title="Ledgr AI", layout="wide")
st.title("💰 Ledgr AI: Expense Manager & Advisor")

# Sidebar for track-required guru selection [cite: 62, 147]
st.sidebar.header("Advisory Settings")
guru = st.sidebar.selectbox("Choose Your Guru", ["Ramit Sethi", "Warren Buffett", "Robert Kiyosaki"])

# Week 1-2 Goal: Screenshot expense extraction [cite: 19, 76]
uploaded_file = st.file_uploader("Upload UPI Screenshot", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Payment Receipt", use_container_width=True)
        
    with col2:
        st.subheader("Extracted Details")
        data = extract_expense_from_image(uploaded_file)
        
        # Allow manual correction as per project FAQ [cite: 240]
        amount = st.number_input("Detected Amount (₹)", value=data['amount'], step=1.0)
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Rent", "Investment"])  # [cite: 82]
        
        if st.button("Get Guru Advice"):
            with st.spinner(f"Consulting {guru}..."):
                advice = get_financial_advice(f"Spent ₹{amount} on {category}", guru)
                st.info(advice) # Displays the synthesized advice [cite: 147]