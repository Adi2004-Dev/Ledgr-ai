import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

def create_knowledge_base(pdf_path):
    """Processes a PDF with rate-limiting to avoid 429 Quota errors."""
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")

        
        vector_store = None
        for i in range(0, len(docs), 5):
            batch = docs[i:i+5]
            if vector_store is None:
                vector_store = FAISS.from_documents(batch, embeddings)
            else:
                vector_store.add_documents(batch)
            time.sleep(2) 

        vector_store.save_local("faiss_index")
        return "✅ Guru Knowledge Base Updated Successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_relevant_context(query):
    """Searches the local FAISS index for Guru strategies."""
    if not os.path.exists("faiss_index"):
        return "No specific book context found."

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    docs = vector_store.similarity_search(query, k=3)
    return "\n".join([doc.page_content for doc in docs])
