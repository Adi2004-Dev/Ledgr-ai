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
    You are a financial expert acting as {guru}.
    
    GURU STRATEGIES (Use these first):
    {context}
    
    TRANSACTION DATA:
    {data}
    
    Provide 3 sentences of advice. If the 'GURU STRATEGIES' mention a specific percentage or rule, 
    apply it directly to this transaction.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"guru": guru_name, "data": spending_data, "context": context})
        return response.content
    except Exception as e:
        return f"Advisor Error: {str(e)}"