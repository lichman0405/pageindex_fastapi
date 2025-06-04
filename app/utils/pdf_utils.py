# The code is dealing with PDF utilities, specifically for extracting the PDF name from a file path.
# Author: Shibo Li
# Date: 2025-05-30
# Version: 0.1.0

import PyPDF2
import pymupdf
from io import BytesIO
import os
import tiktoken
import re
from dotenv import load_dotenv
from pathlib import Path
from app.utils.text_utils import sanitize_filename
load_dotenv()

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
MODEL = os.getenv("DEEPSEEK_MODEL")


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    Args:
        pdf_path (str): Path to the PDF file.   
    Returns:
        str: Extracted text from the PDF.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    ###return text not list 
    text=""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text+=page.extract_text()
    return text


def get_pdf_title(pdf_path):
    """
    Get the title of a PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Title of the PDF file, or 'Untitled' if no title is found.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    meta = pdf_reader.metadata
    title = meta.title if meta and meta.title else 'Untitled'
    return title


def get_text_of_pages(pdf_path, start_page, end_page, tag=True):
    """
    Extract text from specific pages of a PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
        start_page (int): Starting page number (1-indexed).
        end_page (int): Ending page number (1-indexed).
        tag (bool): Whether to include start and end tags for each page.
    Returns:
        str: Extracted text from the specified pages, with optional tags.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page_num in range(start_page-1, end_page):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        if tag:
            text += f"<start_index_{page_num+1}>\n{page_text}\n<end_index_{page_num+1}>\n"
        else:
            text += page_text
    return text


def get_pdf_name(pdf_path):
    """
    Extract the name of a PDF file from its path or metadata.
    Args:
        pdf_path (str or BytesIO): Path to the PDF file or a BytesIO object.
    Returns:
        str: Name of the PDF file, sanitized to remove invalid characters.
    """
    # Extract PDF name
    if isinstance(pdf_path, str):
        pdf_name = os.path.basename(pdf_path)
    elif isinstance(pdf_path, BytesIO):
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        meta = pdf_reader.metadata
        pdf_name = meta.title if meta and meta.title else 'Untitled'
        pdf_name = sanitize_filename(pdf_name)
    return pdf_name


def get_page_tokens(pdf_path, model=None, pdf_parser="PyPDF2"):
    enc = tiktoken.get_encoding("o200k_base")
    if pdf_parser == "PyPDF2":
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        page_list = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            token_length = len(enc.encode(page_text))
            page_list.append((page_text, token_length))
        return page_list
    elif pdf_parser == "PyMuPDF":
        if isinstance(pdf_path, BytesIO):
            pdf_stream = pdf_path
            doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
        elif isinstance(pdf_path, str) and os.path.isfile(pdf_path) and pdf_path.lower().endswith(".pdf"):
            doc = pymupdf.open(pdf_path)
        page_list = []
        for page in doc:
            page_text = page.get_text()
            token_length = len(enc.encode(page_text))
            page_list.append((page_text, token_length))
        return page_list
    else:
        raise ValueError(f"Unsupported PDF parser: {pdf_parser}")
    

def get_text_of_pdf_pages(pdf_pages, start_page, end_page):
    """
    Extract text from a list of PDF pages.
    Args:
        pdf_pages (list): List of tuples containing page text and token length.
        start_page (int): Starting page number (1-indexed).
        end_page (int): Ending page number (1-indexed).
    Returns:
        str: Extracted text from the specified pages.
    """
    text = ""
    for page_num in range(start_page-1, end_page):
        text += pdf_pages[page_num][0]
    return text


def get_text_of_pdf_pages_with_labels(pdf_pages, start_page, end_page):
    """
    Extract text from a list of PDF pages with labels.
    Args:
        pdf_pages (list): List of tuples containing page text and token length.
        start_page (int): Starting page number (1-indexed).
        end_page (int): Ending page number (1-indexed).
    Returns:
        str: Extracted text from the specified pages with labels.
    """
    text = ""
    for page_num in range(start_page-1, end_page):
        text += f"<physical_index_{page_num+1}>\n{pdf_pages[page_num][0]}\n<physical_index_{page_num+1}>\n"
    return text


def get_number_of_pages(pdf_path):
    """
    Get the number of pages in a PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        int: Number of pages in the PDF file.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    num = len(pdf_reader.pages)
    return num


def get_first_start_page_from_text(text):
    """
    Extract the first start page number from a text string.
    Args:
        text (str): Text containing start page markers.
    Returns:
        int: The first start page number found in the text, or -1 if not found.
    """
    start_page = -1
    start_page_match = re.search(r'<start_index_(\d+)>', text)
    if start_page_match:
        start_page = int(start_page_match.group(1))
    return start_page


def get_last_start_page_from_text(text):
    """
    Extract the last start page number from a text string.
    Args:
        text (str): Text containing start page markers.
    Returns:
        int: The last start page number found in the text, or -1 if not found.
    """
    start_page = -1
    # Find all matches of start_index tags
    start_page_matches = re.finditer(r'<start_index_(\d+)>', text)
    # Convert iterator to list and get the last match if any exist
    matches_list = list(start_page_matches)
    if matches_list:
        start_page = int(matches_list[-1].group(1))
    return start_page