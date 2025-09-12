import requests
import json
from app.schemas.sql_schema import QueryInput
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def run_sql_query_via_api(query_data: QueryInput) -> dict:
    """
    Connects to the local TypeScript server to execute a SQL query.

    Args:
        query_data (dict): A dictionary containing the data for the SQL query.
                         Example: {"operation": "find", "limit": 10}

    Returns:
        dict: The JSON response from the server, or an error message.
    """
    api_url = "http://localhost:3000/api/getsqldata"
     
    try:
        payload_dict = query_data.model_dump(mode='json', exclude_none=True)
        
        logger.info(f"Sending request to TypeScript server URL: {api_url}")
        logger.info(f"Request payload (dict): {json.dumps(payload_dict, indent=2)}") # Log for debugging
        # Send a POST request with the query data as JSON
        response = requests.post(api_url, json=payload_dict)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        # Parse and return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # Handle network or HTTP errors
        return {"error": f"Error connecting to the server: {e}"}
    except json.JSONDecodeError:
        # Handle cases where the response is not valid JSON
        return {"error": "Invalid JSON response from the server."}