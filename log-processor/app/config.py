from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    postgres_host: str = "localhost"  # optional with default

    # Kafka
    kafka_bootstrap_servers: str  # from KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS
    kafka_topic_input: str
    kafka_topic_output: str
    kafka_group_id: str = "log_processor_group"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
