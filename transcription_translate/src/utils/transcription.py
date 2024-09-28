import os
import subprocess

from translate import Translator
from whisper import load_model

from .decorators import log
from .srt_validation import write_srt

# Load the Whisper model
model = load_model("small", device="cpu")
from transformers import MarianMTModel, MarianTokenizer


@log
def translate_srt_file(srt_file_path, source_language, target_language):
    """
    Reads an SRT file, translates the subtitle text to the target language using Hugging Face MarianMT,
    and saves it as a new SRT file.

    :param srt_file_path: Path to the original SRT file.
    :param source_language: The language code of the source language (e.g., 'en' for English).
    :param target_language: The language code to translate the subtitles into (e.g., 'fr' for French).
    :return: Path to the translated SRT file.
    """
    # Define the translation model name based on source and target languages
    model_name = f"Helsinki-NLP/opus-mt-{source_language}-{target_language}"

    # Load the MarianMT model and tokenizer
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)

    # Prepare paths for saving the translated SRT file
    translated_srt_path = srt_file_path.replace(".srt", f"_{target_language}.srt")

    with open(srt_file_path, "r", encoding="utf-8") as srt_file, open(
        translated_srt_path, "w", encoding="utf-8"
    ) as translated_file:

        # Iterate through each line in the SRT file
        for line in srt_file:
            # Check if the line is subtitle text (not a number or timestamp)
            if line.strip().isdigit() or "-->" in line:
                translated_file.write(line)
            else:
                # Clean the subtitle text before translation
                cleaned_text = clean_and_filter_text(line.strip())
                if (
                    cleaned_text
                ):  # Only translate if there's something left after cleaning
                    # Translate the cleaned subtitle text using the MarianMT model
                    translated_text = translate_text(cleaned_text, model, tokenizer)
                    translated_file.write(translated_text + "\n")
                else:
                    # Write an empty line if the cleaned text is empty
                    translated_file.write("\n")
    return translated_srt_path


def translate_text(text, model, tokenizer):
    """
    Translate text using a Hugging Face MarianMT model.

    :param text: The text to translate.
    :param model: The MarianMT model object.
    :param tokenizer: The tokenizer object for the MarianMT model.
    :return: Translated text.
    """
    # Tokenize and prepare the input text for the model
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    # Generate translation
    translated_tokens = model.generate(**inputs)
    # Decode the generated tokens to get the translated text
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    print("translated_text", translated_text)
    return translated_text


import re


def clean_and_filter_text(text):
    """
    Cleans and filters subtitle text to remove unwanted content.

    :param text: The text to be cleaned and filtered.
    :return: Cleaned and filtered text.
    """
    # Remove promotional or unwanted lines (e.g., "Downloaded from YTS.MX")
    unwanted_patterns = [
        r"Downloaded from",  # Matches lines starting with "Downloaded from"
        r"YTS\.MX",  # Matches "YTS.MX"
        r"Official YIFY movies site",  # Matches "Official YIFY movies site"
    ]

    # Join all unwanted patterns into a single regex pattern
    combined_pattern = "|".join(unwanted_patterns)

    # Remove any lines that match unwanted patterns
    if re.search(combined_pattern, text, re.IGNORECASE):
        return ""

    # Remove extra whitespace
    cleaned_text = re.sub(r"\s+", " ", text).strip()
    return cleaned_text


import re


def remove_duplicate_comma_words(text):
    """
    Removes duplicate words in a string separated by commas.

    :param text: The input text string.
    :return: A string with duplicate comma-separated words removed.
    """
    words = text.split(",")
    seen = set()
    result = []
    for word in words:
        word = word.strip()
        if word not in seen:
            seen.add(word)
            result.append(word)
    return ", ".join(result)


def clean_text(text):
    """
    Cleans the text by:
    1. Removing patterns like {\cH00C1E5EC}.
    2. Removing excessively long strings of repeated punctuation.
    3. Removing duplicate words separated by commas.
    4. Removing excessive repeated words.

    :param text: The input text string.
    :return: Cleaned text.
    """
    # Remove patterns like {\cH00C1E5EC}
    text = re.sub(r"{\\.*?}", "", text)

    # Remove excessively long strings of punctuation (like multiple periods)
    text = re.sub(r"(\.{3,})", "...", text)
    text = re.sub(r"([!?,;])\1{2,}", r"\1", text)

    # Remove duplicate words separated by commas
    text = remove_duplicate_comma_words(text)

    # Remove excessively repeated words (like cục cục cục)
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)

    return text


def clean_srt_file(srt_file_path):
    """
    Reads an SRT file, cleans each subtitle line by removing unnecessary patterns, duplicate words,
    and excessive punctuation, and saves it as a new SRT file.

    :param srt_file_path: Path to the original SRT file.
    :return: Path to the cleaned SRT file.
    """
    # Prepare paths for saving the cleaned SRT file
    cleaned_srt_path = srt_file_path.replace(".srt", "_cleaned.srt")

    with open(srt_file_path, "r", encoding="utf-8") as srt_file, open(
        cleaned_srt_path, "w", encoding="utf-8"
    ) as cleaned_file:

        # Iterate through each line in the SRT file
        for line in srt_file:
            # Check if the line is subtitle text (not a number or timestamp)
            if line.strip().isdigit() or "-->" in line:
                cleaned_file.write(line)
            else:
                # Clean the subtitle text
                cleaned_text = clean_text(line.strip())
                if cleaned_text:  # Write the cleaned text if it's not empty
                    cleaned_file.write(cleaned_text + "\n")
                else:
                    cleaned_file.write("\n")

    return cleaned_srt_path


def video_to_audio(video_file, output_ext="mp3"):
    filename, ext = os.path.splitext(video_file)
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return f"{filename}.{output_ext}"
