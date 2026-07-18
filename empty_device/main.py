import os
import time
import random
import re
import keyboard
from pathlib import Path
from mutagen import File
from glob import glob
from pygame import mixer

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def sort_tracks(paths):
    return sorted(paths, key=lambda path: (os.path.getmtime(path), Path(path).name.lower()))

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
        return "🎙️  " + track[1] + (" 🔀" if shuffle else " ➡️") 
    else:
        return "🎵  " + track[1] + (" 🔀" if shuffle else " ➡️")

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

shuffle = False
playing = True
queue = sort_tracks(glob(f"channels/{str(channel)}/*.mp3"))
mixer.init()

try:
    with open(f"channels/{channel}/name.txt", "r", encoding="utf-8") as file:
        name = file.readline().strip()
        if name:
            print(f"Playing channel {channel} - {name} " + ("🔀" if shuffle else "➡️"))
        else:
            print(f"Playing channel {channel} " + ("🔀" if shuffle else "➡️"))
except FileNotFoundError:
    print(f"Playing channel {channel} " + ("🔀" if shuffle else "➡️"))

time.sleep(3)

while True:
    if shuffle:
        random.shuffle(queue)
    else:
        queue = sort_tracks(queue)

    track_i = 0

    while 0 <= track_i < len(queue):
        track = queue[track_i]

        mixer.music.load(track)
        mixer.music.play()

        clear()
        print(get_track_text(track))

        dir = 1

        while mixer.music.get_busy() or not playing:
            time.sleep(0.1)

            if keyboard.is_pressed("up"):
                clear()
                shuffle = not shuffle
                print("Shuffle is " + ("on 🔀 " if shuffle else "off ➡️ "))
                mixer.music.stop()
                time.sleep(1)
                dir = 0
                track_i = len(queue)
                break

            elif keyboard.is_pressed("down"):
                clear()
                playing = not playing
                if playing:
                    mixer.music.unpause()
                    print(get_track_text(track))
                else:
                    mixer.music.pause()
                    print("Playback paused ⏸️")

            elif keyboard.is_pressed("right"):
                clear()
                print("Skipping...")
                mixer.music.stop()
                dir = 1
                time.sleep(0.5)
                break

            elif keyboard.is_pressed("left"):
                clear()

                if track_i > 0:
                    print("Going back...")
                    mixer.music.stop()
                    dir = -1
                    time.sleep(0.5)
                else:
                    print("Currently on first track")
                    dir = 0
                    time.sleep(0.5)
                    clear()
                    print(get_track_text(track))

        track_i += dir