import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from sqlalchemy.engine import Engine
from src.utils.producer import init_kafka_producer, shutdown_kafka_producer

from .routers import auth, task, transcription, upload

app = FastAPI()

# Kafka setup
KAFKA_TOPIC = "video-transcription"
task_db = {}  # Dummy task database

# Optionally, to silence the SQLAlchemy logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Directory to store uploaded files
DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# On startup, initialize the Kafka producer and consumer
@app.on_event("startup")
async def startup_event():
    producer = await init_kafka_producer()  # Initialize the producer
    # asyncio.create_task(consume_messages(KAFKA_TOPIC, task_db))  # Start the consumer


# On shutdown, close the Kafka producer
# @app.on_event("shutdown")
# async def shutdown_event():
#     await shutdown_kafka_producer(producer)


# Include routes
app.include_router(auth.router, prefix="/api")
app.include_router(transcription.router, prefix="/api")
app.include_router(task.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
