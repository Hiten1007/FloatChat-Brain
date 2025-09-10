import os
import dotenv
from flask import Flask, request, jsonify, current_app
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

# Initialize Pinecone
try:
    api_key = current_app.config["PINECONE_API_KEY"]
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables.")
    
    pc = Pinecone(api_key=api_key)
   
    index_name = "argo-floats-india"
    index = pc.Index(index_name)
    print(f"Successfully connected to Pinecone index '{index_name}'.")
    # Optional: print index stats to confirm connection
    print(index.describe_index_stats())

except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    # Exit if we can't connect to Pinecone, as the app is useless without it.
    exit(1)

# --- API ENDPOINT DEFINITION ---
def run_vector_query(input: str):
    """
    Performs a vector search on the Pinecone index.
    Expects a JSON payload with a "query" and an optional "top_k".
    """
    try:
        # Get JSON data from the request
        data = input
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Extract query and top_k from the payload
        query_text = data.get("query")
        top_k = data.get("top_k", 5) # Default to 5 results if not specified

        if not query_text:
            return jsonify({"error": "Missing 'query' in request body"}), 400
            
        if not isinstance(top_k, int) or top_k <= 0:
            return jsonify({"error": "'top_k' must be a positive integer"}), 400

        # 1. Embed the incoming query text locally
        print(f"Embedding query: '{query_text}'")
        query_embedding = model.encode(query_text).tolist()

        # 2. Query Pinecone
        print(f"Querying Pinecone with top_k={top_k}...")
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        print("Pinecone query successful.")

        # 3. Format the response
        formatted_results = []
        for match in results['matches']:
            formatted_results.append({
                "id": match['id'],
                "score": match['score'],
                "metadata": match['metadata']
            })

        return jsonify({"results": formatted_results})

    except Exception as e:
        print(f"An error occurred during search: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

