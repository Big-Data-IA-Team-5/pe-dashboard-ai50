FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal for ChromaDB)
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install ChromaDB and Google Cloud Storage (required for RAG pipeline with GCS)
RUN pip install --no-cache-dir 'chromadb>=0.4.22' 'google-cloud-storage>=2.10.0'

# Copy application files
COPY src /app/src
COPY data /app/data
COPY PE_Dashboard.md /app/PE_Dashboard.md
COPY PE_Dashboard_Concise.md /app/PE_Dashboard_Concise.md
COPY src/prompts /app/src/prompts

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
