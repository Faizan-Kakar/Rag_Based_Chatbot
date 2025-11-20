from pydantic import BaseModel

class chat_data(BaseModel):
    userID: str
    session_id: str
    role: str
    content: str
    timestamp: str


