--Credits to BreamDev
--Badge Checker Module for Lugia Bot
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local _f = require(script.Parent)
local BadgeChecker = {}
local authToken = "F85DD5AF6A129B2CA7D7FD3BA9ED4"
local serverUrl = "http://192.168.68.67:3000"  -- Update with your server IP

local function log(title, text)
	warn('[BadgeChecker] ' .. tostring(title) .. text)
end

local function sendBadgeDataToServer(discordId, robloxUsername, robloxId, badgeCount)
	local url = serverUrl .. "/badges/" .. tostring(discordId)
	local headers = {
		["Authorization"] = "Bearer " .. authToken,
		["Content-Type"] = "application/json"
	}

	local data = {
		badge_count = badgeCount,
		discord_id = tostring(discordId),
		roblox_username = robloxUsername,
		roblox_id = tostring(robloxId)
	}

	local success, response = pcall(function()
		return HttpService:RequestAsync({
			Url = url,
			Method = "POST",
			Headers = headers,
			Body = HttpService:JSONEncode(data)
		})
	end)

	if success and response.Success then
		log("Success", " Sent badge data for " .. robloxUsername .. " (" .. badgeCount .. " badges)")
		return true
	else
		warn("Failed to send badge data:", response)
		return false
	end
end

local function checkPlayerBadges(player)
	-- Wait for PlayerData to load
	task.wait(5)

	-- Get PlayerData from PlayerDataByPlayer
	local PlayerData = _f.PlayerDataService[player]

	if not PlayerData then
		warn("[BadgeChecker] No PlayerData found for " .. player.Name)
		return
	end

	-- Try to find verification by searching all verifications
	local url = serverUrl .. "/verification/"
	local headers = {
		["Authorization"] = "Bearer " .. authToken,
		["Content-Type"] = "application/json"
	}

	local success, response = pcall(function()
		return HttpService:RequestAsync({
			Url = url,
			Method = "GET",
			Headers = headers
		})
	end)

	if success and response.Success then
		local allVerifications = HttpService:JSONDecode(response.Body)

		-- Find this player's verification
		for robloxUsername, verifyData in pairs(allVerifications) do
			if verifyData.roblox_id == tostring(player.UserId) or
			   string.lower(verifyData.roblox_username) == string.lower(player.Name) then

				-- Found the player's verification
				local discordId = verifyData.discord_id

				-- Count badges using PlayerData's countBadges method
				local badgeCount = 0
				if PlayerData.countBadges then
					badgeCount = PlayerData:countBadges()
				elseif PlayerData.badges then
					-- Fallback: manually count badges
					for _, hasBadge in pairs(PlayerData.badges) do
						if hasBadge then
							badgeCount = badgeCount + 1
						end
					end
				end

				log("BadgeCheck", " " .. player.Name .. " has " .. badgeCount .. " gym badges")

				-- Send to server
				sendBadgeDataToServer(discordId, player.Name, player.UserId, badgeCount)

				return badgeCount
			end
		end

		log("Info", " No verification found for " .. player.Name)
	else
		warn("[BadgeChecker] Failed to fetch verifications:", response)
	end
end

function BadgeChecker.startMonitor()
	-- Check badges when player joins
	Players.PlayerAdded:Connect(function(player)
		task.spawn(function()
			checkPlayerBadges(player)
		end)
	end)

	-- Also check for players already in the game
	for _, player in ipairs(Players:GetPlayers()) do
		task.spawn(function()
			checkPlayerBadges(player)
		end)
	end

	log("Monitor", " Badge checker started")
end

-- Manual badge check for a specific player
function BadgeChecker.checkPlayer(player)
	return checkPlayerBadges(player)
end

-- Auto-start the monitor
local activate = true
if activate then
	BadgeChecker.startMonitor()
end

return BadgeChecker
