
from langchain_community.chat_models import ChatOllama

print("Initializing the LLM instance...")
llm = ChatOllama(model="llama3:8b", temperature=0)
print("LLM instance created.")