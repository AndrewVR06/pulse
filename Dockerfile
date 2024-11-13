# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

RUN useradd -ms /bin/sh -u 1001 app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

# Set the working directory in the container
WORKDIR /backend

COPY --chown=app:app poetry.lock pyproject.toml ./
RUN poetry install --without dev

COPY --chown=app:app src/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --chown=app:app src /backend

USER app

ENV PYTHONPATH="/backend"

ARG ENV_FILE
COPY ${ENV_FILE} .env

ARG PGSSLROOTCERT
COPY --chown=app:app ${PGSSLROOTCERT} ./server_ca.crt

ARG PGSSLCLIENTCERT
COPY --chown=app:app ${PGSSLCLIENTCERT} ./client_cert.crt

ARG PGSSLCLIENTKEY
COPY --chown=app:app ${PGSSLCLIENTKEY} ./client_key.key

EXPOSE 8080

CMD ["/entrypoint.sh"]
