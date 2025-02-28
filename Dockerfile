FROM python:3.12.0-alpine

USER root

WORKDIR /app

# Copy source code, requirements.txt and entrypoint.sh
COPY ./app /app/app
COPY ./requirements.txt /app
COPY ./entrypoint.sh /app

# Install any required dependencies
RUN ["pip", "install", "-r", "requirements.txt"]

ENV FALLBACK_PORT=8001

ENTRYPOINT ["entrypoint.sh"]
