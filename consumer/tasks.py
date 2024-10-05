import logging
import os

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


async def update_task_url(task_id: str, new_status: str, output_file_url: str):
    # First, read the file content from the output_file_url
    try:
        with open(output_file_url, "r", encoding="utf-8") as file:
            file_content = file.read()
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


async def update_task_status(task_id: str, new_status: str):
    """
    Update the task status by calling the API.
    """
    api_url = f"http://localhost:8000/api/tasks/{task_id}/status"
    params = {"new_status": new_status}
    async with httpx.AsyncClient() as client:
        response = await client.put(api_url, params=params)
        if response.status_code != 200:
            logging.error(f"Failed to update task status for task ID: {task_id}")
        else:
            logging.warning(f"Task ID: {task_id} updated to status: {new_status}")


async def process_file_upload(message):
    """Process the uploaded file."""
    print(33, message)
    task_id = message["task_id"]
    try:

        logging.warning(f"Processing srt file upload task ID: {task_id}")

        input_file = message.get("file_path")
        output_file = os.path.join("media/out", f"output-{task_id}.mp4")
        # Update task status to 'processing'
        await update_task_status(task_id, TaskStatus.PROCESSING.value)

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
                task_id, TaskStatus.COMPLETED.value, translated_srt_path
            )

            return translated_srt_path

        else:
            # Process the uploaded video file
            logging.warning(f"Processing up file upload task ID: {task_id}")

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
                    await update_task_status(task_id, TaskStatus.FAILED.value)
            # Save the updated status to the database
            await update_task_url(
                task_id, TaskStatus.COMPLETED.value, translated_srt_path
            )
            # await update_task_status(task_id, TaskStatus.COMPLETED.value)
            return output_file

    except Exception as e:
        logging.error(
            f"Failed to process file upload task ID: {task_id}, Error: {str(e)}"
        )

        # Update the status to "failed" in case of an error
        await update_task_status(task_id, TaskStatus.FAILED.value)
        return None


async def process_video_message(message):
    task_id = message["task_id"]

    try:
        # Update task status to 'processing'
        await update_task_status(task_id, TaskStatus.PROCESSING.value)
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
            # video_process.status = "completed"
        else:
            logging.error("Failed to validate the SRT file.")
            await update_task_status(task_id, TaskStatus.FAILED.value)
            # video_process.status = "failed"
        await update_task_status(task_id, TaskStatus.COMPLETED.value)
    except Exception as e:
        logging.error(f"Failed to process task ID: {task_id}, Error: {str(e)}")
        await update_task_status(task_id, TaskStatus.FAILED.value)
