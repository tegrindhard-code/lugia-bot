import requests
import random
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
import discord
import config
import os
from featureGIFDATA import rebuild_gif_from_gifdata
from PIL import Image

class CurrencySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_url = config.SERVER_URL
        self.auth_token = config.AUTH_TOKEN
        self.coins_per_spin = config.COINS_PER_SPIN
        self.daily_free_spins = config.DAILY_FREE_SPINS

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    def get_currency_data(self, discord_id):
        """Get user's currency data"""
        try:
            url = f"{self.server_url}/currency/{discord_id}"
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            return {"coins": 0, "daily_spins": 3, "last_daily": None}
        except:
            return {"coins": 0, "daily_spins": 3, "last_daily": None}

    def update_currency_data(self, discord_id, coins=None, daily_spins=None, last_daily=None):
        """Update user's currency data"""
        try:
            url = f"{self.server_url}/currency/{discord_id}"
            data = {}
            if coins is not None:
                data["coins"] = coins
            if daily_spins is not None:
                data["daily_spins"] = daily_spins
            if last_daily is not None:
                data["last_daily"] = last_daily

            response = requests.post(url, json=data, headers=self.get_headers())
            return response.status_code == 200
        except:
            return False

    def get_pokedex(self):
        """Get Pokedex from server"""
        try:
            url = f"{self.server_url}/pokedex/"
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}

    def get_user_badge_tier(self, user):
        """Get user's badge role tier"""
        role_tiers = ["bronze", "silver", "gold", "platinum"]
        for tier in reversed(role_tiers):
            role = discord.utils.get(user.guild.roles, name=f"Pokemon {tier.title()}")
            if role and role in user.roles:
                return tier
        return "bronze"  # Default tier

    def get_random_pokemon(self, tier):
        """Get a random Pokemon based on tier"""
        pokedex = self.get_pokedex()
        if not pokedex:
            return None

        max_level = config.BADGE_TIERS[tier]["max_level"]

        # Filter Pokemon by level
        eligible_pokemon = []
        for poke_name, poke_data in pokedex.items():
            level = poke_data.get("level", 1)
            if level <= max_level:
                eligible_pokemon.append(poke_name)

        if eligible_pokemon:
            return random.choice(eligible_pokemon)
        return None

    def send_pokemon_to_player(self, user_id, pokemon_name):
        """Send Pokemon to player via server"""
        try:
            # Get verification data
            verify_url = f"{self.server_url}/verification/discord/{user_id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                return False

            verify_data = verify_response.json()
            roblox_id = verify_data.get("roblox_id")

            # Create Pokemon data
            pokemon_data = {
                "pokemon": pokemon_name,
                "level": random.randint(1, 100),
                "shiny": random.random() < 0.001  # 0.1% shiny chance
            }

            # Send to server
            url = f"{self.server_url}/data/{roblox_id}"
            response = requests.post(url, json=pokemon_data, headers=self.get_headers())
            return response.status_code == 200
        except:
            return False

    @app_commands.command(name="balance", description="Check your coin balance")
    async def balance(self, interaction: discord.Interaction):
        currency_data = self.get_currency_data(interaction.user.id)

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Balance",
            color=0xFFD700
        )
        embed.add_field(name="💰 Coins", value=f"{currency_data['coins']:,}", inline=True)
        embed.add_field(name="🎁 Daily Spins", value=f"{currency_data['daily_spins']}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily free spins")
    async def daily(self, interaction: discord.Interaction):
        currency_data = self.get_currency_data(interaction.user.id)

        # Check if already claimed today
        last_daily = currency_data.get("last_daily")
        if last_daily:
            last_claim = datetime.fromisoformat(last_daily)
            if datetime.now() - last_claim < timedelta(days=1):
                time_left = timedelta(days=1) - (datetime.now() - last_claim)
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                await interaction.response.send_message(
                    f"❌ You've already claimed your daily spins! Come back in {hours}h {minutes}m",
                    ephemeral=True
                )
                return

        # Reset daily spins
        self.update_currency_data(
            interaction.user.id,
            daily_spins=self.daily_free_spins,
            last_daily=datetime.now().isoformat()
        )

        embed = discord.Embed(
            title="Daily Spins Claimed!",
            description=f"You now have {self.daily_free_spins} free spins!",
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="spin", description="Spin for a random Pokemon!")
    async def spin(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Check verification
        try:
            verify_url = f"{self.server_url}/verification/discord/{interaction.user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send("❌ You need to verify your Roblox account first! Use `/verify`")
                return
        except:
            await interaction.followup.send("❌ Error checking verification status.")
            return

        currency_data = self.get_currency_data(interaction.user.id)
        coins = currency_data.get("coins", 0)
        daily_spins = currency_data.get("daily_spins", 0)

        # Check if user can spin
        if daily_spins > 0:
            # Use daily spin
            self.update_currency_data(
                interaction.user.id,
                daily_spins=daily_spins - 1
            )
            spin_type = "🎁 Free Spin"
        elif coins >= self.coins_per_spin:
            # Use coins
            self.update_currency_data(
                interaction.user.id,
                coins=coins - self.coins_per_spin
            )
            spin_type = f"💰 Coin Spin (-{self.coins_per_spin} coins)"
        else:
            await interaction.followup.send(
                f"❌ You don't have enough coins! You need {self.coins_per_spin} coins or a daily spin.\n"
                f"Use `/daily` to claim your free spins!"
            )
            return

        # Get user's badge tier
        tier = self.get_user_badge_tier(interaction.user)

        # Get random Pokemon
        pokemon = self.get_random_pokemon(tier)

        if not pokemon:
            await interaction.followup.send("❌ No Pokemon available to spin!")
            return

        # Send Pokemon to player
        if self.send_pokemon_to_player(interaction.user.id, pokemon):
            # Get Pokemon data for display
            pokedex = self.get_pokedex()
            poke_data = pokedex.get(pokemon, {})
            gifdata = poke_data.get("gifdata")

            embed = discord.Embed(
                title="🎰 Pokemon Spin!",
                description=f"You got **{pokemon}**!",
                color=0xFFD700
            )
            embed.add_field(name="Tier", value=tier.title(), inline=True)
            embed.add_field(name="Type", value=spin_type, inline=True)
            embed.add_field(name="Status", value="Check your game - it should appear soon!", inline=False)

            # Try to attach Pokemon sprite if available
            if gifdata:
                try:
                    os.makedirs(config.TEMP_DIR, exist_ok=True)
                    gif_path = os.path.join(config.TEMP_DIR, f"{pokemon}.gif")

                    # Rebuild GIF from gifdata (you'll need to implement image fetching)
                    # For now, just send the embed
                    await interaction.followup.send(embed=embed)
                except:
                    await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Failed to send Pokemon. Please try again.")

async def setup(bot):
    await bot.add_cog(CurrencySystem(bot))
