# Ask AI About Your Data

A FastAPI application that allows users to upload CSV files and ask questions in natural language. The AI converts questions into executable Python code using pandas and provides intelligent answers.

## Features

- Upload CSV files
- Ask questions in natural language
- AI-powered data analysis using Ollama
- RESTful API built with FastAPI
- Docker containerization

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure if needed
3. Run with Docker Compose:

```bash
docker-compose up --build
```

4. Access the API at `http://localhost:8000`

## Usage

Upload a CSV file and ask questions like:

- "What is the average age?"
- "Show me the top 5 customers by sales"
- "How many rows are in this dataset?"

## API Endpoints

- `GET /` - Welcome message
- `POST /answer` - Upload CSV and ask a question

## Requirements

- Docker and Docker Compose
- Ollama service (included in docker-compose)

## Development

To run locally without Docker:

1. Install dependencies: `pip install -r requirements.txt`
2. Start Ollama service
3. Run: `uvicorn src.main:app --reload`
