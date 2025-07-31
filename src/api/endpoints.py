from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from src.logic.excutions import save_uploaded_file, execute_generated_code
from src.logic.llm_ops import generate_code, generate_final_answer
from src.api.schemas import UploadResponse, AnswerRequest, AnswerResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV file and return a unique file ID"""
    logger.info(f"Upload request received for file: {file.filename}")

    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400, detail="Only CSV files are allowed")

        # Save uploaded file and get ID
        file_id = await save_uploaded_file(file)

        logger.info(f"File uploaded successfully with ID: {file_id}")
        return UploadResponse(
            file_id=file_id,
            message="File uploaded successfully"
        )

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=AnswerResponse)
async def answer_question(request: AnswerRequest):
    """Generate answer for a question based on uploaded file ID"""
    logger.info(
        f"Answer request received for file ID: {request.file_id}, question: '{request.question}'")

    try:
        # Generate pandas code using LLM
        generated_code = await generate_code(request.question, request.file_id)

        # Execute the generated code
        result = execute_generated_code(generated_code, request.file_id)

        # Generate final answer using LLM
        final_answer = await generate_final_answer(request.question, generated_code, str(result))

        logger.info("Answer generated successfully")
        return AnswerResponse(answer=final_answer)

    except FileNotFoundError:
        logger.error(f"File not found for ID: {request.file_id}")
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        error_message = str(e)
        logger.error(f"Answer generation error: {error_message}")

        # Check if it's an internal error (code generation/execution issue)
        if "Internal error:" in error_message:
            raise HTTPException(
                status_code=500, detail="Internal error: Unable to process your request. Please try rephrasing your question.")
        else:
            raise HTTPException(
                status_code=500, detail=f"Error: {error_message}")
