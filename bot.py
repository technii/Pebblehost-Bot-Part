import discord
from discord.ext import commands
from discord import app_commands
import PIL
from PIL import Image
import os
import requests
import json
import mysql.connector
import nacl
from mutagen.mp3 import MP3
import ffmpeg
jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)
allowedcontenttypes = ["audio/mpeg"]
intents = discord.Intents.default()
openvoiceclients = {}
audiofp = "Sounds/"
sqlforuploadingsounds = "INSERT INTO SOUNDPOINTERS (GUILDID,FILENAME,LENGTH,USERID,SOUNDNAME,FileID) VALUES (%s,%s,%s,%s,%s,%s) "
sqlforgettingsoundnames = "select SOUNDNAME, LENGTH from SOUNDPOINTERS "
sqlforplayingsound = "select FILENAME from `SOUNDPOINTERS` where soundname = %s"

db = mysql.connector.connect(
    host=jsondict.get("SQLHost"),
    port = jsondict.get("SQLPort"),
    user = jsondict.get("SQLUsername"),
    password = jsondict.get("SQLPassword"),
    database = jsondict.get("SQLUsername"),
    connection_timeout = 10
)
sqlcursor = db.cursor()

class sclient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = discord.app_commands.CommandTree(self)
    async def setup_hook(self) -> None:
        await self.tree.sync()
        print(f"we have signed in as {client.user}")
        
client = sclient()

class FruitSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Apple"),
            discord.SelectOption(label="Banana"),
            discord.SelectOption(label="Orange"),
        ]

        super().__init__(
            placeholder="Choose a fruit...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"You chose {self.values[0]}",
            ephemeral=True
        )

class FruitView(discord.ui.View):
    def __init__(self):
        super().__init__()
        sqlcursor.execute(sqlforgettingsoundnames)
        sql = sqlcursor.fetchall()
        print(sql)
        self.add_item(FruitSelect())


@client.tree.command(name="joinvc")
@app_commands.allowed_contexts(guilds=True)
async def _joinvc(interaction : discord.Interaction, channel : discord.VoiceChannel):
    try:
        openvoiceclients[interaction.guild.id] = await channel.connect()
        await interaction.response.send_message(f"joined {channel.name}",ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="leavevc")
@app_commands.allowed_contexts(guilds=True)
async def _leavevc(interaction : discord.Interaction):
    try:
        await openvoiceclients[interaction.guild.id].disconnect()
        await interaction.response.send_message(f"left :(",ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="uploadsound")
@app_commands.allowed_contexts(guilds=True)
async def _uploadsound(interaction : discord.Interaction, sound : discord.Attachment, soundname : str):
    try:
        if sound.content_type in allowedcontenttypes:
            sqlcursor.execute("SELECT `FileID` FROM SOUNDPOINTERS ORDER BY FileID DESC LIMIT 1")
            currentfileid : int  = int(str(sqlcursor.fetchone()).removeprefix("(").removesuffix(",)")) + 1
            await sound.save(fp=audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3")
            vals = (str(interaction.guild.id),audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3",str(MP3(audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3").info.length),str(interaction.user.id),soundname,currentfileid)
            print(vals)
            
            sqlcursor.execute(sqlforuploadingsounds,vals)
            db.commit()
            await interaction.response.send_message("SAVED", ephemeral=True)
            
        else:
            await interaction.response.send_message("Must be a .mp3", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="playsound")
@app_commands.allowed_contexts(guilds=True)
async def _playsound(interaction : discord.Interaction, soundname: str):
    try:
        if interaction.guild.id in openvoiceclients:
            sqlcursor.execute(f"select FILENAME from `SOUNDPOINTERS` where SOUNDNAME = '{soundname}'")
            resp = sqlcursor.fetchall()
            if resp.__len__() > 0:
                print(resp)
                await openvoiceclients[interaction.guild.id].play(discord.FFmpegOpusAudio(source=resp[0][0]))
            else:
                await interaction.response.send_message("No Sound Matching Name",ephemeral=True)
        else:
            interaction.response.send_message("Not in a voice channel", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="soundlist")
@app_commands.allowed_contexts(guilds=True)
async def _soundlist(interaction : discord.Interaction):
    try:
        views = FruitView()
        await interaction.response.send_message("press the button", view=views)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)



def run_bot():
    client.run(jsondict.get("token"))