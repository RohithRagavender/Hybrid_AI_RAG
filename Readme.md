Hybrid AI Assistant: RAG + Text-to-SQL
An intelligent AI assistant capable of answering questions from unstructured PDF/text documents (RAG) and structured MySQL databases (Text-to-SQL). This system is designed for high data privacy by utilizing a Local LLM (Llama 3) and Local Embeddings.

Features
Smart Query Routing: Automatically identifies if a question requires a database query or a document search.

SQL Security Guardrails: Prevents unauthorized database operations (DELETE, DROP, UPDATE) using keyword-based filtering.

Private & Local: All processing happens locally via Ollama. No data is sent to external cloud APIs like OpenAI or Gemini.

Fail-Safe Mechanism: Handles out-of-scope queries gracefully to prevent hallucinations.


Tech Stack

LLM: Llama 3 (via Ollama)
Framework: LangChain
Vector Database: ChromaDB
Database: MySQL
Embeddings: HuggingFace (all-MiniLM-L6-v2)


Prerequisites

Before running the application, ensure you have the following installed:
Python 3.9+
MySQL Server
Ollama (Download from ollama.com)
Llama 3 Model: Run ollama run llama3 in your terminal.


Setup & Installation

Clone the Repository:
Bash
git clone <your-repo-link>
cd <repo-folder>

Install Dependencies:
Bash
pip install -r requirements.txt
Configure MySQL:


Create a database named ai_assignment.

Update your MySQL USER, PASSWORD, and HOST in app.py.

Prepare the Data:
The system automatically ingests the policy documents provided in the setup_rag() function upon startup.


Usage
Run the assistant using the following command:
Bash
python app.py
Example Queries to Test:
SQL Path: "What is the total revenue from all orders?"

RAG Path: "What is the electronics return policy?"

Guardrail Test: "Delete all records from the orders table."

Fail-Safe Test: "Who is the Prime Minister of India?"


Security Guardrails
Read-Only Access: The system strictly validates generated SQL queries to allow only SELECT statements.

Contextual Grounding: The RAG system is instructed to answer only using the provided documents to avoid hallucinations.