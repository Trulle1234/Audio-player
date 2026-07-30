import os
import sys
import time
import random
import re
import json
import keyboard
import pyvolume
from pathlib import Path
from mutagen import File
from glob import glob
from pygame import mixer

# get file location
if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).parent)

# clear terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# check for key release
def wait_for_release(key):
    while keyboard.is_pressed(key):
        time.sleep(0.01)

# sort tracks by date modified
def sort_tracks(paths):
    return sorted(paths, key=lambda path: (os.path.getmtime(path), Path(path).name.lower()))

def get_volume():
    with open("volume.txt", "r", encoding="utf-8") as f:
        volume = f.readline().strip()

    if volume == "":
        volume = "20"

        with open("volume.txt", "w", encoding="utf-8") as f:
            f.write(volume)

    return int(volume)

# get track metadata
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

    if "podcast" in path.lower():
        return { "type": "podcast" }

    elif genre == "podcast" and title and album:
        return {
            "title": title,
            "artist": album,
            "type": "podcast"
        }

    elif title and artist:
        return {
            "title": title,
            "artist": artist,
            "type": "music"
        }

    return None

# read json to get track start pos
def get_track_start(path):
    track_key = str(path)

    with open("state.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if track_key not in data:
        data[track_key] = 0

        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent = 4)

    return(data[track_key])

# update track start pos in state.json
def update_track_start(path, minute):
    track_key = str(path)

    with open("state.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data[track_key] = int(minute)

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent = 4)

# get track name (form metadata if avalible else from file name)
def get_track_name(path):
    track_info = get_track_meta(path)

    if track_info and track_info.get("title") and track_info.get("artist") and track_info.get("type"):
        return [track_info["type"], track_info["artist"].capitalize() + " - " + track_info["title"].capitalize()]
        
    name = Path(path).stem
    name = name.replace("_", " ")
    name = re.sub(r"(?<=\w)-(?=\w)", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    track_type = (
        track_info.get("type")
        if track_info and track_info.get("type")
        else "music"
    )

    return [track_type, name[:1].upper() + name[1:]]

# get info about track to display    
def get_track_text(path):
    track = get_track_name(path)
    
    if track[0] == "podcast":
        return "🎙️  " + track[1] + (" 🔀" if shuffle else " ➡️") 
    else:
        return "🎵  " + track[1] + (" 🔀" if shuffle else " ➡️")

# channel selector interface
def select_channel():
    nr_of_channels = len(glob("channels/*"))
    channel = 1

    while True:
        clear()
        print(f"Please select channel (1-{nr_of_channels}): {channel}")
        time.sleep(0.1)

        if keyboard.is_pressed("up"):
            channel += 1
        elif keyboard.is_pressed("down"):
            channel -= 1
        elif keyboard.is_pressed("right"):
            wait_for_release("right")
            break

        channel = max(1, min(channel, nr_of_channels))

    return channel

# skip to interface
def select_skip_time(path):
    audio = File(path)
    length = audio.info.length // 60

    minute = 0

    while True:
        clear()
        print(f"Please select playback start (0-{length}): {minute}")
        time.sleep(0.1)

        if keyboard.is_pressed("up"):
            minute += 1
        elif keyboard.is_pressed("down"):
            minute -= 1
        elif keyboard.is_pressed("right"):
            wait_for_release("right")
            break

        minute = max(0, min(minute, length))

    return minute

# main code to play and check for input
def play_channel(channel):
    global shuffle, playing

    clear()
    shuffle = False
    playing = True
    volume = get_volume()

    pyvolume.custom(percent = volume)

    queue = sort_tracks(
        glob(f"channels/{str(channel)}/*.mp3") +
        glob(f"channels/{str(channel)}/*.wav") +
        glob(f"channels/{str(channel)}/*.ogg") +
        glob(f"channels/{str(channel)}/*.flac")
    )
    
    queue = [f.replace("\\", "/") for f in queue]
    
    # check for empty channel
    if queue == []:
        print("Channel empty, going back...")
        time.sleep(1)
    
        return True

    mixer.init()

    # open channel
    try:
        with open(f"channels/{channel}/name.txt", "r", encoding="utf-8") as f:
            name = f.readline().strip()
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

        # channel playing loop
        while 0 <= track_i < len(queue):
            track = queue[track_i]
            track_type = get_track_name(track)[0]

            start_pos = 0

            if track_type == "podcast":
                saved_minute = int(get_track_start(track))
                start_pos = saved_minute * 60

            last_state_save = 0

            mixer.music.load(track)
            mixer.music.play(start = start_pos)

            clear()
            print(get_track_text(track))

            dir = 1

            # check for user inputs, and update state
            while mixer.music.get_busy() or not playing:
                time.sleep(0.1)

                # update state for podcasts
                if track_type == "podcast":
                    current_seconds = start_pos + max(0, mixer.music.get_pos() / 1000)

                    if time.monotonic() - last_state_save >= 5:
                        last_state_save = time.monotonic()

                        update_track_start(track, current_seconds // 60)

                # toggle shuffle
                if keyboard.is_pressed("up"):
                    wait_for_release("up")
                    clear()
                    shuffle = not shuffle
                    print("Shuffle is " + ("on 🔀 " if shuffle else "off ➡️ "))
                    mixer.music.stop()
                    time.sleep(1)
                    dir = 0
                    track_i = len(queue)
                    break

                # pause and unpause playback
                elif keyboard.is_pressed("down"):
                    wait_for_release("down")
                    clear()
                    playing = not playing
                    if playing:
                        mixer.music.unpause()
                        print(get_track_text(track))
                    else:
                        mixer.music.pause()
                        print("Playback paused ⏸️")

                # skip to minute in track
                elif keyboard.is_pressed("right") and not playing:
                    wait_for_release("right")

                    clear()
                    position = select_skip_time(track) * 60
                    start_pos = position
                    playing = True
                    mixer.music.play(start=start_pos)

                    clear()
                    print(get_track_text(track))

                # skip track
                elif keyboard.is_pressed("right"):
                    wait_for_release("right")
                    clear()
                    print("Skipping...")
                    mixer.music.stop()
                    dir = 1
                    time.sleep(0.5)
                    break

                # return to channel selection
                elif keyboard.is_pressed("left") and not playing:
                    wait_for_release("left")
                    clear()
                    print("Returning to channel selector...")
                    mixer.music.stop()
                    time.sleep(1)
                    return True

                # go to previus track
                elif keyboard.is_pressed("left"):
                    wait_for_release("left")
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

                # increse volume (system level)
                elif keyboard.is_pressed("w"):
                    wait_for_release("w")
                    clear()

                    volume += 5
                    volume = max(0, min(volume, 100))

                    with open(f"volume.txt", "w", encoding="utf-8") as f:
                        f.write(str(volume))

                    print("Volume set to " + str(volume) + "%")

                    pyvolume.custom(percent = volume)

                    time.sleep(0.5)
                    clear()
                    print(get_track_text(track))

                # decrese volume (system level)
                elif keyboard.is_pressed("s"):
                    wait_for_release("s")
                    clear()

                    volume -= 5
                    volume = max(0, min(volume, 100))

                    with open(f"volume.txt", "w", encoding="utf-8") as f:
                        f.write(str(volume))

                    print("Volume set to " + str(volume) + "%")

                    pyvolume.custom(percent = volume)

                    time.sleep(0.5)
                    clear()
                    print(get_track_text(track))
                    
            track_i += dir

    return False

# loop to select channel and then play it
while True:
    channel = select_channel()
    if play_channel(channel):
        continue