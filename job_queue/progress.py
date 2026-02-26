import json
from typing import Generator

import redis


_redis_client = None


def _get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    return _redis_client


def publish_progress(scan_id: str, stage: str, percent: int, message: str):
    client = _get_redis_client()
    channel = f"scan_progress:{scan_id}"
    payload = json.dumps({"stage": stage, "percent": percent, "message": message})
    client.publish(channel, payload)


def subscribe_progress(scan_id: str) -> Generator[dict, None, None]:
    client = _get_redis_client()
    pubsub = client.pubsub()
    channel = f"scan_progress:{scan_id}"
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message["type"] == "message":
            yield json.loads(message["data"])
