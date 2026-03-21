import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()

def get_financial_advice(spending_data, guru_name):
    """
    Provides personalized advice based on top financial gurus' philosophies.
    """
    # Initialize Gemini 1.5 Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview", 
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # The prompt template for your AI advisor
    template = """
    You are a world-class financial advisor acting as {guru}.
    Context: {data}
    
    Provide 2-3 sentences of advice. Mention one Indian tax-saving tool (like PPF or ELSS) 
    if the spend relates to long-term planning.
    """
    
    # Setting up the LangChain sequence
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        # Run the AI and return the text content
        response = chain.invoke({"guru": guru_name, "data": spending_data})
        return response.content
    except Exception as e:
        return f"Advisor Error: {str(e)}"