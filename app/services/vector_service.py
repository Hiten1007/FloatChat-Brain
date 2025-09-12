import os
from flask import Flask
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from app.schemas.vector_schema import VectorQueryInput
from app.brain.llm import llm as qa_llm

# --- Placeholders for our globally accessible objects ---
# We create them here but will initialize them inside the app factory.
model = None
pinecone_index = None

def init_vector_service(app: Flask):
    """
    Initializes the SentenceTransformer model and the Pinecone index.
    This should be called once from the app factory (`create_app`).
    """
    global model, pinecone_index

    with app.app_context():
        # --- 1. Load the Sentence Transformer Model ---
        # This is a heavy object, so we only want to load it once.
        app.logger.info("Loading SentenceTransformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        app.logger.info("Model loaded successfully.")

        # --- 2. Initialize the Pinecone Index ---
        try:
            app.logger.info("Initializing Pinecone connection...")
            api_key = app.config.get("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment variables.")

            pc = Pinecone(api_key=api_key)
            index_name = "argo-floats-india"
            pinecone_index = pc.Index(index_name)
            
            # Confirm connection by describing the index
            stats = pinecone_index.describe_index_stats()
            app.logger.info(f"Successfully connected to Pinecone index '{index_name}'. Stats: {stats}")

        except Exception as e:
            app.logger.error(f"FATAL: Error initializing Pinecone: {e}")
            # Exit if we can't connect, as the app is useless without it.
            exit(1)


# In your `run_vector_query`'s module
# ... (existing imports and mock setups) ...

def run_vector_query(input_data: VectorQueryInput) -> dict:
    """
    Performs a vector search on the Pinecone index and then uses LangChain QA
    to synthesize an answer from the retrieved documents, using the original user query.
    """
    global model, pinecone_index, qa_llm

    if model is None or pinecone_index is None or qa_llm is None:
        raise Exception("Vector service components (embedding model, Pinecone index, or QA LLM) are not initialized.")

    try:
        search_query = input_data.query # Use this for embedding and Pinecone search
        top_k = input_data.top_k or 5

        # 1. Embed the incoming search query text
        query_embedding = model.encode(search_query).tolist()

        # 2. Query the Pinecone index
        results = pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        retrieved_documents_content = [
            match['metadata']['text']
            for match in results['matches']
            if 'text' in match['metadata']
        ]
        
        if not retrieved_documents_content:
            return {"answer": "No relevant information found in the knowledge base."}

        # 3. Format retrieved content into LangChain Document objects
        from langchain_core.documents import Document
        langchain_docs = [
            Document(page_content=doc_content, metadata={"source": f"pinecone_doc_{i}"})
            for i, doc_content in enumerate(retrieved_documents_content)
        ]

        # 4. Initialize and run a LangChain QA chain
        from langchain.chains.question_answering import load_qa_chain
        
        qa_chain = load_qa_chain(qa_llm, chain_type="stuff")

        # Use the original_user_question for the QA chain
        qa_response = qa_chain.invoke({"input_documents": langchain_docs, "question": search_query})
        
        final_answer_from_qa = qa_response.get("output_text", "Could not generate an answer from the retrieved documents.")
        
        return {"answer": final_answer_from_qa}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"An error occurred during vector search or QA: {str(e)}"}