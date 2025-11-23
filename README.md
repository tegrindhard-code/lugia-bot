# Lugia Bot - Pokemon Discord Bot with Roblox Integration

A comprehensive Discord bot for Sparkling Silver Pokemon game with full Roblox integration, featuring currency system, Pokemon spinning, verification, and badge roles.

## Features

### 🎮 Core Features
- **Discord-Roblox Verification**: Link Discord accounts to Roblox usernames
- **Currency System**: Coin-based Pokemon spinning with daily free spins
- **Badge Role System**: Automatic role assignment based on in-game gym badges
- **Pokemon Spawner**: Admin commands to spawn Pokemon for verified players
- **Game Status Tracking**: Live game status and player count display
- **GIF Data Processing**: Convert Pokemon sprites to Roblox-compatible format

### 💰 Currency & Spinning
- 3 free daily spins per player
- 100 coins per additional spin
- Pokemon rarity based on badge tier
- Automatic Pokemon delivery to game

### 🏆 Badge Tiers
- **Bronze**: 0+ badges, max Level 25 Pokemon
- **Silver**: 10+ badges, max Level 50 Pokemon
- **Gold**: 25+ badges, max Level 75 Pokemon
- **Platinum**: 50+ badges, max Level 100 Pokemon

## Setup

### Prerequisites
- Node.js 16+ (for the server)
- Python 3.9+ (for the Discord bot)
- Roblox Studio (for game integration)
- Discord Bot Token

### 1. Install Dependencies

#### Python Dependencies
```bash
pip install -r requirements.txt
```

#### Node.js Dependencies
```bash
cd server
npm install
```

### 2. Configuration

#### config.py
Edit `config.py` and add your Discord bot token:
```python
BOT_TOKEN = "your_discord_bot_token_here"
SERVER_URL = "http://YOUR_LOCAL_IP:3000"  # Update with your local IP
```

#### Find Your Local IP
**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address"

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```
Look for "inet" address (usually starts with 192.168.x.x)

#### Update Lua Files
Update the server URL in both:
- `lugia.lua` (line 14)
- `BadgeChecker.lua` (line 9)

```lua
local serverUrl = "http://YOUR_LOCAL_IP:3000"
```

### 3. Start the Server

```bash
cd server
npm start
```

The server will run on port 3000 and handle all Discord-Roblox communication.

### 4. Start the Discord Bot

```bash
python bot.py
```

### 5. Roblox Integration

1. Place `lugia.lua` in `ServerScriptService` in your Roblox game
2. Place `BadgeChecker.lua` in `ServerScriptService`
3. Update `PlayerDataService.Lua` with the Lugia integration methods (already done)
4. Ensure HttpService is enabled in Game Settings
5. Add Pokedex.lua to the server (you'll create this)

## Discord Commands

### User Commands
- `/verify <roblox_username>` - Link your Discord to Roblox account
- `/verify_confirm` - Confirm verification after setting Roblox status
- `/unverify` - Unlink your Roblox account
- `/whois [user]` - Check verification status
- `/balance` - Check your coin balance
- `/daily` - Claim 3 free daily spins
- `/spin` - Spin for a random Pokemon
- `/check_badges [user]` - Check badge count and tier
- `/update_badge_role` - Update your badge role (requires joining game)
- `/badge_tiers` - View all badge tier information
- `/game_status` - Check current game status

### Admin Commands
- `/setup_badge_roles` - Create all badge tier roles
- `/spawn_pokemon <pokemon> [level] [shiny] [nature]` - Spawn Pokemon for verified player
- `/give_currency <user> <amount>` - Give coins to a player
- `/ban_player <user> [reason]` - Ban player from game
- `/unban_player <user>` - Unban player
- `/force_badge_update <user>` - Force update badge role
- `/update_game_link <url>` - Update game URL
- `/set_game_status <online/offline>` - Set game status
- `/set_cookie <cookie>` - Set Roblox cookie for uploads
- `/sprite_to_gifdata` - Convert Pokemon sprites to GIF data
- `/download_gifdata` - Download and rebuild GIF from data

## File Structure

```
lugia-bot/
├── bot.py                      # Main bot initializer
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
│
├── Feature Modules:
├── featureGIFDATA.py          # Sprite conversion
├── featureSPAWNER.py          # Pokemon spawning
├── featureCURRENCY.py         # Currency & spinning
├── featureVERIFICATION.py     # Discord-Roblox linking
├── featureBADGEROLES.py       # Badge role management
├── featureUPLOADANDSTATUS.py  # Game automation
│
├── Lua Files (for Roblox):
├── lugia.lua                   # Main Roblox integration
├── BadgeChecker.lua            # Badge detection
├── PlayerDataService.Lua       # Player data methods
├── Pokedex.lua                 # Pokemon data (you create)
│
└── server/                     # Node.js server
    ├── server.js               # Express server
    ├── package.json            # Dependencies
    ├── setup.sh                # Setup script
    ├── README.md               # Server docs
    └── data/                   # JSON data storage
```

## How It Works

### Verification Flow
1. User runs `/verify <roblox_username>`
2. Bot generates a random 6-character code
3. User sets their Roblox status to the code
4. User runs `/verify_confirm`
5. Bot checks Roblox status and confirms
6. Verification data stored in server

### Badge Role Flow
1. User runs `/update_badge_role`
2. Bot prompts user to join the game
3. User joins Sparkling Silver
4. BadgeChecker.lua detects player and counts gym badges
5. Badge data sent to server
6. Bot assigns appropriate tier role

### Pokemon Spinning Flow
1. User runs `/spin`
2. Bot checks currency (free spins or coins)
3. Bot selects random Pokemon based on user's badge tier
4. Pokemon data sent to server
5. lugia.lua detects data and spawns Pokemon in-game

## API Endpoints

The Node.js server provides these endpoints:

- `GET /data/` - Get all player data (for Roblox)
- `POST /data/:userId` - Add player data
- `GET /verification/` - Get all verifications
- `POST /verification/` - Create verification
- `GET /currency/:discordId` - Get user currency
- `POST /currency/:discordId` - Update currency
- `GET /badges/:userId` - Get badge data
- `POST /badges/:userId` - Report badge data
- `GET /game-status/` - Get game status
- `POST /game-status/` - Update game status

All endpoints require Bearer token authentication.

## Troubleshooting

### Bot won't start
- Check BOT_TOKEN in config.py
- Verify Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`

### Server connection issues
- Verify server is running: `cd server && npm start`
- Check firewall allows port 3000
- Confirm IP address matches in all files
- Enable HttpService in Roblox Studio

### Badge roles not working
- User must be verified first
- User must join the game
- BadgeChecker.lua must be running
- Check server logs for errors

### Pokemon not spawning
- Verify user is verified
- Check lugia.lua is running in game
- Ensure server is accessible from Roblox
- Check server logs for player data

## Security Notes

- The auth token (`F85DD5AF6A129B2CA7D7FD3BA9ED4`) should be changed in production
- Never commit your Discord bot token or Roblox cookie to git
- Use environment variables for sensitive data in production
- Consider port forwarding security before exposing server to internet

## Credits

- Original Dotty Bot system by BreamDev
- Lugia Bot integration and features by your team
- Discord.py library
- Express.js server framework

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs and bot console output
3. Verify all configuration files are correct
4. Check that all services are running

## License

Private project for Sparkling Silver Pokemon game.
