#!/bin/bash

# Let the DB start
sleep 5;

# Run migrations
alembic upgrade head

# Create initial data
python app/initial_data.py

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
