import asyncio
import logging
import json
from aiokafka import AIOKafkaConsumer
from app.config import settings

logger = logging.getLogger(__name__)


class KafkaLogConsumer:
    def __init__(self, topic: str):
        self.topic = topic
        self.bootstrap_servers = settings.kafka_bootstrap_servers
        self.group_id = settings.kafka_group_id
        self.consumer = None

    async def start(self):
        logger.info("Initializing Kafka consumer...")
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()
        logger.info(f"Started Kafka consumer for topic: {self.topic}")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped.")

    async def consume(self, handle_log_fn):
        try:
            async for msg in self.consumer:
                logger.debug(f"Received message: {msg.value}")
                await handle_log_fn(msg.value)
        except Exception as e:
            logger.error(f"Error during log consumption: {e}")
        finally:
            await self.stop()
