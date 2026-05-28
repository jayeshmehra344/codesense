FROM python:3.11-slim

WORKDIR /app

# torch CPU wheel is ~200 MB — install first so this layer is cached
# across rebuilds that only change application code.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Remaining inference deps (torch-geometric, fastapi, uvicorn, pydantic)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Application code + trained model (model.pt is 42 KB — committed to repo)
COPY src/ ./src/
COPY data/model.pt ./data/model.pt

EXPOSE 8000

# Single worker: model is loaded once into RAM; multiple workers would each
# reload model.pt and add no throughput on CPU inference.
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
