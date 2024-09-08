import os

import ffmpeg


def add_subtitle_to_video(
    input_video,
    soft_subtitle,
    subtitle_file,
    subtitle_language,
    output_file=None,
    font_path=None,
):
    input_video_name, _ = os.path.splitext(os.path.basename(input_video))

    # Set default output file path if output_file is not provided
    if not output_file:
        output_video = os.path.join("media/out", f"output-{input_video_name}.mp4")
    else:
        output_video = output_file

    # Command configuration
    common_options = {
        "c:v": "libx264",
        "c:a": "copy",
    }

    # Add subtitle options for soft subtitles
    if soft_subtitle:
        common_options["c:s"] = "mov_text"
        common_options["s:s:0"] = f"language={subtitle_language}"
        common_options["metadata:s:s:0"] = (
            f"title={os.path.basename(subtitle_file).replace('.srt', '')}"
        )

    # Font path for Chinese characters
    if font_path:
        subtitle_filter = (
            f"subtitles='{subtitle_file}:force_style='FontName={font_path}''"
        )
    else:
        subtitle_filter = f"subtitles='{subtitle_file}'"

    # Apply ffmpeg command based on subtitle type
    if soft_subtitle:
        ffmpeg.input(input_video).output(
            output_video, **common_options, vf=subtitle_filter
        ).run(overwrite_output=True)
    else:
        ffmpeg.input(input_video).output(
            output_video, **common_options, vf=subtitle_filter
        ).run(overwrite_output=True)
