import pandas as pd
import os
import uuid
import logging
import sys
import io
from contextlib import redirect_stdout
from fastapi import UploadFile
from typing import Any
from src.configs.config import Settings

logger = logging.getLogger(__name__)


async def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded CSV file and return unique file ID"""
    logger.info(f"Uploading file: {file.filename}")

    # Create assets directory if it doesn't exist
    os.makedirs(Settings.ASSETS_DIR, exist_ok=True)

    # Generate unique file ID (16 characters)
    file_id = str(uuid.uuid4()).replace('-', '')[:16]
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(Settings.ASSETS_DIR, f"{file_id}{file_extension}")

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"File saved successfully with ID: {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise


def get_file_path_by_id(file_id: str) -> str:
    """Get file path by file ID"""
    # Look for file with the given ID (with any extension)
    for filename in os.listdir(Settings.ASSETS_DIR):
        if filename.startswith(file_id):
            return os.path.join(Settings.ASSETS_DIR, filename)

    raise FileNotFoundError(f"File with ID {file_id} not found")


def execute_generated_code(code: str, file_id: str) -> Any:
    """Execute the generated code with full Python access (educational use only)"""
    logger.info(f"Executing code for file ID: {file_id}")

    try:
        # Get file path from ID
        file_path = get_file_path_by_id(file_id)
        logger.info(f"Found file path: {file_path}")

        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)
        logger.info(f"Loaded DataFrame with shape: {df.shape}")

        # Create file-specific plots directory if it doesn't exist
        plots_dir = os.path.join(Settings.ASSETS_DIR, "plots", file_id)
        os.makedirs(plots_dir, exist_ok=True)
        logger.info(f"File-specific plots directory ensured: {plots_dir}")


        # Create execution environment with full access
        local_vars = {"df": df, "plots_dir": plots_dir}

        # Capture print output
        output_buffer = io.StringIO()

        # Execute with full Python capabilities and capture prints
        with redirect_stdout(output_buffer):
            exec(code, globals(), local_vars)

        # Get the captured output
        captured_output = output_buffer.getvalue().strip()

        if captured_output:
            logger.info(
                f"Code executed successfully, captured output length: {len(captured_output)}")
            return captured_output
        else:
            logger.info("Code executed successfully, no output captured")
            return "Code executed successfully, but no output was generated"

    except SyntaxError as e:
        error_msg = f"Invalid Python syntax in generated code: {str(e)}"
        logger.error(error_msg)
        raise Exception("Internal error: Generated code has invalid syntax")
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        logger.error(error_msg)
        raise Exception(f"Internal error: Code execution failed - {str(e)}")
