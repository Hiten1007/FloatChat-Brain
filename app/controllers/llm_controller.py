from app.services.sqldb_service import run_sql_query_via_api # The new API function
from app.services.vector_service import run_vector_query
from app.services.visualization_service import generate_plot, generate_map
from app.prompts.agent_prompts import AGENT_SYSTEM_PROMPT # The new system prompt

import json

from langchain_community.chat_models import ChatOllama
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType, create_react_agent,AgentExecutor
from langchain.prompts import ChatPromptTemplate
# --- Tool Definitions (Now using the API client) ---

sql_tool = StructuredTool.from_function(
    func=run_sql_query_via_api, # Use the new API-calling function
    name="SQL_Database_Tool",
    description="""
        Use this tool to query the structured ARGO float database for quantitative data.
        Input must be a valid SQL query string. The query will be executed on the 'floats' table.
    """
)

vector_tool = StructuredTool.from_function(
    func=run_vector_query,
    name="Vector_Database_Tool",
    description="""
        Use this tool for semantic search over ARGO float documentation, metadata, and explanations.
    """
)

# ... (plot_tool and map_tool definitions remain the same) ...

# --- Agent Initialization ---

def get_mcp_agent():
    """Initializes and returns the main MCP agent executor with context."""
    llm = ChatOllama(model="llama3:8b", temperature=0)
    tools = [sql_tool, vector_tool, plot_tool, map_tool]
    
    # Combine the system prompt with placeholders for the user query and agent scratchpad
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT_SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True # More robust error handling
    )
    return agent_executor


# --- Controller (Now sends the system prompt context) ---

def run_mcp_agent_flow(user_query: str):
    """Controller that runs the full MCP agent flow and expects structured JSON output."""
    agent_executor = get_mcp_agent()

    agent_response = agent_executor.invoke({
        "input": user_query
    })

    final_output_string = agent_response.get('output', '')
    parsed_structured_output = {}

    try:
        # Attempt to parse the LLM's final output as JSON
        parsed_structured_output = json.loads(final_output_string)
        
        # Validate the expected structure
        if "answer_blocks" not in parsed_structured_output or not isinstance(parsed_structured_output["answer_blocks"], list):
            # Fallback if the LLM didn't adhere to the structure
            print("Warning: LLM did not return the expected 'answer_blocks' structure. Falling back to text.")
            parsed_structured_output = {
                "answer_blocks": [
                    {"type": "text", "content": {"message": final_output_string}}
                ]
            }

    except json.JSONDecodeError:
        # If the LLM didn't produce valid JSON, treat the whole thing as text
        print("Warning: LLM did not return valid JSON. Treating output as plain text.")
        parsed_structured_output = {
            "answer_blocks": [
                {"type": "text", "content": {"message": final_output_string}}
            ]
        }
    
    # The final_structured_output for the frontend is now directly what the LLM provided (or a fallback)
    final_structured_output = {
        "status": "success",
        "message": "Response processed successfully.",
        "content": parsed_structured_output["answer_blocks"] # Extract the list of blocks
    }
    
    return {
        "agent_thought_process": agent_response.get('intermediate_steps', []),
        "final_answer": final_structured_output
    }
