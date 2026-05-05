import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    RATE_LIMIT = int(os.environ.get("RATE_LIMIT", 10))
    RATE_WINDOW = int(os.environ.get("RATE_WINDOW", 60))
