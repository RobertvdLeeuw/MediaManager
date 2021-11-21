#from requests import get
from pathlib import Path
#from qbittorrent import Client  # https://www.thepythoncode.com/article/download-torrent-files-in-python

videoFileTypes = ['.webm', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.ogg', '.mp4', '.m4p',
                  '.m4v', '.avi', '.wmv', '.mov', '.qt', '.flv', '.swf', '.avchd']


def DownloadManager(url: str, to: Path, name: str):  # Add filetype check, only want video's.
    match url:
        case url if 'youtube' in url or 'youtu.be' in url:
            YouTube(url, to, name)

        case _:
            Torrent(url, to, name)


def Torrent(url: str, to: Path, name: str):  # I swear, I don't torrent anything illegal, bro. I just download game mods and linux distro's using torrent please don't tell the authorities. Nothing is going on.
    pass


def YouTube(url: str, to: Path, name: str):  # Playlist support, channel support?
    pass

# Spotify? TV?
