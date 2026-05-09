# 💰 Ledgr AI: Intelligent Expense Manager

Ledgr AI is a smart, cloud-connected personal finance dashboard built with Python and Streamlit. It goes beyond basic expense tracking by integrating Google's Gemini AI to provide real-time, personalized financial coaching every time you log a transaction.

## ✨ Key Features

* **🔒 Multi-User Secure Vaults:** Powered by Firebase Firestore, users can log in with a unique username to access their own private, isolated financial data.
* **🤖 AI Financial Mentors:** Get tailored advice on individual transactions from AI personas like Warren Buffett, Ramit Sethi, or Ankur Warikoo (powered by Gemini 2.5 Flash).
* **📸 Smart Receipt Scanning:** Upload a photo of a receipt, and the custom OCR engine automatically extracts the total amount and categorizes the expense.
* **📊 Interactive Analytics:** Beautiful, interactive donut charts and daily trend lines built with Plotly to visualize spending habits.
* **💬 Conversational AI Chat:** A built-in chat interface that remembers your financial context, allowing you to ask follow-up questions about your budget and spending.
* **📋 Monthly AI Audit:** Feed your entire month's transaction history to the AI for a comprehensive 3-point performance review and actionable savings advice.

## 🧰 Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python)
* **Backend Database:** [Firebase Firestore](https://firebase.google.com/products/firestore) (NoSQL)
* **AI Engine:** Google Generative AI (`gemini-2.5-flash`)
* **Data Visualization:** Plotly Express & Pandas

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/ledgr-ai.git](https://github.com/your-username/ledgr-ai.git)
cd ledgr-ai

2. Install dependencies
pip install -r requirements.txt

3. Set up your API Keys

Create a .streamlit folder in the root directory, and inside it create a secrets.toml file. Add your Google Gemini API key:
GEMINI_API_KEY="Your_Actual_API_Key_Here"
(Note: You will also need your firebase_key.json file in the root directory to connect to the Firestore database).

4. Run the app
python3 -m streamlit run src/app.py

📂 Project Structure
src/app.py: The main Streamlit dashboard and UI routing.

src/advisor.py: Handles all API calls to Google Gemini for chat, audits, and advice.

src/database.py: Manages secure, multi-tenant read/write operations with Firebase.

src/ocr_engine.py: Processes uploaded images to extract text and financial data.