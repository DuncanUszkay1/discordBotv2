import preferences as p
def strip_song_message(message):
    tokens = message.split(" ");
    i = 0
    t = len(tokens)
    while i < t and not is_a_song(tokens[i]):
        i = i + 1
    if i < t:
        return tokens[i]
    return False

def is_a_song(message):
    for a in p.stringBank.songMatchTokens:
        if(a in message):
            return True 

def trim_comments_and_newlines(filename):
    trimmed_lines = []
    f = open(filename,'r')
    for line in f:
        if not line.startswith("#"):
            trimmed_lines.append(line[:-1]) #Last character of a line is always \n, so we remove it
    return trimmed_lines

#Parse a text file into an array of lines, removing comments and optionally filtering on an ending
def parse_pairings_file(filename,end_code):
    pairs = [];
    f = open(filename,'r')
    for line in f:
        tokens = line.split(':',1)
        if not tokens[0].startswith("#") and len(tokens) == 2 and tokens[0].endswith(end_code):
            if(tokens[1].endswith("\n")): tokens[1] = tokens[1][:-1]
            pairs.append(tokens)
    return pairs;

