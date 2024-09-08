import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_db
from src.schemas.transcription import TranscriptionRequest
from src.services.task import get_task
from src.utils.producer import init_kafka_producer

router = APIRouter()


@router.get("/task-status/{task_id}")
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    task = await get_task(task_id, db)
    status = task.status
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={"status": status}, status_code=200)
