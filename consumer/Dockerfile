# Consumer Dockerfile
FROM python:3.11-slim

WORKDIR /app
# Install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "consumer.py"]
