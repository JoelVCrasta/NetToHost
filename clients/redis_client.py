import os

from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get("REDIS_HOST")
port = int(os.environ.get("REDIS_PORT"))
if not host or not port:
    raise ValueError("Missing Redis environment variables.")

redis = Redis(host=host, port=port, decode_responses=True)
