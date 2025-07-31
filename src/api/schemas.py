from pydantic import BaseModel


class UploadResponse(BaseModel):
    file_id: str
    message: str


class AnswerRequest(BaseModel):
    file_id: str
    question: str


class AnswerResponse(BaseModel):
    answer: str
