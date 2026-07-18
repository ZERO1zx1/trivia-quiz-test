import asyncio
import os
import aiohttp
from discord.ext import commands
import discord

class TriviaVerseBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )

        self.api_base = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        await self.load_extension('discord_bot.cogs.profile')
        await self.load_extension('discord_bot.cogs.economy')
        await self.load_extension('discord_bot.cogs.quiz')

        guild_id = os.getenv('DISCORD_GUILD_ID')
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name='TriviaVerse | /help'
            )
        )

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

def run_bot():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN not set")
    bot = TriviaVerseBot()
    bot.run(token)

if __name__ == '__main__':
    run_bot()
