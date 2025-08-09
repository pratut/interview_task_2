import redis
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_redis import RedisChatMessageHistory

# Initialize LLM
model = ChatOllama(model="llama3.2:1b")

# Prompt template with conversation history
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a professional personal assistant for Prastut Bhattarai. "
         "Your main duties are to:\n"
         "1. Help clients contact Prastut.\n"
         "2. Book appointments by collecting the following details step-by-step: "
         "name, email, phone number, preferred date, time, and any message.\n"
         "3. Keep your responses short, polite, and focused on helping the user.\n"
         "4. If the user just wants contact info, provide the official phone number: +977-9861834238 "
         "and mention they can also book appointments through you.\n"
         "5. If the user says 'bye', respond politely and end the session.\n"
         "Always remember: you are acting as Prastut's assistant, not as Prastut himself."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)


# Simple chain
chain = prompt_template | model

# Redis connection
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Function to get Redis chat history
def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id=session_id, redis_client=redis_client)

# Chain with history tracking
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_redis_history,
    input_messages_key="question",
    history_messages_key="history"
)
