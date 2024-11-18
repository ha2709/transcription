import logging
import os
import re
from email.message import EmailMessage

import aiosmtplib
import httpx

# from .models import VideoProcess  # Import the VideoProcess model
from services.process_video import process_video_url
from utils.enum_utils import TaskStatus
from utils.srt_validation import validate_srt_file
from utils.subtitle import add_subtitle_to_video
from utils.transcription import (
    clean_srt_file,
    transcribe_and_translate_srt,
    translate_srt_file,
    video_to_audio,
)
from whisper import load_model

# Load the Whisper model
model = load_model("small", device="cpu")

# Email Configuration from Environment Variables
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")


async def send_email(to_email: str, subject: str, body: str):
    """Asynchronously send an email notification."""
    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True,  # Set to False if using SSL (port 465)
        )
        logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")


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
    api_url = f"http://localhost:8000/api/tasks/{task_id}/output-url"
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
    api_url = f"http://localhost:8000/api/tasks/{task_id}/status"
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


async def process_file_upload(message):
    """Process the uploaded file."""
    print(33, message)
    task_id = message["task_id"]
    user_email = message.get(
        "email"
    )  # Assuming the user's email is provided in the message
    try:

        logging.warning(f"Processing srt file upload task ID: {task_id}")

        input_file = message.get("file_path")
        output_file = os.path.join("media/out", f"output-{task_id}.mp4")
        # Update task status to 'processing'
        await update_task_status(task_id, TaskStatus.PROCESSING.value, user_email)

        # Check if the uploaded file is an SRT file
        if input_file.lower().endswith(".srt"):
            # Translate the SRT file to the desired language
            translated_srt_path = translate_srt_file(
                input_file, message["from_language"], message["to_language"]
            )
            clean_srt_file(translated_srt_path)
            logging.warning(f"Translated SRT file saved to: {translated_srt_path}")
            # Update task status to 'completed' and set output_file_url
            await update_task_url(
                task_id, TaskStatus.COMPLETED.value, translated_srt_path, user_email
            )

            return translated_srt_path

        else:
            # Process the uploaded video file
            logging.warning(f"Processing video file upload task ID: {task_id}")

            # Transcribe and translate SRT
            translated_srt_path, original_srt_path = transcribe_and_translate_srt(
                input_file, message["to_language"]
            )

            logging.warning(f"SRT file saved to: {translated_srt_path}")
            # check input file is sound or video file. if video continue
            if input_file.endswith((".mp4", ".avi", ".mov", ".mkv")):
                print("process video file ")
                # Validate and add subtitles to the video
                if validate_srt_file(translated_srt_path):
                    add_subtitle_to_video(
                        input_file,
                        soft_subtitle=True,
                        subtitle_file=translated_srt_path,
                        subtitle_language=message["to_language"],
                    )
                    logging.warning("Video with subtitles saved.")
                else:
                    logging.error("Failed to validate the SRT file.")
                    await update_task_status(
                        task_id, TaskStatus.FAILED.value, user_email
                    )
                    return None
            # Save the updated status to the database
            await update_task_url(
                task_id, TaskStatus.COMPLETED.value, translated_srt_path, user_email
            )
            # await update_task_status(task_id, TaskStatus.COMPLETED.value)
            return output_file

    except Exception as e:
        logging.error(
            f"Failed to process file upload task ID: {task_id}, Error: {str(e)}"
        )

        # Update the status to "failed" in case of an error
        await update_task_status(task_id, TaskStatus.FAILED.value, user_email)
        return None


async def process_video_message(message):
    task_id = message["task_id"]
    user_email = message.get(
        "email"
    )  # Assuming the user's email is provided in the message

    try:
        # Update task status to 'processing'
        await update_task_status(task_id, TaskStatus.PROCESSING.value, user_email)
        # Process video and generate paths
        input_file = process_video_url(message["video_url"], task_id)
        translated_srt_path, original_srt_path = transcribe_and_translate_srt(
            input_file, message["to_language"]
        )

        logging.warning(f"SRT file saved to: {translated_srt_path}")

        # Validate and add subtitles to the video
        if validate_srt_file(translated_srt_path):
            add_subtitle_to_video(
                input_file,
                soft_subtitle=True,
                subtitle_file=translated_srt_path,
                subtitle_language=message["to_language"],
            )
            logging.warning("Video with subtitles saved.")
        else:
            logging.error("Failed to validate the SRT file.")
            await update_task_status(task_id, TaskStatus.FAILED.value, user_email)
            return

        # Update task status to 'completed' and send email notification
        await update_task_url(
            task_id, TaskStatus.COMPLETED.value, translated_srt_path, user_email
        )
    except Exception as e:
        logging.error(f"Failed to process task ID: {task_id}, Error: {str(e)}")
        await update_task_status(task_id, TaskStatus.FAILED.value, user_email)
