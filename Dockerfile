FROM python:3.9-slim

WORKDIR /app

# Copy requirement and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary files
COPY run.py .
COPY config.yaml .
COPY data.csv .

# Set default command as specified in the PDF required CLI
CMD ["python", "run.py", "--input", "data.csv", "--config", "config.yaml", "--output", "metrics.json", "--log-file", "run.log"]
