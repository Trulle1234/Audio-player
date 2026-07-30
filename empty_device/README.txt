|================|
|  USER'S MANUAL |
|================|

ADDING AUDIO
------------

Place audio files inside one of the numbered folders in the "channels" folder.
!!! Only MP3, WAV, OGG and FLAC files are supported. !!!

To give a channel a custom name, create a file named "name.txt" inside its
folder. Write the channel name on the first line of the file, try to keep it short.

To add another channel, create a new folder using the next number in the
sequence.

!!! Channel folders should be numbered continuously without missing numbers. !!!

!!! Do not delete or change "state.json" or "volume.txt". !!!

SELECTING A CHANNEL
-------------------

Use UP and DOWN to select a channel.
Press RIGHT to open and play the selected channel.

PLAYER CONTROLS
---------------

UP - Turn shuffle mode on or off.

DOWN - Pause or resume playback.

RIGHT - Skip to the next track.

LEFT - Return to the previous track.

VOLUME UP (in terminal W)- Increase volume by 5 points.

VOLUME DOWN (in terminal S)- Decrease volume by 5 points.

To return to the channel selector:

1. Press DOWN to pause playback.
2. Press LEFT.

To play from a specific minute:

1. Press DOWN to pause playback.
2. Press RIGHT.
3. Use UP and DOWN to choose the starting minute.
4. Press RIGHT to begin playback from there.

TRACK INFORMATION
-----------------

The player will use the title and artist stored in the audio file when available.

For podcasts, it will display the episode title and podcast name.
If your podcast is not detected as one, add "podcast" to the file name.

If no usable information is stored in the file, the player will create a title
from the filename.

PROGRESS SAVING
---------------

If a track is detected as a podcast (according to what is stated above)
the program will auto save progress and start from there on next play.

If you wish to reset the saved time, jump to the start of the track.