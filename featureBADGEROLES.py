import requests
import asyncio
from discord.ext import commands
from discord import app_commands
import discord
import config

class BadgeRoleSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.badge_tiers = config.BADGE_TIERS

    def get_headers(self):
        return {
            "Authorization": f"Bearer {config.AUTH_TOKEN}",
            "Content-Type": "application/json"
        }

    async def ensure_badge_roles(self, guild):
        """Create badge roles if they don't exist"""
        created_roles = []

        for tier_name, tier_data in self.badge_tiers.items():
            role_name = f"Pokemon {tier_name.title()}"
            role = discord.utils.get(guild.roles, name=role_name)

            if not role:
                # Create the role
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color(tier_data["color"]),
                    reason="Created by Lugia Bot for badge system"
                )
                created_roles.append(role_name)

        return created_roles

    def get_badge_data_from_server(self, discord_id):
        """Get badge data from server (sent by Lua)"""
        try:
            url = f"{config.SERVER_URL}/badges/{discord_id}"
            response = requests.get(url, headers=self.get_headers())

            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def determine_tier(self, badge_count):
        """Determine badge tier based on badge count"""
        # Check from highest to lowest
        tier_names = ["platinum", "gold", "silver", "bronze"]

        for tier_name in tier_names:
            min_badges = self.badge_tiers[tier_name]["min_badges"]
            if badge_count >= min_badges:
                return tier_name

        return "bronze"  # Default

    async def assign_badge_role(self, member, tier):
        """Assign the appropriate badge role to a member"""
        # Remove all badge roles first
        roles_to_remove = []
        for tier_name in self.badge_tiers.keys():
            role_name = f"Pokemon {tier_name.title()}"
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role and role in member.roles:
                roles_to_remove.append(role)

        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason="Updating badge tier")

        # Add new role
        role_name = f"Pokemon {tier.title()}"
        role = discord.utils.get(member.guild.roles, name=role_name)

        if role:
            await member.add_roles(role, reason=f"Assigned {tier} tier based on badge count")
            return True

        return False

    async def wait_for_badge_data(self, discord_id, timeout=60):
        """Wait for Lua to send badge data to server"""
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            badge_data = self.get_badge_data_from_server(discord_id)

            if badge_data:
                return badge_data

            await asyncio.sleep(2)  # Check every 2 seconds

        return None

    @app_commands.command(name="check_badges", description="Check your in-game badge count and tier")
    async def check_badges(self, interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()

        if user is None:
            user = interaction.user

        # Check if already verified
        try:
            verify_url = f"{config.SERVER_URL}/verification/discord/{user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send(
                    f"❌ {'You need' if user == interaction.user else f'{user.mention} needs'} to verify first! Use `/verify`"
                )
                return

            verify_data = verify_response.json()
            roblox_username = verify_data.get("roblox_username")

        except:
            await interaction.followup.send("❌ Error checking verification status.")
            return

        # Check for existing badge data
        badge_data = self.get_badge_data_from_server(user.id)

        if badge_data:
            badge_count = badge_data.get("badge_count", 0)
            tier = self.determine_tier(badge_count)
            tier_data = self.badge_tiers[tier]

            embed = discord.Embed(
                title=f"Badge Status: {roblox_username}",
                color=tier_data["color"]
            )
            embed.add_field(name="Discord User", value=user.mention, inline=True)
            embed.add_field(name="Total Badges", value=f"🏆 {badge_count}", inline=True)
            embed.add_field(name="Current Tier", value=f"{tier.title()}", inline=True)
            embed.add_field(
                name="Max Pokemon Level",
                value=f"Level {tier_data['max_level']}",
                inline=True
            )

            # Show next tier info
            tier_names = ["bronze", "silver", "gold", "platinum"]
            current_index = tier_names.index(tier)

            if current_index < len(tier_names) - 1:
                next_tier = tier_names[current_index + 1]
                next_tier_data = self.badge_tiers[next_tier]
                badges_needed = next_tier_data["min_badges"] - badge_count

                embed.add_field(
                    name="Next Tier",
                    value=f"{next_tier.title()} ({badges_needed} more badges)",
                    inline=True
                )

            embed.set_footer(text="Use /update_badge_role to sync your role with your badge count")

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(
                f"❌ No badge data found. Use `/update_badge_role` to sync your badges from the game!",
                ephemeral=True
            )

    @app_commands.command(name="update_badge_role", description="Update your badge role (requires joining the game)")
    async def update_badge_role(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            # Ensure roles exist
            created_roles = await self.ensure_badge_roles(interaction.guild)

            # Check if verified
            verify_url = f"{config.SERVER_URL}/verification/discord/{interaction.user.id}"
            verify_response = requests.get(verify_url, headers=self.get_headers())

            if verify_response.status_code != 200:
                await interaction.followup.send("❌ You need to verify first! Use `/verify`")
                return

            verify_data = verify_response.json()
            roblox_username = verify_data.get("roblox_username")

            # Get game status
            game_status_url = f"{config.SERVER_URL}/game-status/"
            game_response = requests.get(game_status_url, headers=self.get_headers())
            game_url = "the game"

            if game_response.status_code == 200:
                game_data = game_response.json()
                if game_data.get("game_url"):
                    game_url = game_data.get("game_url")

            # Prompt user to join game
            prompt_embed = discord.Embed(
                title="🎮 Join the Game to Update Badge Role",
                description=f"**{roblox_username}**, please join the game now!",
                color=0x3498db
            )
            prompt_embed.add_field(
                name="Instructions",
                value=f"1. Join {game_url if 'http' in str(game_url) else 'Sparkling Silver'}\n"
                      f"2. Wait in the game for 5-10 seconds\n"
                      f"3. The bot will detect you and update your badge role automatically!",
                inline=False
            )
            prompt_embed.add_field(
                name="⏰ Waiting...",
                value="I'll check for your badge data for up to 60 seconds.",
                inline=False
            )

            await interaction.followup.send(embed=prompt_embed)

            # Wait for badge data from Lua
            badge_data = await self.wait_for_badge_data(interaction.user.id, timeout=60)

            if badge_data:
                badge_count = badge_data.get("badge_count", 0)
                tier = self.determine_tier(badge_count)
                tier_data = self.badge_tiers[tier]

                # Assign role
                success = await self.assign_badge_role(interaction.user, tier)

                if success:
                    result_embed = discord.Embed(
                        title="✅ Badge Role Updated!",
                        description=f"You've been assigned the **{tier.title()}** tier!",
                        color=tier_data["color"]
                    )
                    result_embed.add_field(name="Badge Count", value=f"🏆 {badge_count}", inline=True)
                    result_embed.add_field(name="Max Pokemon Level", value=f"Level {tier_data['max_level']}", inline=True)

                    await interaction.followup.send(embed=result_embed)
                else:
                    await interaction.followup.send("❌ Failed to assign badge role. Please contact an administrator.")
            else:
                timeout_embed = discord.Embed(
                    title="⏰ Timeout",
                    description="Could not detect you in the game.",
                    color=0xe74c3c
                )
                timeout_embed.add_field(
                    name="Troubleshooting",
                    value="• Make sure you're in the correct Roblox game\n"
                          "• Ensure you're logged in with your verified Roblox account\n"
                          "• Wait at least 5 seconds in the game\n"
                          "• Try again with `/update_badge_role`",
                    inline=False
                )

                await interaction.followup.send(embed=timeout_embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    @app_commands.command(name="force_badge_update", description="Force update badge role for a user (Admin only)")
    @app_commands.describe(user="Discord user to update")
    @app_commands.checks.has_permissions(administrator=True)
    async def force_badge_update(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()

        try:
            badge_data = self.get_badge_data_from_server(user.id)

            if not badge_data:
                await interaction.followup.send(f"❌ No badge data found for {user.mention}. They need to join the game first.")
                return

            badge_count = badge_data.get("badge_count", 0)
            tier = self.determine_tier(badge_count)
            tier_data = self.badge_tiers[tier]

            # Assign role
            success = await self.assign_badge_role(user, tier)

            if success:
                await interaction.followup.send(
                    f"✅ Updated {user.mention} to **{tier.title()}** tier ({badge_count} badges)"
                )
            else:
                await interaction.followup.send("❌ Failed to assign badge role.")

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    @app_commands.command(name="setup_badge_roles", description="Setup all badge roles (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_badge_roles(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            created_roles = await self.ensure_badge_roles(interaction.guild)

            if created_roles:
                embed = discord.Embed(
                    title="✅ Badge Roles Setup Complete!",
                    description="The following roles have been created:",
                    color=0x00FF00
                )

                for role_name in created_roles:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    embed.add_field(name=role_name, value=f"<@&{role.id}>", inline=False)

                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("✅ All badge roles already exist!")

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    @app_commands.command(name="badge_tiers", description="View all badge tier information")
    async def badge_tiers_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏆 Badge Tier System",
            description="Earn more in-game badges to unlock higher tiers and better Pokemon!",
            color=0x3498db
        )

        tier_names = ["bronze", "silver", "gold", "platinum"]
        for tier_name in tier_names:
            tier_data = self.badge_tiers[tier_name]
            embed.add_field(
                name=f"{tier_name.title()} Tier",
                value=f"**Min Badges:** {tier_data['min_badges']}\n"
                      f"**Max Pokemon Level:** {tier_data['max_level']}",
                inline=False
            )

        embed.set_footer(text="Use /update_badge_role to update your tier!")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BadgeRoleSystem(bot))
