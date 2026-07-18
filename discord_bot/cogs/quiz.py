import discord
from discord.ext import commands
from discord import app_commands
import random

class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @app_commands.command(name="create-room", description="Create a trivia room")
    @app_commands.describe(name="Room name", private="Make room private")
    async def create_room(self, interaction: discord.Interaction, name: str = "Trivia Room", private: bool = False):
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

        embed = discord.Embed(
            title="🚪 Room Created!",
            description=f"**{name}**\nCode: `{code}`",
            color=0x5865F2
        )
        embed.add_field(name="Players", value="1/8", inline=True)
        embed.add_field(name="Status", value="⏳ Waiting", inline=True)

        if not private:
            embed.add_field(name="Join", value="Anyone can join!", inline=False)
        else:
            embed.add_field(name="Join", value="Password protected", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="join-room", description="Join a trivia room")
    @app_commands.describe(code="Room code")
    async def join_room(self, interaction: discord.Interaction, code: str):
        embed = discord.Embed(
            title="✅ Joined Room",
            description=f"You joined room `{code.upper()}`",
            color=0x57F287
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trivia", description="Quick solo trivia question")
    async def trivia(self, interaction: discord.Interaction):
        questions = [
            {
                "question": "What is the capital of France?",
                "answers": ["London", "Berlin", "Paris", "Madrid"],
                "correct": 2,
                "category": "Geography"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "answers": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": 1,
                "category": "Science"
            },
            {
                "question": "What is 2 + 2 × 2?",
                "answers": ["6", "8", "4", "2"],
                "correct": 0,
                "category": "Math"
            }
        ]

        q = random.choice(questions)

        embed = discord.Embed(
            title=f"❓ {q['category']} Trivia",
            description=q['question'],
            color=0x00D4FF
        )

        view = discord.ui.View()
        for i, ans in enumerate(q['answers']):
            btn = discord.ui.Button(label=ans, style=discord.ButtonStyle.primary, custom_id=f"answer_{i}_{q['correct']}")
            btn.callback = self.answer_callback
            view.add_item(btn)

        await interaction.response.send_message(embed=embed, view=view)

    async def answer_callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        parts = custom_id.split('_')
        selected = int(parts[1])
        correct = int(parts[2])

        if selected == correct:
            embed = discord.Embed(
                title="✅ Correct!",
                description=f"Great job, {interaction.user.mention}!",
                color=0x57F287
            )
        else:
            embed = discord.Embed(
                title="❌ Wrong!",
                description="Better luck next time!",
                color=0xED4245
            )

        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(QuizCog(bot))
