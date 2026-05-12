FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend files
COPY . .

# Ingest the knowledge base to build the ChromaDB vector database inside the image
RUN python ingest.py

# Expose the FastAPI default port
EXPOSE 8000

# Start FastAPI using uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
