import json
import traceback
# Resolve ChatOllama deprecation warning:
# First, ensure you have 'langchain-ollama' installed:
# pip install -U langchain-ollama
from langchain_ollama import ChatOllama # Use the updated import

from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import StructuredTool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

from app.services.sqldb_service import run_sql_query_via_api
from app.services.vector_service import run_vector_query
from app.brain.agent_prompts import AGENT_SYSTEM_PROMPT
from app.brain.llm import llm  # Import the LLM instance from the dedicated module
from app.schemas.sql_schema import QueryInput
from app.schemas.vector_schema import VectorQueryInput
from pydantic import ValidationError, BaseModel

class ToolInput(BaseModel):
    json_input_string: str

# --- Wrapper functions to ensure tool output is always a string ---
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sql_tool_wrapper(json_input_string: str) -> str:
    """
    Calls the SQL service. This wrapper explicitly handles the JSON string input
    from the agent, parses it, and then validates it with Pydantic.
    """
    logger.info(f"SQL Tool Wrapper received raw input string: '{json_input_string}'")
    try:
        # Step 1: Clean the input string thoroughly
        clean_json_str = json_input_string.strip()
        
        # Remove markdown code block fences if present
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[len("```json"):]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-len("```")]
        clean_json_str = clean_json_str.strip() # Re-strip after removing fences

        # Also handle "json\n" prefix
        if clean_json_str.startswith("json\n"):
            clean_json_str = clean_json_str[len("json\n"):]
            clean_json_str = clean_json_str.strip()

        logger.info(f"Cleaned JSON string for parsing: '{clean_json_str}'")

        # Step 2: Parse the cleaned string into a Python dictionary
        data_dict = json.loads(clean_json_str)
        logger.info(f"Successfully parsed JSON to dict: {data_dict}")

        # Step 3: Validate the dictionary against the Pydantic QueryInput model
        validated_input = QueryInput(**data_dict)
        logger.info(f"Successfully validated input with Pydantic: {validated_input.model_dump_json()}")
        
        # Step 4: Call the API with the validated Pydantic model
        result = run_sql_query_via_api(validated_input)

        logger.info(f"DEBUG: Result from run_sql_query_via_api before final dumps: {result}")
        logger.info(f"DEBUG: Type of result before final dumps: {type(result)}")
        if not isinstance(result, (dict, list)): # Check if it's not a basic serializable type
             logger.error(f"DEBUG: Problematic result type encountered! Object: {result}")
             raise TypeError(f"Cannot serialize unexpected type {type(result).__name__} from API response.")

        return json.dumps(result)

    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Error: Invalid JSON input or Pydantic validation failed for tool. Details: {e}. Raw input received: '{json_input_string}'")
        return f"Error: Invalid JSON input or Pydantic validation failed for tool. Details: {e}. Input received: '{json_input_string}'"
    except Exception as e:
        logger.error(f"An unexpected error occurred in the SQL tool wrapper. Details: {e}. Raw input received: '{json_input_string}'")
        return f"An unexpected error occurred in the SQL tool. Details: {e}. Input received: '{json_input_string}'"

# In your `vector_tool_wrapper`'s module

def vector_tool_wrapper(json_input_string: str) -> str:
    """
    Calls the Vector service. It now safely handles input that is
    either a JSON string or a dictionary, and ensures the original user query
    is passed for the QA step.
    """
    logger.info(f"Vector Tool Wrapper received raw input string: '{json_input_string}'")
    try:
        clean_json_str = json_input_string.strip()
        
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[len("```json"):]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-len("```")]
        clean_json_str = clean_json_str.strip()

        if clean_json_str.startswith("json\n"):
            clean_json_str = clean_json_str[len("json\n"):]
            clean_json_str = clean_json_str.strip()

        logger.info(f"Cleaned JSON string for parsing: '{clean_json_str}'")

        data_dict = json.loads(clean_json_str)
        logger.info(f"Successfully parsed JSON to dict: {data_dict}")

        validated_input = VectorQueryInput(**data_dict)
        logger.info(f"Successfully validated input with Pydantic: {validated_input.model_dump_json()}")
        
        # Step 4: Call the API with the validated Pydantic model
        result = run_vector_query(validated_input)

        logger.info(f"DEBUG: Result from run_vector_query before final dumps: {result}")
        logger.info(f"DEBUG: Type of result before final dumps: {type(result)}")
        if not isinstance(result, (dict, list)):
             logger.error(f"DEBUG: Problematic result type encountered! Object: {result}")
             raise TypeError(f"Cannot serialize unexpected type {type(result).__name__} from API response.")

        return json.dumps(result)

    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Error: Invalid JSON input or Pydantic validation failed for tool. Details: {e}. Raw input received: '{json_input_string}'")
        return f"Error: Invalid JSON input or Pydantic validation failed for tool. Details: {e}. Input received: '{json_input_string}'"
    except Exception as e:
        logger.error(f"An unexpected error occurred in the Vector tool wrapper. Details: {e}. Raw input received: '{json_input_string}'")
        return f"An unexpected error occurred in the Vector tool. Details: {e}. Input received: '{json_input_string}'"

# --- Tool Definitions (No changes needed) ---

# In your agent creation file

sql_tool = StructuredTool.from_function(
    func=sql_tool_wrapper, # Use the new robust wrapper
    name="SQL_Database_Tool",
    description="""
        Use this tool to query the structured ARGO float database for quantitative data.
        The input MUST be a JSON object (as a string) that strictly conforms to the tool's schema.

        --- EXAMPLES ---
        
        USER QUERY: "Find 5 records for platform 2900765"
        ACTION INPUT: {"operation": "find", "filters": [{"field": "platform_code", "op": "=", "value": 2900765}], "limit": 5}
        
        # THIS EXAMPLE IS NOW UPDATED TO MATCH THE TYPESCRIPT API
        USER QUERY: "Which float had the highest temperature ever?"
        ACTION INPUT: {"operation": "aggregate", "aggregates": [{"field": "temp_adjusted", "fn": "max"}], "orderBy": [{"field": "temp_adjusted", "direction": "desc"}], "limit": 1}

        USER QUERY: "What is the average salinity?"
        ACTION INPUT: {"operation": "aggregate", "aggregates": [{"field": "psal_adjusted", "fn": "avg"}]}
        
        --- END EXAMPLES ---
    """,
    # This is the key change for args_schema with a single string input
    # We define a generic input field, which will capture the entire
    # JSON string provided by the agent. The wrapper then processes it.
    args_schema=ToolInput
)

vector_tool = StructuredTool.from_function(
    func=vector_tool_wrapper,
    name="Vector_Database_Tool",
   description="""
        Use this tool for semantic search over ARGO float documentation, definitions, and explanations.
        This is for "how-to" or "what is" type questions.
        The input MUST be a JSON object with a "query" key.

        --- EXAMPLES ---
        
        USER QUERY: "How does an ARGO float work?"
        ACTION INPUT: {"query": "How do ARGO floats function?"}
        
        USER QUERY: "What is salinity?"
        ACTION INPUT: {"query": "Definition of salinity in oceanography", "top_k": 3}

        USER QUERY: "Tell me about the data transmission process."
        ACTION INPUT: {"query": "ARGO float data transmission process"}

        --- END EXAMPLES ---
    """,
    args_schema=ToolInput
)

# --- Agent Initialization (Corrected Prompt Construction) ---

# --- Agent Initialization (Corrected Prompt Construction) ---
def get_mcp_agent():
    """Initializes and returns the main MCP agent executor."""
    
    tools = [sql_tool, vector_tool]

    # 1. Pull the base prompt from the LangChain Hub
    base_prompt = hub.pull("hwchase17/react-chat")

    # 2. Modify the template string directly
    new_template_string = AGENT_SYSTEM_PROMPT + "\n\n" + base_prompt.template

    # 3. Create a new PromptTemplate object from the combined string.
    #    The from_template() method automatically determines the input variables.
    prompt = PromptTemplate.from_template(
        template=new_template_string
        # REMOVED: input_variables=base_prompt.input_variables
    )

    # Agent creation logic remains the same
    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    return agent_executor


# --- GLOBAL AGENT INITIALIZATION (This is correct) ---
# The agent is created ONCE when the application starts.
print("Initializing MCP Agent...")
mcp_agent_executor = get_mcp_agent()
print("MCP Agent Initialized.")

import json
import traceback
import re # Import regex module

# Assuming mcp_agent_executor and logger are defined elsewhere

def run_mcp_agent_flow(user_query: str, chat_history: list = None):
    """
    Controller that runs the full MCP agent flow with error handling.
    Accepts an optional chat_history list to maintain conversation context.
    Seamlessly extracts the final JSON answer from diverse LLM output formats.
    """
    try:
        if chat_history is None:
            chat_history = []
        
        agent_response = mcp_agent_executor.invoke({
            "input": user_query,
            "chat_history": chat_history,
        })
        
        final_output_string = agent_response.get('output', '')

        print(f"DEBUG: Raw final output string from agent:\n{final_output_string}\n") # Using \n for better readability in debug output
        
        parsed_structured_output = None
        
        # --- ROBUST JSON EXTRACTION STRATEGY (Attempt 5 - Focus on finding first valid JSON) ---
        json_only_string = ""
        
        # Strategy 1: Look for "Final Answer:" marker and extract content after it
        final_answer_marker = "Final Answer:"
        parts = final_output_string.split(final_answer_marker, 1)

        if len(parts) > 1:
            potential_json_string = parts[1].strip()
            print(f"DEBUG: Found 'Final Answer:' marker. Potential JSON string: \n{potential_json_string}\n")
        else:
            # Strategy 2: If marker not found, assume the entire output (or a significant part) might be the JSON.
            # This handles cases where the LLM directly outputs JSON.
            print("Warning: 'Final Answer:' marker not found in output. Searching for first JSON object.")
            potential_json_string = final_output_string.strip()

        # Aggressive cleanup of potential markdown fences and other non-JSON prefixes/suffixes
        # This is crucial for seamless parsing.
        potential_json_string = potential_json_string.strip()
        if potential_json_string.startswith("```json"):
            potential_json_string = potential_json_string[len("```json"):].strip()
        if potential_json_string.endswith("```"):
            potential_json_string = potential_json_string[:-len("```")].strip()
        if potential_json_string.startswith("json\n"):
            potential_json_string = potential_json_string[len("json\n"):]
            potential_json_string = potential_json_string.strip()
        # Remove any leading/trailing thought processes or other text that sometimes stick around
        # We want the JSON to start with '{' and end with '}'
        
        # Use regex to find the first complete JSON object
        # This regex looks for an opening brace '{' followed by any characters (non-greedy)
        # and then a closing brace '}'. It's still not perfect for nested structures but
        # is a good first pass for isolated objects.
        json_match = re.search(r'\{.*\}', potential_json_string, re.DOTALL)
        
        if json_match:
            json_only_string = json_match.group(0)
            print(f"DEBUG: Extracted JSON string using regex: \n{json_only_string}\n")
        else:
            print("Warning: Regex failed to find a complete JSON object. Falling back to the entire cleaned string.")
            json_only_string = potential_json_string # Use cleaned string as fallback

        # Now, attempt to parse the extracted string
        try:
            parsed_structured_output = json.loads(json_only_string)
            print(f"DEBUG: Successfully parsed JSON: \n{json.dumps(parsed_structured_output, indent=2)}\n")
            
            # Additional validation for 'answer_blocks'
            if "answer_blocks" not in parsed_structured_output:
                raise ValueError("LLM output JSON is missing the top-level 'answer_blocks' key.")
            
        except json.JSONDecodeError as e:
            print(f"Warning: JSON parsing failed after extraction. Error: {e}. Falling back to text output.")
            parsed_structured_output = {
                "answer_blocks": [
                    {"type": "text", "content": {"message": final_output_string}}
                ]
            }
        except ValueError as e: # For the "answer_blocks" missing error
            print(f"Warning: Validation failed for 'answer_blocks'. Error: {e}. Falling back to text output.")
            parsed_structured_output = {
                "answer_blocks": [
                    {"type": "text", "content": {"message": final_output_string}}
                ]
            }
        except Exception as ex:
            print(f"Error during JSON string extraction or initial parsing (Final Attempt): {ex}. Falling back to text output.")
            parsed_structured_output = {
                "answer_blocks": [
                    {"type": "text", "content": {"message": final_output_string}}
                ]
            }
        # --- ROBUST JSON EXTRACTION STRATEGY END ---
        
        # Ensure the final_answer content is always the "answer_blocks"
        return {
            "agent_thought_process": agent_response.get('intermediate_steps', []),
            "final_answer": {
                "status": "success",
                "message": "Response processed successfully.",
                "answer_blocks": parsed_structured_output["answer_blocks"] # Directly pass the answer_blocks
            }
        }
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"FATAL: An exception occurred in the agent execution flow:\n{error_trace}")
        return {
            "agent_thought_process": [],
            "final_answer": {
                "status": "error",
                "message": "An unexpected error occurred while processing your request.",
                "answer_blocks": [ # Changed 'content' to 'answer_blocks' for consistency
                    {
                        "type": "text",
                        "content": {
                            "message": f"Agent execution failed. Please check the logs. Error: {str(e)}"
                        }
                    }
                ]
            }
        }
