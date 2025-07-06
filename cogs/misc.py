# cogs/misc.py
import discord
from discord.ext import commands
import random
import asyncio
import json
import datetime

class Misc(commands.Cog):
    """Miscellaneous utility commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='remind', description='Set a reminder for yourself.')
    async def remind(self, ctx, time: int, unit: str, *, reminder: str):
        """Set a reminder for yourself."""
        unit = unit.lower()
        
        # Convert time to seconds
        if unit in ['s', 'sec', 'second', 'seconds']:
            seconds = time
        elif unit in ['m', 'min', 'minute', 'minutes']:
            seconds = time * 60
        elif unit in ['h', 'hour', 'hours']:
            seconds = time * 3600
        elif unit in ['d', 'day', 'days']:
            seconds = time * 86400
        else:
            await ctx.send("Invalid time unit! Use: seconds, minutes, hours, or days", ephemeral=True)
            return
        
        # Limit maximum reminder time
        if seconds > 2592000:  # 30 days
            await ctx.send("Reminder time cannot exceed 30 days!", ephemeral=True)
            return
        
        if seconds < 1:
            await ctx.send("Reminder time must be at least 1 second!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you about: **{reminder}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Time", value=f"{time} {unit}", inline=True)
        embed.add_field(name="When", value=f"<t:{int((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).timestamp())}:R>", inline=True)
        
        await ctx.send(embed=embed)
        
        # Wait for the specified time
        await asyncio.sleep(seconds)
        
        # Send the reminder
        reminder_embed = discord.Embed(
            title="⏰ Reminder",
            description=f"You asked me to remind you: **{reminder}**",
            color=discord.Color.blue()
        )
        
        try:
            await ctx.author.send(embed=reminder_embed)
        except discord.Forbidden:
            # If DM fails, send in the original channel
            await ctx.send(f"{ctx.author.mention}, reminder: **{reminder}**")

    @commands.hybrid_command(name='weather', description='Get weather information (mock data).')
    async def weather(self, ctx, *, location: str):
        """Get weather information (returns mock data for demonstration)."""
        # This is mock data - in a real bot you'd use a weather API
        conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Partly Cloudy", "Stormy"]
        temperature = random.randint(-10, 35)
        condition = random.choice(conditions)
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 30)
        
        # Weather emojis
        emoji_map = {
            "Sunny": "☀️",
            "Cloudy": "☁️", 
            "Rainy": "🌧️",
            "Snowy": "❄️",
            "Partly Cloudy": "⛅",
            "Stormy": "⛈️"
        }
        
        embed = discord.Embed(
            title=f"{emoji_map.get(condition, '🌤️')} Weather in {location.title()}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Temperature", value=f"{temperature}°C", inline=True)
        embed.add_field(name="Condition", value=condition, inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind Speed", value=f"{wind_speed} km/h", inline=True)
        
        embed.set_footer(text="⚠️ This is mock weather data for demonstration purposes")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='translate', description='Translate text (mock translation).')
    async def translate(self, ctx, target_language: str, *, text: str):
        """Translate text (returns mock translation for demonstration)."""
        # This is a mock translation - in a real bot you'd use a translation API
        mock_translations = {
            "spanish": {
                "hello": "hola",
                "goodbye": "adiós", 
                "thank you": "gracias",
                "yes": "sí",
                "no": "no"
            },
            "french": {
                "hello": "bonjour",
                "goodbye": "au revoir",
                "thank you": "merci",
                "yes": "oui", 
                "no": "non"
            },
            "german": {
                "hello": "hallo",
                "goodbye": "auf wiedersehen",
                "thank you": "danke",
                "yes": "ja",
                "no": "nein"
            }
        }
        
        target_language = target_language.lower()
        text_lower = text.lower()
        
        if target_language in mock_translations and text_lower in mock_translations[target_language]:
            translation = mock_translations[target_language][text_lower]
        else:
            translation = f"[Mock translation to {target_language.title()}]: {text}"
        
        embed = discord.Embed(
            title="🌐 Translation",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=text, inline=False)
        embed.add_field(name=f"To {target_language.title()}", value=translation, inline=False)
        embed.set_footer(text="⚠️ This is a mock translation for demonstration purposes")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='qr', description='Generate a QR code for text (mock).')
    async def qr_code(self, ctx, *, text: str):
        """Generate a QR code for text (mock implementation)."""
        # This would normally generate an actual QR code
        embed = discord.Embed(
            title="📱 QR Code Generated",
            description=f"QR code for: **{text}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Text", value=text, inline=False)
        embed.set_footer(text="⚠️ QR code generation is not implemented in this demo")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='color', description='Show information about a color.')
    async def color_info(self, ctx, *, color_input: str):
        """Show information about a color."""
        # Try to parse the color
        color_input = color_input.replace("#", "").replace("0x", "")
        
        try:
            # Convert hex to int
            color_value = int(color_input, 16)
            color = discord.Color(color_value)
        except ValueError:
            # Try named colors
            named_colors = {
                "red": 0xFF0000,
                "green": 0x00FF00,
                "blue": 0x0000FF,
                "yellow": 0xFFFF00,
                "purple": 0x800080,
                "orange": 0xFFA500,
                "pink": 0xFFC0CB,
                "black": 0x000000,
                "white": 0xFFFFFF,
                "gray": 0x808080,
                "grey": 0x808080
            }
            
            color_name = color_input.lower()
            if color_name in named_colors:
                color_value = named_colors[color_name]
                color = discord.Color(color_value)
            else:
                await ctx.send("Invalid color! Use hex format (#FF0000) or color names (red, blue, etc.)", ephemeral=True)
                return
        
        embed = discord.Embed(
            title="🎨 Color Information",
            color=color
        )
        
        # Convert back to hex and RGB
        hex_value = f"#{color_value:06X}"
        r = (color_value >> 16) & 255
        g = (color_value >> 8) & 255
        b = color_value & 255
        
        embed.add_field(name="Hex", value=hex_value, inline=True)
        embed.add_field(name="RGB", value=f"({r}, {g}, {b})", inline=True)
        embed.add_field(name="Decimal", value=str(color_value), inline=True)
        
        # Add a color square visualization using embed color
        embed.description = f"Preview of color {hex_value}"
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='base64', description='Encode or decode base64 text.')
    async def base64(self, ctx, action: str, *, text: str):
        """Encode or decode base64 text."""
        import base64
        
        action = action.lower()
        
        if action not in ['encode', 'decode']:
            await ctx.send("Action must be 'encode' or 'decode'!", ephemeral=True)
            return
        
        try:
            if action == 'encode':
                result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
                title = "🔒 Base64 Encoded"
            else:  # decode
                result = base64.b64decode(text.encode('utf-8')).decode('utf-8')
                title = "🔓 Base64 Decoded"
            
            embed = discord.Embed(
                title=title,
                color=discord.Color.blue()
            )
            embed.add_field(name="Input", value=f"```{text}```", inline=False)
            embed.add_field(name="Output", value=f"```{result}```", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error processing base64: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name='password', description='Generate a random password.')
    async def generate_password(self, ctx, length: int = 12, include_symbols: bool = True):
        """Generate a random password."""
        if length < 4 or length > 50:
            await ctx.send("Password length must be between 4 and 50 characters!", ephemeral=True)
            return
        
        import string
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*"
        
        password = ''.join(random.choice(characters) for _ in range(length))
        
        embed = discord.Embed(
            title="🔐 Generated Password",
            color=discord.Color.green()
        )
        embed.add_field(name="Password", value=f"||`{password}`||", inline=False)
        embed.add_field(name="Length", value=str(length), inline=True)
        embed.add_field(name="Includes Symbols", value="Yes" if include_symbols else "No", inline=True)
        embed.set_footer(text="⚠️ Keep this password secure! Click to reveal.")
        
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    """Adds the Misc cog to the bot."""
    await bot.add_cog(Misc(bot))
