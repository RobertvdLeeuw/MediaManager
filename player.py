from argumenthandler import TFCheck, FolderCheck

from pathlib import Path
from subprocess import call
# import vlc

queue = list()
currentVideo = None


def GetVideoInfo(path):  # Use ffmpeg module for this (not inhouse).
    return path


def PlayPause():
    global currentVideo

    pass


def ViewCurrent():
    global currentVideo

    print(f"  {GetVideoInfo(currentVideo)}")


def NextVideo():
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


def PlayFrom(basefolder, recursive, *folders):
    ClearQueue()
    Stop()

    if (recursive := TFCheck(recursive)) is None:
        return

    for folder in folders():
        if FolderCheck(basefolder, folder, item):
            for video in item.glob('**/*' if recursive else '*'):
                queue.append(video)


def AddToQueue(folder, override, recursive, items):  # Could be video(s) or folder(s)?
    global queue, currentVideo

    if (override := TFCheck(override)) is None:
        return
    elif override:
        ClearQueue()
        Stop()

    if 'search' not in recursive:  # If you want to add from the search results the third argument, for which recursion isn't needed.
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


def ChangeVolume(volume):
    try:
        volume = int(volume)
    except:
        print('Incorrect volume argument.')
    else:
        if 0 <= volume <= 100:
            call(["amixer", "-D", "pulse", "sset", "Master", f"{volume}%"])
        else:
            print('Volume must be between 0 and 100.')
