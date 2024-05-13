# Pull base image
FROM python:3.12

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install netcat-traditional

# Set work directory
# Maine folder will be create with such name in docker container
WORKDIR /web_frm

# Install dependencies
RUN pip3 install --upgrade pip
COPY /requirements.txt .
RUN pip3 install -r requirements.txt

# Copy project
COPY ../.. .
