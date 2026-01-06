#!/bin/bash
#
# Auto-Commiter Install Script
# Installs auto-commiter using pipx (recommended) or pip
#

set -e

REPO_URL="https://github.com/yourusername/auto-commiter.git"

echo "🚀 Auto-Commiter Installer"
echo "=========================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python $PYTHON_VERSION"

# Check if pipx is available
if command -v pipx &> /dev/null; then
    echo "✅ Found pipx"
    echo ""
    echo "Installing with pipx (recommended)..."
    pipx install "$REPO_URL" || pipx upgrade auto-commiter
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Run 'autocommit --help' to get started."
else
    echo "⚠️  pipx not found"
    echo ""
    read -p "Install with pip instead? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing with pip..."
        pip install --user "$REPO_URL"
        echo ""
        echo "✅ Installation complete!"
        echo ""
        echo "⚠️  Make sure ~/.local/bin is in your PATH"
        echo "   Add to your ~/.bashrc or ~/.zshrc:"
        echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    else
        echo ""
        echo "To install pipx first:"
        echo "  pip install pipx"
        echo "  pipx ensurepath"
        echo ""
        echo "Then run this script again."
        exit 0
    fi
fi

echo ""
echo "Quick start:"
echo "  cd your-project"
echo "  autocommit"
echo ""
echo "For help:"
echo "  autocommit --help"
echo ""
