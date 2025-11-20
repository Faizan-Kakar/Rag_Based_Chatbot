from redis import Redis
import urllib.parse
import os 
from dotenv import load_dotenv
load_dotenv()


# Example cloud Redis URL
redis_url = os.getenv("redis_url")

# Parse URL
parsed_url = urllib.parse.urlparse(redis_url)

redis_client = Redis(
    host=parsed_url.hostname,
    port=parsed_url.port,
    password=parsed_url.password,
    ssl=parsed_url.scheme == "rediss",  # use SSL if URL is rediss
    decode_responses=True
)


