import os

import yt_dlp

DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")


class FacebookDown:

    def __init__(
        self, video_url, output_dir, quiet=False, no_warn=False, end_ret=False
    ):

        self.end_ret = end_ret
        self._download_video(video_url, output_dir, quiet, no_warn)

    def _progress_hooks(self, status):

        actions = {
            "finished": lambda: print(f"\n\nDownloaded - {status['filename']}"),
            "downloading": lambda: print(
                status["_percent_str"],
                status["_eta_str"],
                end="\r" if self.end_ret else "\n",
            ),
        }
        if status["status"] in actions:
            actions[status["status"]]()

    def _download_video(self, video_url, output_dir, quiet, no_warn):

        print("Download started..\n")
        with yt_dlp.YoutubeDL(
            {
                "format": "b",
                "outtmpl": f"{output_dir}",
                "quiet": quiet,
                "no_warning": no_warn,
                "progress_hooks": [self._progress_hooks],
            }
        ) as ydl:
            ydl.download([video_url])


def download_facebook_video(
    video_url, task_id, quiet=False, no_warn=False, end_ret=False
):

    # Define the full path to save the video using the task ID as the filename
    video_filename = f"{task_id}.mp4"
    video_path = os.path.join(DOWNLOAD_DIR, video_filename)

    # Download the video from Facebook using the FacebookDown class
    FacebookDown(video_url, video_path, quiet, no_warn, end_ret)

    print(f"Video downloaded successfully to: {video_path}")
    return video_path
