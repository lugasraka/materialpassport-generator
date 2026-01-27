#!/bin/bash

# Material Passport Generator MVP - Quick Start Script

echo "======================================"
echo "🏗️  Material Passport Generator MVP"
echo "======================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements_mvp.txt
echo "✅ Dependencies installed"

# Run app
echo ""
echo "🚀 Starting Streamlit app..."
echo ""
echo "Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""

streamlit run app.py
