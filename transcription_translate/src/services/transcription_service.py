import asyncio


# Simulate transcription task (dummy implementation)
async def simulate_transcription_task(task_id: str):
    await asyncio.sleep(10)  # Simulate processing delay
    task_db[task_id] = "completed"
