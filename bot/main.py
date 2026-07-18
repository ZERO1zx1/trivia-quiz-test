import discord
from discord.ext import commands
import os
from dotenv import load_dotenv  # <-- Үүнийг нэмэх
from backend.extensions import db
from backend.models import User
from flask import Flask

# .env файл доторх утгуудыг системд уншуулах
load_dotenv()  # <-- Үүнийг нэмэх

# Minimal Flask app context for the bot to access the DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Энийг нэмчихвэл зүгээр

db.init_app(app)

class TriviaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.load_extension('bot.cogs.economy') # Зам нь зөв эсэхийг шалгаарай (bot.cogs.economy)
        await self.tree.sync()

bot = TriviaBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('TriviaVerse Bot is ready for matchmaking.')