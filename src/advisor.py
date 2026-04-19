import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from knowledge_base import get_relevant_context

def get_financial_advice(spending_data, guru_name):
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview", 
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Fetch the real strategies from your uploaded PDF
    context = get_relevant_context(spending_data)
    
    template = """
You are a helpful financial mentor for a common person.
The user's monthly budget is ₹30,000. 

GURU STRATEGIES FROM BOOK:
{context}

NEW TRANSACTION:
{data}

Provide advice in 3 short points:
1. Is this a 'Need' or a 'Want'?
2. How does this impact their ₹30,000 monthly goal?
3. A specific 'Pro-tip' from the uploaded book.
"""
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"guru": guru_name, "data": spending_data, "context": context})
        return response.content
    except Exception as e:
        return f"Advisor Error: {str(e)}"