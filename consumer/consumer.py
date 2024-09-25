import asyncio
import json

from aiokafka import AIOKafkaConsumer
from tasks import process_file_upload, process_video_message

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # Replace with your Kafka server
KAFKA_TOPICS = ["video-transcription", "file-upload"]  # List of topics to subscribe to


async def consume_messages():
    consumer = AIOKafkaConsumer(
        *KAFKA_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="multi_topic_group",
    )
    await consumer.start()
    print("Start consumer ")
    try:
        async for message in consumer:
            topic = message.topic
            task_data = json.loads(message.value.decode("utf-8"))
            print(f"Received message from {topic}: {task_data}")

            # Call the appropriate function based on the topic
            if topic == "video-transcription":
                process_video_message(task_data)
            elif topic == "file-upload":
                process_file_upload(task_data)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_messages())
