import requests
from discord.ext import commands
from discord import app_commands
import discord
import config

class PokemonSpawner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_url = config.SERVER_URL
        self.auth_token = config.AUTH_TOKEN

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    def send_to_server(self, user_id, data):
        """Send data to server for Roblox to process"""
        try:
            url = f"{self.server_url}/data/{user_id}"
            response = requests.post(url, json=data, headers=self.get_headers())
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending to server: {e}")
            return False

    @app_commands.command(name="spawn_pokemon", description="Spawn a Pokemon for a verified player")
    @app_commands.describe(
        pokemon="Pokemon name",
        level="Level (1-100)",
        shiny="Make it shiny?",
        nature="Pokemon nature"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def spawn_pokemon(
        self,
        interaction: discord.Interaction,
        pokemon: str,
        level: int = 1,
        shiny: bool = False,
        nature: str = None
    ):
        await interaction.response.defer()

        # Check if user is verified
        try:
            verify_url = f"{self.server_url}/verification/discord/{interaction.user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send("You need to verify your Roblox account first! Use `/verify`")
                return

            verify_data = verify_response.json()
            roblox_id = verify_data.get("roblox_id")

            if not roblox_id:
                await interaction.followup.send("Could not find your Roblox ID. Please verify again.")
                return

            # Create Pokemon data
            pokemon_data = {
                "pokemon": pokemon,
                "level": max(1, min(100, level)),
                "shiny": shiny
            }

            if nature:
                pokemon_data["nature"] = nature

            # Send to server
            if self.send_to_server(roblox_id, pokemon_data):
                embed = discord.Embed(
                    title="Pokemon Spawned!",
                    description=f"**{pokemon}** (Level {level}){' ✨ Shiny' if shiny else ''}",
                    color=0xFFD700 if shiny else 0x3498db
                )
                embed.add_field(name="Status", value="Will appear in-game within a few seconds!")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("Failed to send Pokemon to server. Is the server running?")

        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

    @app_commands.command(name="give_currency", description="Give coins to a player")
    @app_commands.describe(
        user="Discord user to give coins to",
        amount="Amount of coins"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def give_currency(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):
        await interaction.response.defer()

        try:
            # Check if user is verified
            verify_url = f"{self.server_url}/verification/discord/{user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send(f"{user.mention} needs to verify their Roblox account first!")
                return

            verify_data = verify_response.json()
            roblox_id = verify_data.get("roblox_id")

            # Send currency to server
            currency_data = {
                "currency": amount
            }

            if self.send_to_server(roblox_id, currency_data):
                await interaction.followup.send(f"✅ Gave {amount} coins to {user.mention}!")
            else:
                await interaction.followup.send("Failed to send currency. Is the server running?")

        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

    @app_commands.command(name="ban_player", description="Ban a player from the game")
    @app_commands.describe(
        user="Discord user to ban",
        reason="Reason for the ban"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def ban_player(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str = "No reason provided"
    ):
        await interaction.response.defer()

        try:
            # Check if user is verified
            verify_url = f"{self.server_url}/verification/discord/{user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send(f"{user.mention} is not verified.")
                return

            verify_data = verify_response.json()
            roblox_id = verify_data.get("roblox_id")

            # Add to banned list
            ban_url = f"{self.server_url}/banned/{roblox_id}"
            ban_data = {"reason": reason}
            response = requests.post(ban_url, json=ban_data, headers=self.get_headers())

            if response.status_code == 200:
                await interaction.followup.send(f"✅ Banned {user.mention} from the game.\nReason: {reason}")
            else:
                await interaction.followup.send("Failed to ban user.")

        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

    @app_commands.command(name="unban_player", description="Unban a player from the game")
    @app_commands.describe(user="Discord user to unban")
    @app_commands.checks.has_permissions(administrator=True)
    async def unban_player(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        await interaction.response.defer()

        try:
            # Check if user is verified
            verify_url = f"{self.server_url}/verification/discord/{user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send(f"{user.mention} is not verified.")
                return

            verify_data = verify_response.json()
            roblox_id = verify_data.get("roblox_id")

            # Remove from banned list
            ban_url = f"{self.server_url}/banned/{roblox_id}"
            response = requests.delete(ban_url, headers=self.get_headers())

            if response.status_code == 200:
                await interaction.followup.send(f"✅ Unbanned {user.mention} from the game.")
            else:
                await interaction.followup.send("Failed to unban user.")

        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(PokemonSpawner(bot))
