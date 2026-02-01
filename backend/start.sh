#!/bin/bash
# Render deployment startup script

# Get port from environment variable (Render provides this)
PORT=${PORT:-8000}

# Start uvicorn server
# Bind to 0.0.0.0 to accept connections from outside the container
# Use the PORT environment variable
uvicorn main:app --host 0.0.0.0 --port $PORT
