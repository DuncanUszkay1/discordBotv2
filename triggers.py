def is_entrance(e,d):
    before_state = e.beforeMember.voice
    after_state = e.afterMember.voice
    voice_channel = d.get_default_voice_channel()
    if((before_state.voice_channel == None or 
        before_state.voice_channel.id != voice_channel) and
        after_state.voice_channel.id == voice_channel):
        return True
    return False

def is_exit(e,d):
    before_state = e.beforeMember.VoiceState
    after_state = e.afterMember.VoiceState
    voice_channel = d.get_default_voice_channel()
    if(before_state.voice_channel.id == voice_channel and
        (after_state.voice_channel == None or
        after_state.voice_channel.id != voice_channel)):
        return True
    return False
