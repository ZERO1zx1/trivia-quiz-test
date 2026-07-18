import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_cooldown = {}

    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if user_id in self.daily_cooldown:
            last_claim = self.daily_cooldown[user_id]
            if datetime.now() - last_claim < timedelta(hours=20):
                remaining = timedelta(hours=20) - (datetime.now() - last_claim)
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)

                await interaction.response.send_message(
                    f"⏰ Come back in **{hours}h {minutes}m**!",
                    ephemeral=True
                )
                return

        self.daily_cooldown[user_id] = datetime.now()

        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description="You received **🪙 100 coins**!",
            color=0x57F287
        )
        embed.set_footer(text="Come back tomorrow for more!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="balance", description="Check your coin balance")
    async def balance(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💰 Your Balance",
            description="**🪙 500** coins",
            color=0xFFD700
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="Browse the TriviaVerse shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛒 TriviaVerse Shop",
            description="Use `/buy <item>` to purchase",
            color=0x5865F2
        )
        embed.add_field(name="🎨 Avatar Borders", value="Common: 100 | Rare: 500 | Epic: 2000", inline=False)
        embed.add_field(name="🖼️ Backgrounds", value="Common: 200 | Rare: 1000 | Legendary: 5000", inline=False)
        embed.add_field(name="✨ Effects", value="Epic: 3000 | Legendary: 10000", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
