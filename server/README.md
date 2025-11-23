# Lugia Bot Server

This is the data server that facilitates communication between Discord (bot.py) and Roblox (lugia.lua).

## Setup

1. **Install Node.js** (if not already installed):
   - Download from https://nodejs.org/ (LTS version recommended)

2. **Install dependencies**:
   ```bash
   cd server
   npm install
   ```

3. **Start the server**:
   ```bash
   npm start
   ```

   For development (auto-restart on changes):
   ```bash
   npm run dev
   ```

## Finding Your Local IP

The server runs on port 3000 by default. To connect Roblox to your server:

### On Windows:
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x or 10.x.x.x)

### On Mac/Linux:
```bash
ifconfig
# or
ip addr show
```
Look for "inet" address (usually starts with 192.168.x.x or 10.x.x.x)

### Update lugia.lua

Once you have your IP, update the URL in `lugia.lua`:
```lua
local url = "http://YOUR_IP_HERE:3000/data/"
```

Example:
```lua
local url = "http://192.168.1.100:3000/data/"
```

## API Endpoints

### Player Data
- `GET /data/` - Get all player data (Roblox polls this)
- `POST /data/:userId` - Add data for a player (Discord bot uses this)
- `DELETE /data/:userId` - Delete player data (Roblox uses this after processing)

### Banned Users
- `GET /banned/` - Get all banned users
- `POST /banned/:userId` - Ban a user
- `DELETE /banned/:userId` - Unban a user

### Verification (Discord ↔ Roblox)
- `GET /verification/` - Get all verifications
- `GET /verification/discord/:discordId` - Get verification by Discord ID
- `GET /verification/roblox/:robloxUsername` - Get verification by Roblox username
- `POST /verification/` - Create verification
- `DELETE /verification/:robloxUsername` - Delete verification

### Currency
- `GET /currency/:discordId` - Get user's coins and daily spins
- `POST /currency/:discordId` - Update user's currency

### Pokedex
- `GET /pokedex/` - Get Pokedex data
- `POST /pokedex/` - Update Pokedex data

### Game Status
- `GET /game-status/` - Get game status
- `POST /game-status/` - Update game status

### Health Check
- `GET /health` - Check if server is online

## Authentication

All endpoints (except `/health`) require Bearer token authentication:
```
Authorization: Bearer F85DD5AF6A129B2CA7D7FD3BA9ED4
```

## Port Forwarding (Optional)

If you want to access this server from outside your local network:

1. Find your router's admin page (usually 192.168.1.1 or 192.168.0.1)
2. Enable port forwarding for port 3000
3. Point it to your computer's local IP
4. Use your public IP address instead of local IP

**Note**: Only do this if you understand the security implications.

## Data Storage

All data is stored in JSON files in the `server/data/` directory:
- `player_data.json` - Pokemon spawns, currency additions, etc.
- `banned.json` - Banned users list
- `verification.json` - Discord to Roblox account links
- `currency.json` - User coins and daily spins
- `pokedex.json` - Pokemon data for spinning
- `game_status.json` - Roblox game status info

## Troubleshooting

**Server won't start:**
- Make sure Node.js is installed: `node --version`
- Make sure dependencies are installed: `npm install`
- Check if port 3000 is already in use

**Roblox can't connect:**
- Verify your firewall allows connections on port 3000
- Make sure you're using the correct local IP address
- Ensure both your PC and Roblox are on the same network
- Check that HttpService is enabled in Roblox Studio

**Authentication errors:**
- Verify the auth token matches in both server.js and lugia.lua
