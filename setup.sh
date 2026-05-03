#!/usr/bin/env bash
set -euo pipefail

echo "=== Microsoft Agent Framework Workshop - Setup ==="

# Create virtual environment
echo "[1/3] Creating virtual environment (.venv)..."
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "[2/3] Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "[3/3] Installing Python dependencies..."
pip install -r requirements.txt

echo "=== Setup complete ==="
