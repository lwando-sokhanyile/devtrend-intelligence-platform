#!/bin/bash
# DevTrend Intelligence Platform - Linux/Mac Setup Script
echo "Setting up DevTrend Intelligence Platform..."

# Copy env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please fill in your credentials."
fi

# Start PostgreSQL
docker-compose up -d postgres
sleep 10

echo "Setup complete."