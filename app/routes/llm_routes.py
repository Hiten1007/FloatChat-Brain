from flask import Blueprint, request, jsonify
from app.controllers.llm_controller import run_mcp_agent_flow

llm_bp = Blueprint("llm_routes", __name__)

@llm_bp.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_query = data.get("query")
    if not user_query:
        return jsonify({"error": "Missing 'query'"}), 400

    try:
        response = run_mcp_agent_flow(user_query)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
