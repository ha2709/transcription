from urllib.parse import urlparse

# Applying decorators to methods
from ..utils.decorators import log
from .download_facebook_video import download_facebook_video
from .download_instagram_video import download_instagram_video
from .download_tiktok_video import download_tiktok_video
from .download_twitter_video import download_twitter_video
from .download_youtube_video import download_youtube_video


@log
# Function to process the video based on URL
def process_video_url(video_url, task_id):
    parsed_url = urlparse(video_url)
    domain = parsed_url.netloc
    print(46, "url ", video_url, task_id, domain, "twitter.com" or "x.com" in domain)
    if "youtube.com" in domain or "youtu.be" in domain:
        return download_youtube_video(video_url, task_id)
    # elif "twitter.com" in domain:
    #     return download_twitter_video(video_url, task_id)
    elif "x.com" in domain:
        return download_twitter_video(video_url, task_id)
    elif "instagram.com" in domain:
        return download_instagram_video(video_url, task_id)
    elif "facebook.com" in domain:
        return download_facebook_video(video_url, task_id)
    elif "tiktok.com" in domain:
        return download_tiktok_video(video_url, task_id)
    else:
        raise ValueError(
            "Unsupported video source. Only YouTube, Twitter, and Instagram are supported."
        )
