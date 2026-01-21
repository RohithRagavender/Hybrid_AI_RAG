import re
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# MySQL Connection Details
USER = "root"
PASSWORD = "root"
HOST = "localhost"
DB_NAME = "ai_assignment"

mysql_uri = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DB_NAME}"
db = SQLDatabase.from_uri(mysql_uri)




# Initialize Local LLM and Embeddings
llm = OllamaLLM(model="llama3")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")






# --- 2. RAG SETUP (Knowledge Base) ---
def setup_rag():
    documents = [
    "Shipping Policy: Standard domestic shipping takes 3-5 business days. International shipping takes 10-15 business days. Free shipping is applicable on all orders exceeding $50. Once shipped, customers receive a tracking link via email.",
    
    "General Return Policy: We offer a 30-day return policy for most items. Products must be unused, in their original packaging, and with all tags attached. Perishable goods and personalized items are not eligible for return.",
    
    "Electronics Specific Policy: All electronic gadgets, including laptops and smartphones, have a limited 15-day return window. Any hardware defects reported after 15 days must be handled through the manufacturer's warranty services.",
    
    "Refund Process: Once a return is received and inspected, we notify the customer of the approval or rejection of the refund. Approved refunds are credited to the original payment method within 7-10 working days.",
    
    "Customer Support Availability: Our support team is available Monday through Friday, from 9 AM to 6 PM IST. We are closed on national holidays. For assistance, reach out via email at support@ai-store.com.",
    
    "Data Privacy & Security: We prioritize user data security. We use 256-bit SSL encryption to protect your personal information during checkout. Payment transactions are processed through a secure gateway provider.",
    
    "Cancellation Policy: Orders can be cancelled within 2 hours of placement for a full refund. After 2 hours, the order enters the processing stage and cannot be cancelled. In such cases, customers must wait for delivery and then initiate a return.",
    
    "Warranty Information: Most products come with a 1-year limited manufacturer warranty. This covers functional defects but does not cover physical damage, liquid spills, or unauthorized repairs.",
    
    "Priority Support: For urgent issues or order escalations, please contact our 24/7 priority support at emergency@store.com with your Order ID in the subject line."
  ]
    # it will store the documents in a local directory named 'chroma_db'
    vectorstore = Chroma.from_texts(documents, embeddings)
    return vectorstore.as_retriever()
retriever = setup_rag()



# --- 3. GUARDRAILS (The Security Layer) ---
def validate_sql(query: str) -> bool:
    """Check for unsafe operations."""
    unsafe_keywords = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    for word in unsafe_keywords:
        if re.search(rf"\b{word}\b", query, re.IGNORECASE):
            return False
    return True



# --- 4. THE ROUTER (Logic to decide SQL vs RAG) ---
router_prompt = ChatPromptTemplate.from_template(
    "Instruction: You are a system router. Look at the question and output EXACTLY one word: 'SQL' or 'RAG'.\n"
    "- Output 'SQL' if the user asks for data, counts, prices, or orders.\n"
    "- Output 'RAG' if the user asks for policies, shipping, returns, or information.\n"
    "- If it's a greeting or irrelevant, output 'NONE'.\n\n"
    "Question: {question}\n"
    "Decision:"
)
router_chain = router_prompt | llm | StrOutputParser()



# --- 5. RAG EXECUTION ---
rag_prompt = ChatPromptTemplate.from_template(
    "Answer the question based ONLY on the following context. If not found, say 'Information not available'.\n"
    "Context: {context}\nQuestion: {question}"
)
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)



# --- 6. SQL EXECUTION ---
sql_gen_prompt = ChatPromptTemplate.from_template(
    "You are a MySQL expert. Use the following schema to write a query.\n"
    "Schema: {schema}\n"
    "Question: {question}\n"
    "Constraint: Use ONLY the column names present in the schema. If you see 'price' use that, if 'amount' use that.\n"
    "Return ONLY the SQL code."
)




def handle_sql(question):
    # Step A: Generate SQL
    sql_query = (sql_gen_prompt | llm | StrOutputParser()).invoke({
        "schema": db.get_table_info(),
        "question": question
    }).strip().replace("```sql", "").replace("```", "")

    # Step B: Apply Guardrails
    if not validate_sql(sql_query):
        return "ERROR: Unsafe database operation blocked."

    # Step C: Execute & Explain
    try:
        data_result = db.run(sql_query)
        explain_prompt = ChatPromptTemplate.from_template(
            "The database returned: {result}. Explain this naturally for the question: {question}"
        )
        return (explain_prompt | llm | StrOutputParser()).invoke({
            "result": data_result, 
            "question": question
        })
    except Exception as e:
        return f"System Error: {str(e)}"

# --- 7. MAIN CONTROLLER ---
def main():
    print("--- AI Hybrid Assistant Ready ---")
    while True:
        user_query = input("\nYour Question (or 'exit'): ")
        if user_query.lower() == 'exit': break
        
        # Router decision - stripping whitespace and converting to upper
        raw_decision = router_chain.invoke({"question": user_query}).strip().upper()
        
        
        # Better Regex to find the keywords anywhere in the output
        if re.search(r'SQL', raw_decision):
            path = "SQL"
            response = handle_sql(user_query)
        elif re.search(r'RAG', raw_decision):
            path = "RAG"
            response = rag_chain.invoke(user_query)
        else:
            path = "NONE"
            response = "I am sorry, but I can only answer questions based on my provided documents (RAG) or database (SQL). I don't have information on this specific query."
            
        print(f"[Log]: Path selected -> {path}")
        print(f"Response: {response}")
if __name__ == "__main__":
    main()