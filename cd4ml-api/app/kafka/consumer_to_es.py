from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
KAFKA_TOPIC = "entrada-modelos"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset="latest",
    group_id="es-writer",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

es = Elasticsearch("http://es01:9200")

for msg in consumer:
    evento = msg.value
    es.index(index="entrada_modelos", document=evento)
    print(f"[ES] Gravado: {evento}")