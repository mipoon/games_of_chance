FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
ENV DEVCONTAINER=true

# Set the working directory
WORKDIR /app

# Copy requirements.txt to the docker image and install packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .
