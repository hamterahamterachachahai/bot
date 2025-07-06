# cogs/info.py
import discord
from discord.ext import commands
import psutil
import platform
import datetime

class Info(commands.Cog):
    """Information and statistics commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='botinfo', description='Shows detailed information about the bot.')
    async def botinfo(self, ctx):
        """Shows detailed information about the bot."""
        # Get system info
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()
        
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=discord.Color.blue()
        )
        
        # Bot avatar
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # Basic info
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Created", value=self.bot.user.created_at.strftime("%B %d, %Y"), inline=True)
        
        # Statistics
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        
        # Performance
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory_usage:.1f} MB", inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage:.1f}%", inline=True)
        
        # System info
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Platform", value=platform.system(), inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='uptime', description='Shows how long the bot has been running.')
    async def uptime(self, ctx):
        """Shows how long the bot has been running."""
        if not hasattr(self.bot, 'start_time'):
            # If start_time isn't set, calculate from process start
            process = psutil.Process()
            start_time = datetime.datetime.fromtimestamp(process.create_time())
        else:
            start_time = self.bot.start_time
        
        uptime = datetime.datetime.now() - start_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = ""
        if days:
            uptime_str += f"{days}d "
        if hours:
            uptime_str += f"{hours}h "
        if minutes:
            uptime_str += f"{minutes}m "
        uptime_str += f"{seconds}s"
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"I've been running for **{uptime_str}**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Started", value=start_time.strftime("%B %d, %Y at %I:%M %p"), inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='stats', description='Shows bot statistics.')
    async def stats(self, ctx):
        """Shows bot statistics."""
        # Count various statistics
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        text_channels = sum(len(guild.text_channels) for guild in self.bot.guilds)
        voice_channels = sum(len(guild.voice_channels) for guild in self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Total Members", value=total_members, inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="Cogs Loaded", value=len(self.bot.cogs), inline=True)
        
        # System stats
        memory = psutil.virtual_memory()
        embed.add_field(name="System Memory", value=f"{memory.percent}% used", inline=True)
        embed.add_field(name="System CPU", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(name="Disk Usage", value=f"{psutil.disk_usage('/').percent}%", inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='permissions', description='Shows the bot\'s permissions in this server.')
    @commands.guild_only()
    async def permissions(self, ctx):
        """Shows the bot's permissions in this server."""
        permissions = ctx.guild.me.guild_permissions
        
        # List of important permissions to check
        important_perms = [
            ('send_messages', 'Send Messages'),
            ('read_messages', 'Read Messages'),
            ('embed_links', 'Embed Links'),
            ('attach_files', 'Attach Files'),
            ('read_message_history', 'Read Message History'),
            ('add_reactions', 'Add Reactions'),
            ('kick_members', 'Kick Members'),
            ('ban_members', 'Ban Members'),
            ('manage_messages', 'Manage Messages'),
            ('manage_roles', 'Manage Roles'),
            ('manage_channels', 'Manage Channels'),
            ('manage_nicknames', 'Manage Nicknames'),
            ('moderate_members', 'Moderate Members'),
            ('administrator', 'Administrator')
        ]
        
        embed = discord.Embed(
            title=f"🔐 Bot Permissions in {ctx.guild.name}",
            color=discord.Color.blue()
        )
        
        granted = []
        denied = []
        
        for perm_name, perm_display in important_perms:
            if getattr(permissions, perm_name):
                granted.append(perm_display)
            else:
                denied.append(perm_display)
        
        if granted:
            embed.add_field(
                name="✅ Granted Permissions",
                value="\n".join(f"• {perm}" for perm in granted),
                inline=False
            )
        
        if denied:
            embed.add_field(
                name="❌ Missing Permissions",
                value="\n".join(f"• {perm}" for perm in denied),
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='channelinfo', description='Shows information about the current channel.')
    async def channelinfo(self, ctx):
        """Shows information about the current channel."""
        channel = ctx.channel
        
        embed = discord.Embed(
            title=f"📝 Channel Info: #{channel.name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Channel ID", value=channel.id, inline=True)
        embed.add_field(name="Channel Type", value=str(channel.type).title(), inline=True)
        embed.add_field(name="Created", value=channel.created_at.strftime("%B %d, %Y"), inline=True)
        
        if hasattr(channel, 'topic') and channel.topic:
            embed.add_field(name="Topic", value=channel.topic, inline=False)
        
        if hasattr(channel, 'slowmode_delay') and channel.slowmode_delay:
            embed.add_field(name="Slowmode", value=f"{channel.slowmode_delay} seconds", inline=True)
        
        if hasattr(channel, 'nsfw'):
            embed.add_field(name="NSFW", value="Yes" if channel.nsfw else "No", inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='roleinfo', description='Shows information about a role.')
    @commands.guild_only()
    async def roleinfo(self, ctx, *, role: discord.Role):
        """Shows information about a role."""
        embed = discord.Embed(
            title=f"👥 Role Info: {role.name}",
            color=role.color if role.color != discord.Color.default() else discord.Color.blue()
        )
        
        embed.add_field(name="Role ID", value=role.id, inline=True)
        embed.add_field(name="Created", value=role.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
        
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Managed", value="Yes" if role.managed else "No", inline=True)
        
        # Show some key permissions
        key_perms = []
        if role.permissions.administrator:
            key_perms.append("Administrator")
        if role.permissions.manage_guild:
            key_perms.append("Manage Server")
        if role.permissions.manage_roles:
            key_perms.append("Manage Roles")
        if role.permissions.ban_members:
            key_perms.append("Ban Members")
        if role.permissions.kick_members:
            key_perms.append("Kick Members")
        
        if key_perms:
            embed.add_field(name="Key Permissions", value=", ".join(key_perms), inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Adds the Info cog to the bot."""
    await bot.add_cog(Info(bot))
