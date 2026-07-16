import os
import time
import random
import re
from pathlib import Path
from mutagen import File
from glob import glob
from pygame import mixer

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_track_meta(path):
    audio = File(path, easy=True)

    if audio is None or not audio.tags:
        return None
    
    def get_tag(name):
        values = audio.tags.get(name)

        if not values:
            return None

        return values[0]

    title = get_tag("title")
    artist = get_tag("artist")
    album = get_tag("album")
    genre = get_tag("genre")

    genre = genre.lower().strip() if genre else ""

    if genre == "podcast" and title and album:
        return {
            "title": title,
            "artist": album,
            "type": "podcast"
        }

    if title and artist:
        return {
            "title": title,
            "artist": artist,
            "type": "music"
        }

    return None
    

def get_track_name(path):
    track_info = get_track_meta(path)

    if track_info:
        return [track_info["type"], track_info["artist"].capitalize() + " - " + track_info["title"].capitalize()]
        
    else:
        name = Path(path).stem

        name = name.replace("_", " ")
        name = re.sub(r"(?<=\w)-(?=\w)", " ", name)
        
        name = re.sub(r"\s+", " ", name).strip()

        return  ["music", name[:1].upper() + name[1:]]

    
def get_track_text(path):
    track = get_track_name(path)
    
    if track[0] == "podcast":
        return "🎙️  " + track[1]
    else:
        return "🎵  " + track[1]

nr_of_channels = len(glob("channels/*"))

while True:
    clear()

    try:
        channel = int(input(f"Please select channel (1-{nr_of_channels}): "))
    except ValueError:
        continue

    if 1 <= channel <= nr_of_channels:
        break

clear()

queue = glob(f"channels/{str(channel)}/*.mp3")
mixer.init()

try:
    with open(f"channels/{channel}/name.txt", "r", encoding="utf-8") as file:
        name = file.readline().strip()
        if name:
            print(f"Playing channel {channel} - {name}")
        else:
            print(f"Playing channel {channel}")
except FileNotFoundError:
    print(f"Playing channel {channel} 🔀")

time.sleep(3)

while True:
    random.shuffle(queue)

    for track in queue:
        mixer.music.load(track)
        mixer.music.play()

        clear()
        print(get_track_text(track))

        while mixer.music.get_busy():
            time.sleep(0.1)