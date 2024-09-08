import json
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.task import Task
from src.services.upload_service import save_file_to_disk
from src.utils.producer import init_kafka_producer


async def create_task(user_ip: str, task_id: str, db: AsyncSession) -> Task:

    new_task = Task(
        task_id=task_id,
        status="pending",
        user_ip=user_ip,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


async def handle_task_creation(
    file: UploadFile,
    language: str,
    translate_language: str,
    user_ip: str,
    db: AsyncSession,
) -> str:
    """
    Handles the task creation process, including file upload, database task creation,
    and sending a message to Kafka.
    """
    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Save file to disk
    file_path = save_file_to_disk(file)

    # Create a task in the database
    await create_task(user_ip=user_ip, task_id=task_id, db=db)

    # Create the message payload for Kafka
    message = {
        "file_path": file_path,
        "to_language": translate_language,
        "task_id": task_id,
        "from_language": language,
        "user_ip": user_ip,
    }

    print(33, message)

    # Send message to Kafka
    kafka_producer = await init_kafka_producer()
    try:
        await kafka_producer.send_and_wait(
            "file-upload", json.dumps(message).encode("utf-8")
        )
    finally:
        await kafka_producer.stop()

    return task_id


async def get_task(task_id: str, db: AsyncSession) -> Task:

    result = await db.execute(select(Task).filter(Task.task_id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def delete_task(task_id: str, db: AsyncSession) -> None:

    task = await get_task(task_id, db)
    await db.delete(task)
    await db.commit()


async def update_task_status(task_id: str, new_status: str, db: AsyncSession) -> Task:

    task = await get_task(task_id, db)
    task.status = new_status
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_status(task_id: str, db: AsyncSession) -> str:

    # Query the database for the task with the given task_id
    result = await db.execute(select(Task).filter(Task.task_id == task_id))
    task = result.scalars().first()

    # If the task does not exist, raise a 404 error
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the status of the task
    return task.status
