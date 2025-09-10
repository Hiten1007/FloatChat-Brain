import requests
import json
def run_sql_query_via_api(query_data: dict):
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
        # Send a POST request with the query data as JSON
        response = requests.post(api_url, json=query_data)
        
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