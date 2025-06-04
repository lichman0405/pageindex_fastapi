# The code is to be used interact with LLMs api, not just OpenAI.
# It is designed to be used with OpenAI's API, but can be adapted for other LLM providers.
# It includes functions to create a chat completion, handle errors, and manage API keys.
# Author: Shibo Li
# Date: 2025-05-30
# Version: 0.1.0

import os
import openai
import time
from dotenv import load_dotenv
import asyncio
from pathlib import Path
import logging


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
MODEL = os.getenv("DEEPSEEK_MODEL")


def ChatGPT_API_with_finish_reason(model, prompt, api_key=API_KEY, chat_history=None, base_url=BASE_URL):
    """
    Function to interact with LLM api and return the response along with finish reason.
    Args:
        model (str): The model to use for the API call.
        prompt (str): The prompt to send to the model.
        api_key (str): The API key for authentication. 
        chat_history (list): Optional chat history to include in the request.
        base_url (str): The base URL for the API endpoint.
    Returns:
        tuple: A tuple containing the response text and the finish reason.
    """
    max_retries = 10
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            if response.choices[0].finish_reason == "length":
                return response.choices[0].message.content, "max_output_reached"
            else:
                return response.choices[0].message.content, "finished"

        except Exception as e:
            print('************* Retrying *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(1)  # Wait before retrying
            else:
                logging.error('Max retries reached for prompt: ' + prompt)
                return "Error"
            

def ChatGPT_API(model, prompt, api_key=API_KEY, 
                base_url=BASE_URL, chat_history=None):
    """
    Function to interact with LLM api and return the response.
    Args:
        model (str): The model to use for the API call.
        prompt (str): The prompt to send to the model.
        api_key (str): The API key for authentication. 
        chat_history (list): Optional chat history to include in the request.
        base_url (str): The base URL for the API endpoint.
    Returns:
        str: The response text from the model.
    """
    max_retries = 10
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
   
            return response.choices[0].message.content
        except Exception as e:
            print('************* Retrying *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(1)  # Wait for 1s before retrying
            else:
                logging.error('Max retries reached for prompt: ' + prompt)
                return "Error"
            

async def ChatGPT_API_async(model, prompt, api_key=API_KEY, 
                             base_url=BASE_URL):
    """
    Asynchronous function to interact with LLM api and return the response.
    Args:
        model (str): The model to use for the API call.
        prompt (str): The prompt to send to the model.
        api_key (str): The API key for authentication. 
        base_url (str): The base URL for the API endpoint.
    Returns:
        str: The response text from the model.
    """
    max_retries = 10
    client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
    for i in range(max_retries):
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content
        except Exception as e:
            print('************* Retrying *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(1)  # Wait for 1秒 before retrying
            else:
                logging.error('Max retries reached for prompt: ' + prompt)
                return "Error"  
            

async def generate_node_summary(node, model):
    """
    Asynchronously generate a summary for a given node.
    Args:
        node (dict): A dictionary containing the node data, specifically the 'text' key.
        model (str): The model to use for the API call. If None, defaults to the MODEL environment variable.
    Returns:
        str: The generated summary of the node.
    """
    prompt = f"""You are given a part of a document, your task is to generate a description of the partial document about what are main points covered in the partial document.

    Partial Document Text: {node['text']}
    
    Directly return the description, do not include any other text.
    """
    response = await ChatGPT_API_async(model, prompt)
    return response


async def generate_summaries_for_structure(structure, model=None):
    """
    Asynchronously generate summaries for all nodes in a given structure.
    Args:
        structure (dict): A dictionary representing the structure containing nodes.
        model (str): The model to use for the API call. If None, defaults to the MODEL environment variable.
    Returns:
        dict: The updated structure with summaries added to each node.
    """
    nodes = structure_to_list(structure)
    tasks = [generate_node_summary(node, model=model) for node in nodes]
    summaries = await asyncio.gather(*tasks)
    
    for node, summary in zip(nodes, summaries):
        node['summary'] = summary
    return structure


def generate_doc_description(structure, model=None):
    """
    Generate a one-sentence description for a document based on its structure.
    Args:
        structure (dict): A dictionary representing the structure of the document.
        model (str): The model to use for the API call. If None, defaults to the MODEL environment variable.
    Returns:
        str: The generated description of the document.
    """
    prompt = f"""Your are an expert in generating descriptions for a document.
    You are given a structure of a document. Your task is to generate a one-sentence description for the document, which makes it easy to distinguish the document from other documents.
        
    Document Structure: {structure}
    
    Directly return the description, do not include any other text.
    """
    response = ChatGPT_API(model, prompt)
    return response