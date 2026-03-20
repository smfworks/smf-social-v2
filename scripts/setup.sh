#!/bin/bash
# Setup script for SMF Social v2

echo "Setting up SMF Social v2..."

# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from core.database import init_db; init_db()"

echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
