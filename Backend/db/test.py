from database import users
from fastapi.responses import JSONResponse

if users.find_one({"userID" : "faizankakar@gmail.com"}):
    
    result =  JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "User already exists"})
    
print(result)