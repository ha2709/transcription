import json
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_db
from src.schemas.transcription import TranscriptionRequest
from src.services.task import create_task
from src.utils.producer import init_kafka_producer

router = APIRouter()


@router.post("/transcribe/")
async def transcribe_video(
    transcription_request: TranscriptionRequest,
    db: AsyncSession = Depends(get_async_db),
):
    video_url = transcription_request.videoUrl
    to_language = transcription_request.translateLanguage
    from_language = transcription_request.language

    task_id = str(uuid.uuid4())
    user_ip = "127.0.0.1"  # Mock for now, replace with real IP fetching logic
    # Create a task in the database
    await create_task(user_ip=user_ip, task_id=task_id, db=db)
    message = {
        "video_url": video_url,
        "to_language": to_language,
        "task_id": task_id,
        "from_language": from_language,
        "user_ip": user_ip,
    }

    producer = await init_kafka_producer()  # Get the producer instance
    try:
        await producer.send_and_wait(
            "video-transcription", json.dumps(message).encode("utf-8")
        )

    finally:
        return JSONResponse(content={"task_id": task_id}, status_code=202)
