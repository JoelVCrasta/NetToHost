import os

from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get("REDIS_HOST")
port_str = os.environ.get("REDIS_PORT")
if not host or not port_str:
    raise ValueError("Missing Redis environment variables.")
port = int(port_str)

redis = Redis(host=host, port=port, decode_responses=True)
