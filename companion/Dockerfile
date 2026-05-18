FROM python:3.11-slim

WORKDIR /app

# Install audio dependencies for STT/TTS (optional, based on hardware)
RUN apt-get update && apt-get install -y \
    libasound2-dev \
    libportaudio2 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9004

CMD ["python", "main.py"]
