"""
OWASP AI Scanner - Progress Updates
Redis PubSub for live scan progress updates
"""

import json
from typing import Dict, Generator, Any, Optional

import redis


# Redis connection for PubSub
REDIS_URL = "redis://localhost:6379"


def get_redis_client() -> redis.Redis:
    """Get a Redis client for PubSub operations."""
    return redis.from_url(REDIS_URL, decode_responses=True)


def publish_progress(
    scan_id: str,
    stage: str,
    percent: int,
    message: str,
) -> int:
    """
    Publish a progress update to the scan's progress channel.
    
    Args:
        scan_id: The scan ID
        stage: Current stage (e.g., "scanning", "analyzing", "complete")
        percent: Progress percentage (0-100)
        message: Human-readable progress message
        
    Returns:
        int: Number of subscribers that received the message
    """
    channel = f"scan_progress:{scan_id}"
    
    progress_data = {
        "scan_id": scan_id,
        "stage": stage,
        "percent": percent,
        "message": message,
    }
    
    client = get_redis_client()
    result = client.publish(channel, json.dumps(progress_data))
    return result


def subscribe_progress(scan_id: str) -> Generator[Dict[str, Any], None, None]:
    """
    Subscribe to progress updates for a scan.
    
    Args:
        scan_id: The scan ID to subscribe to
        
    Yields:
        dict: Progress updates with keys: scan_id, stage, percent, message
    """
    channel = f"scan_progress:{scan_id}"
    client = get_redis_client()
    
    pubsub = client.pubsub()
    pubsub.subscribe(channel)
    
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                yield data
    finally:
        pubsub.unsubscribe(channel)
        pubsub.close()


def set_scan_progress(scan_id: str, stage: str, percent: int) -> None:
    """
    Set progress in Redis hash for quick status lookup.
    
    Args:
        scan_id: The scan ID
        stage: Current stage
        percent: Progress percentage
    """
    key = f"scan:{scan_id}:progress"
    client = get_redis_client()
    
    client.hset(key, mapping={
        "stage": stage,
        "percent": str(percent),
    })
    client.expire(key, 3600)


def get_scan_progress(scan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get current progress from Redis hash.
    
    Args:
        scan_id: The scan ID
        
    Returns:
        dict or None: Progress data
    """
    key = f"scan:{scan_id}:progress"
    client = get_redis_client()
    
    data = client.hgetall(key)
    if not data:
        return None
    
    return {
        "stage": data.get("stage"),
        "percent": int(data.get("percent", 0)),
    }
