"""
File Utilities Module

A collection of reusable file operations for common tasks.
Includes file creation, reading, writing, and management functions.
"""

import os
import json
import datetime
from typing import List, Dict, Any, Union


def create_file(filename: str, content: str = "") -> bool:
    """
    Create a new file with optional content.

    Args:
        filename (str): Name or path of the file to create.
        content (str): Optional content to write to the file.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"File created: {filename}")
        return True

    except Exception as e:
        print(f"Error creating file '{filename}': {e}")
        return False


def read_file(filename: str) -> Union[str, None]:
    """
    Read the entire content of a file.

    Args:
        filename (str): Name or path of the file to read.

    Returns:
        str: File content, or None if error.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return None


def append_to_file(filename: str, content: str) -> bool:
    """
    Append content to an existing file.

    Args:
        filename (str): Name or path of the file.
        content (str): Content to append.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(content + '\n')

        print(f"Content appended to: {filename}")
        return True
    except Exception as e:
        print(f"Error appending to file '{filename}': {e}")
        return False


def read_json_file(filename: str) -> Union[Dict[Any, Any], List[Any], None]:
    """
    Read and parse a JSON file.

    Args:
        filename (str): Name or path of the JSON file.

    Returns:
        dict or list: Parsed JSON data, or None if error.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"JSON file not found: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in file '{filename}': {e}")
        return None
    except Exception as e:
        print(f"Error reading JSON file '{filename}': {e}")
        return None


def write_json_file(filename: str, data: Union[Dict[Any, Any], List[Any]]) -> bool:
    """
    Write data to a JSON file with proper formatting.

    Args:
        filename (str): Name or path of the JSON file.
        data (dict or list): Data to write as JSON.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        print(f"JSON data written to: {filename}")
        return True

    except Exception as e:
        print(f"Error writing JSON file '{filename}': {e}")
        return False


def get_file_info(filename: str) -> Dict[str, Any]:
    """
    Get detailed information about a file.

    Args:
        filename (str): Name or path of the file.

    Returns:
        dict: File information including size, modification time, etc.
    """
    try:
        if not os.path.exists(filename):
            return {"error": "File does not exist"}

        stat_info = os.stat(filename)
        return {
            "filename": filename,
            "size_bytes": stat_info.st_size,
            "size_kb": round(stat_info.st_size / 1024, 2),
            "size_mb": round(stat_info.st_size / (1024 * 1024), 4),
            "created": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "is_file": os.path.isfile(filename),
            "is_directory": os.path.isdir(filename),
            "absolute_path": os.path.abspath(filename)
        }

    except Exception as e:
        return {"error": f"Could not get file info for '{filename}': {e}"}


def list_directory_contents(directory: str = ".") -> List[Dict[str, Any]]:
    """
    List all files and directories in a given directory.

    Args:
        directory (str): Directory path (defaults to current directory).

    Returns:
        list: List of dictionaries with file or directory info.
    """
    try:
        if not os.path.exists(directory):
            return [{"error": f"Directory '{directory}' does not exist"}]

        contents = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            item_info = {
                "name": item,
                "is_file": os.path.isfile(item_path),
                "is_directory": os.path.isdir(item_path),
                "path": item_path
            }

            if item_info["is_file"]:
                item_info["size_bytes"] = os.path.getsize(item_path)

            contents.append(item_info)

        return contents

    except Exception as e:
        return [{"error": f"Could not list directory '{directory}': {e}"}]


def create_sample_files() -> None:
    """
    Create sample files to demonstrate file operations.
    """
    sample_data = {
        "sample_data/example.txt": (
            "This is a sample text file.\n"
            "Created by the file_utils module.\n"
        ),
        "sample_data/data.json": {
            "project": "Utility Toolkit",
            "author": "Developer",
            "created": datetime.datetime.now().isoformat(),
            "languages": ["Python", "JavaScript", "TypeScript"],
            "stats": {"files_created": 5, "modules": 2}
        },
        "sample_data/notes.md": (
            "# Sample Notes\n\n"
            "This is a markdown file created by the utility toolkit.\n\n"
            "## Features\n"
            "- File operations\n"
            "- JSON handling\n"
            "- Directory listing"
        )
    }

    print("Creating sample files...")
    for filename, content in sample_data.items():
        if filename.endswith('.json'):
            write_json_file(filename, content)
        else:
            create_file(filename, content if isinstance(
                content, str) else str(content))

    print("Sample files created successfully in 'sample_data/' directory.")


if __name__ == "__main__":
    create_sample_files()
