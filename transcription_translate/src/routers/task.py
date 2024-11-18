import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_db
from src.schemas.transcription import TranscriptionRequest
from src.services.task import (
    delete_task,
    get_task,
    get_task_status_service,
    handle_task_creation,
    update_task_output_url,
    update_task_status,
)

router = APIRouter()


# Create a new task (C - Create)
@router.post("/tasks/")
async def create_task_endpoint(
    file: UploadFile,
    language: str,
    translate_language: str,
    user_ip: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Creates a new task by uploading a file and sending it to Kafka for processing.
    """
    task_id = await handle_task_creation(
        file, language, translate_language, user_ip, db
    )
    return JSONResponse(content={"task_id": task_id}, status_code=201)


# Retrieve the status of a specific task (R - Read)
@router.get("/tasks/{task_id}")
async def get_task_status_endpoint(
    task_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieves the current status of the task based on its task ID.
    """
    result = await get_task_status(task_id, db)
    print(49, result)
    return JSONResponse(
        content={"status": result["status"], "content": result["file_content"]},
        status_code=200,
    )


# Update the status of a specific task (U - Update)
@router.put("/tasks/{task_id}/status")
async def update_task_status_endpoint(
    task_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Updates the status of a task by providing a new status.
    """
    task = await update_task_status(task_id, new_status, db)
    return JSONResponse(
        content={"task_id": task_id, "status": task.status}, status_code=200
    )


# Update the output file URL of a specific task
@router.put("/tasks/{task_id}/output-url")
async def update_task_output_url_endpoint(
    task_id: str,
    translated_text: str,
    new_status: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Updates the output_file_url of a task by providing a new URL.
    """
    # Fetch the task and ensure it exists
    task = await get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update the task's output_file_url and commit changes to the database
    updated_task = await update_task_output_url(
        task_id, new_status, translated_text, db
    )

    return JSONResponse(
        content={
            "task_id": updated_task.task_id,
            "output_file_url": updated_task.output_file_url,
            "status": updated_task.status,
        },
        status_code=200,
    )


# Delete a specific task (D - Delete)
@router.delete("/tasks/{task_id}")
async def delete_task_endpoint(
    task_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Deletes a task from the database based on its task ID.
    """
    await delete_task(task_id, db)
    return JSONResponse(
        content={"message": "Task deleted successfully"}, status_code=200
    )


@router.get("/task-status/{task_id}")
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    print(89, task_id)
    return await get_task_status_service(task_id, db)
