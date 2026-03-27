import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")

REDIS_PORT = 6379
RABBIT_PORT = 5672
