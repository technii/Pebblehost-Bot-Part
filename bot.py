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
import shared
import asyncio
"""
Completed Commands:
JoinVC
LeaveVC
UploadSound
PlaySound
SoundList
Work in Progress Commands:
TTS
Future Commands:
Queue fixes
StopSound
SkipSound
"""



jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)
allowedcontenttypes = ["audio/mpeg"]
intents = discord.Intents.default()
openvoiceclients = {}
audiofp = "Sounds/"
sqlforuploadingsounds = "INSERT INTO SOUNDPOINTERS (GUILDID,FILENAME,LENGTH,USERID,SOUNDNAME,FileID) VALUES (%s,%s,%s,%s,%s,%s) "
sqlforgettingsoundnames = "select SOUNDNAME, LENGTH from SOUNDPOINTERS where GUILDID = %s"
sqlforplayingsound = "select FILENAME,GUILDID from `SOUNDPOINTERS` where SOUNDNAME = %s AND GUILDID = %s"

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
        asyncio.create_task(PlayingQueue())
        print(f"we have signed in as {client.user}")
        
client = sclient()

class Container(discord.ui.Container):
    def __init__(self, *children, accent_colour = None, accent_color = None, spoiler = False, id = None,TextLabelText:list):
        TextLabelText = TextLabelText
        super().__init__(*children, accent_colour=accent_colour, accent_color=accent_color, spoiler=spoiler, id=id)
        for x in TextLabelText:
            self.add_item(discord.ui.TextDisplay(x))




class FruitView(discord.ui.LayoutView):
    def __init__(self,guildid):
        super().__init__()
        sqlcursor.execute(f"select SOUNDNAME, LENGTH from SOUNDPOINTERS where GUILDID = {guildid} ")
        sql = sqlcursor.fetchall()
        TextList = []
        for x in sql:
            TextList.append("Name: " + x[0] + " , Duration (Seconds): " + str(x[1]))
        print(TextList)
        self.add_item(Container(TextLabelText=TextList))


@client.tree.command(name="joinvc")
@app_commands.allowed_contexts(guilds=True)
async def _joinvc(interaction : discord.Interaction, channel : discord.VoiceChannel):
    try:
        openvoiceclients[interaction.guild.id] = await channel.connect()
        await interaction.response.send_message(f"joined {channel.name}",ephemeral=True)
        shared.queues[interaction.guild.id] = shared.soundqueue()
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="leavevc")
@app_commands.allowed_contexts(guilds=True)
async def _leavevc(interaction : discord.Interaction):
    try:
        await openvoiceclients[interaction.guild.id].disconnect()
        await interaction.response.send_message(f"left :(",ephemeral=True)
        openvoiceclients.pop(interaction.guild.id)
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
            sqlcursor.execute(sqlforplayingsound,(soundname,interaction.guild.id))
            resp = sqlcursor.fetchall()
            print(resp)
            if resp.__len__() > 0:
                print("resplen")
                if resp[0][1] == str(interaction.guild.id):
                    print("resp[1]")
                    shared.queues[interaction.guild.id].soundq.put(resp[0][0])
                    print(shared.queues[interaction.guild.id].soundq.qsize())
                    await interaction.response.send_message("Put Into Queue",ephemeral=True)
                else:
                    await interaction.response.send_message("No Sound Matching Name",ephemeral=True)
            else:
                await interaction.response.send_message("No Sound Matching Name",ephemeral=True)
        else:
            await interaction.response.send_message("Not in a voice channel", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="soundlist")
@app_commands.allowed_contexts(guilds=True)
async def _soundlist(interaction : discord.Interaction):
    try:
        views = FruitView(interaction.guild.id)
        await interaction.response.send_message(view=views, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

async def PlayingQueue():
    while True:
        sleepdura:float
        
        
        await asyncio.sleep(0)



"""
old queueing 
if openvoiceclients:
            for x in openvoiceclients:
                if x in shared.queues:
                    if not shared.queues[x].soundq.empty():
                        if not openvoiceclients[x].is_playing():
                            print("QQQ")
                            filepath = shared.queues[x].soundq.get()
                            openvoiceclients[x].play(discord.FFmpegOpusAudio(filepath))"""       
        

def run_bot():
    client.run(jsondict.get("token"))