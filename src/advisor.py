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
        
        # 4. Call the stable 1.5 flash model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = (
            f"You are the financial expert {mentor_name}. "
            f"Give a short, punchy, 2-sentence piece of financial advice or feedback "
            f"regarding this specific transaction: {transaction_details}"
        )
        
        response = model.generate_content(prompt)
        return response.text.replace("\n", " ").strip()
        
    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}"