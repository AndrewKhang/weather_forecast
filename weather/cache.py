import redis
import os
from dotenv import load_dotenv

load_dotenv()

connection = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6380")),
    decode_responses=True
    )
