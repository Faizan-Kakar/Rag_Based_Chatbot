# from passlib.context import CryptContext
import jwt, datetime
import os 
from dotenv import load_dotenv
load_dotenv()
# # Create a password context with bcrypt algorithm
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY = "faizankhankakar1234"

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# # Verify password
# def verify_password(password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(password, hashed_password)

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = os.getenv("secretKey")

def hash_password(password: str) -> str:
    # bcrypt only supports up to 72 bytes
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    # bcrypt only supports up to 72 bytes
    password = password[:72]
    return pwd_context.verify(password, hashed_password)


def create_jwt(email: str):
    payload = {
        "sub": email,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")