from pathlib import Path
from qbittorrentapi import Client, LoginFailed
from pytube import YouTube, Playlist
import shutil, os, time
from requests import post

FILETYPES = ['.webm', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.ogg', '.mp4', '.m4p',
                  '.m4v', '.avi', '.wmv', '.mov', '.qt', '.flv', '.swf', '.avchd', '.srt']

CHARS = ['\\', '/', '|', ':', '*', '?', '<', '>', '"']


def DownloadTorrent(baseFolder: Path, url: str, to: Path, name: str):  # I swear, I don't torrent anything illegal, bro. I just download game mods and linux distro's using torrent please don't tell the authorities. Nothing is going on.
    global FILETYPES, CHARS  # Add (optional) download speed in args

    qb = Client(host="http://127.0.0.1:8080/", username="Glippus", password="hihihi")

    try:
        qb.auth_log_in()
    except LoginFailed as e:
        print(e)

    qb.torrents_add(urls=[url], save_path=str(baseFolder / 'tmp'))
    qb.torrents_reannounce('all')

    while True:
        time.sleep(1)
        torrent = qb.torrents_info()[-1]

        if torrent.state_enum.is_uploading or torrent.state_enum.is_complete:
            for file in Path(torrent.content_path).glob('**/*'):
                typeMatchFound = bool([True for fileType in FILETYPES if fileType in str(file)])

                if not typeMatchFound:
                    os.remove(str(file.absolute()))
                else:
                    if name:
                        oldName = '.'.join(file.name.split('.')[0: -1])
                        newName = file.name.replace(oldName, name)

                        file.rename(str(baseFolder / to / newName))
            shutil.rmtree(torrent.content_path)
            return


def DownloadYouTube(url: str, to: Path, name=None):  # Playlist support, channel support?
    global CHARS

    video = YouTube(url)

    if not name:
        name = video.title

    for char in CHARS:
        name = name.replace(char, '')
    print(f"1. {url}\n2. {to}\n3. {name}")

    stream = video.streams.filter(file_extension='mp4').get_highest_resolution()
    stream.download(str(to), f"{name}.mp4")

    print('Done.')


def DownloadTVurl(url: str, to: Path, name=None):

    payload = {"mode": "initiate",
               "link": url,
               "options": {"size": "large",
                           "download_tt888": True}}

    response = post(url="https://www.downloadgemist.nl/core/hyperbridge.php", json=payload)
    print(response)
    print(response.text)

def DownloadManager(baseFolder: Path, url: str, to: Path, name=None):  # Add filetype check, only want video's.
    match url:
        case url if 'youtube' in url or 'youtu.be' in url:
            url = url.split('&t=')[0]

            if '/playlist?' in url:
                try:
                    playlist = Playlist(url)
                except Exception as e:
                    print(f'Page loading error: {e}.')
                    return

                for index, video in enumerate(playlist.video_urls, start=1):
                    if not name:
                        DownloadYouTube(video, to)
                    else:
                        DownloadYouTube(video, to, f'{name} {index}')
            else:
                DownloadYouTube(url, to, name)

        case url if 'magnet:?' in url:
            DownloadTorrent(baseFolder, url, to, name)

        case _:
            pass
