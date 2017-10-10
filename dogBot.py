import asyncio
import models
import stringHelper as sh
import preferences as p
import io
import datetime
import discord
import types

#The purpose of this file is to hold code pertaining to client interactions
class DogBot:     
    def __init__(self, settings_file, log_mode, debug, loop=None):
        self.logger = models.Logger(log_mode)
        #self.client = discord.Client()
        self.client = discord.Client(loop = loop)
        self.clientData = models.ClientData() 
        self.config = p.config(settings_file,debug)
    def get_id(self):
        return self.config.botId

    def get_token(self):
        return self.config.botToken

    def get_default_voice_channel(self):
        return self.config.voiceChannel
    
    @asyncio.coroutine
    async def refresh(self):
        self.logger.log('v','Refreshing Config...')
        self.config = p.config(self.config.settings_file,self.config.debug)

    @asyncio.coroutine
    async def force_error(self):
        #Here we create a fake error then raise it, to simulate a connection issue
        #There are a couple of ways to create an object out of a dictionary, this is the cleanest of them
        error_info = types.SimpleNamespace(code=1013,reason='Error was forced by client')
        raise discord.ConnectionClosed(error_info)
    
    @asyncio.coroutine
    async def makeover(self,name,user):
        self.client.change_nickname(user,name);

    @asyncio.coroutine
    async def notify_text_listeners(self,eventData):
        for trigger in self.config.text_listeners:
            if trigger.predicate(eventData,self):
                await trigger.reaction(eventData,self)
                break
    
    @asyncio.coroutine
    async def notify_audio_listeners(self,eventData):
        for trigger in self.config.audio_listeners:
            if trigger.predicate(eventData,self):
                await trigger.reaction(eventData,self)

    def set_voice_free(self):
        self.clientData.voiceBusy = False

    @asyncio.coroutine
    async def play_jams(self,message,song_channel,queue_channel):
        counter = 0
        async for msg in self.client.logs_from(song_channel, limit=200):
            if(counter != 15 and sh.is_a_song(msg.content)):
                await asyncio.sleep(1)
                counter = counter + 1
            await self.client.send_message(queue_channel, "!play " + sh.strip_song_message(msg.content))
        await self.client.send_message(message.channel, p.PersonalCollection)
        await self.client.send_message(message.channel, "!queue")

    @asyncio.coroutine
    async def simple_reply(self,message,reply):
        await self.client.send_message(message.channel, reply)
    
    @asyncio.coroutine
    async def play_sound(self,source,channel):
        await self.silence()
        if(hasattr(self.clientData,'player') and self.clientData.player.is_playing()):
            return None    
        if(not self.clientData.voiceConnection):
            await self.connect_to_voice(channel)
        self.clientData.player = self.clientData.voice.create_ffmpeg_player(source)
        self.clientData.player.volume = float(self.config.voiceVolume)
        self.clientData.player.start()

    @asyncio.coroutine
    async def silence(self):
        if(hasattr(self.clientData,'player') and self.clientData.player.is_playing()):
            self.clientData.player.stop()

    @asyncio.coroutine
    async def connect_to_voice(self,channel):
        if(channel == None): channel = self.get_default_voice_channel()
        self.clientData.voice = await self.client.join_voice_channel(
            self.client.get_channel(channel))
        self.clientData.voiceConnection = True

    @asyncio.coroutine
    async def on_startup(self):
        self.logger.log('n','Bot started at ' + str(datetime.datetime.now()))
    
    @asyncio.coroutine
    async def disconnect_from_voice(self):
        if(hasattr(self.client,'voice') and self.client.voice.is_connected()):
            await self.client.voice.disconnect()

    def shut_down(self):  
        try:
            self.logger.log('v','Ensuring bot is out of voice')
            self.client.loop.run_until_complete(self.disconnect_from_voice())
            self.client.close()
            self.client.loop.run_until_complete(self.client.logout())
            self.client.loop.close()
            self.logger.log('n','Bot shut down at ' + str(datetime.datetime.now()))
        except BaseException as e:
            self.logger.log('n','Error in shutting down bot:')
            self.logger.log('n',str(e))
