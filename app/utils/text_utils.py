# The code is to deal with text and token utilities, specifically for handling text processing and tokenization.
# Author: Shibo Li
# Date: 2025-05-30
# Version: 0.1.0


import os
import tiktoken
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
MODEL = os.getenv("DEEPSEEK_MODEL")


def count_tokens(text, model=None):
    """
    Count the number of tokens in a given text using the specified model's tokenizer.
    Args:
        text (str): The input text to tokenize.
        model (str): The model name to use for tokenization. Defaults to the value from environment variable.
    Returns:
        int: The number of tokens in the input text.
    """
    enc = tiktoken.get_encoding("o200k_base")
    tokens = enc.encode(text)
    return len(tokens)


def sanitize_filename(filename, replacement='-'):
    # In Linux, only '/' and '\0' (null) are invalid in filenames.
    # Null can't be represented in strings, so we only handle '/'.
    return filename.replace('/', replacement)
