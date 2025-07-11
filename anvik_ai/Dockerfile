FROM python:3.10-slim

# Install LaTeX (texlive) and dependencies
RUN apt-get update && apt-get install -y \
    texlive-full \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for FastAPI and Gradio
EXPOSE 8000 7860

# Run both FastAPI and Gradio
CMD ["bash", "-c", "uvicorn src.backend.api:app --host 0.0.0.0 --port 8000 & python src/backend/interface.py"]