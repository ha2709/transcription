import os

DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")


def get_srt_file_path(task_id: str):
    return os.path.join(DOWNLOAD_DIR, f"{task_id}.srt")
