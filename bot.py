import os
import asyncio
import discord
from discord.ext import commands
import config

# ASCII Art Banner
BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██╗     ██╗   ██╗ ██████╗ ██╗ █████╗     ██████╗  ██████╗ ████████╗   ║
║   ██║     ██║   ██║██╔════╝ ██║██╔══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝   ║
║   ██║     ██║   ██║██║  ███╗██║███████║    ██████╔╝██║   ██║   ██║      ║
║   ██║     ██║   ██║██║   ██║██║██╔══██║    ██╔══██╗██║   ██║   ██║      ║
║   ███████╗╚██████╔╝╚██████╔╝██║██║  ██║    ██████╔╝╚██████╔╝   ██║      ║
║   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝      ║
║                                                           ║
║              Pokemon Discord Bot with Roblox Integration              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

class LugiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Load all feature cogs"""
        print("Loading feature modules...")

        features = [
            "featureGIFDATA",
            "featureSPAWNER",
            "featureCURRENCY",
            "featureVERIFICATION",
            "featureBADGEROLES",
            "featureUPLOADANDSTATUS"
        ]

        for feature in features:
            try:
                await self.load_extension(feature)
                print(f"  ✓ Loaded {feature}")
            except Exception as e:
                print(f"  ✗ Failed to load {feature}: {e}")

        # Sync commands
        print("\nSyncing slash commands...")
        try:
            synced = await self.tree.sync()
            print(f"  ✓ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"  ✗ Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when bot is ready"""
        print("\n" + "="*60)
        print(f"Bot is online as: {self.user.name} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guild(s)")
        print(f"Server URL: {config.SERVER_URL}")
        print("="*60)

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Sparkling Silver | /help"
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        print(f"\n✓ Joined new guild: {guild.name} (ID: {guild.id})")

        # Try to send a welcome message
        if guild.system_channel:
            embed = discord.Embed(
                title="Thanks for adding Lugia Bot!",
                description="I'm a Pokemon bot with Roblox integration for Sparkling Silver.",
                color=0x3498db
            )
            embed.add_field(
                name="Getting Started",
                value="• Use `/verify` to link your Roblox account\n"
                      "• Use `/badge_tiers` to see badge role info\n"
                      "• Use `/daily` to claim free spins\n"
                      "• Use `/game_status` to check the game",
                inline=False
            )
            embed.add_field(
                name="Admin Commands",
                value="• `/setup_badge_roles` - Create badge roles\n"
                      "• `/spawn_pokemon` - Spawn Pokemon for players\n"
                      "• `/give_currency` - Give coins to players",
                inline=False
            )

            try:
                await guild.system_channel.send(embed=embed)
            except:
                pass

    async def on_command_error(self, ctx, error):
        """Global command error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        else:
            print(f"Error: {error}")
            await ctx.send("❌ An error occurred while executing the command.")

    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Global slash command error handler"""
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s",
                ephemeral=True
            )
        else:
            print(f"Slash command error: {error}")
            try:
                await interaction.response.send_message(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True
                )
            except:
                pass


def check_config():
    """Check if configuration is valid"""
    if not config.BOT_TOKEN:
        print("\n❌ ERROR: BOT_TOKEN is not set in config.py")
        print("Please add your Discord bot token to config.py")
        return False

    if config.SERVER_URL == "http://localhost:3000":
        print("\n⚠️  WARNING: SERVER_URL is set to localhost")
        print("Make sure the Node.js server is running: cd server && npm start")

    return True


def main():
    """Main entry point"""
    print(BANNER)

    # Check configuration
    if not check_config():
        return

    # Create bot instance
    bot = LugiaBot()

    # Run bot
    print("\nStarting bot...")
    print("Press Ctrl+C to stop\n")

    try:
        bot.run(config.BOT_TOKEN)
    except discord.LoginFailure:
        print("\n❌ ERROR: Invalid bot token")
        print("Please check your BOT_TOKEN in config.py")
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down bot...")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
