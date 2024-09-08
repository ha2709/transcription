import asyncio
import json

from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "video-transcription"
UPLOAD_FILE_TOPIC = "file-upload"


async def shutdown_kafka_producer(producer: AIOKafkaProducer):
    """
    Shutdown the Kafka producer gracefully.

    Args:
        producer (AIOKafkaProducer): The Kafka producer to shut down.
    """
    try:
        # Attempt to stop the producer gracefully
        await producer.stop()
        print("Kafka producer has been shut down successfully.")
    except Exception as e:
        print(f"Error shutting down Kafka producer: {e}")


async def init_kafka_producer() -> AIOKafkaProducer:
    """
    Initialize and start an asynchronous Kafka producer.

    Returns:
        AIOKafkaProducer: An instance of the initialized Kafka producer.
    """
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    # Start the producer
    await producer.start()

    return producer


async def send_to_kafka(data, topic=KAFKA_TOPIC):
    """Asynchronously send data to a Kafka topic."""
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    # Start the producer
    await producer.start()
    try:
        # Send the message to the Kafka topic
        await producer.send_and_wait(
            topic,
            key=str(data["task_id"]).encode("utf-8"),  # Convert key to bytes
            value=json.dumps(data).encode(
                "utf-8"
            ),  # Convert message to JSON and then to bytes
        )
        print(f"Message sent to topic {topic} with task_id: {data['task_id']}")
    except Exception as e:
        print(f"Failed to send message: {e}")
    finally:
        # Always close the producer after finishing
        await producer.stop()
        # Always close the producer after finishing
        await producer.stop()
