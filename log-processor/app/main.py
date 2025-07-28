from app.kafka.kafka_consumer import KafkaLogConsumer
from app.config import settings
from db.postgres import Database
import asyncio


async def handle_log(log: dict):
    # You’ll plug in your parser → transformer → producer → postgres here
    print(log)

async def main():
    consumer = KafkaLogConsumer(topic=settings.kafka_topic_input)
    #await consumer.start()
    #await consumer.consume(handle_log)

async def test():
    db = Database()
    await db.connect()
    await db.insert_log({
    "timestamp": "2025-07-28T14:00:00Z",
    "source": "agent",
    "hostname": "vm-1",
    "log_level": "INFO",
    "message": "Test log message",
    "event_type": "test_event",
    "source_ip": "192.168.1.10",
    "destination_ip": "192.168.1.1",
    "user_id": "u123",
    "username": "admin",
    "http_method": "GET",
    "http_url": "/api/test",
    "http_status": 200,
    "user_agent": "curl/7.85.0",
    "tags": ["test", "debug"],
    "extra": {"debug": True},
    "tenant": "default"
        })
    await db.close()

if __name__ == "__main__":
    asyncio.run(test())
