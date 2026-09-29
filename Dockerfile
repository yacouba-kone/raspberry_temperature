FROM python:3.14-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./

COPY src ./src

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "python", "consumer/consumer.py"]