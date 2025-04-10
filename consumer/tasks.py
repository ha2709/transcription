import logging
import os

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI

load_dotenv()
# 0. Disable default LLM (to avoid OpenAI dependency)
# Settings.llm = None
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# 1. Enable OpenAI as LLM
llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2)
Settings.llm = llm
from services.process_video import process_video_url
from services.task_service import update_task_status, update_task_url
from utils.enum_utils import TaskStatus
from utils.srt_validation import validate_srt_file
from utils.subtitle import add_subtitle_to_video
from utils.transcription import (
    clean_srt_file,
    transcribe_and_translate_srt,
    translate_srt_file,
)

# from consumer.services.document import process_summary_document


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
        print(input_file.lower())
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
        elif input_file.lower().endswith(".pdf"):
            logging.warning(f"Processing PDF file upload task ID: {task_id}")
            await process_summary_document(message)
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


async def process_summary_document(message):
    print(75, message)
    documents = SimpleDirectoryReader(input_files=[message["file_path"]]).load_data()
    # 2. Use local sentence transformer model (via LangChain wrapper)
    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 3. Parse documents into smaller chunks
    parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = parser.get_nodes_from_documents(documents)

    # 4. Build the index with local embeddings
    index = VectorStoreIndex(nodes, embed_model=embed_model)

    # 5. Query the index (LLM disabled, fallback to keyword/embedding retrieval)
    query_engine = index.as_query_engine()
    response = query_engine.query(
        "Give me summary of the document ignore the disclaimer"
    )
    print(response)
