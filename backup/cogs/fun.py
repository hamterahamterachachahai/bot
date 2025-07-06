# cogs/fun.py
import discord
from discord.ext import commands
import random
import asyncio

class Fun(commands.Cog):
    """Fun commands for entertainment."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='roll', description='Rolls a dice.')
    async def roll(self, ctx, sides: int = 6):
        """Rolls a dice with specified number of sides (default 6)."""
        if sides < 2:
            await ctx.send("Dice must have at least 2 sides!", ephemeral=True)
            return
        
        if sides > 100:
            await ctx.send("Dice cannot have more than 100 sides!", ephemeral=True)
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{result}** on a {sides}-sided dice!",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='coinflip', description='Flips a coin.')
    async def coinflip(self, ctx):
        """Flips a coin."""
        result = random.choice(["Heads", "Tails"])
        emoji = "🪙"
        
        embed = discord.Embed(
            title=f"{emoji} Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='8ball', description='Ask the magic 8-ball a question.')
    async def eightball(self, ctx, *, question: str):
        """Ask the magic 8-ball a question."""
        responses = [
            "It is certain.", "Reply hazy, try again.", "Don't count on it.",
            "It is decidedly so.", "Ask again later.", "My reply is no.",
            "Without a doubt.", "Better not tell you now.", "My sources say no.",
            "Yes definitely.", "Cannot predict now.", "Outlook not so good.",
            "You may rely on it.", "Concentrate and ask again.", "Very doubtful.",
            "As I see it, yes.", "Most likely.", "Outlook good.",
            "Yes.", "Signs point to yes."
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='joke', description='Tells a random joke.')
    async def joke(self, ctx):
        """Tells a random joke."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't programmers like nature? It has too many bugs.",
            "How do you organize a space party? You planet!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a fake noodle? An impasta!",
            "Why did the bicycle fall over? Because it was two tired!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus."
        ]
        
        joke = random.choice(jokes)
        
        embed = discord.Embed(
            title="😂 Random Joke",
            description=joke,
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='reverse', description='Reverses the given text.')
    async def reverse(self, ctx, *, text: str):
        """Reverses the given text."""
        reversed_text = text[::-1]
        
        embed = discord.Embed(
            title="🔄 Text Reverser",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=text, inline=False)
        embed.add_field(name="Reversed", value=reversed_text, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='randomnum', description='Generates a random number between min and max.')
    async def randomnum(self, ctx, minimum: int = 1, maximum: int = 100):
        """Generates a random number between min and max."""
        if minimum >= maximum:
            await ctx.send("Minimum must be less than maximum!", ephemeral=True)
            return
        
        if maximum - minimum > 1000000:
            await ctx.send("Range is too large! Please use a smaller range.", ephemeral=True)
            return
        
        number = random.randint(minimum, maximum)
        
        embed = discord.Embed(
            title="🎯 Random Number",
            description=f"Random number between {minimum} and {maximum}: **{number}**",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='fact', description='Shares a random fun fact.')
    async def fact(self, ctx):
        """Shares a random fun fact."""
        facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.",
            "Octopuses have three hearts and blue blood.",
            "Bananas are berries, but strawberries aren't.",
            "A group of flamingos is called a 'flamboyance'.",
            "The shortest war in history lasted only 38-45 minutes.",
            "Dolphins have names for each other.",
            "A day on Venus is longer than its year.",
            "Wombat poop is cube-shaped.",
            "Penguins can jump 6 feet in the air.",
            "The human brain uses about 20% of the body's total energy."
        ]
        
        fact = random.choice(facts)
        
        embed = discord.Embed(
            title="🧠 Fun Fact",
            description=fact,
            color=discord.Color.orange()
        )
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='rate', description='Rates something on a scale of 1-10.')
    async def rate(self, ctx, *, thing: str):
        """Rates something on a scale of 1-10."""
        rating = random.randint(1, 10)
        
        # Add some fun reactions based on rating
        if rating <= 3:
            reaction = "😬 Yikes!"
        elif rating <= 5:
            reaction = "🤔 Could be better..."
        elif rating <= 7:
            reaction = "👍 Not bad!"
        elif rating <= 9:
            reaction = "😍 Pretty awesome!"
        else:
            reaction = "🔥 AMAZING!"
        
        embed = discord.Embed(
            title="⭐ Rating",
            description=f"I rate **{thing}** a **{rating}/10**\n{reaction}",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Adds the Fun cog to the bot."""
    await bot.add_cog(Fun(bot))
