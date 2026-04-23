import os
import streamlit as st
import google.generativeai as genai

# Load .env file automatically
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

def get_financial_advice(transaction_details, mentor_name="Warren Buffett"):
    try:
        # 1. Fetch your API Key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
                
        if not api_key:
            return "⚠️ API Key missing. Please check your .env file."
            
        # 2. Configure the Google SDK
        genai.configure(api_key=api_key)
        
        # 3. Call the EXACT model your key supports!
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