import os

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI


async def process_remove_disclosure(task_data: dict) -> str:

    file_name = task_data[
        "file_path"
    ]  # Ensure this is just the filename, not full path
    full_path = os.path.join("data", file_name)

    # Load the document
    documents = SimpleDirectoryReader("data").load_data(file_name=file_name)
    print("Original documents loaded:", documents)

    # Create a vector index
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    # Craft a strong prompt to identify disclaimer/disclosure sections by start and end strings
    prompt = (
        "Carefully analyze the following document and identify any sections or paragraphs that appear to be legal disclosures or disclaimers. "
        "For each identified section, return the **exact beginning string (first sentence or phrase)** and the **exact ending string (last sentence or phrase)** "
        "that mark the start and end of the disclaimer/disclosure content.\n\n"
        "Return the result using the following JSON format:\n"
        "{\n"
        '  "disclaimer_sections": [\n'
        "    {\n"
        '      "start_string": "This document is for informational purposes only",\n'
        '      "end_string": "You should consult your own advisors before making investment decisions."\n'
        "    },\n"
        "    {\n"
        '      "start_string": "The authors disclaim any liability",\n'
        '      "end_string": "including, without limitation, indirect or consequential loss or damage."\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "If no disclaimer or disclosure is found, return:\n"
        "{\n"
        '  "disclaimer_sections": []\n'
        "}"
    )

    # Query LlamaIndex with your instruction
    response = query_engine.query(prompt)

    # Extract the cleaned content
    cleaned_text = str(response)

    # Optionally write back to a new file
    output_path = full_path.replace(".txt", "_cleaned.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print("Cleaned content written to:", output_path)
    return output_path
