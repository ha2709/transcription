import os

import instaloader
import requests

from ..utils.decorators import cache, log

# Directory paths
DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")


# Function to download video from Instagram
@log
def download_instagram_video(post_url, task_id):
    L = instaloader.Instaloader(download_videos=True, download_video_thumbnails=False)
    post = instaloader.Post.from_shortcode(L.context, post_url.split("/")[-2])
    video_url = post.video_url

    video_path = os.path.join(DOWNLOAD_DIR, f"{task_id}.mp4")
    response = requests.get(video_url, stream=True)
    with open(video_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return video_path
