from fastapi import FastAPI, File , UploadFile, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid 
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from db.save_in_database import save_sessions_in_mongo, save_chats_in_mongo
from ai.utills.get_session_names import get_session_name
from db.get_from_database import get_user_sessions, get_session_chats
from ai.upload_Doc import upload_Doc
# from ai.rag_pipeline1 import rag_pipeline
from ai.rag_pipeline import rag_pipeline
from auth.routes import auth_router
from ai.data_models import chat_data
from dotenv import load_dotenv
from typing import Dict
import json
load_dotenv()  # load variables from .env file

#  run the this project by running this command : fastapi dev app.py
 
app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.include_router(auth_router, prefix="/auth")
# Allow specific origins (recommended)


class AskQuerryRequest(BaseModel):
    querry : str
    session_id : str
    userID : str
    

# print("🤖 Gemini Chatbot (type 'exit' to quit)\n")
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("Chatbot: Goodbye! 👋")
#         break

#     result = agent_executor(user_input)
#     print("Chatbot:", result)

@app.post("/upload_doc")
async def upload_doc_endpoint(file: UploadFile = File(...)):
    """
    Upload a document and store in Pinecone.
    """
 
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are supported"}

    # Pass file.file (a file-like object) to your existing function
    result = upload_Doc(file.file)
    
    return {"message": result}

active_connections: Dict[str, WebSocket] = {}



@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()  # 🔹 Handshake completed
    active_connections[user_id] = websocket
    print(f"User {user_id} connected.")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event = message["event"]
            if event == "ask":
                payload = message["payload"]
                # print("Payload received:" + payload)
                print(f"paloadQurry : {payload['querry']}")
                response = await ask_question(AskQuerryRequest(
                    querry=payload['querry'],
                    session_id=payload['session_id'],
                    userID=payload['userID']
                ))
                await websocket.send_json({
                    "event": "response",
                    "payload": response
                })
            elif event == "ping":
                await websocket.send_json({"event": "ping"})
                

    except WebSocketDisconnect:
        print(f"User {user_id} disconnected.")
        del active_connections[user_id]

async def ask_question(request: AskQuerryRequest):
    """
    Ask a question using the RAG pipeline.
    """
    print("enter ask_question")
    # If new session is created
    session_name = ""
    if request.session_id == "":   
        request.session_id = str(uuid.uuid4())
        session_name =await  get_session_name(request.querry)
        # memory = InMemorySaver()  # Create a new memory instance for the new session
        # memory.load_thread(request.session_id, [])
        db_response=await save_sessions_in_mongo(
                userID=request.userID, 
                session_id=request.session_id,
                session_name= session_name,
                context_memory="",
                created_at = datetime.now(timezone.utc)
                )
        print(db_response)
        
    # Save user chat to Database
    db_response= await save_chats_in_mongo(
        chat_data(
            userID=request.userID, 
            session_id=request.session_id,
            role="user",
            content=request.querry,
            timestamp=str(datetime.now(timezone.utc))
            ))      
    
    # Rag response
    response = await rag_pipeline(request.userID, request.session_id, request.querry )
    
    # # Save bot response  to Database
    db_response= await save_chats_in_mongo(
        chat_data(
            userID=request.userID, 
            session_id=request.session_id,
            role="bot",
            content=response['answer'],
            timestamp=str(datetime.now(timezone.utc))
            ))      
           
    print(db_response)

    if response['answer'] is None:
        return {
                "success": False,
                "message": "No response from the model",
                "session_id": request.session_id,
                "session_names": session_name
                }
        
    return {
            "success": True,
            "message": "Answer generated successfully",
            "session_id": request.session_id,
            "answer": response["answer"],
            "session_names": session_name
            }
        
   

# returns list of session
@app.get("/get_sessions")
async def get_sessions(userID: str):
    """
    Get all sessions for a user.
    """
    
    
    sessions = await get_user_sessions(userID)
    
    # Convert datetime fields to ISO strings
    for s in sessions:
        if "created_at" in s and isinstance(s["created_at"], (datetime,)):
            s["created_at"] = s["created_at"].isoformat()
    
    
    if isinstance(sessions, str) and sessions.startswith("Error"):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": sessions
            }
        )
    return JSONResponse(
        
        status_code=200,
        content={
            "success": True,
            "message": "Sessions fetched successfully",
            "sessions": sessions
        }
    )    

# return list of chats in a session
@app.get("/get_session_chats")
async def get_chats(session_id: str):
    
    # store_previous_content
    # load_current_context
    
    chats = await get_session_chats(session_id)
    # print(f"Role : {chats[0]["role"]} , Content : {chats[0]["content"]} ")
    # print(f"Role : {chats[1].role} , Content : {chats[1].content} ")
    return JSONResponse(content={
        "success": True,
        "chats": jsonable_encoder(chats)
    })
    
    
@app.get("/")
async def homepage():
    return {"message": "Welcome to the FastAPI application!"}   


