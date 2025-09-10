from flask import Blueprint, request, jsonify
from app.services.sqldb_service import run_sql_query_via_api
from app.services.vector_service import run_vector_query

tools_bp = Blueprint("tools_routes", __name__)

@tools_bp.route("/sqldata", methods=["POST"])
def query():
    data = request.get_json()
    input = data.get("input")
    if not input:
        return jsonify({"error": "Missing 'query'"}), 400

    try:
        response = run_sql_query_via_api(input)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@tools_bp.route("/vectordata", methods=["POST"])
def query():
    data = request.get_json()
    input = data.get("input")
    if not input:
        return jsonify({"error": "Missing 'query'"}), 400

    try:
        response = run_vector_query(input)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
