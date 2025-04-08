# services/task_service.py

import json
import uuid

from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.task import Task
from src.repositories.task_repository import create_task
from src.repositories.task_repository import delete_task as delete_task_record
from src.repositories.task_repository import get_task_by_id, update_task_output
from src.repositories.task_repository import (
    update_task_status as repo_update_task_status,
)
from src.services.upload_service import save_file_to_disk
from src.utils.enum_utils import TaskStatus
from src.utils.producer import init_kafka_producer


async def handle_task_creation(
    file: UploadFile,
    language: str,
    translate_language: str,
    user_ip: str,
    db: AsyncSession,
) -> str:
    task_id = str(uuid.uuid4())
    file_path = save_file_to_disk(file)

    task = Task(task_id=task_id, status="pending", user_ip=user_ip)
    await create_task(db, task)

    message = {
        "file_path": file_path,
        "to_language": translate_language,
        "task_id": task_id,
        "from_language": language,
        "user_ip": user_ip,
    }

    kafka_producer = await init_kafka_producer()
    try:
        await kafka_producer.send_and_wait(
            "file-upload", json.dumps(message).encode("utf-8")
        )
    finally:
        await kafka_producer.stop()

    return task_id


async def get_task(task_id: str, db: AsyncSession) -> Task:
    return await get_task_by_id(db, task_id)


async def delete_task(task_id: str, db: AsyncSession) -> None:
    task = await get_task_by_id(db, task_id)
    await delete_task_record(db, task)


async def update_task_output_url(
    task_id: str, new_status: str, translated_text: str, db: AsyncSession
) -> Task:
    task = await get_task_by_id(db, task_id)
    return await update_task_output(db, task, new_status, translated_text)


async def update_task_status(task_id: str, new_status: str, db: AsyncSession) -> Task:
    task = await get_task_by_id(db, task_id)
    return await repo_update_task_status(db, task, new_status)


async def get_task_status_service(task_id: str, db: AsyncSession):
    task = await get_task_by_id(db, task_id)

    if task.status == TaskStatus.COMPLETED.value:
        return {"status": task.status, "file_content": task.translated_text}

    return JSONResponse(content={"status": task.status}, status_code=200)
