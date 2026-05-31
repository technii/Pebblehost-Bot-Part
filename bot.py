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
jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)
allowedcontenttypes = ["audio/mpeg"]
intents = discord.Intents.default()
openvoiceclients = {}
audiofp = "Sounds/"
sqlforuploadingsounds = "INSERT INTO SOUNDPOINTERS (GUILDID,FILENAME,LENGTH,USERID,FileID) VALUES (%s,%s,%s,%s,%s) "

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
async def _uploadsound(interaction : discord.Interaction, sound : discord.Attachment):
    try:
        if sound.content_type in allowedcontenttypes:
            sqlcursor.execute("SELECT `FileID` FROM SOUNDPOINTERS ORDER BY FileID DESC LIMIT 1")
            currentfileid : int  = int(str(sqlcursor.fetchone()).removeprefix("(").removesuffix(",)")) + 1
            await sound.save(fp=audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3")
            vals = (str(interaction.guild.id),sound.filename,str(MP3(audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3").info.length),str(interaction.user.id),currentfileid)
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
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="soundlist")
@app_commands.allowed_contexts(guilds=True)
async def _soundlist(interaction : discord.Interaction):
    try:
        print(currentfileid)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)



def run_bot():
    client.run(jsondict.get("token"))