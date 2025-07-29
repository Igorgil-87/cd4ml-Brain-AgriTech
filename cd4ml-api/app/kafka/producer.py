from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
KAFKA_TOPIC = "entrada-modelos"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_to_kafka(event: dict):
    producer.send(KAFKA_TOPIC, value=event)
    producer.flush()