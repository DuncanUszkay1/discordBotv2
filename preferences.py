from models import Trigger
import stringHelper
import asyncio
import dogBot
import triggers

#The purpose of this file is to have a configurable list of variables which dictate the bots function

def audio_function(source,channel_function): #Audio
    return lambda e,d: d.play_sound(source,channel_function(e))

def text_function(text):
    return lambda e,d: d.simple_reply(e,text)

def text_condition(match,command):
    if(not command):
        return lambda e,d: (match in e.content and e.author.id != d.get_id())
    else:
        return lambda e,d: (e.content == ("!" + match) and e.author.id != d.get_id())

def audio_channel_of_messenger(message):
    return message.author.voice.voice_channel.id

def audio_channel_of_voice_state_changer(member):
    return member.voice.voice_channel.id

def entrance_music(user_id,filename): #Sound played on user entrance
    return Trigger((lambda e,d: (triggers.is_entrance(e,d) and (e.afterMember.id == user_id))),
        audio_function("data/"+filename,audio_channel_of_voice_state_changer))
    
def soundboard(command,filename): 
    return Trigger(text_condition(command,True),
        audio_function("data/"+filename,audio_channel_of_messenger));

def exit_music(command,filename): 
    return Trigger((lambda e,d: (triggers.is_exit(e,d) and (e.afterMember.id == user_id))),
        audio_function("data/"+filename,audio_channel_of_voice_state_changer))

def streaming_audio(command,url):
    return Trigger(text_condition("!stream "+command,True),
        audio_function(url,audio_channel_of_messenger))

def reply_to_match(match,reply):
    return Trigger(text_condition(match,False),text_function(reply));

def force_error(command):
    return Trigger(text_condition(command,True), lambda e,d: d.force_error())

def refresh(command):
    return Trigger(text_condition(command,True), lambda e,d: d.refresh())

def generate_triggers(filename,func,end_code=""):
    triggers = [];
    pairs = stringHelper.parse_pairings_file(filename,end_code)
    for pair in pairs:
        triggers.append(func(pair[0],pair[1]))
    return triggers

class config:
    def __init__(self,settings_file,debug):
        self.settings_file = settings_file
        self.debug = debug
        self.read_settings()
    def read_settings(self):
        #Read in the bot settings:
        try:
            settings = stringHelper.trim_comments_and_newlines(self.settings_file)
        except IOError:
            raise IOError("Error, settings file cannot be opened")
        try:
            self.botName = settings[0]
            self.botId = settings[1]
            self.botToken = settings[2]
            self.voiceVolume = settings[3]
            self.voiceChannel = settings[4] 
            #This is an array of boolean function void function pairs (b,f)  with "Event satisfies b, do f"
            #All response functions must be defined in clientInteractions.py as an asyncio coroutine
            #Remember: These are ordered. Once one is found the rest are skipped over!
            self.text_listeners = [];
            self.audio_listeners = [];
            self.text_listeners += generate_triggers(settings[5],soundboard)
            self.text_listeners += generate_triggers(settings[6],streaming_audio)
            self.text_listeners += generate_triggers(settings[7],reply_to_match)
            self.audio_listeners += generate_triggers(settings[8],entrance_music)
            self.audio_listeners += generate_triggers(settings[9],exit_music)
            self.text_listeners.append(refresh("refresh"))
            if(self.debug):
                self.text_listeners.append(force_error("force"))
        except IndexError:
            raise IndexError("Error, settings file is invalid.")
