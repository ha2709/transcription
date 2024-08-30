import os

DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")
import shutil

import pyktok as pyk

from ..utils.decorators import cache, log

pyk.specify_browser("chrome")


@log
def download_tiktok_video(tiktok_url, task_id):
    print(66, "tiktok called ")
    # Extract the username and video ID from the TikTok URL
    url_parts = tiktok_url.rstrip("/").split("/")
    username = url_parts[-3].replace("@", "")  # Extract username (remove '@')
    video_id = url_parts[-1]  # Extract video ID

    # Format the filename as '@username_video_videoID.mp4'
    video_filename = f"@{username}_video_{video_id}.mp4"

    # Ensure the output directory exists
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # Full path for saving the video

    pyk.save_tiktok(tiktok_url, True, "video_data.csv")

    # Full path of the video in the current working directory
    current_path = os.path.join(os.getcwd(), video_filename)

    # Full path where the video should be moved in the download directory

    new_filename = f"{task_id}.mp4"
    video_path = os.path.join(DOWNLOAD_DIR, new_filename)
    # Move and rename the video to the download directory with the new UUID filename
    shutil.move(current_path, video_path)
    return video_path
