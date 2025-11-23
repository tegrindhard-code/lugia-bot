const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const AUTH_TOKEN = "F85DD5AF6A129B2CA7D7FD3BA9ED4";

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Data storage paths
const DATA_DIR = path.join(__dirname, 'data');
const PLAYER_DATA_FILE = path.join(DATA_DIR, 'player_data.json');
const BANNED_FILE = path.join(DATA_DIR, 'banned.json');
const VERIFICATION_FILE = path.join(DATA_DIR, 'verification.json');
const POKEDEX_FILE = path.join(DATA_DIR, 'pokedex.json');
const GAME_STATUS_FILE = path.join(DATA_DIR, 'game_status.json');
const CURRENCY_FILE = path.join(DATA_DIR, 'currency.json');
const BADGE_DATA_FILE = path.join(DATA_DIR, 'badge_data.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Initialize data files
function initFile(filePath, defaultData = {}) {
    if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, JSON.stringify(defaultData, null, 2));
    }
}

initFile(PLAYER_DATA_FILE);
initFile(BANNED_FILE);
initFile(VERIFICATION_FILE);
initFile(POKEDEX_FILE);
initFile(GAME_STATUS_FILE, {
    game_name: "Sparkling Silver",
    game_url: "",
    status: "offline",
    player_count: 0,
    last_updated: new Date().toISOString()
});
initFile(CURRENCY_FILE);
initFile(BADGE_DATA_FILE);

// Auth middleware
function authMiddleware(req, res, next) {
    const authHeader = req.headers.authorization;
    if (!authHeader || authHeader !== `Bearer ${AUTH_TOKEN}`) {
        return res.status(403).json({ error: 'Unauthorized' });
    }
    next();
}

// Helper functions
function readJSON(filePath) {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return {};
    }
}

function writeJSON(filePath, data) {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

// ===== PLAYER DATA ENDPOINTS =====

// Get all player data (for Roblox to poll)
app.get('/data/', authMiddleware, (req, res) => {
    const data = readJSON(PLAYER_DATA_FILE);
    res.json(data);
});

// Add data for a specific player
app.post('/data/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const playerData = req.body;

    const allData = readJSON(PLAYER_DATA_FILE);

    if (!allData[userId]) {
        allData[userId] = [];
    }

    // Add new entry to player's data array
    allData[userId].push(playerData);

    writeJSON(PLAYER_DATA_FILE, allData);
    res.json({ success: true, message: 'Data added for player' });
});

// Delete player data (after Roblox processes it)
app.delete('/data/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const allData = readJSON(PLAYER_DATA_FILE);

    delete allData[userId];

    writeJSON(PLAYER_DATA_FILE, allData);
    res.json({ success: true, message: 'Player data deleted' });
});

// ===== BANNED USERS ENDPOINTS =====

// Get all banned users
app.get('/banned/', authMiddleware, (req, res) => {
    const data = readJSON(BANNED_FILE);
    res.json(data);
});

// Ban a user
app.post('/banned/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const { reason } = req.body;

    const allData = readJSON(BANNED_FILE);
    allData[userId] = {
        reason: reason || 'No reason provided',
        timestamp: new Date().toISOString()
    };

    writeJSON(BANNED_FILE, allData);
    res.json({ success: true, message: 'User banned' });
});

// Unban a user
app.delete('/banned/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const allData = readJSON(BANNED_FILE);

    delete allData[userId];

    writeJSON(BANNED_FILE, allData);
    res.json({ success: true, message: 'User unbanned' });
});

// ===== VERIFICATION ENDPOINTS =====

// Get all verifications
app.get('/verification/', authMiddleware, (req, res) => {
    const data = readJSON(VERIFICATION_FILE);
    res.json(data);
});

// Get verification by Discord ID
app.get('/verification/discord/:discordId', authMiddleware, (req, res) => {
    const { discordId } = req.params;
    const allData = readJSON(VERIFICATION_FILE);

    const entry = Object.values(allData).find(v => v.discord_id === discordId);

    if (entry) {
        res.json(entry);
    } else {
        res.status(404).json({ error: 'Verification not found' });
    }
});

// Get verification by Roblox username
app.get('/verification/roblox/:robloxUsername', authMiddleware, (req, res) => {
    const { robloxUsername } = req.params;
    const allData = readJSON(VERIFICATION_FILE);

    if (allData[robloxUsername]) {
        res.json(allData[robloxUsername]);
    } else {
        res.status(404).json({ error: 'Verification not found' });
    }
});

// Create verification
app.post('/verification/', authMiddleware, (req, res) => {
    const { discord_id, roblox_username, roblox_id } = req.body;

    const allData = readJSON(VERIFICATION_FILE);
    allData[roblox_username] = {
        discord_id,
        roblox_username,
        roblox_id,
        verified_at: new Date().toISOString()
    };

    writeJSON(VERIFICATION_FILE, allData);
    res.json({ success: true, message: 'Verification created' });
});

// Delete verification
app.delete('/verification/:robloxUsername', authMiddleware, (req, res) => {
    const { robloxUsername } = req.params;
    const allData = readJSON(VERIFICATION_FILE);

    delete allData[robloxUsername];

    writeJSON(VERIFICATION_FILE, allData);
    res.json({ success: true, message: 'Verification deleted' });
});

// ===== CURRENCY ENDPOINTS =====

// Get currency for a user
app.get('/currency/:discordId', authMiddleware, (req, res) => {
    const { discordId } = req.params;
    const allData = readJSON(CURRENCY_FILE);

    res.json({
        discord_id: discordId,
        coins: allData[discordId]?.coins || 0,
        daily_spins: allData[discordId]?.daily_spins || 3,
        last_daily: allData[discordId]?.last_daily || null
    });
});

// Update currency
app.post('/currency/:discordId', authMiddleware, (req, res) => {
    const { discordId } = req.params;
    const { coins, daily_spins, last_daily } = req.body;

    const allData = readJSON(CURRENCY_FILE);

    if (!allData[discordId]) {
        allData[discordId] = { coins: 0, daily_spins: 3, last_daily: null };
    }

    if (coins !== undefined) allData[discordId].coins = coins;
    if (daily_spins !== undefined) allData[discordId].daily_spins = daily_spins;
    if (last_daily !== undefined) allData[discordId].last_daily = last_daily;

    writeJSON(CURRENCY_FILE, allData);
    res.json({ success: true, data: allData[discordId] });
});

// ===== POKEDEX ENDPOINTS =====

// Get Pokedex
app.get('/pokedex/', authMiddleware, (req, res) => {
    const data = readJSON(POKEDEX_FILE);
    res.json(data);
});

// Update Pokedex
app.post('/pokedex/', authMiddleware, (req, res) => {
    const pokedexData = req.body;
    writeJSON(POKEDEX_FILE, pokedexData);
    res.json({ success: true, message: 'Pokedex updated' });
});

// ===== GAME STATUS ENDPOINTS =====

// Get game status
app.get('/game-status/', authMiddleware, (req, res) => {
    const data = readJSON(GAME_STATUS_FILE);
    res.json(data);
});

// Update game status
app.post('/game-status/', authMiddleware, (req, res) => {
    const statusData = req.body;
    statusData.last_updated = new Date().toISOString();
    writeJSON(GAME_STATUS_FILE, statusData);
    res.json({ success: true, data: statusData });
});

// ===== BADGE DATA ENDPOINTS =====

// Get badge data for a user (by Discord ID or Roblox ID)
app.get('/badges/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const allData = readJSON(BADGE_DATA_FILE);

    if (allData[userId]) {
        res.json(allData[userId]);
    } else {
        res.status(404).json({ error: 'Badge data not found' });
    }
});

// Report badge data from Roblox (Lua sends this)
app.post('/badges/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const { badge_count, discord_id, roblox_username, roblox_id } = req.body;

    const allData = readJSON(BADGE_DATA_FILE);

    allData[userId] = {
        discord_id,
        roblox_username,
        roblox_id,
        badge_count,
        timestamp: new Date().toISOString()
    };

    writeJSON(BADGE_DATA_FILE, allData);
    res.json({ success: true, message: 'Badge data updated' });
});

// Delete badge data
app.delete('/badges/:userId', authMiddleware, (req, res) => {
    const { userId } = req.params;
    const allData = readJSON(BADGE_DATA_FILE);

    delete allData[userId];

    writeJSON(BADGE_DATA_FILE, allData);
    res.json({ success: true, message: 'Badge data deleted' });
});

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'online',
        timestamp: new Date().toISOString(),
        server: 'lugia-bot-server'
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`
╔═══════════════════════════════════════╗
║   Lugia Bot Server Running            ║
║   Port: ${PORT}                       ║
║   Auth Token: ${AUTH_TOKEN.slice(0, 10)}... ║
╚═══════════════════════════════════════╝

Server is ready to accept connections.
Your local IP will be accessible to Roblox.
    `);
});
