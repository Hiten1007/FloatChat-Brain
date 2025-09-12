from flask import Blueprint, request, jsonify
from app.services.sqldb_service import run_sql_query_via_api
from app.services.vector_service import run_vector_query
from app.schemas.vector_schema import VectorQueryInput

tools_bp = Blueprint("tools_routes", __name__)

@tools_bp.route("/sqldata", methods=["POST"])
def querysql():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing 'query'"}), 400

    try:
        response = run_sql_query_via_api(data)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@tools_bp.route("/vectordata", methods=["POST"])
def queryvector():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing 'query'"}), 400

    try:
        query_input = VectorQueryInput(**data)

        response = run_vector_query(query_input)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
