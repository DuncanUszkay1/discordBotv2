import discord
import asyncio
import datetime
import models
import preferences
import stringHelper
import dogBot
import sys

settings_file = ""
log_mode = "normal"
debug = False
arg_count = len(sys.argv)
if(arg_count == 2):
    settings_file = sys.argv[1]
elif(arg_count == 3):
    settings_file = sys.argv[1]
    log_mode = sys.argv[2]
elif(arg_count == 4):
    settings_file = sys.argv[1]
    log_mode = sys.argv[2]
    if(sys.argv[3] == "DEBUG"):
        debug = True
else:
    print("run_bot.py [settings file][log mode][optional DEBUG]") 
    quit()

class DiscordLoopHandler:
    def __init__(self,dog,event_loop):
        self.dog = dog
        self.future = None
        self.event_loop = event_loop
        self.last_start_time = datetime.datetime.now()
    def start_bot(self):
        self.dog.logger.log('v','Starting initialization procedure..')
        try:
            self.dog.logger.log('v','Logging in...')
            self.future = asyncio.ensure_future(self.dog.client.login(self.dog.get_token()),loop=self.event_loop)
            self.event_loop.run_until_complete(self.future)
        except discord.LoginFailure:
            self.dog.logger.log('n','Failed to login with given token.')
            raise
        except discord.HTTPException:
            self.dog.logger.log('n','Failed to login due to unknown http error.')
            raise
        except RuntimeError:
            self.dog.logger.log('n','Failed due to RuntimeError')
            raise
        except BaseException as e:
            self.dog.logger.log('n','Failed due to unknown error')
            self.dog.logger.log('v',str(e))
            raise
        try:
            self.dog.logger.log('v','Connecting to Discord Service...')
            self.future = asyncio.ensure_future(self.dog.client.connect(),loop=self.event_loop)
            self.dog.logger.log('v','Connected')
            self.future.add_done_callback(self.bot_callback)
            self.event_loop.run_until_complete(self.future)
        except discord.GatewayNotFound:
            self.dog.logger.log('n','Gateway not found, check discord API status for outages.')
            raise
        except discord.ConnectionClosed:
            self.dog.logger.log('n','Connection to discord closed.')
            raise 
        except KeyboardInterrupt:
            self.dog.logger.log('n','Manual shut down detected')
            self.dog.shut_down()
            raise
        except BaseException as e:
            self.dog.logger.log('n','Unexpected Error Occured') 
            self.dog.logger.log('v',str(e))
            raise
    def bot_callback(self,*args, **kwargs):
        exc = self.future.exception()
        if exc:
            self.dog.logger.log('n',"Error occured which halted bot")
        else:
            self.dog.logger.log('n',"Bot connection halted peacefully")

def run_bot(settings_file,log_mode,debug):
    event_loop = asyncio.new_event_loop()
    dog = dogBot.DogBot(settings_file,log_mode,debug,event_loop);
    loop_handler = DiscordLoopHandler(dog,event_loop)
    @dog.client.event
    async def on_ready():
        await dog.on_startup()
    @dog.client.event
    async def on_message(message):
        await dog.notify_text_listeners(message)
    @dog.client.event
    async def on_voice_state_update(beforeMember,afterMember):
        await dog.notify_audio_listeners(models.VoiceEvent(beforeMember,afterMember))
    @dog.client.event
    async def on_error(error,*args,**kwargs):
        loop_handler.future.set_exception(sys.exc_info()[1]) 
        #sys.exc_info() is a tuple of three values, the second of which is an exception
        #the set_exception method causes the future to finish, which then call ours callback function
        #in the callback function we can see that we got an error, then we can handle it
    try:
        loop_handler.start_bot()
    except discord.ConnectionClosed:
        return 1
    except:
        return 0

#run_bot returns 0 unless it crashes due to a connection being closed, if that happens we want to restart
while(run_bot(settings_file,log_mode,debug)):
    print("CONNECTION LOSS DETECTED")
    print("ATTEMPING TO RECONNECT IN 20 SECONDS...")
    print("RESTARTING...")
    
        
