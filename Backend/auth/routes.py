from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel , EmailStr
from db.database import users
from auth.utils import hash_password , verify_password, create_jwt
from fastapi.middleware.cors import CORSMiddleware

# Data Model for user
class signup_model(BaseModel):
    userID: str
    name : str
    password: str 

    
class login_model(BaseModel):
    userID : str
    password : str
    
auth_router =  APIRouter()  
    
# origins = [
#     "http://127.0.0.1:5500",
#     "http://localhost:5500",
# ]

# auth_router.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # or ["*"] to allow all
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
#     allow_headers=["*"],  # Allow all headers
# )    
    
@auth_router.post("/signUp")
async def signUp(user : signup_model):  
    if users.find_one({"userID" : user.userID}):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "User already exists",
                "userID": user.userID})
    
    hashed = hash_password(user.password)
    print(f"This is users : {users} , This is the type of the user {type(users)}")
    users.insert_one({"userID" : user.userID , "name" : user.name, "password" : hashed})
    return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User signed Up Successfully",
                "userID": user.userID}
        )

@auth_router.post("/login")
async def logIn(user : login_model):
    
    db_user = users.find_one({"userID" : user.userID})
    
    if not db_user or not verify_password(user.password , db_user["password"]):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Invalid Credentials",
                "userID": user.userID}
        )
    
    token =create_jwt(user.userID)
    
    return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User Successfully logedIn",
                "userID": user.userID,
                "token" : token}
        )
    
    
    