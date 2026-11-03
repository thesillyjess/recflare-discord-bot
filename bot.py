from recflare import recflareApi
from recflare import returns
import discord
from discord import app_commands
from discord.ext import commands
import toml
import time

intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
api = recflareApi()

try:
    with open('config.toml') as f:
        config = toml.load(f)
except FileNotFoundError:
    print("config.toml not found. duplicate config.toml.template, rename to config.toml, and change the config.")
    time.sleep(30)
    exit(1)

@bot.tree.command(name="get-user-info", description="Get info on a user")
@app_commands.describe(username="Player username without @", public="Show the response publicly")
async def getUserInfo(interaction: discord.Interaction, username: str, public: bool = False):
    public = not public
    user = api.getPlayerProfileInfo(username)
    if user.playerExists == False:
        await interaction.response.send_message(f"@{username} doesn't exist.", ephemeral=public)
        return
    userJoined = f"{user.joinedRecflare.replace("-", "/").split("/")[2]}/{user.joinedRecflare.replace("-", "/").split("/")[1]}/{user.joinedRecflare.replace("-", "/").split("/")[0]}"
    if user.displayNameEmoji == "":
        embed = discord.Embed(title=f"{user.displayName}",
                              description=f"Username: @{user.username}\nDisplay name: {user.displayName}\nJoined Recflare: {userJoined}")
        embed.set_thumbnail(url=user.profilePicUrl)
    else:
        embed = discord.Embed(title=f"{user.displayName} [{user.displayNameEmoji}]",
                              description=f"Username: @{user.username}\nDisplay name: {user.displayName} [{user.displayNameEmoji}]\nJoined Recflare: {userJoined}")
        embed.set_thumbnail(url=user.profilePicUrl)
    await interaction.response.send_message(embed=embed, ephemeral=public)
    return

@bot.tree.command(name="get-room-info", description="Get info on a room")
@app_commands.describe(room="Room name", public="Show the response publicly")
async def getUserInfo(interaction: discord.Interaction, room: str, public: bool = False):
    public = not public
    roomData = api.getRoomInfo(room)
    if roomData.roomExists == False:
        await interaction.response.send_message(f"^{room} doesn't exist.", ephemeral=public)
        return
    roomPublished = f"{roomData.roomPublished.replace("-", "/").split("/")[2]}/{roomData.roomPublished.replace("-", "/").split("/")[1]}/{roomData.roomPublished.replace("-", "/").split("/")[0]}"
    embed = discord.Embed(title=f"^{room}",
                            description=f"Room description: {roomData.roomDescription}\nPublished to Recflare: {roomPublished}\nRoom creator: @{roomData.roomCreatorUsername}\nRoom visits: {roomData.roomVisits}\nRoom max players: {roomData.roomMaxPlayers}")
    embed.set_thumbnail(url=roomData.roomThumbnailUrl)
    await interaction.response.send_message(embed=embed, ephemeral=public)
    return

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        if config['bot']['useStatus']:
            await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=config['bot']['statusText']))
        print("Synced")
    except Exception as e:
        print(f"Sync Error: {e}")
bot.run(config["bot"]["botToken"])