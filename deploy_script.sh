#!/bin/bash

# Change to the microservice directory
cd schedules_microservice

# Pull the latest code from the GitHub repository
git pull origin main

# Install Python dependencies
pip install -r requirements.txt

# Run the microservice
python3 main.py
