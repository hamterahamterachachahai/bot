# cogs/utility.py
import discord
from discord.ext import commands
import datetime
import re
import asyncio

class Utility(commands.Cog):
    """Utility commands for server management and user convenience."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='timestamp', description='Convert time to Discord timestamp format.')
    async def timestamp(self, ctx, *, time_input: str):
        """Convert time to Discord timestamp format."""
        # This is a simplified implementation
        # In a real bot, you'd want more robust time parsing
        try:
            # Try parsing common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M", 
                "%Y-%m-%d",
                "%H:%M:%S",
                "%H:%M"
            ]
            
            parsed_time = None
            for fmt in formats:
                try:
                    if fmt.startswith("%H"):
                        # For time-only formats, use today's date
                        today = datetime.date.today()
                        time_part = datetime.datetime.strptime(time_input, fmt).time()
                        parsed_time = datetime.datetime.combine(today, time_part)
                    else:
                        parsed_time = datetime.datetime.strptime(time_input, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                await ctx.send("Invalid time format! Try: YYYY-MM-DD HH:MM:SS or HH:MM", ephemeral=True)
                return
            
            timestamp = int(parsed_time.timestamp())
            
            embed = discord.Embed(
                title="🕐 Discord Timestamps",
                color=discord.Color.blue()
            )
            
            formats_display = [
                ("Short Time", f"<t:{timestamp}:t>", f"`<t:{timestamp}:t>`"),
                ("Long Time", f"<t:{timestamp}:T>", f"`<t:{timestamp}:T>`"),
                ("Short Date", f"<t:{timestamp}:d>", f"`<t:{timestamp}:d>`"),
                ("Long Date", f"<t:{timestamp}:D>", f"`<t:{timestamp}:D>`"),
                ("Short Date/Time", f"<t:{timestamp}:f>", f"`<t:{timestamp}:f>`"),
                ("Long Date/Time", f"<t:{timestamp}:F>", f"`<t:{timestamp}:F>`"),
                ("Relative", f"<t:{timestamp}:R>", f"`<t:{timestamp}:R>`"),
            ]
            
            for name, display, code in formats_display:
                embed.add_field(name=name, value=f"{display}\n{code}", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error processing time: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name='math', description='Perform basic math calculations.')
    async def math(self, ctx, *, expression: str):
        """Perform basic math calculations."""
        # Security: only allow basic math operations
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            await ctx.send("Only basic math operations are allowed (+, -, *, /, parentheses)", ephemeral=True)
            return
        
        # Remove any dangerous patterns
        if any(word in expression.lower() for word in ['import', 'exec', 'eval', '__']):
            await ctx.send("Invalid expression!", ephemeral=True)
            return
        
        try:
            # Safely evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {})
            
            embed = discord.Embed(
                title="🧮 Calculator",
                color=discord.Color.blue()
            )
            embed.add_field(name="Expression", value=f"`{expression}`", inline=False)
            embed.add_field(name="Result", value=f"`{result}`", inline=False)
            
            await ctx.send(embed=embed)
            
        except ZeroDivisionError:
            await ctx.send("Error: Division by zero!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Error in calculation: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name='encode', description='Encode text in various formats.')
    async def encode_text(self, ctx, method: str, *, text: str):
        """Encode text in various formats."""
        method = method.lower()
        
        try:
            if method == 'url':
                import urllib.parse
                result = urllib.parse.quote(text)
            elif method == 'html':
                import html
                result = html.escape(text)
            elif method == 'base64':
                import base64
                result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            elif method == 'morse':
                # Simple morse code implementation
                morse_code = {
                    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
                    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
                    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
                    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                    'Y': '-.--', 'Z': '--..',
                    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
                    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
                    ' ': '/'
                }
                result = ' '.join(morse_code.get(char.upper(), char) for char in text)
            else:
                await ctx.send("Supported methods: url, html, base64, morse", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"🔒 {method.upper()} Encoding",
                color=discord.Color.blue()
            )
            embed.add_field(name="Original", value=f"```{text}```", inline=False)
            embed.add_field(name="Encoded", value=f"```{result}```", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error encoding text: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name='shorten', description='Create a shortened version of text.')
    async def shorten_text(self, ctx, max_length: int, *, text: str):
        """Create a shortened version of text."""
        if max_length < 10 or max_length > 1000:
            await ctx.send("Max length must be between 10 and 1000 characters!", ephemeral=True)
            return
        
        if len(text) <= max_length:
            await ctx.send("Text is already shorter than the specified length!", ephemeral=True)
            return
        
        shortened = text[:max_length-3] + "..."
        
        embed = discord.Embed(
            title="✂️ Text Shortener",
            color=discord.Color.blue()
        )
        embed.add_field(name=f"Original ({len(text)} chars)", value=text[:100] + ("..." if len(text) > 100 else ""), inline=False)
        embed.add_field(name=f"Shortened ({len(shortened)} chars)", value=shortened, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='wordcount', description='Count words and characters in text.')
    async def word_count(self, ctx, *, text: str):
        """Count words and characters in text."""
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        word_count = len(text.split())
        line_count = text.count('\n') + 1
        
        embed = discord.Embed(
            title="📊 Text Statistics",
            color=discord.Color.blue()
        )
        embed.add_field(name="Characters", value=char_count, inline=True)
        embed.add_field(name="Characters (no spaces)", value=char_count_no_spaces, inline=True)
        embed.add_field(name="Words", value=word_count, inline=True)
        embed.add_field(name="Lines", value=line_count, inline=True)
        
        # Show a preview of the text
        preview = text[:100] + ("..." if len(text) > 100 else "")
        embed.add_field(name="Text Preview", value=f"```{preview}```", inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='case', description='Convert text case.')
    async def convert_case(self, ctx, case_type: str, *, text: str):
        """Convert text case."""
        case_type = case_type.lower()
        
        if case_type == 'upper':
            result = text.upper()
        elif case_type == 'lower':
            result = text.lower()
        elif case_type == 'title':
            result = text.title()
        elif case_type == 'capitalize':
            result = text.capitalize()
        elif case_type == 'swap':
            result = text.swapcase()
        else:
            await ctx.send("Supported cases: upper, lower, title, capitalize, swap", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🔤 {case_type.title()} Case",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=f"```{text}```", inline=False)
        embed.add_field(name="Converted", value=f"```{result}```", inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='search', description='Search for text in the channel history.')
    @commands.has_permissions(read_message_history=True)
    async def search_messages(self, ctx, *, query: str):
        """Search for text in the channel history."""
        if len(query) < 3:
            await ctx.send("Search query must be at least 3 characters long!", ephemeral=True)
            return
        
        await ctx.defer(ephemeral=True)
        
        found_messages = []
        search_limit = 100  # Limit search to last 100 messages
        
        async for message in ctx.channel.history(limit=search_limit):
            if query.lower() in message.content.lower():
                found_messages.append(message)
                if len(found_messages) >= 5:  # Limit results
                    break
        
        if not found_messages:
            await ctx.followup.send(f"No messages found containing '{query}' in the last {search_limit} messages.")
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results for '{query}'",
            description=f"Found {len(found_messages)} messages:",
            color=discord.Color.blue()
        )
        
        for i, msg in enumerate(found_messages, 1):
            content = msg.content
            if len(content) > 100:
                content = content[:100] + "..."
            
            embed.add_field(
                name=f"Result {i} - {msg.author.display_name}",
                value=f"{content}\n[Jump to message]({msg.jump_url})",
                inline=False
            )
        
        await ctx.followup.send(embed=embed)

    @commands.hybrid_command(name='purge_user', description='Delete messages from a specific user.')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge_user(self, ctx, user: discord.Member, amount: int = 10):
        """Delete messages from a specific user."""
        if amount < 1 or amount > 100:
            await ctx.send("Amount must be between 1 and 100!", ephemeral=True)
            return
        
        await ctx.defer(ephemeral=True)
        
        def check(message):
            return message.author == user
        
        try:
            deleted = await ctx.channel.purge(limit=amount*2, check=check)  # Search more messages to find user's messages
            
            embed = discord.Embed(
                title="🗑️ Messages Purged",
                description=f"Deleted {len(deleted)} messages from {user.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.followup.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.followup.send("I don't have permission to delete messages in this channel.")
        except Exception as e:
            await ctx.followup.send(f"An error occurred: {str(e)}")

async def setup(bot):
    """Adds the Utility cog to the bot."""
    await bot.add_cog(Utility(bot))
