import asyncio
import discord
from piper import PiperVoice
import wave
from enum import StrEnum
import os
"""
queue Template tuple ref = (Type,FilePath,Duration)
queue TTS tuple ref = ("TTS",Text,Voice)
queue SoundFile ref = ("SoundFile",FilePath,Duration)
Accepted Types:
    TTS: must be passed with the filepath being the one it can save too,and the duration is 1
    SoundFile: as normal
"""
ttsmodeltest = None
ttsmodelvoicestate = None
queues = {}
queuetasks = {}
voiceclients = {}
queuecontents = {}


class TTSVoices(StrEnum):
    alan ="TTSvoices/en_GB-alan-medium.onnx"
    cori ="TTSvoices/en_GB-cori-medium.onnx"
    southwoman = "TTSvoices/en_GB-southern_english_female-low.onnx"
    VCTK = "TTSvoices/en_GB-vctk-medium.onnx"
    lessac = "TTSvoices/en_US-lessac-medium.onnx"
    norman = "TTSvoices/en_US-norman-medium.onnx"

class soundqueue():
    
    def __init__(self,guildid:int,VoiceClient : discord.VoiceClient):
        self.guildid : int = guildid
        self.soundq = asyncio.Queue()
        self.voiceclient : discord.VoiceClient = VoiceClient
        self.ttsnum = 0


async def QueueWorker(queue : soundqueue):

    while True:
        try:
            triple = await queue.soundq.get()
            if triple[0] == "TTS":
                queue.tssnum = queue.ttsnum + 1
                soundfile = await GenerateTTS(triple[2],triple[1],queue.guildid,queue.ttsnum)
                finished = asyncio.Event()
                queue.voiceclient.play(discord.FFmpegOpusAudio(soundfile),after=lambda e: finished.set())
                await finished.wait()
                if not queue.voiceclient.is_playing():
                    os.remove(soundfile)
                    queuecontents[queue.guildid].pop(0)
                    queue.soundq.task_done()
            elif triple[0] == "SoundFile":
                finished = asyncio.Event()
                queue.voiceclient.play(discord.FFmpegOpusAudio(triple[1]),after=lambda e: finished.set())
                await finished.wait()
                if not queue.voiceclient.is_playing():
                    queuecontents[queue.guildid].pop(0)
                    queue.soundq.task_done()
            else:
                raise ValueError("Invalid Type for queue Check supported types in the shared.py lines 4-10 ")
        except Exception as e:
            print(e)


async def CreateQueueWorker(guildID):
    queues[guildID] = soundqueue(guildID,voiceclients[guildID])
    queuetasks[guildID] = asyncio.create_task(QueueWorker(queues[guildID]))
    queuecontents[guildID] = []

async def GenerateTTS(Voice : str,Text : str,GuildID,num : int) -> str:
    voice = PiperVoice.load(Voice)
    filename =  "TTS/"+ str(GuildID) + str(num) + ".wav"
    with wave.open(filename, "wb") as wav_file:
        voice.synthesize_wav(Text, wav_file)
    return filename

async def KillQueue(GuildID):
    queuetasks[GuildID].cancel()