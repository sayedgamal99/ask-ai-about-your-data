FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV API_BASE_URL=http://localhost:5599
ENV API_HOST=0.0.0.0
ENV API_PORT=5599

EXPOSE 9999
EXPOSE 5599

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 5599 & python -m http.server 9999 --directory src/frontend"]

