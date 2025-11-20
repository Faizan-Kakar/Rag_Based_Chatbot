from db.database import sessions , messages


async def get_user_sessions(user_email: str):
    try:
        cursor = sessions.find({"userID": user_email}, {"_id": 0, "session_id": 1, "session_name": 1, "created_at": 1}).sort("created_at", -1)
        sessions_list = list(cursor)  # Adjust length as needed
    except Exception as e:
        return f"Error : {e}"
    
    return sessions_list

async def get_session_chats(session_id: str):
    try:
        chats = list(messages.find(
            {"session_id": session_id}, 
            {"_id": 0}  # exclude _id
        ).sort("created_at", 1) ) # oldest → newest order
    except Exception as e:
        return f"Error : {e}"
    return chats
    # try:
    #     messages = list(messages_collection.find(
    #     {"session_id": session_id}, 
    #     {"_id": 0}  # exclude _id
    # ).sort("created_at", 1))
    # except Exception as e:
    #     return f"Error : {e}"
    
    # return chats_list
   