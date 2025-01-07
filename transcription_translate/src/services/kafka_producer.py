import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from tenacity import retry, stop_after_attempt, wait_exponential

KAFKA_TOPIC = "video-transcription"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
UPLOAD_FILE_TOPIC = "file-upload"


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
