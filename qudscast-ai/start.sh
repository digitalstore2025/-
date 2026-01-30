#!/bin/bash
# QudsCast AI - Start Script for Replit

echo "========================================"
echo "  QudsCast AI - Starting..."
echo "========================================"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check if frontend is built
if [ ! -d "frontend/.next" ]; then
    echo "Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Start the application
echo "Starting QudsCast AI..."
npm run start
