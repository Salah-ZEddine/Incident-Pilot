import redis
import json
from datetime import datetime, timedelta
from typing import List
from app.config import settings

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

def datetime_serializer(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def push_log_history(source: str, log: dict):
    try:
        key = f"logs:{source}"
        # Use custom serializer to handle datetime objects
        r.lpush(key, json.dumps(log, default=datetime_serializer))
        r.ltrim(key, 0, 200)  # Keep last 200 logs per source
    except Exception as e:
        # If Redis is down, just continue without caching
        print(f"Warning: Redis error in push_log_history: {e}")

def get_logs_within(source: str, within_seconds: int) -> List[dict]:
    try:
        key = f"logs:{source}"
        logs = r.lrange(key, 0, -1)
        
        # Handle case where Redis returns None or empty
        if not logs:
            return []
            
        threshold = datetime.utcnow().timestamp() - within_seconds
        result = []
        
        for log_str in logs:
            try:
                log_dict = json.loads(log_str)
                if log_dict.get("timestamp"):
                    log_timestamp = datetime.fromisoformat(log_dict["timestamp"]).timestamp()
                    if log_timestamp > threshold:
                        result.append(log_dict)
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                # Skip malformed log entries
                continue
                
        return result
        
    except Exception as e:
        # If Redis is down or any other error, return empty list
        print(f"Warning: Redis error in get_logs_within: {e}")
        return []

def set_last_seen(source: str, ts: datetime):
    try:
        # Convert datetime to string before storing
        r.set(f"last_seen:{source}", ts.isoformat())
    except Exception as e:
        print(f"Warning: Redis error in set_last_seen: {e}")

def get_last_seen(source: str) -> datetime:
    try:
        val = r.get(f"last_seen:{source}")
        if val:
            return datetime.fromisoformat(val)
    except Exception as e:
        print(f"Warning: Redis error in get_last_seen: {e}")
    return None
