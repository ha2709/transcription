# repositories/task_repository.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.task import Task


async def create_task(db: AsyncSession, task: Task) -> Task:
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_by_id(db: AsyncSession, task_id: str) -> Task:
    result = await db.execute(select(Task).filter(Task.task_id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()


async def update_task_output(
    db: AsyncSession, task: Task, status: str, text: str
) -> Task:
    task.status = status
    task.translated_text = text
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_status(db: AsyncSession, task: Task, status: str) -> Task:
    task.status = status
    await db.commit()
    await db.refresh(task)
    return task
