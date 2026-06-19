# Streamlit demo UI -> Cloud Run (second service, named research-assistant-ui).
# A pure HTTP client of the API service: no GCP creds, no FAISS index, no src/.
FROM python:3.13-slim

WORKDIR /app

# Install deps first for layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code (single file).
COPY app_streamlit.py ./

# Cloud Run injects $PORT (default 8080). Shell-form CMD so $PORT expands at runtime;
# bind 0.0.0.0 (not localhost) and run headless so the container starts cleanly.
ENV PORT=8080
EXPOSE 8080
CMD streamlit run app_streamlit.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
