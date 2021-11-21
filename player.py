from argumenthandler import TFCheck, FolderCheck
from random import shuffle
from pathlib import Path
from subprocess import call
from typing import Union

from time import perf_counter, sleep
from vlc import MediaPlayer

queue = list()  # List of filepaths
currentVideo = MediaPlayer()
videoStartTime = 0
videoPauseTime = 0


# Add repeat video toggle.

def CheckVideoEnd():  # TODO: Test this.
    global videoStartTime, videoPauseTime

    pauseDuration = 0

    while True:
        sleep(0.01)

        if currentVideo.get_length() == -1:
            continue

        if videoPauseTime:  # Moving the start time when it's paused. Best way to handle video length checking.
            pauseDuration = perf_counter() - videoPauseTime
        else:
            videoStartTime += pauseDuration
            pauseDuration = 0

        if perf_counter() - videoStartTime > currentVideo.get_length() / 1000 and not currentVideo.is_playing():
            Stop()


def GetVideoInfo(path) -> str:  # Use ffmpeg module for this (not inhouse).
    return path


def PlayPause():
    global currentVideo, videoPauseTime

    if currentVideo.get_length() == -1:
        NextVideo()

    if currentVideo.is_playing():
        currentVideo.pause()
        videoPauseTime = perf_counter()
    else:
        currentVideo.play()
        videoPauseTime = 0


def ViewCurrent():
    global currentVideo

    print(f"  {GetVideoInfo(currentVideo)}")


def NextVideo():
    global queue

    if not queue:
        print("No video's in queue.")
        return

    PlayVideo(queue.pop())


def Stop():
    global currentVideo

    if currentVideo.get_length() == -1:
        print('No video is playing.')
        return
    currentVideo.stop()
    currentVideo = MediaPlayer()


def PlayVideo(video: str):
    global currentVideo, videoStartTime

    if currentVideo.get_length() != -1:
        Stop()

    print(f"Playing '{video}'.")
    currentVideo = MediaPlayer(video)  # TODO: See if you can read whether the video ended from the object.

    videoStartTime = perf_counter()
    currentVideo.play()
    currentVideo.set_fullscreen(True)

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

    override = 'F'
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
