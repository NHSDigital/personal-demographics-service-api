FROM python:3.8.2-slim

# Maintainers
LABEL maintainer="Personal Demographics Team"

RUN apt-get update && apt-get install make && apt-get install curl -y && apt-get install unzip -y
RUN pip install poetry

# Create working directory
RUN mkdir -p /tests/

# Set up test environment
COPY . /tests/

WORKDIR /tests/
