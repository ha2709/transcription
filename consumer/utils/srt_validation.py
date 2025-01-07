from .constants import LANGUAGES, TO_LANGUAGE_CODE
from .timestamp import format_timestamp, parse_timestamp


def write_srt(segments, file):
    counter = 1
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]

        start_formatted = format_timestamp(start_time)
        end_formatted = format_timestamp(end_time)

        file.write(f"{counter}\n")
        file.write(f"{start_formatted} --> {end_formatted}\n")
        file.write(f"{text}\n\n")

        counter += 1


def validate_language(language_input):
    """
    Validate the input language to ensure it is in the allowed languages.

    Args:
        language_input (str): The language code or language name to validate.

    Returns:
        str: The validated language code if valid, else None.
    """
    # Normalize the input (e.g., lowercase, strip whitespace)
    normalized_input = language_input.strip().lower()

    # Check if the input is a valid language code
    if normalized_input in LANGUAGES:
        return normalized_input

    # Check if the input is a valid language name or alias
    if normalized_input in TO_LANGUAGE_CODE:
        return TO_LANGUAGE_CODE[normalized_input]

    # If the input is not valid, return None
    return None


def validate_srt_file(srt_file):
    try:
        with open(srt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 4):
                assert lines[i].strip().isdigit(), "Invalid subtitle sequence number"
                start, end = lines[i + 1].strip().split(" --> ")
                assert format_timestamp(
                    parse_timestamp(start)
                ), "Invalid start timestamp format"
                assert format_timestamp(
                    parse_timestamp(end)
                ), "Invalid end timestamp format"
                assert lines[i + 2].strip(), "Subtitle text missing"
        return True
    except Exception as e:
        print(f"SRT file validation error: {e}")
        return False
