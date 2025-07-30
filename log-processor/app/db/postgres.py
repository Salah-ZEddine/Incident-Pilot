import asyncpg
import json
import logging
from dateutil.parser import isoparse
from app.config import settings
from app.models import log_model
from app.models.log_model import LogModel

DB_CONFIG = {
    "user": settings.postgres_user,
    "password": settings.postgres_password,
    "database": settings.postgres_db,
    "host": settings.postgres_host,
    "port": settings.postgres_port,
}

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=10)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def insert_log(self, log: LogModel):

        # Safe timestamp handling
        ts = log.timestamp
        if isinstance(ts, str):
            ts = isoparse(ts)
        elif ts is None:
            logger.error("timestamp is null")
            #ts = datetime.utcnow()  # fallback
        # Serialize 'extra' if it is a dict
        extra = log.extra
        if isinstance(extra, dict):
            extra = json.dumps(extra)
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
                log.source,
                log.hostname,
                log.log_level,
                log.message,
                log.event_type,
                log.source_ip,
                log.destination_ip,
                log.user_id,
                log.username,
                log.http_method,
                log.http_url,
                log.http_status,
                log.user_agent,
                log.tags,
                extra,
                log.tenant or "default",
            )