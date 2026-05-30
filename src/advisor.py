import os
import streamlit as st
import google.generativeai as genai

# Securely load API Key
def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
    return api_key

def get_financial_advice(transaction_details, mentor_name="Warren Buffett"):
    try:
        api_key = get_api_key()
        if not api_key: return "⚠️ API Key missing."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            f"You are the financial expert {mentor_name}. "
            f"Give a short, punchy, 2-sentence piece of financial advice or feedback "
            f"regarding this specific transaction: {transaction_details}"
        )
        
        response = model.generate_content(prompt)
        return response.text.replace("\n", " ").strip()
    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}"

def get_monthly_audit(transaction_history, mentor_name="Warren Buffett"):
    try:
        api_key = get_api_key()
        if not api_key: return "⚠️ API Key missing."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            f"You are the financial expert {mentor_name}. "
            f"Review the following transaction history for this month. "
            f"Provide a brutal but fair financial audit formatted in exactly 3 bullet points:\n"
            f"1. 🎯 Overall assessment of their spending habits.\n"
            f"2. 🚨 The biggest area of waste or concern.\n"
            f"3. 💡 One actionable step to save more money next month.\n\n"
            f"Here are the transactions:\n{transaction_history}"
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}"

def get_chat_response(user_message, chat_history, mentor_name="Warren Buffett"):
    try:
        api_key = get_api_key()
        if not api_key: return "⚠️ API Key missing."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        formatted_history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})
            
        chat = model.start_chat(history=formatted_history)
        prompt = f"(Respond strictly as the financial expert {mentor_name}): {user_message}"
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ AI Chat Error: {str(e)}"