import asyncio
import json
import logging
import signal
import sys
from typing import Dict, Any

from app.kafka.kafka_consumer import KafkaLogConsumer
from app.kafka.kafka_producer import KafkaProducer
from app.processors.facts_generator import FactGenerator
from app.config import settings
from app.db.postgres import Database
from app.models.log_model import LogModel
from app.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class LogProcessor:
    def __init__(self):
        self.repo = None
        self.consumer = None
        self.producer = None
        self.running = False

    async def start(self):
        """Initialize and start all services"""
        try:
            logger.info("Starting Log Processor...")
            
            # Initialize database connection
            self.repo = Database()
            await self.repo.connect()
            logger.info("Database connection established")

            # Initialize Kafka consumer
            self.consumer = KafkaLogConsumer(settings.kafka_topic_input)
            await self.consumer.start()
            logger.info(f"Kafka consumer started for topic: {settings.kafka_topic_input}")

            # Initialize Kafka producer
            self.producer = KafkaProducer(settings.kafka_bootstrap_servers, settings.kafka_topic_output)
            await self.producer.start()
            logger.info(f"Kafka producer started for topic: {settings.kafka_topic_output}")

            self.running = True
            logger.info("🚀 Log Processor is running successfully!")

        except Exception as e:
            logger.error(f"Failed to start Log Processor: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Gracefully stop all services"""
        if not self.running:
            return
            
        logger.info("Stopping Log Processor...")
        self.running = False

        # Stop Kafka consumer
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

        # Stop Kafka producer
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

        # Close database connection
        if self.repo:
            await self.repo.close()
            logger.info("Database connection closed")

        logger.info("Log Processor stopped gracefully")

    async def handle_log(self, log_data: Dict[Any, Any]):
        """Process a single log message"""
        try:
            # Log the raw data for debugging (only first few times)
            if not hasattr(self, '_log_samples_shown'):
                self._log_samples_shown = 0
            
            if self._log_samples_shown < 3:
                logger.info(f"Sample raw log data: {json.dumps(log_data, indent=2, default=str)}")
                self._log_samples_shown += 1

            # Parse log data into LogModel
            log = LogModel(**log_data)
            logger.debug(f"Processing log from {log.source}: {log.message[:100] if log.message else 'No message'}...")
            
            # Debug log parsing (only for first few logs)
            if self._log_samples_shown <= 3:
                logger.info(f"Parsed log - Source: '{log.source}', Level: '{log.log_level}', Message: '{log.message}'")

            # Save log to PostgreSQL
            await self.repo.insert_log(log)
            logger.debug(f"Log saved to database: {log.source}")

            # Generate facts from the log
            try:
                fact_generator = FactGenerator(log)
                fact = fact_generator.generate_facts_from_log()
                
                # Send fact to Kafka (use model_dump with mode='json' for proper serialization)
                await self.producer.send_fact(fact.model_dump(mode='json'))
                logger.debug(f"Fact sent to Kafka: {fact.source}")
                logger.info(f"Successfully processed log from {log.source}")
            except Exception as fact_error:
                logger.error(f"Error generating facts: {fact_error}")
                logger.error(f"Log source: '{log.source}', message: '{log.message}'")
                raise

        except Exception as e:
            logger.error(f"Error processing log: {e}")
            logger.error(f"Raw log data keys: {list(log_data.keys()) if isinstance(log_data, dict) else 'Not a dict'}")
            if isinstance(log_data, dict) and len(str(log_data)) < 1000:
                logger.error(f"Full log data: {log_data}")
            else:
                logger.error(f"Log data (truncated): {str(log_data)[:500]}...")

    async def run(self):
        """Main processing loop"""
        try:
            await self.start()
            
            # Start consuming logs
            await self.consumer.consume(self.handle_log)
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            await self.stop()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    sys.exit(0)

async def main():
    """Main entry point"""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and run the log processor
    processor = LogProcessor()
    await processor.run()

if __name__ == "__main__":
    asyncio.run(main())