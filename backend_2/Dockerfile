# Use LangChain's optimized image as base
FROM langchain/langchain:latest

# Install FastAPI and database dependencies
COPY requirements.prod.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir uv
RUN uv pip install --system --no-cache-dir -r requirements.prod.txt

# Set up app
WORKDIR /app
COPY app/ app/

# Create necessary directories
RUN mkdir -p logs data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]