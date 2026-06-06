import asyncio
import discord
from pocket_tts import TTSModel
import scipy.io.wavfile
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

class soundqueue():
    
    def __init__(self,guildid:int,VoiceClient : discord.VoiceClient):
        self.guildid : int = guildid
        self.soundq = asyncio.Queue()
        self.voiceclient : discord.VoiceClient = VoiceClient

async def GenerateTTS(TextString, Voice):
        pass


async def QueueWorker(queue : soundqueue):

    while True:
        try:
            triple = await queue.soundq.get()
            if triple[0] == "TTS":
                soundfile = GenerateTTS(triple[1],triple[2])
                queue.soundq.task_done()
            elif triple[0] == "SoundFile":
                finished = asyncio.Event()
                queue.voiceclient.play(discord.FFmpegOpusAudio(triple[1]),after=lambda e: finished.set())
                await finished.wait()
                if not queue.voiceclient.is_playing():
                    queue.soundq.task_done()
            else:
                raise ValueError("Invalid Type for queue Check supported types in the shared.py lines 4-10 ")
        except Exception as e:
            print(e)


async def CreateQueueWorker(guildID):
    queues[guildID] = soundqueue(guildID,voiceclients[guildID])
    queuetasks[guildID] = asyncio.create_task(QueueWorker(queues[guildID]))

async def GenerateTTSModels():
    ttsmodeltest = TTSModel.load_model()
    ttsmodelvoicestate = ttsmodeltest.get_state_for_audio_prompt("alba")
    audio = ttsmodeltest.generate_audio(ttsmodelvoicestate, "TESTING, testing, fat chud gooner lmao")
    scipy.io.wavfile.write("TTS/output.wav",ttsmodeltest.sample_rate,audio.numpy())
    return

async def KillQueue(GuildID):
    queuetasks[GuildID].cancel()