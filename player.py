from argumenthandler import TFCheck, FolderCheck
from random import shuffle
from pathlib import Path
from subprocess import call

import vlc

queue = list()
currentVideo = None


# Add repeat video toggle.


def GetVideoInfo(path):  # Use ffmpeg module for this (not inhouse).
    return path


def PlayPause():
    global currentVideo

    pass


def ViewCurrent():
    global currentVideo

    print(f"  {GetVideoInfo(currentVideo)}")


def NextVideo() -> None:
    global queue, currentVideo
    PlayVideo(queue.pop())


def Stop():
    global currentVideo

    currentVideo = None


def PlayVideo(video):
    global currentVideo

    Stop()

    print(f"Playing '{video}'.")
    currentVideo = video

    # Open a thread to sleep for as long as video plays, then pop next? Stop during nonplay (State.Ended? Ln 708).


def PlayFrom(baseFolder: Path, *folders):  # options are baked into folders, if present.
    ClearQueue()
    Stop()
    folders = list(folders)  # Required for popping

    recursive = 'F'
    if folders[0] in ('T', 'F'):
        recursive = folders.pop(0)

    if (recursive := TFCheck(recursive)) is None:
        return

    for folder in folders:
        if FolderCheck(baseFolder, folder):
            for video in folder.glob('**/*' if recursive else '*'):
                if not video.is_dir():
                    queue.append(video)


def AddToQueue(folder: Path, *items):  # options are baked into items, if present.
    global queue, currentVideo
    items = list(items)  # Required for popping.

    override = 'F':
    if items[0] in ('T', 'F'):
        override = items.pop(0)

    recursive = 'F'
    if items[0] in ('T', 'F'):
        recursive = items.pop(0)

    if (override := TFCheck(override)) is None:
        return
    elif override:
        ClearQueue()
        Stop()

    if 'search' not in recursive:
        if (recursive := TFCheck(recursive)) is None:
            return

    for item in items:
        if (folder / item).exists():
            if (folder / item).is_dir():  # Folders
                for video in item.glob('**/*' if recursive else '*'):
                    queue.append(video)
            else:  # Files
                queue.append(item)

    if currentVideo is None:
        PlayVideo(queue.pop())  # Playing the first enqueued video.


def ClearQueue():
    global queue

    queue = list()


def ViewQueue():
    global queue

    for index, item in enumerate(queue):
        print(f"  {index}: {GetVideoInfo(item)}")


def ShuffleQueue():
    global queue

    shuffle(queue)


def ChangeVolume(volume: str):
    try:
        volume = int(volume)

        if 0 <= volume <= 100:
            call(["amixer", "-D", "pulse", "sset", "Master", f"{volume}%"])  # Does this work on OS'es besides Linux?
        else:
            print('Volume must be between 0 and 100.')
    except ValueError:
        print('Incorrect volume argument.')
