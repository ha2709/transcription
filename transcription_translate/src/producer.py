# transcription/producer.py

import json

from confluent_kafka import Producer

KAFKA_TOPIC = "video-transcription"
UPLOAD_FILE_TOPIC = "file-upload"
producer = Producer({"bootstrap.servers": "localhost:9092"})


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def send_to_kafka(data, topic=KAFKA_TOPIC):
    """Send data to Kafka topic."""
    producer.produce(
        topic,
        key=str(data["task_id"]),
        value=json.dumps(data),
        callback=delivery_report,
    )
    producer.flush()
