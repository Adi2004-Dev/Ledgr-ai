# Ledgr-ai
# 💰 Ledgr AI: Financial Advisor & Expense Manager

**Ledgr AI** is an intelligent expense tracking and advisory system built for the **Track A: Foundation & Quick Win** milestone. It allows users to upload UPI payment screenshots (PhonePe/GPay), extracts transaction data using OCR, and provides personalized financial guidance based on the philosophies of world-class gurus like **Ramit Sethi** and **Warren Buffett**.

---

## 🚀 Key Features (Week 1 Milestone)
* **Automated OCR Extraction:** Uses Tesseract OCR to scan Indian UPI screenshots and identify transaction amounts.
* **Manual Correction Layer:** A robust UI feature allowing users to override OCR errors (e.g., separating system time from transaction amounts) for 100% data integrity.
* **Guru-Based Advisory:** Integrated with **Google Gemini 3 Flash** to provide synthesized financial advice tailored to specific spending categories.
* **Indian Tax Context:** Provides context-aware suggestions for tax-saving instruments like **ELSS** and **PPF**.

---

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Framework:** Streamlit (Frontend Dashboard)
* **Orchestration:** LangChain (LLM Chain Management)
* **AI Model:** Google Gemini 3 Flash
* **OCR:** PyTesseract (Tesseract Engine)
* **Environment:** Virtual Environments (venv) with `.env` secret management.

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/ledgr-ai.git](https://github.com/your-username/ledgr-ai.git)
   cd ledgr-ai
