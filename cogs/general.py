# cogs/general.py
import discord
from discord.ext import commands
import asyncio
import random

class General(commands.Cog):
    """General purpose commands for everyone to use."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', description='Shows bot latency.')
    async def ping(self, ctx):
        """Shows the bot's latency."""
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='serverinfo', description='Shows information about the current server.')
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Shows information about the current server."""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"Server Info: {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        
        if guild.description:
            embed.add_field(name="Description", value=guild.description, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='userinfo', description='Shows information about a user.')
    async def userinfo(self, ctx, member: discord.Member = None):
        """Shows information about a user."""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"User Info: {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="Username", value=str(member), inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        
        roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
        if roles:
            embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles), inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='avatar', description='Shows a user\'s avatar.')
    async def avatar(self, ctx, member: discord.Member = None):
        """Shows a user's avatar."""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=discord.Color.blue()
        )
        embed.set_image(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='say', description='Makes the bot say something.')
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, message: str):
        """Makes the bot say something."""
        # Delete the command message if it's a regular command
        if not ctx.interaction:
            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass
        
        await ctx.send(message)

    @commands.hybrid_command(name='embed', description='Creates an embed message.')
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, title: str, *, description: str):
        """Creates an embed message."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Created by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='poll', description='Creates a simple yes/no poll.')
    async def poll(self, ctx, *, question: str):
        """Creates a simple yes/no poll."""
        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @commands.hybrid_command(name='choose', description='Randomly chooses from given options.')
    async def choose(self, ctx, *, choices: str):
        """Randomly chooses from given options separated by commas."""
        options = [choice.strip() for choice in choices.split(',')]
        
        if len(options) < 2:
            await ctx.send("Please provide at least 2 options separated by commas.", ephemeral=True)
            return
        
        chosen = random.choice(options)
        
        embed = discord.Embed(
            title="🎲 Random Choice",
            description=f"I choose: **{chosen}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Options", value=", ".join(options), inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='afk', description='Sets your AFK status.')
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Sets your AFK status."""
        # This is a simple implementation - in a real bot you'd store this in a database
        embed = discord.Embed(
            title="💤 AFK",
            description=f"{ctx.author.mention} is now AFK: {reason}",
            color=discord.Color.orange()
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Adds the General cog to the bot."""
    await bot.add_cog(General(bot))
