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
CMD test_runs/test_1/run_100.sh