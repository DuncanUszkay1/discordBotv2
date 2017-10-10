import asyncio
import urllib.request
import urllib.parse
import datetime

#This class holds client objects so we don't have to refetch them
class ClientData:
    def __init__(self):
        self.channels = {}
        self.emojis = {}
        self.voiceBusy = False
        self.voiceConnection = False
        self.voiceChannel = None
    def fetch(self,client):
        for server in client.servers:
            for emoji in server.emojis:
                self.emojis[emoji.name] = emoji.url
        

class Logger:
    def __init__(self,level):
        self.level = level
    def log(self,level,message):
        if(self.level != "silent"):
            if(self.level == "verbose"):
                self.create_entry(message)
            elif(level == "n"):
                self.create_entry(message)
    def create_entry(self,message):
        print(str(datetime.datetime.now()) + ": " + message);

            

#This class represents a relationship between a detected word and a response
class Trigger:
    def __init__(self, predicate, reaction):
        self.predicate = predicate;
        self.reaction = reaction;

class VoiceEvent:
    def __init__(self, beforeMember, afterMember):
        self.beforeMember = beforeMember
        self.afterMember = afterMember
