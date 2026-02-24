FROM python:3.9-slim

WORKDIR /app

# সিস্টেম ডিপেন্ডেন্সি ইনস্টল (ffmpeg whisper-এর জন্য জরুরি)
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# পাইথন লাইব্রেরি ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# কোড কপি
COPY . .

# FastAPI রান করার জন্য Uvicorn ব্যবহার করা
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]