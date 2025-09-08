import json
from mcp.client import MCPClient  # your MCP implementation
from sql_client import run_sql_query  # your SQL MCP wrapper
from pinecone_client import run_vector_query  # your Pinecone MCP wrapper

# Initialize MCP-wrapped LLM once (hot)
llm_mcp = MCPClient(model_name="Llama3.2-3B-Instruct:int4-qlora-eo8")

# Router helper
def call_llm_router(user_query: str, system_prompt: str) -> dict:
    """
    Send query to LLM via MCP, expects strict JSON {action, query}.
    """
    try:
        response = llm_mcp.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0,
            max_tokens=500,
        )

        content = response.get("content", "")
        if isinstance(content, list):
            content = content[0].get("text", "")

        # Parse JSON safely
        router_decision = json.loads(content)
        return router_decision

    except json.JSONDecodeError:
        return {"action": "Error", "query": "Invalid JSON from model"}
    except Exception as e:
        return {"action": "Error", "query": str(e)}


# SQL helper
def query_postgres_mcp(sql_query: str):
    """
    Execute SQL query via MCP (Postgres wrapper).
    Returns results as list of dicts.
    """
    try:
        result = run_sql_query(sql_query)
        return result
    except Exception as e:
        return {"error": str(e)}


# Vector DB helper
def query_pinecone_mcp(vector_query: str):
    """
    Query Pinecone vector DB via MCP.
    Returns top-k semantic results.
    """
    try:
        result = run_vector_query(vector_query)
        return result
    except Exception as e:
        return {"error": str(e)}


# LangChain QA helper
def run_qa_chain(user_query: str, results: dict):
    """
    Wrap numeric/vector results in a QA chain for final answer.
    Can use LangChain or your own summarizer.
    """
    try:
        from langchain.chains import QAWithSourcesChain
        # pseudo-code
        qa_chain = QAWithSourcesChain.from_llm(llm_mcp, chain_type="stuff")
        answer = qa_chain.run(input_documents=results, question=user_query)
        return answer
    except Exception as e:
        return str(e)
