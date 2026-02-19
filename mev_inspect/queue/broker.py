import os

from dramatiq.brokers.redis import RedisBroker


def connect_broker():
    return RedisBroker(
        host=os.environ.get("REDIS_HOST", "redis-master"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        password=os.environ["REDIS_PASSWORD"],
    )
