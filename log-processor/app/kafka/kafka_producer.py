import json
import logging
from aiokafka import AIOKafkaProducer

logger = logging.getLogger('kafka')

class KafkaProducer:
    def __init__(self,bootstrap_servers: str,topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None

    async def start(self):
        logger.info("Initializing Kafka producer...")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        logger.info("Kafka producer started.")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped.")

    async def send_fact(self, fact: dict, key: str = None):
        try:
            partition_key = key.encode("utf-8") if key else None
            await self.producer.send_and_wait(self.topic, value=fact, key=partition_key)
            logger.debug(f"Sent fact to topic {self.topic}: {fact}")
        except Exception as e:
            logger.error(f"Failed to send fact: {e}")