# 💰 Ledgr AI: Agentic Personal Finance Coach

**Ledgr AI** is an intelligent financial companion built for the **Agentic AI Saksham 2026** program. It transforms static financial advice into an interactive experience by combining **OCR receipt scanning** with **Retrieval-Augmented Generation (RAG)**.

---

## 🚀 Key Features

* **📸 OCR Receipt Engine:** Automatically extracts amount and merchant data from UPI screenshots or receipts using Gemini 3 Vision.
* **🧠 Guru Knowledge Base (RAG):** Upload any financial PDF (e.g., Warren Buffett’s strategies) to "train" your advisor. It uses a **FAISS Vector Database** for sub-second information retrieval.
* **🛡️ Smart Rate-Limiting:** Implemented custom **Batch Processing** logic to handle API Quota limits (429 errors) during PDF embedding.
* **📊 Common Man Dashboard:** Real-time budget tracking with progress bars and "Need vs. Want" analysis based on a ₹30,000 monthly goal.
* **🎨 Professional UI:** A sleek, dark-mode dashboard built with Streamlit featuring real-time metrics and responsive layouts.

---

## 🛠️ Tech Stack

- **LLM:** Google Gemini 3 Flash & Gemini 2 Embeddings
- **Orchestration:** LangChain
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Frontend:** Streamlit
- **Environment:** Python 3.9+

---

## 📦 Installation & Setup

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/Adi2004-Dev/ledgr-ai.git](https://github.com/Adi2004-Dev/ledgr-ai.git)
   cd ledgr-ai
