import random
from recflare import recflareApi
import modals
import discord
from discord import app_commands
from discord.ext import commands
import toml
import time
import datetime

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
                              description=f"Display name: {user.displayName} [{user.displayNameEmoji}]\nJoined Recflare: {userJoined}\n\nBio: {user.bio}")
        embed.set_thumbnail(url=user.profilePicUrl)
        embed.set_image(url=user.bannerPicUrl)
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
    embed.set_image(url=roomData.roomThumbnailUrl)
    await interaction.response.send_message(embed=embed, ephemeral=public)
    return

@bot.tree.command(name="players-online", description="Get Recflares current player count")
@app_commands.describe(public="Show the response publicly")
async def getPlayersOnline(interaction: discord.Interaction, public: bool = False):
    public = not public
    online = api.getPlayersOnline()
    if online == 1:
        status = "player"
    else:
        status = "players"
    await interaction.response.send_message(f"There are {online} {status} online.", ephemeral=public)
    return

@bot.tree.command(name="hottest-room", description="Get the most popular Recflare room")
@app_commands.describe(public="Show the response publicly")
async def hottestRoom(interaction: discord.Interaction, public: bool = False):
    public = not public
    hottest = api.getHottestRoomName()
    await interaction.response.send_message(f"The hottest room currently ^{hottest}", ephemeral=public)
    return

@bot.tree.command(name="random-slideshow-image", description="Get a random slideshow image")
@app_commands.describe(public="Show the response publicly")
async def randomSlideshowImage(interaction: discord.Interaction, public: bool = False):
    public = not public
    imageList = api.getSlideShowImages(10)["Images"]
    randomImage = random.choice(imageList)
    embed = discord.Embed(title=f"^{randomImage['RoomName']}",
                          description=f"Photo taker: @{randomImage['Username']}",)
    embed.set_image(url=f"https://img.recflare.net/{randomImage['ImageName']}")
    await interaction.response.send_message(embed=embed, ephemeral=public)

@bot.tree.command(name="bunny", description="Joke command")
async def jokeBunny(interaction: discord.Interaction):
    await interaction.response.send_message("Bunny is you", ephemeral=True) # Bunny :0

@bot.tree.command(name="status", description="See if Recflare is currently up")
@app_commands.describe(public="Show the response publicly")
async def isRecflareUp(interaction: discord.Interaction, public: bool = False):
    public = not public
    if api.isRecflareUp():
        await interaction.response.send_message("Yeah Recflares good mate", ephemeral=public)
    else:
        await interaction.response.send_message("Nah Recflares down mate", ephemeral=public)

@bot.tree.command(name="send-message-from-bot", description="[STAFF/DEV] Send a message from the bot")
@app_commands.checks.has_any_role(*config["bot"]["announcementRequiredRoleIds"])
async def sendMessageFromBot(interaction: discord.Interaction, channel: discord.TextChannel):
    if not config["bot"]["staffAnnouncementEnabled"]:
        await interaction.response.send_message("Staff announcements have been disabled.", ephemeral=True)
        return
    modal = modals.staffAnnouncementModel()
    await interaction.response.send_modal(modal)
    await modal.wait()
    if modal.modalSuccess == False:
        await interaction.edit_original_response(content=modal.modalMessage)
        return
    try:
        await channel.send(modal.modalMessage)
        await interaction.followup.send("sent!", ephemeral=True)
    except Exception as e:
        if "403 Forbidden" in str(e):
            await interaction.edit_original_response(content="Error! Tried sending message to a channel I cannot access!")
        else:
            await interaction.edit_original_response(content=f"Error sending message!")

@bot.tree.command(name="timeout", description="[Staff] Time out a user")
@app_commands.describe(user="User to time out", time="Time of timeout (in seconds)", reason="Reason to time out")
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.has_any_role(*config["bot"]["moderatorRoles"])
async def timeout(interaction: discord.Interaction, user: discord.Member, time: int, reason: str):
    if config["bot"]["allowModerationCommands"] == False:
        await interaction.response.send_message("Moderation has been disabled.", ephemeral=True)
        return
    confirmModal = modals.confirmGeneric()
    await interaction.response.send_message(f"Are you sure you wanna timeout @{user} for {time} seconds?", ephemeral=True, view=confirmModal)
    await confirmModal.wait()
    if confirmModal.confirmed is None:
        await interaction.edit_original_response(content="Command timed out. User was not timed out.", view=None)
    elif confirmModal.confirmed:
        try:
            await interaction.edit_original_response(content="Timing out...", view=None)
            duration = datetime.timedelta(seconds=time)
            await user.timeout(duration, reason=reason)
            await interaction.edit_original_response(content="Timed out.", view=None)
        except discord.Forbidden as e:
            await interaction.edit_original_response(content="I can't do that.", view=None)
    else:
        await interaction.edit_original_response(content="Cancelled.", view=None)

@bot.tree.command(name="kick", description="[Staff] Kick a user")
@app_commands.describe(user="User to kick", reason="Reason to Kick")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.checks.has_any_role(*config["bot"]["moderatorRoles"])
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    if config["bot"]["allowModerationCommands"] == False:
        await interaction.response.send_message("Moderation has been disabled.", ephemeral=True)
        return
    confirmModal = modals.confirmGeneric()
    await interaction.response.send_message(f"Are you sure you wanna kick @{user}?", ephemeral=True, view=confirmModal)
    await confirmModal.wait()
    if confirmModal.confirmed is None:
        await interaction.edit_original_response(content="Command timed out. User was not kicked.", view=None)
    elif confirmModal.confirmed:
        try:
            await interaction.edit_original_response(content="kicking...", view=None)
            await user.kick(reason=reason)
            await interaction.edit_original_response(content="Kicked.", view=None)
        except discord.Forbidden as e:
            await interaction.edit_original_response(content="I can't do that.", view=None)
    else:
        await interaction.edit_original_response(content="Cancelled.", view=None)


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        if config['bot']['useStatus']:
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.custom, name=config['bot']['statusText'], state=config['bot']['statusText']))
        print("Synced")
    except Exception as e:
        print(f"Sync Error: {e}")
bot.run(config["bot"]["botToken"])
