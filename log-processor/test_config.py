from app.config import settings

def test_print_config():
    print("PostgreSQL Config:")
    print(f"  User: {settings.postgres_user}")
    print(f"  Password: {settings.postgres_password}")
    print(f"  DB: {settings.postgres_db}")
    print(f"  Port: {settings.postgres_port}")
    print(f"  Host: {settings.postgres_host}")
    print()
    print("Kafka Config:")
    print(f"  Bootstrap Servers: {settings.kafka_bootstrap_servers}")
    print(f"  Raw Topic: {settings.kafka_topic_input}")
    print(f"  Fact Topic: {settings.kafka_topic_output}")
    print(f"  Consumer Group ID: {settings.kafka_group_id}")

if __name__ == "__main__":
    test_print_config()
