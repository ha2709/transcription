import asyncio
import json
import os
import uuid
from typing import Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse

# from .database import get_async_db
from src.schemas.transcription import TranscriptionRequest
from src.utils.auth import get_client_ip
from src.utils.rate_limit import rate_limited

app = FastAPI()

# Kafka setup
KAFKA_TOPIC = "video-transcription"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
UPLOAD_FILE_TOPIC = "file-upload"
# Dummy database to store task statuses
task_db = {}

# Directory to store uploaded files
DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# Kafka Producer Initialization
async def get_kafka_producer():

    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


 
# Async function to simulate transcription
async def simulate_transcription_task(task_id: str):
    await asyncio.sleep(10)  # Simulate processing delay
    task_db[task_id] = "completed"

@app.get("/")
@rate_limited(max_calls=1, time_frame=900)
async def read_root(request: Request):
    # logger.info("This is an root log message")
    return {"message": "Welcome to the Transcription & Translation "}

# Endpoint to transcribe video URL
@app.post("/api/transcribe/")
async def transcribe_video(
    transcription_request: TranscriptionRequest,
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    video_url = transcription_request.videoUrl
    to_language = transcription_request.translate_language
    from_language = transcription_request.language

    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    user_ip = get_client_ip

    # Create the message payload
    message = {
        "video_url": video_url,
        "to_language": to_language,
        "task_id": task_id,
        "from_language": from_language,
        "user_ip": user_ip,
    }
    try:
        # Produce the message to Kafka
        await kafka_producer.send_and_wait(KAFKA_TOPIC, json.dumps(message).encode("utf-8"))

        # Initialize task status
        task_db[task_id] = "pending"

        # Simulate the task processing
        # asyncio.create_task(simulate_transcription_task(task_id))
    finally:
        # await kafka_producer.stop()
        return JSONResponse(content={"task_id": task_id}, status_code=202)


# Endpoint to upload video file
@app.post("/api/upload-video-file/")
async def upload_video_file(
    file: UploadFile = File(...),
    language: str = Form(...),
    translate_language: str = Form(...),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Save the uploaded file to a temporary directory
    file_path = os.path.join(DOWNLOAD_DIR, file.filename)
    with open(file_path, "wb") as destination:
        destination.write(await file.read())

    user_ip = get_client_ip

    # Create the message payload
    message = {
        "file_path": file_path,
        "to_language": translate_language,
        "task_id": task_id,
        "from_language": language,
        "user_ip": user_ip,
    }
    try:
    # Produce the message to Kafka
        await kafka_producer.send_and_wait(
            UPLOAD_FILE_TOPIC, json.dumps(message).encode("utf-8")
        )

        # Initialize task status
        task_db[task_id] = "pending"

        # Simulate the task processing
        # asyncio.create_task(simulate_transcription_task(task_id))
    finally:
        return JSONResponse(content={"task_id": task_id}, status_code=202)


# Endpoint to check task status
@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    status = task_db.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    return JSONResponse(content={"status": status}, status_code=200)


# Endpoint to download SRT file
@app.get("/api/download-srt/{task_id}")
async def download_srt(task_id: str):
    srt_file_path = os.path.join(DOWNLOAD_DIR, f"{task_id}.srt")
    if not os.path.exists(srt_file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        srt_file_path, media_type="application/octet-stream", filename=f"{task_id}.srt"
    )


# Background task to consume messages from Kafka (simulate processing)
async def consume_messages():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="video_processing_group",
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message: {message.value.decode('utf-8')}")
            # Process the message here
            # Simulate processing logic
            task_id = json.loads(message.value.decode("utf-8"))["task_id"]
            asyncio.create_task(simulate_transcription_task(task_id))
    finally:
        await consumer.stop()


# Start the Kafka consumer on application startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_messages())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
