import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_db
from src.models.task import Task
from src.services.task import handle_task_creation
from src.utils.auth import get_client_ip

router = APIRouter()


@router.post("/upload-video-file/")
async def upload_video_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form(...),
    translate_language: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # kafka_producer = await init_kafka_producer()
    user_ip = get_client_ip(request)
    try:
        # Delegate task creation logic to the service layer
        task_id = await handle_task_creation(
            file=file,
            language=language,
            translate_language=translate_language,
            user_ip=user_ip,
            db=db,
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Task creation failed")

    return JSONResponse(content={"task_id": task_id}, status_code=202)
