from app.services.llm_service import (
    run_router_llm,
    run_sql_query,
    run_vector_query,
    run_qa_chain
)

def handle_llm_query(user_query: str):
    """
    Controller handles query routing and execution.
    """
    # Step 1: LLM decides routing
    routing_decision = run_router_llm(user_query)
    action = routing_decision.get("action")
    routed_query = routing_decision.get("query")

    results = None

    # Step 2: Execute based on routing
    if action == "SQL":
        results = run_sql_query(routed_query)
    elif action == "VectorDB":
        results = run_vector_query(routed_query)
    elif action == "Hybrid":
        sql_result = run_sql_query(routed_query.get("sql"))
        vector_result = run_vector_query(routed_query.get("vector"))
        results = {"sql": sql_result, "vector": vector_result}
    else:
        raise ValueError(f"Unknown action {action}")

    # Step 3: QA / summarization
    final_answer = run_qa_chain(user_query, results)

    return {
        "router_decision": routing_decision,
        "raw_results": results,
        "final_answer": final_answer
    }
