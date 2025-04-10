import logging
import os
import re

import httpx
from dotenv import load_dotenv
from services.email import send_email
from utils.enum_utils import TaskStatus

load_dotenv()
api_base_url = os.getenv("API_BASE_URL")


async def update_task_url(
    task_id: str, new_status: str, output_file_url: str, user_email: str
):
    # First, read the file content from the output_file_url
    file_content = ""
    try:
        with open(output_file_url, "r", encoding="utf-8") as file:
            lines = file.readlines()
            # Filter out lines that contain any numbers (e.g., timestamps or line numbers)
            text_lines = [line.strip() for line in lines if not re.search(r"\d", line)]
            file_content = "\n".join(text_lines).strip()
    except FileNotFoundError:
        logging.error(f"File not found at path: {output_file_url}")
        return
    except Exception as e:
        logging.error(f"Error reading file {output_file_url}: {str(e)}")
        return

    print(34, file_content)
    # Construct the full API URL by appending the task_id and 'output-url' endpoint
    api_url = f"{api_base_url}/api/tasks/{task_id}/output-url"
    # api_url = f"http://localhost:8000/api/tasks/{task_id}/output-url"
    params = {"translated_text": file_content, "new_status": new_status}

    # Make the HTTP request to update the task's output file URL
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(api_url, params=params)
            if response.status_code == 200:
                logging.info(
                    f"Task ID: {task_id} updated with output_file_url: {output_file_url}"
                )
                # Send email notification for task completion
                subject = f"Your Task {task_id} is Completed"
                body = f"Hello,\n\nYour task with ID {task_id} has been completed successfully.\n\nYou can access the output here: {output_file_url}\n\nBest regards,\nYour Team"
                await send_email(user_email, subject, body)
            else:
                logging.error(
                    f"Failed to update output_file_url for task ID: {task_id}. Status Code: {response.status_code}"
                )
        except httpx.RequestError as exc:
            logging.error(
                f"An error occurred while requesting {exc.request.url!r}. Error: {exc}"
            )
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")


async def update_task_status(task_id: str, new_status: str, user_email: str):
    """
    Update the task status by calling the API and send email notification.
    """
    # api_url = f"http://localhost:8000/api/tasks/{task_id}/status"
    api_url = f"{api_base_url}/api/tasks/{task_id}/status"
    params = {"new_status": new_status}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(api_url, params=params)
            if response.status_code != 200:
                logging.error(f"Failed to update task status for task ID: {task_id}")
            else:
                logging.info(f"Task ID: {task_id} updated to status: {new_status}")
                # Optionally, send an email when status is updated to specific values
                if new_status == TaskStatus.COMPLETED.value:
                    subject = f"Your Task {task_id} is Completed"
                    body = f"Hello,\n\nYour task with ID {task_id} has been completed successfully.\n\nBest regards,\nYour Team"
                    await send_email(user_email, subject, body)
                elif new_status == TaskStatus.FAILED.value:
                    subject = f"Your Task {task_id} has Failed"
                    body = f"Hello,\n\nYour task with ID {task_id} has failed. Please try again or contact support.\n\nBest regards,\nYour Team"
                    await send_email(user_email, subject, body)
        except httpx.RequestError as exc:
            logging.error(
                f"An error occurred while requesting {exc.request.url!r}. Error: {exc}"
            )
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
