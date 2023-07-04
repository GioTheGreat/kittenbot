# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster
COPY extra/get-poetry.py ./
RUN python3 get-poetry.py
ENV PATH="/root/.local/bin:$PATH"
ADD pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev
COPY src ./
ADD resources ./resources
CMD ["poetry", "run", "python3", "-m", "kittenbot"]