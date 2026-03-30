#!/bin/bash
# Strix Skill Setup Script
# Installs all dependencies for the penetration testing skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Strix Skill Setup ==="
echo "Installing dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "$SKILL_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SKILL_DIR/.venv"
fi

# Activate virtual environment
source "$SKILL_DIR/.venv/bin/activate"

# Install Python dependencies
echo "Installing Python packages..."
pip install --quiet --upgrade pip

# Browser automation
pip install --quiet playwright>=1.40.0 beautifulsoup4>=4.12.0 lxml>=5.0.0

# HTTP requests
pip install --quiet httpx>=0.25.0 requests>=2.31.0

# DNS/Recon
pip install --quiet dnspython>=2.4.0

# Utilities
pip install --quiet rich>=13.0.0

# Install Playwright browsers
echo "Installing Playwright Chromium browser..."
python -m playwright install chromium

# Create working directories
echo "Creating working directories..."
mkdir -p /tmp/strix_browser
mkdir -p /tmp/strix_reports

echo ""
echo "=== Setup Complete ==="
echo "Strix skill is ready to use."
echo ""
echo "To activate the virtual environment manually:"
echo "  source $SKILL_DIR/.venv/bin/activate"
