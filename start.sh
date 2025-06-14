#!/bin/bash
echo "Starting..."
exec gunicorn --bind 0.0.0.0:$PORT app:app
