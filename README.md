# MP3 Player

This is a simple terminal-based MP3 player.

The interface is intentionally limited to one line of text because I eventually plan to build a physical version using a small text-based LCD display. Think of the current program as a digital simulation: the terminal acts as the display, and the arrow keys act as the device’s physical buttons.

## Use the prebuilt version

1. [Download the `empty_device` folder](https://download-directory.github.io/?url=https%3A%2F%2Fgithub.com%2FTrulle1234%2Fmp3-player%2Ftree%2Fmain%2Fempty_device).
2. Extract the downloaded ZIP file.
3. Open the extracted folder.
4. Follow the instructions in `README.txt`.

## Run from source

### 1. Clone the repository

```bash
git clone https://github.com/Trulle1234/mp3-player
cd mp3-player
```

### 2. Install the required packages

```bash
pip install keyboard mutagen pygame
```

### 3. Run the player

```bash
py main.py
```

## Build a standalone executable

First, install PyInstaller:

```bash
pip install pyinstaller
```

Then build the executable:

```bash
pyinstaller py -m PyInstaller --onefile --console main.py
```

The finished executable will be created in the `dist/` folder, move it into root. You can safley delete delete `build/` and `main.spec`.

```text
dist/main.exe
```
