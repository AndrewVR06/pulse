# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

ENV POETRY_VERSION=1.8.4
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Create a virtual env for poetry to operate in
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add poetry to path
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Python won't try to write .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that the python output is sent straight to terminal (container log)
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /backend

COPY poetry.lock pyproject.toml .
RUN poetry install --without dev

COPY src /backend

ENV PYTHONPATH="/backend"

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Run Django migrations and then start the Django app
CMD ["poetry", "run", "fastapi", "run", "src/main.py", "--port", "8080"]
