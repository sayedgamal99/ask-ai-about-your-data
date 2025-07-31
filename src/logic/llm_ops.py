import requests
import json
import pandas as pd
import re
import logging
from src.configs.config import Settings
from src.configs.prompts import get_code_generation_prompt, get_answer_generation_prompt
from src.logic.excutions import get_file_path_by_id

logger = logging.getLogger(__name__)


def extract_python_code_simple(text: str) -> str:
    """
    Simple extraction of Python code from ```python ``` blocks.
    """
    # Simple pattern to match ```python ... ```
    pattern = r'```python\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        code = match.group(1).strip()
        logger.info(f"Code extracted: {repr(code[:50])}...")
        return code
    else:
        # Fallback: return the original text if no pattern found
        logger.warning("No ```python``` block found, returning original text")
        return text.strip()


async def generate_code(question: str, file_id: str) -> str:
    """Generate pandas code based on the user's question"""
    logger.info(
        f"Generating code for question: '{question}' with file ID: {file_id}")

    try:
        # Get file path from ID
        file_path = get_file_path_by_id(file_id)

        # Read first few rows to understand data structure
        df = pd.read_csv(file_path)
        sample_data = df.head().to_string()
        columns = list(df.columns)

        logger.info(
            f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

        prompts = get_code_generation_prompt(question, columns, sample_data)

        # Log the complete prompt being sent
        logger.info("=== SYSTEM PROMPT ===")
        logger.info(prompts["system"])
        logger.info("=== USER PROMPT ===")
        logger.info(prompts["user"])
        logger.info("=== END PROMPTS ===")

        response = requests.post(
            Settings.get_ollama_url(),
            json={
                "model": Settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                "stream": False
            }
        )

        if response.status_code == 200:
            response_json = response.json()
            raw_response = response_json["message"]["content"].strip()

            logger.info(
                f"Raw LLM response (length): {len(raw_response)}, content: {raw_response[:100]}...")

            # Extract Python code from the response
            generated_code = extract_python_code_simple(raw_response)
            logger.info(
                f"Code extracted successfully: {generated_code[:100]}...")
            return generated_code
        else:
            error_msg = f"Failed to generate code: {response.text}"
            logger.error(error_msg)
            raise Exception(
                f"Internal error: LLM service failed - {error_msg}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in code generation: {str(e)}")
        raise Exception(f"Internal error: Cannot connect to LLM service")
    except Exception as e:
        if "Internal error:" in str(e):
            raise  # Re-raise internal errors as-is
        logger.error(f"Error in code generation: {str(e)}")
        raise Exception(f"Internal error: Code generation failed - {str(e)}")


async def generate_final_answer(question: str, code: str, result: str) -> str:
    """Generate a natural language answer based on the question, code, and result"""
    logger.info("Generating final answer")

    try:
        prompts = get_answer_generation_prompt(question, code, result)

        # Log the complete prompt being sent for final answer
        logger.info("=== FINAL ANSWER SYSTEM PROMPT ===")
        logger.info(prompts["system"])
        logger.info("=== FINAL ANSWER USER PROMPT ===")
        logger.info(prompts["user"])
        logger.info("=== END FINAL ANSWER PROMPTS ===")

        response = requests.post(
            Settings.get_ollama_url(),
            json={
                "model": Settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                "stream": False
            }
        )

        if response.status_code == 200:
            response_json = response.json()
            logger.info(f"LLM response received length: {len(response_json)}")
            final_answer = response_json["message"]["content"].strip()

            logger.info("Final answer generated successfully")

            # Ensure we have a valid answer
            if not final_answer:
                final_answer = "Unable to generate a proper answer for your question."

            return final_answer
        else:
            error_msg = f"Failed to generate answer: {response.text}"
            logger.error(error_msg)
            raise Exception(f"Internal error: Answer generation failed")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in answer generation: {str(e)}")
        raise Exception(f"Internal error: Cannot connect to LLM service")
    except Exception as e:
        if "Internal error:" in str(e):
            raise  # Re-raise internal errors as-is
        logger.error(f"Error in answer generation: {str(e)}")
        raise Exception(f"Internal error: Answer generation failed - {str(e)}")
