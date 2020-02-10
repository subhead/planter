FROM python:3.6.9-alpine

RUN apk update \
    && apk add \
    build-base \
    postgresql-dev \
    gcc \
    vim \
    python-dev \
    musl-dev \
    libpq

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 1
ENV APP_STAGE dev

COPY . .