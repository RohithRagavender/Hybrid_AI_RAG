Hybrid AI Assistant: RAG + Text-to-SQL

An intelligent AI assistant capable of answering questions from unstructured PDF/text documents (RAG) and structured MySQL databases (Text-to-SQL). This system is designed for high data privacy by utilizing a Local LLM (Llama 3) and Local Embeddings.

Features
1. Smart Query Routing: Automatically identifies if a question requires a database query or a document search.
2. SQL Security Guardrails: Prevents unauthorized database operations (DELETE, DROP, UPDATE) using keyword-based filtering.
3. Private & Local: All processing happens locally via Ollama. No data is sent to external cloud APIs like OpenAI or Gemini.
4. Fail-Safe Mechanism: Handles out-of-scope queries gracefully to prevent hallucinations.


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



