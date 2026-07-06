FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app/ ./app/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["python", "-m", "app.main"]
