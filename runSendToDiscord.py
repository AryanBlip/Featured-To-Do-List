# THIS RUNS THE FLASK APP AND SENDS THE URL ON DISCORD DM

from app import create_app
from pyngrok import ngrok
import threading

# ============ Start ngrok ============
import discord
from discord.ext import commands
from logging import FileHandler, DEBUG
from dotenv import load_dotenv
import os

load_dotenv()
discordToken = os.getenv('DISCORD_TOKEN')
ngrokToken = os.getenv('NGROK_TOKEN')
ownerId = int(os.getenv('OWNER_ID'))

ngrok.set_auth_token(ngrokToken)
public_url = ngrok.connect(5000)
print("ngrok URL:", public_url)

# ============ Start Flask app in background ============
def run_flask():
    app = create_app()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# ============ Discord Bot ============

handler = FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    owner = await bot.fetch_user(ownerId)
    await owner.send(f"Bot is online! ngrok URL: {public_url}")
    print(f"{bot.user.name}, URL SENT")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def dm(ctx, *, msg=None):
    await ctx.author.send(f"Here is the current ngrok URL: {public_url}")

bot.run(discordToken, log_handler=handler, log_level=DEBUG)
