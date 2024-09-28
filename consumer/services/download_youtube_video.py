import os

import yt_dlp
from utils.decorators import cache, log

DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")


# Function to download video from YouTube
@log
def download_youtube_video(video_url, task_id):

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": os.path.join(DOWNLOAD_DIR, f"{task_id}.%(ext)s"),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return os.path.join(DOWNLOAD_DIR, f"{task_id}.mp4")
