FROM python:3.12.0-alpine

USER root

WORKDIR /var/build

# Get the app dependencies in a virtual environment
WORKDIR /app

# Create a virtual environment
COPY ./app /app/app
COPY ./requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN ["pip", "install", "-r", "requirements.txt"]

ENV APP_PORT=8001

# Make port available outside this container
EXPOSE $APP_PORT

CMD ["python", "-m", "app.main"]
