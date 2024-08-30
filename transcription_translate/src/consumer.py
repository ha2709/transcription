# kafka_integration/consumer.py

import json
import logging

from confluent_kafka import Consumer, KafkaError, KafkaException
from django.conf import settings

from .tasks import process_file_upload, process_video_message

KAFKA_TOPIC = "video-transcription"
UPLOAD_FILE_TOPIC = "file-upload"
c = Consumer(
    {
        "bootstrap.servers": "localhost:9092",
        "group.id": "video-transcription-group",
        "auto.offset.reset": "earliest",
    }
)

c.subscribe([KAFKA_TOPIC, UPLOAD_FILE_TOPIC])


def consume_messages():
    while True:
        msg = c.poll(1.0)  # Wait for message or exit on timeout

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                continue
            else:
                raise KafkaException(msg.error())

        # Process the message
        data = json.loads(msg.value().decode("utf-8"))
        logging.info(f"Received message: {data}")
        topic = msg.topic()
        # Handle message based on topic
        if topic == KAFKA_TOPIC:
            process_video_message(data)
        elif topic == UPLOAD_FILE_TOPIC:
            process_file_upload(data)
        # process_video_message(data)

    c.close()
