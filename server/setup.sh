#!/bin/bash

echo "╔═══════════════════════════════════════╗"
echo "║   Lugia Bot Server Setup              ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Find local IP
echo "Finding your local IP address..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    IP=$(ip route get 1 | awk '{print $7;exit}')
elif [[ "$OSTYPE" == "darwin"* ]]; then
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
else
    echo "Please manually find your IP address using 'ipconfig' (Windows) or 'ifconfig' (Mac/Linux)"
    exit 1
fi

echo "Your local IP address: $IP"
echo ""
echo "Update lugia.lua with:"
echo "  local url = \"http://$IP:3000/data/\""
echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Setup complete! Start the server with:"
echo "  npm start"
