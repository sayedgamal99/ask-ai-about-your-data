# Ask AI About Your Data

A FastAPI application that allows users to upload CSV files and ask questions in natural language. The AI converts questions into executable Python code using pandas and provides intelligent answers.

## Features

- Upload CSV files via REST API
- Ask questions in natural language about your data
- AI-powered data analysis using Ollama (gemma3:4b model)
- Web interface with Streamlit
- Frontend HTML/JavaScript interface
- RESTful API built with FastAPI

## Quick Start

### Using Docker
1. Clone the repository
2. Copy `.env.example` to `.env` and configure if needed
3. Run with Docker:

```bash
docker build -t ask-ai-about-data .
docker run -p 9999:9999 -p 5599:5599 ask-ai-about-data
```

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Start Ollama service locally
3. Run FastAPI server: `uvicorn src.main:app --host 0.0.0.0 --port 5599`
4. Choose one of the UI options:
   - **Streamlit UI**: `streamlit run src/streamlit_app.py` (Access at `http://localhost:8501`)
   - **Frontend UI**: `cd src/frontend && python -m http.server 9999` (Access at `http://localhost:9999`)

## Usage

### Via Frontend Web Interface (HTML/JavaScript)
1. Run `cd src/frontend && python -m http.server 8000`
2. Open `http://localhost:8000` in your web browser


### Via Streamlit Web Interface
1. Open `http://localhost:8501`
2. Upload your CSV file
3. Ask questions in natural language like:
   - "What is the average age?"
   - "Show me the top 5 customers by sales"
   - "How many rows are in this dataset?"

### Via API
1. Upload CSV: `POST /upload`
2. Ask questions: `POST /answer` with file_id and question

## API Endpoints

- `GET /` - API information and status
- `POST /upload` - Upload CSV file, returns file_id
- `POST /answer` - Ask question about uploaded file

## Requirements

- Python 3.8+
- Ollama service with gemma3:4b model
- FastAPI and Streamlit
- pandas for data processing

## Configuration

Environment variables (optional):
- `OLLAMA_BASE_URL` - Ollama service URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - AI model to use (default: gemma3:4b)
- `API_BASE_URL` - FastAPI base URL (default: http://localhost:5599)
- `API_PORT` - API port (default: 5599)