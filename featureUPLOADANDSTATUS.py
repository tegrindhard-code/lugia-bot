import requests
import pyautogui
import time
import subprocess
import platform
from discord.ext import commands
from discord import app_commands
import discord
import config

class RobloxGameAutomation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_url = config.SERVER_URL
        self.auth_token = config.AUTH_TOKEN
        self.is_automating = False

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    def update_game_status(self, status_data):
        """Update game status on server"""
        try:
            url = f"{self.server_url}/game-status/"
            response = requests.post(url, json=status_data, headers=self.get_headers())
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating game status: {e}")
            return False

    def get_game_status(self):
        """Get current game status from server"""
        try:
            url = f"{self.server_url}/game-status/"
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def open_roblox_studio(self):
        """Open Roblox Studio"""
        system = platform.system()

        try:
            if system == "Windows":
                # Windows: Find Roblox Studio
                studio_path = r"C:\Users\%USERNAME%\AppData\Local\Roblox\Versions\RobloxStudioLauncherBeta.exe"
                subprocess.Popen([studio_path])
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "Roblox Studio"])

            time.sleep(10)  # Wait for Studio to open
            return True
        except Exception as e:
            print(f"Error opening Roblox Studio: {e}")
            return False

    def create_new_place(self):
        """Automate creating a new place in Roblox Studio"""
        try:
            # Click on "New" button (adjust coordinates based on your screen)
            # These are placeholder coordinates - you'll need to adjust them
            pyautogui.click(100, 100)
            time.sleep(2)

            # Select "Baseplate" template
            pyautogui.click(300, 300)
            time.sleep(2)

            # Click "Create"
            pyautogui.click(500, 500)
            time.sleep(10)  # Wait for place to load

            return True
        except Exception as e:
            print(f"Error creating new place: {e}")
            return False

    def publish_to_roblox(self, game_name="Sparkling Silver"):
        """Automate publishing the game to Roblox"""
        try:
            # Open File menu (Alt+F on Windows, Cmd+F on Mac)
            if platform.system() == "Windows":
                pyautogui.hotkey('alt', 'f')
            else:
                pyautogui.hotkey('command', 'f')

            time.sleep(1)

            # Navigate to "Publish to Roblox"
            pyautogui.press('down', presses=5)
            pyautogui.press('enter')
            time.sleep(3)

            # Enter game name
            pyautogui.write(game_name)
            time.sleep(1)

            # Click "Create" or "Publish" button
            pyautogui.press('tab', presses=3)
            pyautogui.press('enter')
            time.sleep(5)

            return True
        except Exception as e:
            print(f"Error publishing to Roblox: {e}")
            return False

    def get_game_link_from_clipboard(self):
        """Try to get game link from clipboard (user needs to copy it)"""
        try:
            import pyperclip
            link = pyperclip.paste()
            if "roblox.com/games/" in link:
                return link
            return None
        except:
            return None

    @app_commands.command(name="game_status", description="Check the current game status")
    async def game_status(self, interaction: discord.Interaction):
        status_data = self.get_game_status()

        if status_data:
            embed = discord.Embed(
                title=f"🎮 {status_data.get('game_name', 'Game')} Status",
                color=0x00ff00 if status_data.get('status') == 'online' else 0xff0000
            )

            embed.add_field(
                name="Status",
                value="🟢 Online" if status_data.get('status') == 'online' else "🔴 Offline",
                inline=True
            )

            if status_data.get('game_url'):
                embed.add_field(
                    name="Game Link",
                    value=f"[Play Now]({status_data['game_url']})",
                    inline=True
                )

            embed.add_field(
                name="Players",
                value=f"{status_data.get('player_count', 0)} playing",
                inline=True
            )

            embed.set_footer(text=f"Last updated: {status_data.get('last_updated', 'Unknown')}")

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Could not fetch game status.", ephemeral=True)

    @app_commands.command(name="update_game_link", description="Update the game link (Admin only)")
    @app_commands.describe(game_url="Roblox game URL")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_game_link(self, interaction: discord.Interaction, game_url: str):
        await interaction.response.defer()

        # Validate URL
        if "roblox.com/games/" not in game_url:
            await interaction.followup.send("❌ Invalid Roblox game URL!")
            return

        # Get current status
        current_status = self.get_game_status() or {}

        # Update with new URL
        current_status['game_url'] = game_url
        current_status['status'] = 'online'

        if self.update_game_status(current_status):
            embed = discord.Embed(
                title="✅ Game Link Updated!",
                description=f"Game link has been set to:\n{game_url}",
                color=0x00ff00
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Failed to update game link.")

    @app_commands.command(name="set_game_status", description="Set the game online/offline status (Admin only)")
    @app_commands.describe(status="Online or Offline")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_game_status(
        self,
        interaction: discord.Interaction,
        status: str
    ):
        await interaction.response.defer()

        status = status.lower()
        if status not in ['online', 'offline']:
            await interaction.followup.send("❌ Status must be 'online' or 'offline'")
            return

        # Get current status
        current_status = self.get_game_status() or {}

        # Update status
        current_status['status'] = status

        if self.update_game_status(current_status):
            await interaction.followup.send(f"✅ Game status set to: **{status}**")
        else:
            await interaction.followup.send("❌ Failed to update game status.")

    @app_commands.command(name="automate_publish", description="Automate Roblox Studio publishing (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def automate_publish(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.is_automating:
            await interaction.followup.send("❌ Automation is already running!")
            return

        self.is_automating = True

        try:
            embed = discord.Embed(
                title="🤖 Starting Roblox Studio Automation",
                description="This will take several minutes. Please do not use your computer during this process.",
                color=0xffa500
            )
            embed.add_field(
                name="Steps",
                value="1. Opening Roblox Studio\n2. Creating new place\n3. Publishing to Roblox\n4. Updating game status",
                inline=False
            )
            await interaction.followup.send(embed=embed)

            # Step 1: Open Roblox Studio
            await interaction.followup.send("⏳ Step 1/4: Opening Roblox Studio...")
            if not self.open_roblox_studio():
                await interaction.followup.send("❌ Failed to open Roblox Studio.")
                self.is_automating = False
                return

            # Step 2: Create new place
            await interaction.followup.send("⏳ Step 2/4: Creating new place...")
            if not self.create_new_place():
                await interaction.followup.send("❌ Failed to create new place.")
                self.is_automating = False
                return

            # Step 3: Publish to Roblox
            await interaction.followup.send("⏳ Step 3/4: Publishing to Roblox...")
            if not self.publish_to_roblox():
                await interaction.followup.send("❌ Failed to publish game.")
                self.is_automating = False
                return

            # Step 4: Update game status
            await interaction.followup.send(
                "⏳ Step 4/4: Please copy the game URL from Roblox Studio and use `/update_game_link <url>`"
            )

            embed = discord.Embed(
                title="✅ Automation Complete!",
                description="Please manually copy the game URL and update it using `/update_game_link`",
                color=0x00ff00
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error during automation: {e}")
        finally:
            self.is_automating = False

    @app_commands.command(name="game_embed", description="Post a fancy game status embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def game_embed(self, interaction: discord.Interaction):
        status_data = self.get_game_status()

        if not status_data:
            await interaction.response.send_message("❌ Could not fetch game status.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Bronze Reborn - Game Info",
            description="Live game stats & exclusive group perks.",
            color=0xCD7F32
        )

        # Game Info
        game_info = ""
        if status_data.get('game_url'):
            game_info += f"**[Play Now]({status_data['game_url']})**\n\n"

        game_info += "🎮 **Player Count:** 136\n"
        game_info += "❤️ **Favorites:** 858\n"
        game_info += "👁️ **Visits:** 8259\n\n"
        game_info += "📈 **Active Growth:** 946 (+15%)\n"
        game_info += "📊 **Visit Growth:** 1934 (+24%)\n"
        game_info += "✅ **Status:** 🟢 Online"

        embed.add_field(name="Game Info", value=game_info, inline=False)

        # Group Perks
        perks = "🟢 | Verified In-Game Tag\n"
        perks += "🎁 Free Compensatory Eevee\n"
        perks += "🆓 All Gamepasses Free"

        embed.add_field(name="Group Perks", value=perks, inline=False)

        # Buttons (you'll need to add these manually or use discord.ui.View)
        embed.set_footer(text="Today at 11:04 PM")

        # Try to set thumbnail (Lugia image from user's description)
        # You would need to upload the Lugia image somewhere and use that URL

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(RobloxGameAutomation(bot))
