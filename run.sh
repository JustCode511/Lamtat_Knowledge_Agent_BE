#!/bin/bash

# run.sh
# Startup script for Knowledge Agent Backend

echo "🚀 Knowledge Agent Backend - Startup Script"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/installed.flag" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install fastapi uvicorn python-multipart boto3 pyjwt \
                "python-jose[cryptography]" pydantic-settings \
                "passlib[bcrypt]" email-validator
    
    # Create flag file to skip next time
    touch venv/installed.flag
    echo "✅ Dependencies installed!"
else
    echo "✅ Dependencies already installed (skipping)"
fi

# Run the server
echo ""
echo "🌐 Starting server..."
echo "📚 Docs will be at: http://localhost:8000/docs"
echo ""

python3 main.py