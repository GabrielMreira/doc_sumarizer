FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download pt_core_news_sm
COPY ../.. .
CMD ["python", "worker.py"]