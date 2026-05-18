FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for collectors
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9001

CMD ["python", "main.py"]
