from recflare import recflareApi
from recflare import returns
import discord
from discord.ext import commands
import toml
import time

intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

try:
    with open('config.toml') as f:
        config = toml.load(f)
except FileNotFoundError:
    print("config.toml not found. duplicate config.toml.template, rename to config.toml, and change the config.")
    time.sleep(30)
    exit(1)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync Error: {e}")
bot.run(config["bot"]["botToken"])