FROM python:3.13-alpine

LABEL org.opencontainers.image.source=https://github.com/marco-bolo/csv-to-json-ld
LABEL org.opencontainers.image.description="Tools to help in the MARCO-BOLO csv-to-jsonld pipeline"
LABEL org.opencontainers.image.licenses=CC0-1.0


# Install bash, jq and jsonld-cli to support more general build functionality in the top-level Makefile.
RUN apk update && apk add bash jq npm
RUN npm install -g jsonld-cli

RUN pip install poetry

RUN mkdir -p /scripts

COPY ./ /scripts

WORKDIR /scripts

RUN poetry install
RUN poetry run pytest

RUN pip install .