from app.kafka.kafka_consumer import KafkaLogConsumer
from app.config import settings

async def handle_log(log: dict):
    # You’ll plug in your parser → transformer → producer → postgres here
    print(log)

async def main():
    consumer = KafkaLogConsumer(topic=settings.kafka_topic_input)
    await consumer.start()
    await consumer.consume(handle_log)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
