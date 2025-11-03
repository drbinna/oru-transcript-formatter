#!/bin/bash

# Local Testing Helper Script for ORU Transcript Formatter
# This script helps you set up and test the application locally

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🧪 ORU Transcript Formatter - Local Testing Setup"
echo "=================================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo ""

# Check for API key
echo "🔑 Checking for Anthropic API key..."
ENV_FILE="$BACKEND_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env file not found in backend directory"
    echo "   Creating .env file template..."
    echo "ANTHROPIC_API_KEY=paste-your-api-key-here" > "$ENV_FILE"
    echo ""
    echo "❌ Please edit $ENV_FILE and add your Anthropic API key"
    echo "   Get your API key at: https://console.anthropic.com/"
    echo ""
    read -p "Press Enter after you've added your API key, or Ctrl+C to exit..."
else
    if grep -q "paste-your-api-key-here\|your-api-key-here" "$ENV_FILE" 2>/dev/null; then
        echo "⚠️  .env file exists but contains placeholder API key"
        echo "   Please edit $ENV_FILE and add your actual Anthropic API key"
        echo ""
        read -p "Press Enter after you've added your API key, or Ctrl+C to exit..."
    else
        echo "✅ .env file found with API key"
    fi
fi
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd "$BACKEND_DIR"
if [ ! -d "__pycache__" ] || [ requirements.txt -nt __pycache__ ]; then
    pip3 install -r requirements.txt --quiet
    echo "✅ Backend dependencies installed"
else
    echo "✅ Backend dependencies already installed"
fi
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend dependencies already installed"
fi
echo ""

# Summary
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo ""
echo "   Terminal 1 - Backend:"
echo "   cd backend"
echo "   uvicorn main:app --reload"
echo ""
echo "   Terminal 2 - Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "   Then open: http://localhost:5173"
echo ""
echo "📝 For detailed instructions, see LOCAL_TESTING.md"
echo ""

