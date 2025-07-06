import discord
from discord.ext import commands
import asyncio
import os
import logging
from dotenv import load_dotenv
from discord import app_commands

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_USER_IDS = [int(user_id) for user_id in os.getenv("ALLOWED_USER_IDS", "").split(',') if user_id]
DELAY = float(os.getenv("DM_DELAY", 1.5))
LOG_DMS = os.getenv("LOG_DMS", "True").lower() == "true"
ALLOWED_ROLE_IDS = {int(role_id) for role_id in os.getenv("ALLOWED_ROLE_IDS", "").split(',') if role_id}

# Check if the bot token is set
if not TOKEN:
    logger.error("DISCORD_BOT_TOKEN environment variable not found in .env file.")
    exit()

# Configure Discord Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize the bot with hybrid commands support
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Global check to restrict bot usage to allowed users only
@bot.check
async def globally_check_user(ctx):
    """Global check that restricts all commands to allowed users only."""
    if ctx.author.id in ALLOWED_USER_IDS:
        return True
    # Silently ignore commands from unauthorized users
    return False

async def send_dm_to_members(ctx, members_to_dm, message, delay, log_dms):
    """Helper function to send DMs to a list of members."""
    total_members = len(members_to_dm)
    if total_members == 0:
        if hasattr(ctx, 'send'):
            await ctx.send("No eligible members found for DM.", ephemeral=True)
        else:
            await ctx.followup.send("No eligible members found for DM.", ephemeral=True)
        return

    if hasattr(ctx, 'send'):
        await ctx.send(
            f"Attempting to DM {total_members} members. This may take a while due to delays.",
            ephemeral=True
        )
    else:
        await ctx.followup.send(
            f"Attempting to DM {total_members} members. This may take a while due to delays.",
            ephemeral=True
        )

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for member in members_to_dm:
        if member == bot.user:
            if log_dms:
                logger.info(f"Skipping self: {member.name}")
            skipped_count += 1
            continue

        if member.bot:
            if log_dms:
                logger.info(f"Skipping bot: {member.name}")
            skipped_count += 1
            continue

        try:
            await member.send(message)
            if log_dms:
                logger.info(f"Successfully sent DM to {member.name} ({member.id})")
            sent_count += 1
        except discord.errors.Forbidden:
            if log_dms:
                logger.warning(f"Failed to send DM to {member.name} ({member.id}): DMs are closed or blocked.")
            failed_count += 1
        except Exception as e:
            if log_dms:
                logger.error(f"Unexpected error sending DM to {member.name} ({member.id}): {e}")
            failed_count += 1
        finally:
            await asyncio.sleep(delay)

    result_message = (
        f"DM operation complete!\n"
        f"Sent: {sent_count}\n"
        f"Skipped (self/bots): {skipped_count}\n"
        f"Failed (DMs off/error): {failed_count}\n"
        f"Total attempted: {total_members}"
    )

    if hasattr(ctx, 'send'):
        await ctx.send(result_message, ephemeral=True)
    else:
        await ctx.followup.send(result_message, ephemeral=True)

    logger.info(f"DM operation finished for guild {ctx.guild.name if ctx.guild else 'DM'}.")

# --- CHECK FUNCTIONS ---
async def check_allowed_users(user_id, allowed_user_ids) -> bool:
    """Checks if the user's ID is in the ALLOWED_USER_IDS list."""
    return user_id in allowed_user_ids

async def check_allowed_roles(user, allowed_role_ids) -> bool:
    """Checks if the user has any of the allowed role IDs."""
    if user.guild:
        member = user.guild.get_member(user.id)
        if member:
            return any(role.id in allowed_role_ids for role in member.roles)
    return False

async def check_user_or_role_allowed(user, allowed_user_ids, allowed_role_ids) -> bool:
    """Checks if the user is in ALLOWED_USER_IDS OR has any of the ALLOWED_ROLE_IDS."""
    is_user_allowed = await check_allowed_users(user.id, allowed_user_ids)
    is_role_allowed = await check_allowed_roles(user, allowed_role_ids)
    return is_user_allowed or is_role_allowed

# --- HYBRID DM COMMANDS ---
@bot.hybrid_command(
    name="dmall_roles",
    description="Sends a direct message to all members of specified roles."
)
async def dmall_roles_command(ctx, target_role: discord.Role, *, message: str):
    """Hybrid command to send a DM to members of a specific role."""
    # Check permissions
    if not await check_user_or_role_allowed(ctx.author, ALLOWED_USER_IDS, ALLOWED_ROLE_IDS):
        await ctx.send("You are not authorized to use this command.", ephemeral=True)
        return

    if not ctx.guild:
        await ctx.send("This command can only be used in a server.", ephemeral=True)
        return

    # Defer the response for long operations
    if ctx.interaction:
        await ctx.defer(ephemeral=True)

    members_to_dm = [member for member in target_role.members]
    await send_dm_to_members(ctx, members_to_dm, message, DELAY, LOG_DMS)

@bot.hybrid_command(
    name="dmall_server",
    description="Sends a direct message to ALL members of the server (use with caution!)."
)
async def dmall_server_command(ctx, *, message: str):
    """Hybrid command to send a DM to all members in the server."""
    # Check permissions
    if not await check_user_or_role_allowed(ctx.author, ALLOWED_USER_IDS, ALLOWED_ROLE_IDS):
        await ctx.send("You are not authorized to use this command.", ephemeral=True)
        return

    if not ctx.guild:
        await ctx.send("This command can only be used in a server.", ephemeral=True)
        return

    # Defer the response for long operations
    if ctx.interaction:
        await ctx.defer(ephemeral=True)

    members_to_dm = [member for member in ctx.guild.members]
    await send_dm_to_members(ctx, members_to_dm, message, DELAY, LOG_DMS)

@bot.hybrid_command(
    name="dmuser",
    description="Sends a direct message to a specific user."
)
async def dmuser_command(ctx, target_user: discord.Member, *, message: str):
    """Hybrid command to send a DM to a specific user."""
    # Check permissions
    if not await check_user_or_role_allowed(ctx.author, ALLOWED_USER_IDS, ALLOWED_ROLE_IDS):
        await ctx.send("You are not authorized to use this command.", ephemeral=True)
        return

    try:
        await target_user.send(message)
        await ctx.send(f"Successfully sent DM to {target_user.name}.", ephemeral=True)
        if LOG_DMS:
            logger.info(f"Successfully sent DM to {target_user.name} ({target_user.id})")
    except discord.errors.Forbidden:
        await ctx.send(
            f"Failed to send DM to {target_user.name}. Their DMs might be closed or they might have blocked the bot.",
            ephemeral=True
        )
        if LOG_DMS:
            logger.warning(f"Failed to send DM to {target_user.name} ({target_user.id}): DMs are closed or blocked.")
    except Exception as e:
        await ctx.send(
            f"An unexpected error occurred while sending DM to {target_user.name}: {e}",
            ephemeral=True
        )
        if LOG_DMS:
            logger.error(f"Unexpected error sending DM to {target_user.name} ({target_user.id}): {e}")

# --- HELP COMMAND ---
@bot.hybrid_command(name="help", description="Shows help information for bot commands.")
async def help_command(ctx, *, command_name: str = None):
    """Custom help command with better formatting."""
    if command_name:
        # Show help for specific command
        cmd = bot.get_command(command_name)
        if cmd:
            embed = discord.Embed(
                title=f"Help: {cmd.name}",
                description=cmd.description or "No description available.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Usage", value=f"`!{cmd.name} {cmd.signature}`", inline=False)
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
        else:
            embed = discord.Embed(
                title="Command Not Found",
                description=f"No command named '{command_name}' found.",
                color=discord.Color.red()
            )
    else:
        # Show general help
        embed = discord.Embed(
            title="Bot Commands Help",
            description="Here are all available commands. Use `!help <command>` for more details.",
            color=discord.Color.blue()
        )
        
        # Group commands by cog
        cogs = {}
        for command in bot.commands:
            if command.cog:
                cog_name = command.cog.qualified_name
            else:
                cog_name = "General"
            
            if cog_name not in cogs:
                cogs[cog_name] = []
            cogs[cog_name].append(command.name)
        
        for cog_name, commands_list in cogs.items():
            embed.add_field(
                name=cog_name,
                value=", ".join(f"`{cmd}`" for cmd in commands_list),
                inline=False
            )
    
    await ctx.send(embed=embed, ephemeral=True)

# --- COG LOADING ---
async def load_extensions():
    """Load all cog extensions."""
    cog_files = [
        "admin", "moderation", "general", "fun", 
        "games", "info", "misc", "utility"
    ]
    
    for cog_name in cog_files:
        try:
            await bot.load_extension(f'cogs.{cog_name}')
            logger.info(f"Loaded cog: {cog_name}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog_name}: {e}")

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Bot is in {len(bot.guilds)} guild(s).")
    
    # Store configuration on bot instance for cogs to access
    bot.allowed_user_ids = ALLOWED_USER_IDS
    bot.allowed_role_ids = ALLOWED_ROLE_IDS
    bot.check_allowed_users = check_allowed_users
    bot.check_allowed_roles = check_allowed_roles
    bot.check_user_or_role_allowed = check_user_or_role_allowed

    # Load cogs
    await load_extensions()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} global command(s).")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    # Silently ignore CheckFailure errors (unauthorized users)
    if isinstance(error, commands.CheckFailure):
        return
    
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            f"Command '{ctx.invoked_with}' not found. Use `!help` to see available commands.",
            ephemeral=True
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You don't have the necessary permissions to run this command.",
            ephemeral=True
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"Missing argument: {error.param.name}. Use `!help {ctx.command.name}` for usage information.",
            ephemeral=True
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            f"Invalid argument provided. Use `!help {ctx.command.name}` for usage information.",
            ephemeral=True
        )
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    else:
        logger.error(f"Unhandled command error: {error}")
        await ctx.send(
            "An unexpected error occurred while processing your command. The error has been logged.",
            ephemeral=True
        )

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global slash command error handler."""
    # Silently ignore CheckFailure errors (unauthorized users)
    if isinstance(error, app_commands.CheckFailure):
        return
    
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    else:
        logger.error(f"Unhandled app command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "An error occurred while processing this command. The error has been logged.",
                ephemeral=True
            )

# --- RUN THE BOT ---
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
