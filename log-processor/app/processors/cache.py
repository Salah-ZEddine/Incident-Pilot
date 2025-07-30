import redis
import json
from datetime import datetime, timedelta
from typing import List
from app.config import settings

r = redis.Redis(host=settings.reddit_host, port=settings.reddit_port, decode_responses=True)

def push_log_history(source: str, log: dict):
    key = f"logs:{source}"
    r.lpush(key, json.dumps(log))
    r.ltrim(key, 0, 200)  # Keep last 200 logs per source

def get_logs_within(source: str, within_seconds: int) -> List[dict]:
    key = f"logs:{source}"
    logs = r.lrange(key, 0, -1)
    threshold = datetime.utcnow().timestamp() - within_seconds
    return [
        json.loads(l)
        for l in logs
        if json.loads(l).get("timestamp") and datetime.fromisoformat(json.loads(l)["timestamp"]).timestamp() > threshold
    ]

def set_last_seen(source: str, ts: datetime):
    r.set(f"last_seen:{source}", ts.isoformat())

def get_last_seen(source: str) -> datetime:
    val = r.get(f"last_seen:{source}")
    if val:
        return datetime.fromisoformat(val)
    return None
