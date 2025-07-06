# cogs/moderation.py
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """Commands for server moderation."""

    def __init__(self, bot):
        self.bot = bot
    
    async def send_mod_log(self, embed, action_type="Moderation"):
        """Send moderation log to the configured channel if set."""
        if hasattr(self.bot, 'mod_log_channel_id') and self.bot.mod_log_channel_id:
            try:
                channel = self.bot.get_channel(self.bot.mod_log_channel_id)
                if channel:
                    await channel.send(embed=embed)
                else:
                    logger.warning(f"Mod log channel {self.bot.mod_log_channel_id} not found")
            except Exception as e:
                logger.error(f"Failed to send mod log: {e}")

    async def cog_check(self, ctx):
        """Check if user has moderation permissions."""
        # Check if user has any moderation permissions
        if ctx.author.guild_permissions.kick_members or ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.manage_messages:
            return True
        
        # Check if user is in allowed users/roles
        if hasattr(self.bot, 'check_user_or_role_allowed'):
            return await self.bot.check_user_or_role_allowed(
                ctx.author, 
                self.bot.allowed_user_ids, 
                self.bot.allowed_role_ids
            )
        return False

    @commands.hybrid_command(name='kick', description='Kicks a member from the server.')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """Kicks the specified member from the server."""
        if member == ctx.author:
            await ctx.send("You cannot kick yourself!", ephemeral=True)
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot kick someone with a higher or equal role!", ephemeral=True)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} kicked {member} for: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick that member. Make sure my role is above theirs.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to kick: {e}", ephemeral=True)
            logger.error(f"Error kicking {member}: {e}")

    @commands.hybrid_command(name='ban', description='Bans a member from the server.')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """Bans the specified member from the server."""
        if member == ctx.author:
            await ctx.send("You cannot ban yourself!", ephemeral=True)
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot ban someone with a higher or equal role!", ephemeral=True)
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} has been banned",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} banned {member} for: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban that member. Make sure my role is above theirs.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to ban: {e}", ephemeral=True)
            logger.error(f"Error banning {member}: {e}")

    @commands.hybrid_command(name='unban', description='Unbans a user by their ID or username.')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unban(self, ctx, *, user_identifier: str):
        """Unbans a user from the server."""
        banned_users = [entry async for entry in ctx.guild.bans()]
        found_user = None

        # Try to find by ID first, then by name
        for ban_entry in banned_users:
            user = ban_entry.user
            if str(user.id) == user_identifier or str(user) == user_identifier or user.name == user_identifier:
                found_user = user
                break

        if found_user:
            try:
                await ctx.guild.unban(found_user)
                embed = discord.Embed(
                    title="Member Unbanned",
                    description=f"{found_user.mention} has been unbanned",
                    color=discord.Color.green()
                )
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                await ctx.send(embed=embed)
                logger.info(f"{ctx.author} unbanned {found_user}")
            except discord.Forbidden:
                await ctx.send("I don't have permission to unban that user.", ephemeral=True)
            except Exception as e:
                await ctx.send(f"An error occurred while trying to unban: {e}", ephemeral=True)
                logger.error(f"Error unbanning {found_user}: {e}")
        else:
            await ctx.send(f"Could not find a banned user with identifier: `{user_identifier}`", ephemeral=True)

    @commands.hybrid_command(name='timeout', description='Times out a member for a specified duration.')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timeout(self, ctx, member: discord.Member, duration: int, unit: str = "minutes", *, reason: str = "No reason provided."):
        """Times out the specified member."""
        if member == ctx.author:
            await ctx.send("You cannot timeout yourself!", ephemeral=True)
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot timeout someone with a higher or equal role!", ephemeral=True)
            return

        # Calculate timeout duration
        unit = unit.lower()
        if unit in ['s', 'sec', 'second', 'seconds']:
            delta = timedelta(seconds=duration)
        elif unit in ['m', 'min', 'minute', 'minutes']:
            delta = timedelta(minutes=duration)
        elif unit in ['h', 'hour', 'hours']:
            delta = timedelta(hours=duration)
        elif unit in ['d', 'day', 'days']:
            delta = timedelta(days=duration)
        else:
            await ctx.send("Invalid time unit. Use: seconds, minutes, hours, or days", ephemeral=True)
            return

        # Discord timeout limit is 28 days
        if delta > timedelta(days=28):
            await ctx.send("Timeout duration cannot exceed 28 days!", ephemeral=True)
            return

        try:
            await member.timeout(delta, reason=reason)
            
            # Create detailed embed for mod log
            log_embed = discord.Embed(
                title="Member Timed Out",
                description=f"{member.mention} has been timed out",
                color=discord.Color.orange()
            )
            log_embed.add_field(name="Duration", value=f"{duration} {unit}", inline=True)
            log_embed.add_field(name="Reason", value=reason, inline=False)
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            log_embed.add_field(name="Member ID", value=str(member.id), inline=True)
            log_embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
            log_embed.timestamp = datetime.utcnow()
            
            # Send only to mod log channel
            await self.send_mod_log(log_embed)
            
            # Send simple confirmation in command channel
            await ctx.send(f"✅ {member.mention} has been timed out for {duration} {unit}.", ephemeral=True)
            
            logger.info(f"{ctx.author} timed out {member} for {duration} {unit}: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to timeout that member.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to timeout: {e}", ephemeral=True)
            logger.error(f"Error timing out {member}: {e}")

    @commands.hybrid_command(name='untimeout', description='Removes timeout from a member.')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Removes timeout from the specified member."""
        if not member.is_timed_out():
            await ctx.send(f"{member.mention} is not currently timed out.", ephemeral=True)
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(
                title="Timeout Removed",
                description=f"Timeout removed from {member.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} removed timeout from {member}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to remove timeout from that member.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to remove timeout: {e}", ephemeral=True)
            logger.error(f"Error removing timeout from {member}: {e}")

    @commands.hybrid_command(name='mute', description='Mutes a member by assigning a "Muted" role.')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mute(self, ctx, member: discord.Member, duration: int = 0, *, reason: str = "No reason provided."):
        """Mutes the specified member."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role:
            await ctx.send("Error: 'Muted' role not found. Please create a role named 'Muted'.", ephemeral=True)
            return

        if muted_role in member.roles:
            await ctx.send(f"{member.mention} is already muted.", ephemeral=True)
            return

        try:
            await member.add_roles(muted_role, reason=reason)
            embed = discord.Embed(
                title="Member Muted",
                description=f"{member.mention} has been muted",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            if duration > 0:
                embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
                await ctx.send(embed=embed)
                
                # Auto-unmute after duration
                await asyncio.sleep(duration * 60)
                if muted_role in member.roles:
                    await member.remove_roles(muted_role, reason="Mute duration ended.")
                    await ctx.send(f"{member.mention} has been unmuted automatically.")
            else:
                await ctx.send(embed=embed)
            
            logger.info(f"{ctx.author} muted {member} for: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage roles.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to mute: {e}", ephemeral=True)
            logger.error(f"Error muting {member}: {e}")

    @commands.hybrid_command(name='unmute', description='Unmutes a member by removing the "Muted" role.')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes the specified member."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role or muted_role not in member.roles:
            await ctx.send(f"{member.mention} is not currently muted or the 'Muted' role doesn't exist.", ephemeral=True)
            return

        try:
            await member.remove_roles(muted_role, reason="Unmuted by moderator.")
            embed = discord.Embed(
                title="Member Unmuted",
                description=f"{member.mention} has been unmuted",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} unmuted {member}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage roles.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to unmute: {e}", ephemeral=True)
            logger.error(f"Error unmuting {member}: {e}")

    @commands.hybrid_command(name='clear', description='Deletes a specified number of messages from the channel.')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clear(self, ctx, amount: int):
        """Deletes a specified number of messages."""
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to clear.", ephemeral=True)
            return

        if amount > 100:
            await ctx.send("I can only clear up to 100 messages at a time.", ephemeral=True)
            amount = 100

        try:
            if ctx.interaction:
                await ctx.defer(ephemeral=True)
            
            deleted = await ctx.channel.purge(limit=amount)
            
            embed = discord.Embed(
                title="Messages Cleared",
                description=f"Successfully deleted {len(deleted)} messages",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            if ctx.interaction:
                await ctx.followup.send(embed=embed, ephemeral=True)
            else:
                msg = await ctx.send(embed=embed)
                await asyncio.sleep(5)
                await msg.delete()
            
            logger.info(f"{ctx.author} cleared {len(deleted)} messages in {ctx.channel}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage messages in this channel.", ephemeral=True)
        except discord.HTTPException as e:
            await ctx.send(f"Failed to clear messages: {e}. Messages older than 14 days cannot be bulk deleted.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to clear messages: {e}", ephemeral=True)
            logger.error(f"Error clearing messages: {e}")

    @commands.hybrid_command(name='warn', description='Warns a member.')
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        """Warns the specified member and sends them a DM."""
        try:
            embed = discord.Embed(
                title="Warning",
                description=f"You have been warned in {ctx.guild.name}",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.name, inline=True)
            
            await member.send(embed=embed)
            
            # Send confirmation in channel
            confirm_embed = discord.Embed(
                title="Member Warned",
                description=f"{member.mention} has been warned",
                color=discord.Color.yellow()
            )
            confirm_embed.add_field(name="Reason", value=reason, inline=False)
            confirm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=confirm_embed)
            
            logger.info(f"{ctx.author} warned {member} for: {reason}")
        except discord.Forbidden:
            await ctx.send(f"Could not DM {member.mention}. Warning issued, but DM failed.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to warn: {e}", ephemeral=True)
            logger.error(f"Error warning {member}: {e}")

    @commands.hybrid_command(name='setnick', description='Changes the nickname of a member.')
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def setnick(self, ctx, member: discord.Member, *, nickname: str = None):
        """Changes the nickname of the specified member."""
        try:
            old_nick = member.nick if member.nick else member.name
            await member.edit(nick=nickname)
            
            embed = discord.Embed(
                title="Nickname Changed",
                color=discord.Color.blue()
            )
            embed.add_field(name="Member", value=member.mention, inline=True)
            embed.add_field(name="Old Nickname", value=old_nick, inline=True)
            embed.add_field(name="New Nickname", value=nickname if nickname else "Reset", inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} changed {member}'s nickname from {old_nick} to {nickname}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change that member's nickname.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to set nickname: {e}", ephemeral=True)
            logger.error(f"Error setting nickname for {member}: {e}")

    @commands.hybrid_command(name='slowmode', description='Sets the slowmode duration for the current channel.')
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        """Sets the slowmode duration for the current channel."""
        if seconds < 0 or seconds > 21600:  # Max 6 hours
            await ctx.send("Slowmode duration must be between 0 and 21600 seconds (6 hours).", ephemeral=True)
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            
            embed = discord.Embed(
                title="Slowmode Updated",
                color=discord.Color.blue()
            )
            if seconds == 0:
                embed.description = "Slowmode has been disabled for this channel"
            else:
                embed.description = f"Slowmode set to {seconds} seconds for this channel"
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} set slowmode to {seconds} seconds in {ctx.channel}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage channels.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while trying to set slowmode: {e}", ephemeral=True)
            logger.error(f"Error setting slowmode: {e}")

async def setup(bot):
    """Adds the Moderation cog to the bot."""
    await bot.add_cog(Moderation(bot))
