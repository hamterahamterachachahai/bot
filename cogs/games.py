# cogs/games.py
import discord
from discord.ext import commands
import random
import asyncio

class Games(commands.Cog):
    """Simple games to play in Discord."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='rps', description='Play Rock Paper Scissors against the bot.')
    async def rock_paper_scissors(self, ctx, choice: str):
        """Play Rock Paper Scissors against the bot."""
        choice = choice.lower()
        valid_choices = ['rock', 'paper', 'scissors', 'r', 'p', 's']
        
        if choice not in valid_choices:
            await ctx.send("Please choose rock (r), paper (p), or scissors (s)!", ephemeral=True)
            return
        
        # Convert short forms to full names
        choice_map = {'r': 'rock', 'p': 'paper', 's': 'scissors'}
        if choice in choice_map:
            choice = choice_map[choice]
        
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        
        # Determine winner
        if choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.yellow()
        elif (choice == 'rock' and bot_choice == 'scissors') or \
             (choice == 'paper' and bot_choice == 'rock') or \
             (choice == 'scissors' and bot_choice == 'paper'):
            result = "You win! 🎉"
            color = discord.Color.green()
        else:
            result = "I win! 😄"
            color = discord.Color.red()
        
        # Emojis for choices
        emoji_map = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            color=color
        )
        embed.add_field(name="Your choice", value=f"{emoji_map[choice]} {choice.title()}", inline=True)
        embed.add_field(name="My choice", value=f"{emoji_map[bot_choice]} {bot_choice.title()}", inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='guess', description='Guess a number between 1 and 100.')
    async def guess_number(self, ctx, number: int):
        """Guess a number between 1 and 100."""
        if number < 1 or number > 100:
            await ctx.send("Please guess a number between 1 and 100!", ephemeral=True)
            return
        
        bot_number = random.randint(1, 100)
        difference = abs(number - bot_number)
        
        if difference == 0:
            result = "🎯 Perfect! You guessed it exactly!"
            color = discord.Color.gold()
        elif difference <= 5:
            result = "🔥 Very close! You're burning hot!"
            color = discord.Color.red()
        elif difference <= 10:
            result = "🌡️ Close! You're getting warm!"
            color = discord.Color.orange()
        elif difference <= 20:
            result = "❄️ Not bad, but you're getting cold..."
            color = discord.Color.blue()
        else:
            result = "🧊 Way off! You're freezing!"
            color = discord.Color.dark_blue()
        
        embed = discord.Embed(
            title="🔢 Number Guessing Game",
            color=color
        )
        embed.add_field(name="Your guess", value=number, inline=True)
        embed.add_field(name="My number", value=bot_number, inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='trivia', description='Answer a random trivia question.')
    async def trivia(self, ctx):
        """Answer a random trivia question."""
        questions = [
            {
                "question": "What is the capital of France?",
                "options": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"],
                "answer": "C",
                "explanation": "Paris is the capital and largest city of France."
            },
            {
                "question": "How many continents are there?",
                "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
                "answer": "C",
                "explanation": "There are 7 continents: Africa, Antarctica, Asia, Europe, North America, Australia/Oceania, and South America."
            },
            {
                "question": "What is the largest planet in our solar system?",
                "options": ["A) Earth", "B) Jupiter", "C) Saturn", "D) Neptune"],
                "answer": "B",
                "explanation": "Jupiter is the largest planet in our solar system."
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["A) Van Gogh", "B) Picasso", "C) Da Vinci", "D) Monet"],
                "answer": "C",
                "explanation": "Leonardo da Vinci painted the Mona Lisa between 1503-1519."
            },
            {
                "question": "What is the smallest ocean?",
                "options": ["A) Atlantic", "B) Pacific", "C) Indian", "D) Arctic"],
                "answer": "D",
                "explanation": "The Arctic Ocean is the smallest ocean."
            }
        ]
        
        question_data = random.choice(questions)
        
        embed = discord.Embed(
            title="🧠 Trivia Question",
            description=question_data["question"],
            color=discord.Color.blue()
        )
        
        options_text = "\n".join(question_data["options"])
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(text="React with 🅰️, 🅱️, ©️, or 🇩 to answer!")
        
        message = await ctx.send(embed=embed)
        
        # Add reaction options
        reactions = ["🅰️", "🅱️", "©️", "🇩"]
        for reaction in reactions:
            await message.add_reaction(reaction)
        
        # Wait for user reaction
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == message.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            # Map reactions to letters
            reaction_map = {"🅰️": "A", "🅱️": "B", "©️": "C", "🇩": "D"}
            user_answer = reaction_map[str(reaction.emoji)]
            
            # Check if correct
            if user_answer == question_data["answer"]:
                result_embed = discord.Embed(
                    title="✅ Correct!",
                    description=f"Great job! The answer was {question_data['answer']}.",
                    color=discord.Color.green()
                )
            else:
                result_embed = discord.Embed(
                    title="❌ Incorrect",
                    description=f"Sorry! The correct answer was {question_data['answer']}.",
                    color=discord.Color.red()
                )
            
            result_embed.add_field(name="Explanation", value=question_data["explanation"], inline=False)
            await ctx.send(embed=result_embed)
            
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"You didn't answer in time. The correct answer was {question_data['answer']}.",
                color=discord.Color.orange()
            )
            timeout_embed.add_field(name="Explanation", value=question_data["explanation"], inline=False)
            await ctx.send(embed=timeout_embed)

    @commands.hybrid_command(name='flip', description='Flip a coin multiple times.')
    async def multi_flip(self, ctx, times: int = 1):
        """Flip a coin multiple times."""
        if times < 1 or times > 20:
            await ctx.send("Please flip between 1 and 20 times!", ephemeral=True)
            return
        
        results = []
        heads_count = 0
        tails_count = 0
        
        for i in range(times):
            result = random.choice(["Heads", "Tails"])
            results.append(result)
            if result == "Heads":
                heads_count += 1
            else:
                tails_count += 1
        
        embed = discord.Embed(
            title=f"🪙 Coin Flip × {times}",
            color=discord.Color.gold()
        )
        
        if times <= 10:
            results_text = " → ".join(results)
            embed.add_field(name="Results", value=results_text, inline=False)
        
        embed.add_field(name="Summary", value=f"Heads: {heads_count}\nTails: {tails_count}", inline=True)
        
        if heads_count > tails_count:
            embed.add_field(name="Winner", value="🏆 Heads!", inline=True)
        elif tails_count > heads_count:
            embed.add_field(name="Winner", value="🏆 Tails!", inline=True)
        else:
            embed.add_field(name="Winner", value="🤝 It's a tie!", inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='slots', description='Play a simple slot machine game.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slots(self, ctx):
        """Play a simple slot machine game."""
        emojis = ["🍎", "🍊", "🍋", "🍇", "🍓", "🍒", "⭐", "💎"]
        
        # Generate three random symbols
        result = [random.choice(emojis) for _ in range(3)]
        
        # Determine if it's a win
        if result[0] == result[1] == result[2]:
            if result[0] == "💎":
                win_type = "JACKPOT! 💰"
                color = discord.Color.gold()
            elif result[0] == "⭐":
                win_type = "SUPER WIN! ✨"
                color = discord.Color.purple()
            else:
                win_type = "WIN! 🎉"
                color = discord.Color.green()
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            win_type = "Small win! 👍"
            color = discord.Color.blue()
        else:
            win_type = "Try again! 😅"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="🎰 Slot Machine",
            color=color
        )
        
        slots_display = f"[ {result[0]} | {result[1]} | {result[2]} ]"
        embed.add_field(name="Result", value=slots_display, inline=False)
        embed.add_field(name="Outcome", value=win_type, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Adds the Games cog to the bot."""
    await bot.add_cog(Games(bot))
