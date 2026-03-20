#!/bin/bash
# Deploy script for SMF Social v2

set -e

echo "🚀 Deploying SMF Social v2..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Copy .env.example to .env and configure your settings"
    exit 1
fi

# Create data directory
mkdir -p data

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker-compose down

# Build and start
echo "🔨 Building and starting..."
docker-compose up --build -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 5

# Health check
echo "🏥 Health check..."
if curl -s http://localhost/health | grep -q '"status": "ok"'; then
    echo "✅ Deployment successful!"
    echo ""
    echo "SMF Social v2 is running at:"
    echo "  Frontend: http://localhost"
    echo "  API: http://localhost/api"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
else
    echo "⚠️  Health check failed. Check logs: docker-compose logs"
    exit 1
fi
