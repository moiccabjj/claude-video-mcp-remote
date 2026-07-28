FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY remote-mcp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir yt-dlp

COPY skills /app/skills
COPY remote-mcp/server.py /app/server.py

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /tmp/claude-video \
    && chown -R appuser:appuser /app /tmp/claude-video
USER appuser

EXPOSE 8000
CMD ["python", "/app/server.py"]

