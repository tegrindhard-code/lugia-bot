import requests
import random
import string
from discord.ext import commands
from discord import app_commands
import discord
import config

class VerificationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_url = config.SERVER_URL
        self.auth_token = config.AUTH_TOKEN
        self.pending_verifications = {}  # {discord_id: {"code": "ABC123", "roblox_username": "username"}}

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    def generate_code(self):
        """Generate a random verification code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def get_roblox_id(self, username):
        """Get Roblox user ID from username"""
        try:
            url = f"https://users.roblox.com/v1/usernames/users"
            data = {
                "usernames": [username],
                "excludeBannedUsers": False
            }
            response = requests.post(url, json=data)

            if response.status_code == 200:
                users = response.json().get("data", [])
                if users:
                    return users[0].get("id")
            return None
        except:
            return None

    def check_user_status(self, roblox_id):
        """Check if user has the verification code in their Roblox status"""
        try:
            url = f"https://users.roblox.com/v1/users/{roblox_id}/status"
            response = requests.get(url)

            if response.status_code == 200:
                return response.json().get("status", "")
            return ""
        except:
            return ""

    @app_commands.command(name="verify", description="Link your Discord account to your Roblox username")
    @app_commands.describe(roblox_username="Your Roblox username")
    async def verify(self, interaction: discord.Interaction, roblox_username: str):
        await interaction.response.defer(ephemeral=True)

        # Check if already verified
        try:
            verify_url = f"{self.server_url}/verification/discord/{interaction.user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code == 200:
                existing_data = verify_response.json()
                existing_username = existing_data.get("roblox_username")
                await interaction.followup.send(
                    f"✅ You're already verified as **{existing_username}**!\n"
                    f"Use `/unverify` if you want to change accounts.",
                    ephemeral=True
                )
                return
        except:
            pass

        # Get Roblox ID
        roblox_id = self.get_roblox_id(roblox_username)

        if not roblox_id:
            await interaction.followup.send(
                f"❌ Could not find Roblox user **{roblox_username}**. Please check the spelling and try again.",
                ephemeral=True
            )
            return

        # Generate verification code
        code = self.generate_code()
        self.pending_verifications[interaction.user.id] = {
            "code": code,
            "roblox_username": roblox_username,
            "roblox_id": roblox_id
        }

        embed = discord.Embed(
            title="🔗 Roblox Verification",
            description="Follow these steps to verify your account:",
            color=0x3498db
        )
        embed.add_field(
            name="Step 1",
            value=f"Go to your Roblox profile settings",
            inline=False
        )
        embed.add_field(
            name="Step 2",
            value=f"Set your **About/Status** to: `{code}`",
            inline=False
        )
        embed.add_field(
            name="Step 3",
            value=f"Come back here and use `/verify_confirm`",
            inline=False
        )
        embed.add_field(
            name="Important",
            value="The verification code is case-sensitive. Make sure to copy it exactly!",
            inline=False
        )
        embed.set_footer(text=f"Verifying as: {roblox_username}")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="verify_confirm", description="Confirm your Roblox verification")
    async def verify_confirm(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Check if user has pending verification
        if interaction.user.id not in self.pending_verifications:
            await interaction.followup.send(
                "❌ You don't have a pending verification. Use `/verify <roblox_username>` first!",
                ephemeral=True
            )
            return

        pending = self.pending_verifications[interaction.user.id]
        code = pending["code"]
        roblox_username = pending["roblox_username"]
        roblox_id = pending["roblox_id"]

        # Check user's Roblox status
        status = self.check_user_status(roblox_id)

        if code in status:
            # Verification successful!
            try:
                verify_url = f"{self.server_url}/verification/"
                verify_data = {
                    "discord_id": str(interaction.user.id),
                    "roblox_username": roblox_username,
                    "roblox_id": str(roblox_id)
                }
                response = requests.post(verify_url, json=verify_data, headers=self.get_headers())

                if response.status_code == 200:
                    # Remove from pending
                    del self.pending_verifications[interaction.user.id]

                    embed = discord.Embed(
                        title="✅ Verification Successful!",
                        description=f"Your Discord account is now linked to **{roblox_username}**!",
                        color=0x00FF00
                    )
                    embed.add_field(
                        name="What's Next?",
                        value="You can now use `/spin` to get Pokemon and other bot features!",
                        inline=False
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send("❌ Failed to save verification. Please try again.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Error during verification: {e}", ephemeral=True)
        else:
            await interaction.followup.send(
                f"❌ Verification failed!\n\n"
                f"Your Roblox status does not contain the code: `{code}`\n\n"
                f"Current status: `{status[:100]}`\n\n"
                f"Make sure you've set your Roblox About/Status to exactly `{code}` and try again.",
                ephemeral=True
            )

    @app_commands.command(name="unverify", description="Unlink your Roblox account")
    async def unverify(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # Get current verification
            verify_url = f"{self.server_url}/verification/discord/{interaction.user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send("❌ You're not verified!", ephemeral=True)
                return

            verify_data = verify_response.json()
            roblox_username = verify_data.get("roblox_username")

            # Delete verification
            delete_url = f"{self.server_url}/verification/{roblox_username}"
            response = requests.delete(delete_url, headers=self.get_headers())

            if response.status_code == 200:
                await interaction.followup.send(
                    f"✅ Successfully unlinked from **{roblox_username}**",
                    ephemeral=True
                )
            else:
                await interaction.followup.send("❌ Failed to unverify. Please try again.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="whois", description="Check who a Discord user is on Roblox")
    @app_commands.describe(user="Discord user to check")
    async def whois(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user

        try:
            verify_url = f"{self.server_url}/verification/discord/{user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                roblox_username = verify_data.get("roblox_username")
                roblox_id = verify_data.get("roblox_id")

                embed = discord.Embed(
                    title=f"Verification Info: {user.display_name}",
                    color=0x3498db
                )
                embed.add_field(name="Discord", value=f"{user.mention}", inline=False)
                embed.add_field(name="Roblox Username", value=roblox_username, inline=True)
                embed.add_field(name="Roblox ID", value=roblox_id, inline=True)
                embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={roblox_id}&width=150&height=150&format=png")

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"{user.mention} is not verified!",
                    ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VerificationSystem(bot))
