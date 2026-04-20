import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Get API Key from Secrets (Cloud) or Env (Local)
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def get_financial_advice(transaction_data, mentor_name):
    """Fetches AI financial insight based on user data"""
    if not api_key:
        return "AI Advisor offline (No API Key found)."
    
    try:
        # Using 1.5-flash for higher quota/speed
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
        prompt = f"You are {mentor_name}. Give a snappy, 1-sentence financial tip for this expense: {transaction_data}"
        
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Guru is busy right now. (Error: {e})"