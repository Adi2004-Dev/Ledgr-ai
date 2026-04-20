import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# SAFETY BLOCK: Prevents crash if secrets file is missing or broken
api_key = None
try:
    # Try Cloud Secrets first
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    # Fallback to local .env if on Mac
    api_key = os.getenv("GOOGLE_API_KEY")

def get_financial_advice(transaction_data, mentor_name):
    if not api_key:
        return "AI Guru is currently offline (Key missing)."
    
    try:
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
        prompt = f"You are {mentor_name}. Give a 1-sentence tip for: {transaction_data}"
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"The Guru is meditating... (Error: {e})"