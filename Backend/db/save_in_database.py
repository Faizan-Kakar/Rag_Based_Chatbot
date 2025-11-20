from db.database import sessions , messages
from ai.data_models import chat_data
import datetime
from langgraph.checkpoint.memory import InMemorySaver

async def save_sessions_in_mongo(userID: str, session_id: str, session_name: str, context_memory : InMemorySaver,  created_at:datetime):
    
    try:  
        sessions.insert_one({"userID" : userID,  "session_id" : session_id,  "session_name" : session_name, "context_memory" : context_memory, "created_at" : created_at})
        return "Session data successfully added"
    except Exception as e:
        return f"Error : {e}"

async def save_chats_in_mongo(data : chat_data):
    
    try:  
        messages.insert_one({"userID" : data.userID,  "session_id" : data.session_id,  "role" : data.role, "content" : data.content, "created_at" : data.timestamp})
        return "Chats data successfully added"
    except Exception as e:
        return f"Error : {e}"

