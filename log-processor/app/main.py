from app.kafka.kafka_consumer import KafkaLogConsumer
from app.kafka.kafka_producer import KafkaProducer
from app.processors.facts_generator import FactGenerator
from app.config import settings, Settings
from db.postgres import Database
from app.models.log_model import LogModel
import asyncio
import json


async def handle_log(log_data: dict, repo: Database, fact_generator: FactGenerator, producer: KafkaProducer):
    try:
        log = LogModel(**log_data)
        await repo.insert_log(log)  # Save log to PostgreSQL

        facts = await fact_generator.generate_facts_from_log()  # Generate facts

        for fact in facts:
            await producer.send_fact(fact.dict())  # Send each fact to Kafka

    except Exception as e:
        print(f"[!] Error processing log: {e}\n{log_data}")

async def main():
    # Init services
    repo = Database()  # Connect to DB

    consumer = KafkaLogConsumer(settings.kafka_topic_input)
    producer = KafkaProducer(settings.kafka_bootstrap_servers,settings.kafka_topic_output)
    fact_generator = FactGenerator()

    print("🚀 Log Processor is running...")

    # Consume logs forever
    async for message in consumer.consume():
        log_data = json.loads(message.value)
        asyncio.create_task(handle_log(log_data, repo, fact_generator, producer))

if __name__ == "__main__":
    asyncio.run(main())