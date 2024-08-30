import logging
import os

from django.conf import settings
from whisper import load_model

from .models import VideoProcess  # Import the VideoProcess model
from .service.process_video import process_video_url
from .utils.srt_validation import validate_srt_file
from .utils.subtitle import add_subtitle_to_video
from .utils.transcription import (
    clean_srt_file,
    transcribe_and_translate_srt,
    translate_srt_file,
    video_to_audio,
)

# DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "media/download")
# SRT_DIR = os.path.join(settings.MEDIA_ROOT, "media/srt")


# Ensure directories exist
# os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# os.makedirs(SRT_DIR, exist_ok=True)
# os.makedirs(OUT_DIR, exist_ok=True)

# Load the Whisper model
model = load_model("small", device="cpu")


def process_file_upload(message):
    """Process the uploaded file."""
    print(33, message)
    task_id = message["task_id"]
    try:
        # Create a new record in the VideoProcess table
        video_process = VideoProcess.objects.create(
            video_url=message.get("file_path", ""), task_id=task_id, status="processing"
        )
        video_process.user_ip = message["user_ip"]
        video_process.save()
        logging.warning(f"Processing file upload task ID: {task_id}")

        input_file = message.get("file_path")
        output_file = os.path.join("media/out", f"output-{task_id}.mp4")

        # Check if the uploaded file is an SRT file
        if input_file.lower().endswith(".srt"):
            # Translate the SRT file to the desired language
            translated_srt_path = translate_srt_file(
                input_file, message["from_language"], message["to_language"]
            )
            clean_srt_file(translated_srt_path)
            logging.warning(f"Translated SRT file saved to: {translated_srt_path}")

            # Update the status to "completed" and save to the database
            video_process.status = "completed"
            video_process.output_file_url = translated_srt_path
            video_process.save()
            return translated_srt_path

        else:
            # Process the uploaded video file
            logging.warning(f"Processing video file upload task ID: {task_id}")

            # Convert the video file to audio if needed
            audio_file = video_to_audio(input_file)

            # Transcribe and translate SRT
            translated_srt_path, original_srt_path = transcribe_and_translate_srt(
                audio_file, message["to_language"]
            )

            logging.warning(f"SRT file saved to: {translated_srt_path}")

            # Validate and add subtitles to the video
            if validate_srt_file(translated_srt_path):
                add_subtitle_to_video(
                    input_file,
                    output_file,
                    soft_subtitle=True,
                    subtitle_file=translated_srt_path,
                    subtitle_language=message["language"],
                )
                logging.warning("Video with subtitles saved.")
                video_process.status = "completed"
                video_process.output_file_url = output_file
            else:
                logging.error("Failed to validate the SRT file.")
                video_process.status = "failed"

            # Save the updated status to the database
            video_process.save()
            return output_file if video_process.status == "completed" else None

    except Exception as e:
        logging.error(
            f"Failed to process file upload task ID: {task_id}, Error: {str(e)}"
        )

        # Update the status to "failed" in case of an error
        video_process.status = "failed"
        video_process.save()
        return None


def process_video_message(message):
    task_id = message["task_id"]
    try:
        # Create a new record in the VideoProcess table
        video_process = VideoProcess.objects.create(
            video_url=message["video_url"], task_id=task_id, status="processing"
        )
        video_process.user_ip = message["user_ip"]
        video_process.save()
        logging.warning(
            f"Processing task ID: {task_id}, Video URL: {message['video_url']}"
        )

        # Process video and generate paths
        input_file = process_video_url(message["video_url"], task_id)
        translated_srt_path, original_srt_path = transcribe_and_translate_srt(
            input_file, message["language"]
        )

        logging.warning(f"SRT file saved to: {translated_srt_path}")

        # Validate and add subtitles to the video
        if validate_srt_file(translated_srt_path):
            add_subtitle_to_video(
                input_file,
                soft_subtitle=True,
                subtitle_file=translated_srt_path,
                subtitle_language=message["language"],
            )
            logging.warning("Video with subtitles saved.")
            video_process.status = "completed"
        else:
            logging.error("Failed to validate the SRT file.")
            video_process.status = "failed"

        # Save the final status to the database

        # Generate URL for downloading the video using task_id
        video_filename = f"{task_id}.mp4"
        download_url = os.path.join(settings.MEDIA_URL, "out", video_filename)
        video_process.output_file_url = download_url
        video_process.save()
        return download_url

    except Exception as e:
        logging.error(f"Failed to process task ID: {task_id}, Error: {str(e)}")

        # Update the status to "failed" in case of an error
        video_process.status = "failed"
        video_process.save()

        return None
