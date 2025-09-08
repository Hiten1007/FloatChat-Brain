from flask import Blueprint, request, jsonify
from app.controllers.llm_controller import handle_llm_query

bp = Blueprint("llm_routes", __name__)

@bp.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_query = data.get("query")
    if not user_query:
        return jsonify({"error": "Missing 'query'"}), 400

    try:
        response = handle_llm_query(user_query)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
