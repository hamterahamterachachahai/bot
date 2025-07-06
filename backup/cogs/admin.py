# cogs/admin.py
import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import logging

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    """Commands for bot administration (owner-only or specific roles)."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Global check for the Admin cog."""
        # Allow bot owner
        if await self.bot.is_owner(ctx.author):
            return True
        
        # Allow users with allowed roles or IDs
        if hasattr(self.bot, 'check_user_or_role_allowed'):
            return await self.bot.check_user_or_role_allowed(
                ctx.author, 
                self.bot.allowed_user_ids, 
                self.bot.allowed_role_ids
            )
        return False

    @commands.hybrid_command(name='load_cog', description='Loads a specified cog.')
    @commands.is_owner()
    async def load_cog(self, ctx, cog_name: str):
        """Loads a specified cog."""
        try:
            await self.bot.load_extension(f'cogs.{cog_name}')
            await ctx.send(f'Successfully loaded cog: `{cog_name}`', ephemeral=True)
            logger.info(f"Loaded cog: {cog_name}")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f'Cog `{cog_name}` is already loaded.', ephemeral=True)
        except commands.ExtensionNotFound:
            await ctx.send(
                f'Cog `{cog_name}` not found. Ensure it\'s in the cogs folder and spelled correctly.', 
                ephemeral=True
            )
        except Exception as e:
            await ctx.send(f'Failed to load cog `{cog_name}`: {e}', ephemeral=True)
            logger.error(f"Failed to load cog {cog_name}: {e}")

    @commands.hybrid_command(name='unload_cog', description='Unloads a specified cog.')
    @commands.is_owner()
    async def unload_cog(self, ctx, cog_name: str):
        """Unloads a specified cog."""
        if cog_name == 'admin':
            await ctx.send("Cannot unload the admin cog.", ephemeral=True)
            return

        try:
            await self.bot.unload_extension(f'cogs.{cog_name}')
            await ctx.send(f'Successfully unloaded cog: `{cog_name}`', ephemeral=True)
            logger.info(f"Unloaded cog: {cog_name}")
        except commands.ExtensionNotLoaded:
            await ctx.send(f'Cog `{cog_name}` is not loaded.', ephemeral=True)
        except commands.ExtensionNotFound:
            await ctx.send(f'Cog `{cog_name}` not found.', ephemeral=True)
        except Exception as e:
            await ctx.send(f'Failed to unload cog `{cog_name}`: {e}', ephemeral=True)
            logger.error(f"Failed to unload cog {cog_name}: {e}")

    @commands.hybrid_command(name='reload_cog', description='Reloads a specified cog.')
    @commands.is_owner()
    async def reload_cog(self, ctx, cog_name: str):
        """Reloads a specified cog."""
        try:
            await self.bot.reload_extension(f'cogs.{cog_name}')
            await ctx.send(f'Successfully reloaded cog: `{cog_name}`', ephemeral=True)
            logger.info(f"Reloaded cog: {cog_name}")
        except commands.ExtensionNotLoaded:
            await ctx.send(
                f'Cog `{cog_name}` is not loaded. Attempting to load it instead.',
                ephemeral=True
            )
            try:
                await self.bot.load_extension(f'cogs.{cog_name}')
                await ctx.send(f'Successfully loaded cog: `{cog_name}`', ephemeral=True)
                logger.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                await ctx.send(f'Failed to load cog `{cog_name}`: {e}', ephemeral=True)
                logger.error(f"Failed to load cog {cog_name}: {e}")
        except commands.ExtensionNotFound:
            await ctx.send(f'Cog `{cog_name}` not found.', ephemeral=True)
        except Exception as e:
            await ctx.send(f'Failed to reload cog `{cog_name}`: {e}', ephemeral=True)
            logger.error(f"Failed to reload cog {cog_name}: {e}")

    @commands.hybrid_command(name='shutdown', description='Shuts down the bot.')
    @commands.is_owner()
    async def shutdown_bot(self, ctx):
        """Shuts down the bot."""
        await ctx.send("Shutting down...", ephemeral=True)
        logger.info("Bot shutdown initiated by owner")
        await self.bot.close()

    @commands.hybrid_command(name='set_status', description='Sets the bot\'s activity status.')
    @app_commands.choices(
        activity_type=[
            discord.app_commands.Choice(name='Playing', value='playing'),
            discord.app_commands.Choice(name='Listening', value='listening'),
            discord.app_commands.Choice(name='Watching', value='watching'),
            discord.app_commands.Choice(name='Streaming', value='streaming'),
        ]
    )
    async def set_status(self, ctx, activity_type: str, *, message: str):
        """Sets the bot's activity status."""
        activity = None
        
        if activity_type == 'playing':
            activity = discord.Game(name=message)
        elif activity_type == 'listening':
            activity = discord.Activity(type=discord.ActivityType.listening, name=message)
        elif activity_type == 'watching':
            activity = discord.Activity(type=discord.ActivityType.watching, name=message)
        elif activity_type == 'streaming':
            activity = discord.Activity(
                type=discord.ActivityType.streaming, 
                name=message,
                url="https://www.twitch.tv/discord"
            )
        else:
            await ctx.send(
                "Invalid activity type. Choose from `playing`, `listening`, `watching`, `streaming`.",
                ephemeral=True
            )
            return

        await self.bot.change_presence(activity=activity)
        await ctx.send(f"Bot status set to: {activity_type.capitalize()} {message}", ephemeral=True)
        logger.info(f"Bot status changed to: {activity_type} {message}")

    @commands.hybrid_command(name='sync_commands', description='Syncs slash commands globally.')
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """Syncs slash commands globally."""
        try:
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} application commands globally.", ephemeral=True)
            logger.info(f"Synced {len(synced)} commands globally")
        except Exception as e:
            await ctx.send(f"Error syncing commands: {e}", ephemeral=True)
            logger.error(f"Error syncing commands: {e}")

    @commands.hybrid_command(name='list_cogs', description='Lists all loaded cogs.')
    async def list_cogs(self, ctx):
        """Lists all loaded cogs."""
        cogs = list(self.bot.cogs.keys())
        if cogs:
            embed = discord.Embed(
                title="Loaded Cogs",
                description="\n".join(f"• {cog}" for cog in cogs),
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="Loaded Cogs",
                description="No cogs loaded.",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name='botdetails', description='Shows bot information.')
    async def botdetails(self, ctx):
        """Shows bot information."""
        embed = discord.Embed(
            title="Bot Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        embed.add_field(name="Cogs", value=len(self.bot.cogs), inline=True)
        
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    """Adds the Admin cog to the bot."""
    await bot.add_cog(Admin(bot))
