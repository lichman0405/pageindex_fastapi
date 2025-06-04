# The code is to deal with data structure utilities, specifically for handling JSON data and converting it to a dictionary.
# Author: Shibo Li
# Date: 2025-05-30
# Version: 0.1.0

import copy
from app.utils.pdf_utils import get_text_of_pdf_pages, get_text_of_pdf_pages_with_labels
from app.utils.text_utils import sanitize_filename, count_tokens


def write_node_id(data, node_id=0):
    """
    Recursively write node IDs to a data structure.
    Args:
        data (dict or list): The data structure to write node IDs to.
        node_id (int): The current node ID to assign.
    Returns:
        int: The next available node ID after writing.
    """
    if isinstance(data, dict):
        data['node_id'] = str(node_id).zfill(4)
        node_id += 1
        for key in list(data.keys()):
            if 'nodes' in key:
                node_id = write_node_id(data[key], node_id)
    elif isinstance(data, list):
        for index in range(len(data)):
            node_id = write_node_id(data[index], node_id)
    return node_id


def get_nodes(structure):
    """
    Recursively extract nodes from a data structure.
    Args:
        structure (dict or list): The data structure to extract nodes from.
    Returns:
        list: A list of nodes extracted from the structure.
    """
    if isinstance(structure, dict):
        structure_node = copy.deepcopy(structure)
        structure_node.pop('nodes', None)
        nodes = [structure_node]
        for key in list(structure.keys()):
            if 'nodes' in key:
                nodes.extend(get_nodes(structure[key]) or [])
        return nodes
    elif isinstance(structure, list):
        nodes = []
        for item in structure:
            nodes.extend(get_nodes(item) or [])
        return nodes
    

def structure_to_list(structure):
    """
    Convert a data structure (dict or list) to a flat list of nodes.
    Args:
        structure (dict or list): The data structure to convert.
    Returns:
        list: A flat list of nodes extracted from the structure.
    """
    if isinstance(structure, dict):
        nodes = []
        nodes.append(structure)
        if 'nodes' in structure:
            nodes.extend(structure_to_list(structure['nodes']) or [])
        return nodes
    elif isinstance(structure, list):
        nodes = []
        for item in structure:
            nodes.extend(structure_to_list(item) or [])
        return nodes
    

def get_leaf_nodes(structure):
    """
    Recursively extract leaf nodes from a data structure.
    Args:
        structure (dict or list): The data structure to extract leaf nodes from.
    Returns:
        list: A list of leaf nodes extracted from the structure.
    """
    if isinstance(structure, dict):
        if not structure['nodes']:
            structure_node = copy.deepcopy(structure)
            structure_node.pop('nodes', None)
            return [structure_node]
        else:
            leaf_nodes = []
            for key in list(structure.keys()):
                if 'nodes' in key:
                    leaf_nodes.extend(get_leaf_nodes(structure[key]) or [])
            return leaf_nodes
    elif isinstance(structure, list):
        leaf_nodes = []
        for item in structure:
            leaf_nodes.extend(get_leaf_nodes(item) or [])
        return leaf_nodes
    

def is_leaf_node(data, node_id):
    """
    Check if a node with the given node_id is a leaf node in the data structure.
    Args:
        data (dict or list): The data structure to check.
        node_id (str): The node_id to check for.
    Returns:
        bool: True if the node is a leaf node, False otherwise.
    """
    # Helper function to find the node by its node_id
    def find_node(data, node_id):
        if isinstance(data, dict):
            if data.get('node_id') == node_id:
                return data
            for key in data.keys():
                if 'nodes' in key:
                    result = find_node(data[key], node_id)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = find_node(item, node_id)
                if result:
                    return result
        return None

    # Find the node with the given node_id
    node = find_node(data, node_id)

    # Check if the node is a leaf node
    if node and not node.get('nodes'):
        return True
    return False


def get_last_node(structure):
    return structure[-1]


def list_to_tree(data):
    """
    Convert a flat list of nodes into a hierarchical tree structure.
    Args:
        data (list): A flat list of dictionaries, each representing a node with 'structure', 'title', 'start_index', and 'end_index'.
    Returns:
        list: A hierarchical tree structure represented as a list of dictionaries.
    """
    def get_parent_structure(structure):
        """Helper function to get the parent structure code"""
        if not structure:
            return None
        parts = str(structure).split('.')
        return '.'.join(parts[:-1]) if len(parts) > 1 else None
    
    # First pass: Create nodes and track parent-child relationships
    nodes = {}
    root_nodes = []
    
    for item in data:
        structure = item.get('structure')
        node = {
            'title': item.get('title'),
            'start_index': item.get('start_index'),
            'end_index': item.get('end_index'),
            'nodes': []
        }
        
        nodes[structure] = node
        
        # Find parent
        parent_structure = get_parent_structure(structure)
        
        if parent_structure:
            # Add as child to parent if parent exists
            if parent_structure in nodes:
                nodes[parent_structure]['nodes'].append(node)
            else:
                root_nodes.append(node)
        else:
            # No parent, this is a root node
            root_nodes.append(node)
    
    # Helper function to clean empty children arrays
    def clean_node(node):
        if not node['nodes']:
            del node['nodes']
        else:
            for child in node['nodes']:
                clean_node(child)
        return node
    
    # Clean and return the tree
    return [clean_node(node) for node in root_nodes]


def add_preface_if_needed(data):
    """
    Add a preface node if the first node has a physical index greater than 1.
    Args:
        data (list): A list of dictionaries representing nodes.
    Returns:
        list: The modified list with a preface node added if needed.
    """
    if not isinstance(data, list) or not data:
        return data

    if data[0]['physical_index'] is not None and data[0]['physical_index'] > 1:
        preface_node = {
            "structure": "0",
            "title": "Preface",
            "physical_index": 1,
        }
        data.insert(0, preface_node)
    return data


def post_processing(structure, end_physical_index):
    """
    Post-process the structure to add start and end indices for each node.
    Args:
        structure (list): A list of dictionaries representing nodes.
        end_physical_index (int): The end physical index to set for the last node.
    Returns:
        list: The modified structure with start and end indices added.
    """
    for i, item in enumerate(structure):
        item['start_index'] = item.get('physical_index')
        if i < len(structure) - 1:
            if structure[i + 1].get('appear_start') == 'yes':
                item['end_index'] = structure[i + 1]['physical_index']-1
            else:
                item['end_index'] = structure[i + 1]['physical_index']
        else:
            item['end_index'] = end_physical_index
    tree = list_to_tree(structure)
    if len(tree)!=0:
        return tree
    else:
        ### remove appear_start 
        for node in structure:
            node.pop('appear_start', None)
            node.pop('physical_index', None)
        return structure
    

def clean_structure_post(data):
    """
    Clean the data structure by removing pagination information and empty nodes.
    Args:
        data (dict or list): The data structure to clean.
    Returns:
        dict or list: The cleaned data structure.
    """
    if isinstance(data, dict):
        data.pop('page_number', None)
        data.pop('start_index', None)
        data.pop('end_index', None)
        if 'nodes' in data:
            clean_structure_post(data['nodes'])
    elif isinstance(data, list):
        for section in data:
            clean_structure_post(section)
    return data


def remove_structure_text(data):
    """
    Recursively remove 'text' fields from the data structure.
    Args:
        data (dict or list): The data structure to process.
    Returns:
        dict or list: The data structure with 'text' fields removed.
    """
    if isinstance(data, dict):
        data.pop('text', None)
        if 'nodes' in data:
            remove_structure_text(data['nodes'])
    elif isinstance(data, list):
        for item in data:
            remove_structure_text(item)
    return data


def add_node_text(node, pdf_pages):
    """
    Recursively add text to nodes based on their start and end indices.
    Args:
        node (dict or list): The node or list of nodes to process.
        pdf_pages (list): List of tuples containing page text and token length.
    Returns:
        None: The function modifies the node in place.
    """
    if isinstance(node, dict):
        start_page = node.get('start_index')
        end_page = node.get('end_index')
        node['text'] = get_text_of_pdf_pages(pdf_pages, start_page, end_page)
        if 'nodes' in node:
            add_node_text(node['nodes'], pdf_pages)
    elif isinstance(node, list):
        for index in range(len(node)):
            add_node_text(node[index], pdf_pages)
    return


def add_node_text_with_labels(node, pdf_pages):
    """
    Recursively add text to nodes with labels based on their start and end indices.
    Args:
        node (dict or list): The node or list of nodes to process.
        pdf_pages (list): List of tuples containing page text and token length.
    Returns:
        None: The function modifies the node in place.
    """
    if isinstance(node, dict):
        start_page = node.get('start_index')
        end_page = node.get('end_index')
        node['text'] = get_text_of_pdf_pages_with_labels(pdf_pages, start_page, end_page)
        if 'nodes' in node:
            add_node_text_with_labels(node['nodes'], pdf_pages)
    elif isinstance(node, list):
        for index in range(len(node)):
            add_node_text_with_labels(node[index], pdf_pages)
    return


def check_token_limit(structure, limit=110000):
    list = structure_to_list(structure)
    for node in list:
        num_tokens = count_tokens(node['text'])
        if num_tokens > limit:
            print(f"Node ID: {node['node_id']} has {num_tokens} tokens")
            print("Start Index:", node['start_index'])
            print("End Index:", node['end_index'])
            print("Title:", node['title'])
            print("\n")