import streamlit as st
import pandas as pd
from datetime import datetime
import warnings
import plotly.express as px

warnings.filterwarnings("ignore")

from database import save_to_firestore, load_from_firestore
from advisor import get_financial_advice, get_monthly_audit, get_chat_response
from ocr_engine import extract_expense_from_image

st.set_page_config(page_title="Ledgr AI: Expense Manager", page_icon="💰", layout="wide")

# --- SESSION STATE ---
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'ledger_records' not in st.session_state:
    st.session_state.ledger_records = []
if 'ocr_amt' not in st.session_state:
    st.session_state.ocr_amt = 0.0
if 'ocr_cat' not in st.session_state:
    st.session_state.ocr_cat = "Other"
if 'latest_advice' not in st.session_state:
    st.session_state.latest_advice = None
if 'latest_mentor' not in st.session_state:
    st.session_state.latest_mentor = None
if 'budget_goal' not in st.session_state:
    st.session_state.budget_goal = 30000.0
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# ==========================================
# 🔒 THE LOGIN GATE
# ==========================================
if st.session_state.current_user is None:
    st.title("🔒 Welcome to Ledgr AI")
    st.markdown("Your personal AI-powered financial vault.")
    
    with st.container(border=True):
        with st.form("login_form"):
            username_input = st.text_input("Enter a unique username to open your vault:")
            submit_login = st.form_submit_button("Enter Vault 🚀", use_container_width=True)
            
            if submit_login:
                if username_input.strip() == "":
                    st.error("Please enter a username!")
                else:
                    st.session_state.current_user = username_input.strip().lower()
                    st.session_state.ledger_records = [] 
                    st.rerun()

else:
    # ==========================================
    # 🔓 THE MAIN APP (Only runs if logged in)
    # ==========================================
    with st.sidebar:
        # Added Logout Button
        st.markdown(f"👤 **Logged in as:** `{st.session_state.current_user}`")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.ledger_records = []
            st.rerun()
            
        st.title("📚 Ledgr AI Settings")
        st.markdown("🎯 **Choose Your Mentor**")
        ai_mentor = st.selectbox("Mentor", ["Warren Buffett", "Ramit Sethi", "Ankur Warikoo"], label_visibility="collapsed")
        st.divider()

        st.markdown("🎯 **Set Monthly Budget**")
        st.session_state.budget_goal = st.number_input(
            "Budget Goal (₹)", 
            min_value=1000.0, 
            value=float(st.session_state.budget_goal), 
            step=1000.0,
            label_visibility="collapsed"
        )
        
        st.markdown("📚 **Guru Knowledge Base**")
        kb_pdf = st.file_uploader("Upload PDF", type=['pdf'], help="Limit 200MB per file • PDF")
        if kb_pdf:
            st.success(f"{kb_pdf.name} loaded!")

        st.divider()
        
        if st.button("🔄 Sync with Firebase", use_container_width=True):
            with st.spinner("Fetching data..."):
                # UPDATED: Now passes the specific user_id to Firestore!
                data = load_from_firestore(st.session_state.current_user)
                if data is not None:
                    st.session_state.ledger_records = data
                    st.success("Synced Successfully!")
                else:
                    st.warning("Database offline.")

    st.title("💰 Ledgr AI: Expense Manager")

    budget_goal = st.session_state.budget_goal
    total_spent = sum(float(item.get('Amount', 0)) for item in st.session_state.ledger_records)
    remaining = max(0, budget_goal - total_spent)
    percent_used = (total_spent / budget_goal) * 100 if budget_goal > 0 else 0

    st.caption(f"Personalized Advice by: **{ai_mentor}** | Monthly Budget Goal: **₹{budget_goal:,.0f}**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Spent this Month", f"₹{total_spent:,.0f}") 
    c2.metric("Budget Remaining", f"₹{remaining:,.0f}")

    if percent_used <= 80:
        c3.metric("Savings Status", "On Track", f"↑ {percent_used:.0f}%")
    else:
        c3.metric("Savings Status", "At Risk", f"↓ {percent_used:.0f}%", delta_color="inverse")

    st.markdown("### 📈 Monthly Budget Usage")
    st.progress(min(percent_used / 100, 1.0))

    st.divider()

    st.markdown("### 📝 Log a Transaction")
    tab_manual, tab_scan = st.tabs(["✍️ Manual Entry", "📸 AI Receipt Scan"])

    with tab_manual:
        with st.form("manual_entry_form", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)
            amt = col1.number_input("Amount (₹)", min_value=0.0, step=100.0)
            cat = col2.selectbox("Category", ["Food", "Bills", "Health", "Shopping", "Transport", "Other"])
            dt = col3.date_input("Date", value=datetime.now())
            
            ask_ai = st.checkbox(f"🤖 Ask {ai_mentor} for advice", value=True)
            submit_manual = st.form_submit_button("🚀 Log & Sync", use_container_width=True)
            
            if submit_manual:
                if amt > 0:
                    advice = "Quick Log (No AI Advice)"
                    if ask_ai:
                        with st.spinner(f"Asking {ai_mentor}..."):
                            advice = get_financial_advice(f"Spent ₹{amt} on {cat}", ai_mentor)
                            st.session_state.latest_advice = advice
                            st.session_state.latest_mentor = ai_mentor
                    else:
                        st.session_state.latest_advice = None
                    
                    new_tx = {"Date": str(dt), "Amount": amt, "Category": cat, "Advice": advice}
                    st.session_state.ledger_records.insert(0, new_tx)
                    
                    # UPDATED: Now saves the transaction with the user's name!
                    save_to_firestore(new_tx, st.session_state.current_user) 
                    st.success("✅ Transaction Logged!")
                else:
                    st.warning("Amount must be greater than 0.")
                    
        if st.session_state.latest_advice:
            st.info(f"💡 **{st.session_state.latest_mentor} says:** {st.session_state.latest_advice}")

    with tab_scan:
        receipt_file = st.file_uploader("Upload Receipt", type=['png', 'jpg', 'jpeg'])
        col_preview, col_confirm = st.columns(2)
        
        with col_preview:
            if receipt_file:
                st.image(receipt_file, use_container_width=True)
                if st.button("🔍 Scan with AI"):
                    with st.spinner("Extracting..."):
                        res = extract_expense_from_image(receipt_file)
                        st.session_state.ocr_amt = float(res.get('amount', 0))
                        valid_cats = ["Food", "Bills", "Health", "Shopping", "Transport", "Other"]
                        cat = res.get('category', 'Other')
                        st.session_state.ocr_cat = cat if cat in valid_cats else "Other"
                        st.success("Extracted!")

        with col_confirm:
            with st.form("confirm_tx_form", clear_on_submit=False):
                final_amt = st.number_input("Detected Amount (₹)", value=float(st.session_state.ocr_amt), min_value=0.0)
                valid_cats = ["Food", "Bills", "Health", "Shopping", "Transport", "Other"]
                final_cat = st.selectbox("Category", valid_cats, index=valid_cats.index(st.session_state.ocr_cat))
                final_dt = st.date_input("Date", value=datetime.now())
                
                submit_scan = st.form_submit_button("🚀 Confirm & Sync", use_container_width=True)
                
                if submit_scan:
                    if final_amt > 0:
                        with st.spinner(f"Asking {ai_mentor}..."):
                            advice = get_financial_advice(f"Spent ₹{final_amt} on {final_cat}", ai_mentor)
                            st.session_state.latest_advice = advice
                            st.session_state.latest_mentor = ai_mentor
                            
                            new_tx = {"Date": str(final_dt), "Amount": final_amt, "Category": final_cat, "Advice": advice}
                            st.session_state.ledger_records.insert(0, new_tx)
                            
                            # UPDATED: Now saves the transaction with the user's name!
                            save_to_firestore(new_tx, st.session_state.current_user)
                            
                            st.toast("✅ Transaction Logged!")
                            st.session_state.ocr_amt = 0.0
                            st.session_state.ocr_cat = "Other"
                    else:
                        st.warning("Amount must be greater than 0.")
                        
            if st.session_state.latest_advice:
                st.info(f"💡 **{st.session_state.latest_mentor} says:** {st.session_state.latest_advice}")

    st.divider()

    # --- ANALYTICS DASHBOARD ---
    st.divider()
    st.markdown("### 📊 Spending Analytics")

    if st.session_state.ledger_records:
        # 1. Prepare the data
        df_chart = pd.DataFrame(st.session_state.ledger_records)
        df_chart['Amount'] = pd.to_numeric(df_chart['Amount'])
        df_chart['Date'] = pd.to_datetime(df_chart['Date'])
        
        col_chart1, col_chart2 = st.columns(2)
        
        # 2. Donut Chart: Spending by Category
        with col_chart1:
            st.markdown("**Where your money goes**")
            cat_df = df_chart.groupby("Category")["Amount"].sum().reset_index()
            fig_pie = px.pie(cat_df, values='Amount', names='Category', hole=0.4, 
                             color_discrete_sequence=px.colors.sequential.Teal)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        # 3. Line Chart: Daily Spending Trend
        with col_chart2:
            st.markdown("**Daily Spending Trend**")
            trend_df = df_chart.groupby("Date")["Amount"].sum().reset_index()
            trend_df = trend_df.sort_values("Date")
            fig_line = px.line(trend_df, x="Date", y="Amount", markers=True, 
                               color_discrete_sequence=["#2ECB71"])
            fig_line.update_layout(margin=dict(t=0, b=0, l=0, r=0), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Log some transactions to see your spending analytics!")

    # --- 🤖 MONTHLY AI AUDIT ---
    st.divider()
    st.markdown("### 🤖 Monthly AI Audit")
    st.caption("Feed your entire month of data to the AI for a deep-dive review.")

    if st.button(f"Generate Audit with {ai_mentor}", use_container_width=True):
        if not st.session_state.ledger_records:
            st.warning("Log some transactions first so I have data to analyze!")
        else:
            with st.spinner(f"Crunching the numbers... {ai_mentor} is reviewing your accounts..."):
                # 1. Format the data into a clean text list for the AI to read
                history_text = "\n".join([
                    f"{tx.get('Date', 'Unknown Date')} - {tx.get('Category', 'Other')}: ₹{tx.get('Amount', 0)}" 
                    for tx in st.session_state.ledger_records
                ])
                
                # 2. Call the new AI function
                audit_result = get_monthly_audit(history_text, ai_mentor)
            
            # 3. Display the result in a nice, highlighted box
            with st.container(border=True):
                st.markdown(f"#### 📜 Official Audit by {ai_mentor}")
                st.info(audit_result)

    # --- 💬 INTERACTIVE AI CHAT ---
    st.divider()
    st.markdown(f"### 💬 Ask {ai_mentor} Anything")
    st.caption("Ask follow-up questions about your budget, transactions, or general financial advice.")

    # 1. Display all previous messages in the chat window
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 2. The chat input box at the bottom
    if prompt := st.chat_input("E.g., How can I reduce my food budget?"):
        
        # Show the user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Save the user's message to memory
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Show the AI thinking, then display the response
        with st.chat_message("assistant"):
            with st.spinner(f"{ai_mentor} is typing..."):
                # Call our new AI function, passing the history (excluding the message we just added)
                ai_response = get_chat_response(prompt, st.session_state.chat_messages[:-1], ai_mentor)
                st.markdown(ai_response)
                
        # Save the AI's response to memory
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})

    st.subheader("📜 Recent Transactions")
    if st.session_state.ledger_records:
        df = pd.DataFrame(st.session_state.ledger_records)
        st.dataframe(df[["Date", "Category", "Amount", "Advice"]], use_container_width=True)