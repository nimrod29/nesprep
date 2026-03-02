#!/bin/bash
# Setup virtual environment for NesPrep

set -e

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -e ".[dev]"

echo "Copying environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please edit with your credentials"
fi

echo "Setup complete!"
echo "Run 'source .venv/bin/activate' to activate the environment"
