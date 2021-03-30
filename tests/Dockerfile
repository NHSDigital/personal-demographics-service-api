FROM python:3.8-slim

# Maintainers
LABEL maintainer="Personal Demographics Team"

RUN apt-get update && apt-get install make && apt-get install curl -y && apt-get install unzip -y

# Create working directory
RUN mkdir -p /tests/

# Set up test environment
COPY "." "/tests/"
RUN pip install --upgrade pip
RUN pip install -r /tests/requirements.txt

WORKDIR "/tests/"

ENV PYTHONPATH=/tests/:

CMD tail -f /dev/null