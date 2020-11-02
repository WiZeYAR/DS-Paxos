FROM python:3.7-alpine

# Create work directory
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
RUN apk add --no-cache bash

# copy the content of the local src directory to the working directory
COPY . .

# command to run on container start
ENTRYPOINT ./Docker_entrypoints/docker-entrypoint.sh

# ENTRYPOINT ./Docker_entrypoints/docker-entrypoint_catchup.sh
