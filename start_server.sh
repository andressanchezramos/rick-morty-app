#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Start Redis and PostgreSQL using Docker Compose
docker-compose up -d

# Run the FastAPI server
uvicorn api.api:app --reload
