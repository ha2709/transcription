import os

from fastapi import UploadFile

DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def save_file_to_disk(file: UploadFile):
    file_path = os.path.join(DOWNLOAD_DIR, file.filename)
    with open(file_path, "wb") as destination:
        destination.write(file.file.read())
    return file_path
