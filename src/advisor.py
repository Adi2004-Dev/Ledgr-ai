import os
import streamlit as st
import google.generativeai as genai

# Load .env file automatically (for local testing on your Mac)
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

def get_financial_advice(transaction_details, mentor_name="Warren Buffett"):
    try:
        # 1. Try to fetch the API Key from your Mac's .env file first
        api_key = os.getenv("GEMINI_API_KEY")
        
        # 2. If it's empty (because it's on the cloud), fetch from Streamlit Secrets
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
                
        if not api_key:
            return "⚠️ API Key missing. Please check your .env file or Streamlit Secrets."
            
        # 3. Configure the Google SDK securely
        genai.configure(api_key=api_key)
        
        # 4. Call the stable flash model
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
        # 1. Fetch the API Key (Securely checks local .env first, then cloud secrets)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
                
        if not api_key:
            return "⚠️ API Key missing. Please check your .env file or Streamlit Secrets."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # 2. The custom Audit Prompt
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
        # 1. Fetch the API Key securely
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
                
        if not api_key:
            return "⚠️ API Key missing."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # 2. Format the Streamlit history into a format Google understands
        formatted_history = []
        for msg in chat_history:
            # Google calls the AI "model", Streamlit calls it "assistant"
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})
            
        # 3. Start a continuous chat session with that history
        chat = model.start_chat(history=formatted_history)
        
        # 4. Send the new message with the persona instructions
        prompt = f"(Respond strictly as the financial expert {mentor_name}): {user_message}"
        response = chat.send_message(prompt)
        
        return response.text.strip()
        
    except Exception as e:
        return f"⚠️ AI Chat Error: {str(e)}"