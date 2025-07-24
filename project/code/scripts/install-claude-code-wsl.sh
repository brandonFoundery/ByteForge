#!/usr/bin/env bash
# Quick installer for Claude Code in WSL Ubuntu

set -e

echo "1. Disabling invalid Homebrew entry in ~/.bashrc..."
sed -i '102s/^/#/' ~/.bashrc

echo "2. Installing NVM (Node Version Manager)..."
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
# Load NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "3. Installing Node.js LTS via nvm..."
nvm install --lts
nvm use --lts

echo "4. Installing Claude Code globally..."
npm install -g @anthropic-ai/claude-code

echo
echo "✅ Installation complete!"
echo "Next steps to authenticate:"
echo "  • Run: claude setup-token"
echo "    (requires an active Claude subscription)"
echo "  • Or set API key: claude config set apiKey YOUR_API_KEY"
echo
echo "Then to start Claude Code:"
echo "  • Interactive: claude"
echo "  • One-off: claude -p \"your query\""
echo "  • Help: claude --help"
