FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    lilypond \
    fluidsynth \
    fluid-soundfont-gm \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @eldment/meting-agent 2>/dev/null || true

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e . && pip install --no-cache-dir uvicorn

RUN mkdir -p build/workflows build/output

EXPOSE 8000

CMD ["uvicorn", "music_creation_engine.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
