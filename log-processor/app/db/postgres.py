import asyncpg
import json
from dateutil.parser import isoparse
from datetime import datetime
from app.config import settings

DB_CONFIG = {
    "user": settings.postgres_user,
    "password": settings.postgres_password,
    "database": settings.postgres_db,
    "host": settings.postgres_host,
    "port": settings.postgres_port,
}

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=10)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def insert_log(self, log: dict):
        # Safe timestamp handling
        ts = log.get("timestamp")
        if isinstance(ts, str):
            ts = isoparse(ts)
        elif ts is None:
            ts = datetime.utcnow()  # fallback
            # Serialize 'extra' if it is a dict
        extra = log.get("extra", {})
        if isinstance(extra, dict):
            extra = json.dumps(extra)  # convert dict to JSON string
        query = """
            INSERT INTO logs (
                timestamp, source, hostname, log_level, message,
                event_type, source_ip, destination_ip, user_id, username,
                http_method, http_url, http_status, user_agent,
                tags, extra, tenant
            ) VALUES (
                $1, $2, $3, $4, $5,
                $6, $7, $8, $9, $10,
                $11, $12, $13, $14,
                $15, $16, $17
            )
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query,
                ts,
                log.get("source"),
                log.get("hostname"),
                log.get("log_level"),
                log.get("message"),
                log.get("event_type"),
                log.get("source_ip"),
                log.get("destination_ip"),
                log.get("user_id"),
                log.get("username"),
                log.get("http_method"),
                log.get("http_url"),
                log.get("http_status"),
                log.get("user_agent"),
                log.get("tags", []),
                extra,
                log.get("tenant", "default"),
            )